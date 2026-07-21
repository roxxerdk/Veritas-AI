import hashlib
import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.document import Document, ProcessingJob
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.pipeline.ingestion_pipeline import IngestionPipeline
from app.services.vectorstore.qdrant_service import QdrantService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

# Local directory where raw uploaded documents are cached
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


def calculate_checksum(file_content: bytes) -> str:
    """Calculates SHA-256 checksum of a file to check for duplicates."""
    return hashlib.sha256(file_content).hexdigest()


def run_ingestion_pipeline(doc_id: int):
    """Worker helper to execute the background ingestion pipeline."""
    pipeline = IngestionPipeline(doc_id)
    pipeline.process()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uploads a new document, saves it, and spawns the background ingestion pipeline."""
    # Check if file format is supported
    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower().replace(".", "")
    if file_ext not in ["pdf", "docx", "txt", "md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: '.{file_ext}'. Supported formats are: PDF, DOCX, TXT, MD"
        )

    # Read file content to generate checksum
    contents = await file.read()
    checksum = calculate_checksum(contents)

    # Reset file pointer after reading contents
    await file.seek(0)

    # Check if document already exists by checksum
    existing_doc = db.query(Document).filter(Document.checksum == checksum).first()
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This file has already been uploaded (Filename: {existing_doc.filename})."
        )

    # Define local file storage path
    local_filename = f"{checksum}.{file_ext}"
    storage_path = os.path.join(UPLOAD_DIR, local_filename)

    # Write file content to local storage
    try:
        with open(storage_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save document locally: {str(e)}"
        )

    # Save Document record to DB
    new_doc = Document(
        filename=filename,
        file_type=file_ext.upper(),
        file_size=len(contents),
        storage_path=storage_path,
        checksum=checksum,
        status="uploaded",
        uploaded_by=current_user.id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Create initial ProcessingJob entry in DB
    new_job = ProcessingJob(
        document_id=new_doc.id,
        status="queued"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_doc)

    # Dispatch ingestion task asynchronously
    background_tasks.add_task(run_ingestion_pipeline, new_doc.id)

    return new_doc


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all documents uploaded by the current user."""
    return db.query(Document).filter(Document.uploaded_by == current_user.id).all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a document from local store, database, and Qdrant vector index."""
    # Look up document by ID and verify ownership
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied."
        )

    # Delete local file from disk
    if os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    # Clear vectors from Qdrant
    try:
        qdrant_service = QdrantService()
        qdrant_service.delete_document_vectors(doc.id)
    except Exception:
        # Continue db deletion even if vector store fails
        pass

    # Delete Document from DB (cascades deletes to jobs and chunks)
    db.delete(doc)
    db.commit()
    return
