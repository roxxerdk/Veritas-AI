from typing import List, Dict, Any, Optional
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.vectorstore.qdrant_service import QdrantService


class SemanticRetriever:
    def __init__(self, embedding_service: EmbeddingService, qdrant_service: QdrantService):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Converts query string to vector embedding and performs dense semantic search in Qdrant."""
        if not query:
            return []
        
        # 1. Embed query
        query_vector = self.embedding_service.embed_query(query)
        
        # 2. Search Qdrant
        results = self.qdrant_service.search_vectors(
            query_vector=query_vector,
            top_k=top_k,
            filter_dict=filter_dict
        )
        return results
