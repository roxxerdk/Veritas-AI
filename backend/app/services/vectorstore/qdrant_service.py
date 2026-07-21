import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.config.settings import settings

logger = logging.getLogger("veritas-ai.vectorstore")

COLLECTION_NAME = "veritas_chunks"
VECTOR_DIMENSION = 384  # Dimension for BAAI/bge-small-en-v1.5


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self._init_collection()

    def _init_collection(self):
        """Verifies if the veritas_chunks collection exists in Qdrant; initializes it if absent."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if COLLECTION_NAME not in collection_names:
                logger.info(f"Creating collection '{COLLECTION_NAME}' in Qdrant with dimension {VECTOR_DIMENSION}...")
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                
                # Create a payload text index on 'content' for lexical keyword matching
                self.client.create_payload_index(
                    collection_name=COLLECTION_NAME,
                    field_name="content",
                    field_schema="text"
                )
                logger.info(f"Collection '{COLLECTION_NAME}' initialized successfully.")
        except Exception as e:
            logger.error(f"Error checking/initializing Qdrant collection: {str(e)}")
            raise e

    def upsert_chunks(self, points: List[PointStruct]) -> bool:
        """Upserts a list of vector points (with embeddings and payload metadata) to Qdrant."""
        if not points:
            return True
        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                wait=True,
                points=points
            )
            return True
        except Exception as e:
            logger.error(f"Error upserting points to Qdrant: {str(e)}")
            raise e

    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Performs a dense vector semantic search query in Qdrant using the unified query_points API."""
        try:
            response = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=top_k,
                with_payload=True
            )
            
            search_results = response.points
            formatted_results = []
            for hit in search_results:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vectors in Qdrant: {str(e)}")
            raise e

    def search_keyword(
        self,
        query_text: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Performs a keyword-based lexical search utilizing Qdrant payload text matching."""
        try:
            # Query Qdrant with full-text search match conditions on the content payload field
            search_results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter={
                    "must": [
                        {
                            "key": "content",
                            "match": {
                                "text": query_text
                            }
                        }
                    ]
                },
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )[0]
            
            # Since Qdrant scroll doesn't return BM25 scores natively, we assign a placeholder score
            # of 1.0 down to 0.1 for ranking, RRF will merge this.
            formatted_results = []
            for idx, hit in enumerate(search_results):
                formatted_results.append({
                    "id": hit.id,
                    "score": round(1.0 - (idx * 0.1), 2),  # Mock relevance decay
                    "payload": hit.payload
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Error performing keyword payload search: {str(e)}")
            raise e

    def delete_document_vectors(self, document_id: int):
        """Clears all indexed vector chunks belonging to a deleted document."""
        try:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "document_id",
                                "match": {
                                    "value": document_id
                                }
                            }
                        ]
                    }
                }
            )
            logger.info(f"Deleted vector chunks for document_id={document_id} from Qdrant.")
        except Exception as e:
            logger.error(f"Failed to delete document vector chunks: {str(e)}")
            raise e
