from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Document(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # PDF, DOCX, TXT, MD
    file_size = Column(Integer, nullable=False)  # size in bytes
    storage_path = Column(String, nullable=False) # local storage filepath or cloud URL
    checksum = Column(String, unique=True, index=True, nullable=False) # For duplicate prevention
    
    # Metadata & Tracking
    page_count = Column(Integer, nullable=True)
    language = Column(String, default="en")
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    processing_error = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)   # general metadata (author, keywords, etc.)
    
    # Ownership
    uploaded_by = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    content = Column(String, nullable=False)
    token_count = Column(Integer, nullable=False)
    vector_id = Column(String, nullable=True) # UUID pointing to Qdrant vector index
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class ProcessingJob(Base):
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="queued") # queued, parsing, chunking, embedding, completed, failed
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="jobs")
