from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.models.document import DocumentChunk, Document


class KeywordRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Queries the SQL database for document chunks matching keyword search constraints."""
        if not query:
            return []

        # Split search terms
        terms = [t.strip() for t in query.split() if t.strip()]
        if not terms:
            return []

        # Construct full text search condition or LIKE fallbacks
        # We query the DocumentChunk content matches
        conditions = []
        for term in terms:
            conditions.append(DocumentChunk.content.ilike(f"%{term}%"))

        # Query matches and join with Document to fetch metadata payload
        results = (
            self.db.query(DocumentChunk, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .filter(or_(*conditions))
            .limit(top_k)
            .all()
        )

        formatted_results = []
        for idx, (chunk, filename) in enumerate(results):
            formatted_results.append({
                "id": chunk.vector_id or str(chunk.id),
                "score": round(1.0 - (idx * 0.1), 2),  # decay score based on query ordering
                "payload": {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "filename": filename,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_count": chunk.token_count
                }
            })

        return formatted_results
