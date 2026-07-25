from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectorstore.qdrant_service import QdrantService
from app.services.retrieval.semantic import SemanticRetriever
from app.services.retrieval.keyword import KeywordRetriever
from app.services.retrieval.rrf import ReciprocalRankFusion


class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        
        # Instantiate retrieval components
        self.semantic_retriever = SemanticRetriever(self.embedding_service, self.qdrant_service)
        self.keyword_retriever = KeywordRetriever(self.db)
        self.rrf = ReciprocalRankFusion()

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Orchestrates hybrid (semantic + keyword) retrieval with RRF rank consolidation."""
        if not query:
            return []

        # 1. Fetch Semantic search candidates (double the target size to feed fusion candidate pool)
        semantic_hits = self.semantic_retriever.retrieve(
            query=query,
            top_k=top_k * 2,
            filter_dict=filter_dict
        )

        # 2. Fetch Keyword search candidates
        keyword_hits = self.keyword_retriever.retrieve(
            query=query,
            top_k=top_k * 2,
            filter_dict=filter_dict
        )

        # 3. Fuse lists using RRF
        fused_hits = self.rrf.merge(
            semantic_results=semantic_hits,
            keyword_results=keyword_hits
        )

        # 4. Return top-k matches
        return fused_hits[:top_k]
