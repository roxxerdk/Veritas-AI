import os
import sys
import unittest
from sqlalchemy.orm import Session

# Add backend/ to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal, engine
from app.models.user import User
from app.models.document import Document, DocumentChunk, ProcessingJob
from app.core.security import get_password_hash
from app.services.pipeline.ingestion_pipeline import IngestionPipeline
from app.services.retrieval.retrieval_service import RetrievalService
from app.database.base import Base


class TestIngestionAndRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Bind connection and create session
        cls.db: Session = SessionLocal()
        
        # 1. Setup a test user
        cls.user = cls.db.query(User).filter(User.email == "test_rag@veritas.ai").first()
        if not cls.user:
            cls.user = User(
                email="test_rag@veritas.ai",
                hashed_password=get_password_hash("testpassword123"),
                is_active=True
            )
            cls.db.add(cls.user)
            cls.db.commit()
            cls.db.refresh(cls.user)

        # 2. Write a temporary text file representing an uploaded file
        cls.test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_doc.txt"))
        cls.test_content = (
            "Veritas AI is an Enterprise Self-Correcting Retrieval-Augmented Generation (RAG) Platform. "
            "It features a multi-agent workflow that performs self-correction before answering. "
            "The platform leverages LangGraph for orchestration, Qdrant for vector indexing, and Gemini for reasoning. "
            "This project is a modular production-grade hackathon MVP designed to be completed in 4 days. "
            "For evidence validation, the platform implements citation extraction and confidence scores. "
            "Hallucinations are minimized by enforcing a strict refusal logic if evidence is insufficient."
        )
        with open(cls.test_file_path, "w", encoding="utf-8") as f:
            f.write(cls.test_content)

    @classmethod
    def tearDownClass(cls):
        # Cleanup test files
        if os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)
            
        # Clean test user and its records from DB
        db = SessionLocal()
        user = db.query(User).filter(User.email == "test_rag@veritas.ai").first()
        if user:
            db.delete(user)
            db.commit()
        db.close()

    def test_end_to_end_pipeline(self):
        # 1. Register Document in Postgres
        doc = Document(
            filename="test_doc.txt",
            file_type="TXT",
            file_size=len(self.test_content),
            storage_path=self.test_file_path,
            checksum="test_checksum_hash_123456",
            status="uploaded",
            uploaded_by=self.user.id
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        # Register initial job
        job = ProcessingJob(document_id=doc.id, status="queued")
        self.db.add(job)
        self.db.commit()

        # 2. Run the Ingestion Pipeline
        pipeline = IngestionPipeline(doc.id)
        pipeline.process()

        # 3. Refresh and Assert Database Updates
        self.db.refresh(doc)
        self.db.refresh(job)

        self.assertEqual(doc.status, "completed")
        self.assertEqual(job.status, "completed")
        self.assertIsNotNone(doc.metadata_json)
        self.assertIn("ingestion_metrics", doc.metadata_json)
        
        # Verify chunks were written to SQL
        chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0].token_count, len(chunks[0].content.split()))

        # 4. Perform Hybrid Search Query
        retrieval_service = RetrievalService(self.db)
        search_results = retrieval_service.search("What is Veritas AI?", top_k=2)

        # Assert search hits return
        self.assertGreater(len(search_results), 0)
        self.assertIn("score", search_results[0])
        self.assertIn("payload", search_results[0])
        
        # Verify content contains target facts
        top_hit_content = search_results[0]["payload"]["content"]
        self.assertIn("Veritas AI", top_hit_content)


if __name__ == "__main__":
    unittest.main()
