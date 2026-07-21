from typing import Dict, Any, List
from app.services.agents.base_agent import BaseAgent


class EvidenceVerificationAgent(BaseAgent):
    def verify(
        self,
        relevant_chunks: List[Dict[str, Any]],
        answer: str
    ) -> Dict[str, Any]:
        """Validates that claims in the answer are grounded in context evidence chunks."""
        prompt_template = self.load_prompt("evidence_verification")
        
        # Build context string
        context_str = "\n---\n".join([
            f"[Source index: {i}] {hit.get('payload', {}).get('content', '')}"
            for i, hit in enumerate(relevant_chunks)
        ])
        
        prompt = prompt_template.format(
            context=context_str,
            answer=answer
        ) + "\nJSON Response:"
        
        response_text = self.call_llm(prompt)
        parsed_json = self.parse_json_response(response_text)
        
        return {
            "verified": bool(parsed_json.get("verified", True)),
            "confidence": float(parsed_json.get("confidence", 1.0)),
            "unsupported": parsed_json.get("unsupported", [])
        }
