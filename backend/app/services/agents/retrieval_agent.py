from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.retrieval.retrieval_service import RetrievalService


class RetrievalAgent:
    def __init__(self, db: Session):
        self.retrieval_service = RetrievalService(db)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Queries the hybrid retrieval service using semantic and keyword matching."""
        # Simple wrapper calling the completed RRF service
        return self.retrieval_service.search(query=query, top_k=top_k, filter_dict=filter_dict)
