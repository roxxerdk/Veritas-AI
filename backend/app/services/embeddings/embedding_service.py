import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("veritas-ai.embeddings")


class EmbeddingService:
    _model_instance = None

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._init_model()

    def _init_model(self):
        # Cache the model instance globally at the class level so it loads only once
        if EmbeddingService._model_instance is None:
            logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
            try:
                # Automatically selects CUDA GPU if available, falls back to CPU
                EmbeddingService._model_instance = SentenceTransformer(self.model_name)
                logger.info(f"SentenceTransformer '{self.model_name}' loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading embedding model: {str(e)}")
                raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of document strings."""
        if not texts:
            return []
        try:
            embeddings = EmbeddingService._model_instance.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings for documents: {str(e)}")
            raise e

    def embed_query(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a single search query string."""
        if not text:
            return []
        try:
            embedding = EmbeddingService._model_instance.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {str(e)}")
            raise e
