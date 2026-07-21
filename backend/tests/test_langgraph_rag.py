import os
import sys
import unittest
from sqlalchemy.orm import Session

# Add backend/ to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import app.database.base to register all mappers and relationships in SQLAlchemy
from app.database.base import Base
from app.database.session import SessionLocal
from app.models.user import User
from app.models.document import Document, DocumentChunk, ProcessingJob
from app.core.security import get_password_hash
from app.services.pipeline.ingestion_pipeline import IngestionPipeline
from app.workflows.langgraph.graph import app_graph


class TestLangGraphRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db: Session = SessionLocal()
        
        # 1. Setup a test user
        cls.user = cls.db.query(User).filter(User.email == "test_agents@veritas.ai").first()
        if not cls.user:
            cls.user = User(
                email="test_agents@veritas.ai",
                hashed_password=get_password_hash("agentpassword123"),
                is_active=True
            )
            cls.db.add(cls.user)
            cls.db.commit()
            cls.db.refresh(cls.user)

        # 2. Write a temporary text file representing an uploaded file
        cls.test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_test_doc.txt"))
        cls.test_content = (
            "Veritas AI is an Enterprise Self-Correcting Retrieval-Augmented Generation (RAG) Platform. "
            "It runs on Docker and uses Python 3.12 for the backend API server. "
            "For caching, it utilizes Redis running on standard port 6379. "
            "To prevent duplicate file ingestion, it calculates SHA-256 checksums."
        )
        with open(cls.test_file_path, "w", encoding="utf-8") as f:
            f.write(cls.test_content)

        # 3. Register and Ingest Document
        cls.doc = Document(
            filename="agent_test_doc.txt",
            file_type="TXT",
            file_size=len(cls.test_content),
            storage_path=cls.test_file_path,
            checksum="agent_test_checksum_hash_987",
            status="uploaded",
            uploaded_by=cls.user.id
        )
        cls.db.add(cls.doc)
        cls.db.commit()
        cls.db.refresh(cls.doc)

        pipeline = IngestionPipeline(cls.doc.id)
        pipeline.process()

    @classmethod
    def tearDownClass(cls):
        # Cleanup files and test user
        if os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)
            
        db = SessionLocal()
        user = db.query(User).filter(User.email == "test_agents@veritas.ai").first()
        if user:
            db.delete(user)
            db.commit()
        db.close()

    def test_in_domain_agent_query(self):
        # Build state
        initial_state = {
            "original_query": "What port does Redis run on in Veritas AI?",
            "current_query": "What port does Redis run on in Veritas AI?",
            "chat_history": [],
            "intent": "",
            "entities": [],
            "search_keywords": [],
            "retrieved_chunks": [],
            "relevant_chunks": [],
            "generated_answer": "",
            "reflection_feedback": "",
            "verification_feedback": "",
            "verified_claims": [],
            "citations": [],
            "confidence_score": 1.0,
            "rewrite_loop_count": 0,
            "reflection_loop_count": 0,
            "refusal": False,
            "execution_trace": []
        }

        # Run Graph
        config = {"configurable": {"db": self.db}}
        final_state = app_graph.invoke(initial_state, config=config)

        # Asserts
        self.assertFalse(final_state["refusal"])
        self.assertIn("6379", final_state["generated_answer"])
        self.assertGreaterEqual(final_state["confidence_score"], 0.8)
        self.assertGreater(len(final_state["citations"]), 0)
        self.assertGreater(len(final_state["execution_trace"]), 0)
        
        # Verify trace has node stamps
        trace_str = "".join(final_state["execution_trace"])
        self.assertIn("Query Understanding", trace_str)
        self.assertIn("Retrieval Agent", trace_str)
        self.assertIn("Context Evaluation", trace_str)
        self.assertIn("Response Generation", trace_str)

    def test_out_of_scope_agent_query(self):
        # Query that is completely out of domain
        initial_state = {
            "original_query": "How do I make a chocolate cake?",
            "current_query": "How do I make a chocolate cake?",
            "chat_history": [],
            "intent": "",
            "entities": [],
            "search_keywords": [],
            "retrieved_chunks": [],
            "relevant_chunks": [],
            "generated_answer": "",
            "reflection_feedback": "",
            "verification_feedback": "",
            "verified_claims": [],
            "citations": [],
            "confidence_score": 1.0,
            "rewrite_loop_count": 0,
            "reflection_loop_count": 0,
            "refusal": False,
            "execution_trace": []
        }

        config = {"configurable": {"db": self.db}}
        final_state = app_graph.invoke(initial_state, config=config)

        # Assert correct refusal route
        self.assertTrue(final_state["refusal"])
        self.assertIn("out of scope", final_state["generated_answer"].lower())


if __name__ == "__main__":
    unittest.main()
