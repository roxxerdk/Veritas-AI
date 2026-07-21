import logging
from typing import Dict, Any, List
from app.services.agents.base_agent import BaseAgent

logger = logging.getLogger("veritas-ai.agents.context_evaluation")


class ContextEvaluationAgent(BaseAgent):
    def evaluate_chunk(self, query: str, chunk_content: str, chunk_id: Any) -> Dict[str, Any]:
        """Evaluates a single document chunk for relevance against the query."""
        prompt_template = self.load_prompt("context_evaluation")
        
        # Inject context variables safely using .replace to prevent JSON curly brace conflicts
        prompt = (
            prompt_template
            .replace("{query}", query)
            .replace("{chunk}", chunk_content)
        ) + "\nJSON Response:"
        
        try:
            response_text = self.call_llm(prompt)
            parsed_json = self.parse_json_response(response_text)
            return {
                "chunk_id": chunk_id,
                "relevant": bool(parsed_json.get("relevant", False)),
                "reason": parsed_json.get("reason", "No reason provided")
            }
        except Exception as e:
            logger.error(f"Context evaluation failed for chunk {chunk_id}: {str(e)}")
            # Graceful fallback: treat as irrelevant to be safe
            return {
                "chunk_id": chunk_id,
                "relevant": False,
                "reason": f"Evaluation error: {str(e)}"
            }

    def evaluate_all(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluates a batch of chunks and returns only those deemed relevant."""
        relevant_chunks = []
        for hit in chunks:
            payload = hit.get("payload", {})
            content = payload.get("content", "")
            chunk_id = payload.get("chunk_id", hit.get("id"))
            
            result = self.evaluate_chunk(query, content, chunk_id)
            if result["relevant"]:
                relevant_chunks.append(hit)
                
        return relevant_chunks
