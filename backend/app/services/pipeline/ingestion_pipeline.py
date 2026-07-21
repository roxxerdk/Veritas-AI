import logging
import time
import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from qdrant_client.models import PointStruct

from app.database.session import SessionLocal
from app.models.document import Document, DocumentChunk, ProcessingJob
from app.services.parsers.parser_factory import ParserFactory
from app.services.preprocessing.cleaner import TextCleaner
from app.services.chunking.recursive_chunker import RecursiveChunker
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectorstore.qdrant_service import QdrantService

logger = logging.getLogger("veritas-ai.pipeline")


class IngestionPipeline:
    def __init__(self, document_id: int):
        self.document_id = document_id
        # We spawn a fresh database session inside the pipeline background execution context
        self.db: Session = SessionLocal()
        
        # Instantiate services
        self.cleaner = TextCleaner()
        self.chunker = RecursiveChunker()
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def process(self):
        """Orchestrates the end-to-end ingestion pipeline asynchronously, updating state & capturing metrics."""
        start_time = time.time()
        metrics: Dict[str, Any] = {}
        
        # Fetch document and active job
        doc = self.db.query(Document).filter(Document.id == self.document_id).first()
        if not doc:
            logger.error(f"Ingestion failed: Document ID {self.document_id} not found in database.")
            self.db.close()
            return

        job = self.db.query(ProcessingJob).filter(
            ProcessingJob.document_id == self.document_id
        ).order_by(ProcessingJob.created_at.desc()).first()

        if not job:
            job = ProcessingJob(document_id=self.document_id, status="queued")
            self.db.add(job)
            self.db.commit()

        try:
            # 1. Parsing Phase
            job.status = "parsing"
            self.db.commit()
            
            parse_start = time.time()
            parser = ParserFactory.get_parser(doc.storage_path)
            parsed_doc = parser.parse(doc.storage_path)
            
            metrics["parse_latency_sec"] = round(time.time() - parse_start, 3)
            doc.page_count = parsed_doc.metadata.get("page_count", 1)
            self.db.commit()

            # 2. Text Cleaning Phase
            job.status = "cleaning"  # custom intermediate status
            self.db.commit()
            
            clean_start = time.time()
            cleaned_text = self.cleaner.clean(parsed_doc.text)
            metrics["clean_latency_sec"] = round(time.time() - clean_start, 3)

            # 3. Text Chunking Phase
            job.status = "chunking"
            self.db.commit()
            
            chunk_start = time.time()
            raw_chunks = self.chunker.split_text(cleaned_text)
            
            # If chunks are extracted on a per-page basis inside parser, map them
            # For simplicity, we chunk the full cleaned document text.
            metrics["chunk_count"] = len(raw_chunks)
            metrics["chunk_latency_sec"] = round(time.time() - chunk_start, 3)

            if not raw_chunks:
                raise ValueError("No text extracted or text chunking resulted in empty segments.")

            # 4. Generating Embeddings (Batch mode)
            job.status = "embedding"
            self.db.commit()
            
            embed_start = time.time()
            embeddings = self.embedding_service.embed_documents(raw_chunks)
            metrics["embedding_latency_sec"] = round(time.time() - embed_start, 3)

            # 5. Indexing Vectors (Qdrant & PostgreSQL)
            job.status = "indexing"
            self.db.commit()
            
            index_start = time.time()
            points = []
            chunk_db_objects = []

            for idx, (content, embedding) in enumerate(zip(raw_chunks, embeddings)):
                # Generate unique ID for Qdrant vector point
                vector_uuid = str(uuid.uuid4())
                
                # Setup metadata payload
                payload = {
                    "document_id": doc.id,
                    "chunk_id": idx,
                    "filename": doc.filename,
                    "page_number": 1,  # mapping page numbers dynamically can be extended later
                    "chunk_index": idx,
                    "content": content,
                    "token_count": len(content.split())  # simple word count as token heuristic
                }
                
                # Build Qdrant PointStruct
                points.append(
                    PointStruct(
                        id=vector_uuid,
                        vector=embedding,
                        payload=payload
                    )
                )

                # Build PostgreSQL Chunk object
                chunk_db_objects.append(
                    DocumentChunk(
                        document_id=doc.id,
                        chunk_index=idx,
                        page_number=1,
                        content=content,
                        token_count=payload["token_count"],
                        vector_id=vector_uuid,
                        metadata_json=payload
                    )
                )

            # Bulk save chunks in Postgres
            self.db.add_all(chunk_db_objects)
            self.db.commit()

            # Bulk upload points to Qdrant
            self.qdrant_service.upsert_chunks(points)
            metrics["indexing_latency_sec"] = round(time.time() - index_start, 3)

            # 6. Finalize Ingestion Metrics
            total_time = time.time() - start_time
            metrics["total_ingestion_time_sec"] = round(total_time, 3)
            
            doc.status = "completed"
            doc.metadata_json = {
                **(doc.metadata_json or {}),
                "ingestion_metrics": metrics
            }
            job.status = "completed"
            job.error_message = None
            self.db.commit()
            logger.info(f"Ingestion successful for document ID {self.document_id} in {total_time:.3f}s. Chunks: {len(raw_chunks)}")

        except Exception as e:
            logger.error(f"Ingestion pipeline failed on document ID {self.document_id}: {str(e)}", exc_info=True)
            self.db.rollback()
            
            doc.status = "failed"
            doc.processing_error = str(e)
            
            job.status = "failed"
            job.error_message = str(e)
            self.db.commit()
            
        finally:
            self.db.close()
