from typing import Dict, Any, List
from app.services.agents.base_agent import BaseAgent


class ReflectionAgent(BaseAgent):
    def reflect(
        self,
        query: str,
        relevant_chunks: List[Dict[str, Any]],
        answer: str
    ) -> Dict[str, Any]:
        """Performs a critique of the answer checking for hallucinations and completeness."""
        prompt_template = self.load_prompt("reflection")
        
        # Build context string
        context_str = "\n---\n".join([
            hit.get("payload", {}).get("content", "")
            for hit in relevant_chunks
        ])
        
        prompt = (
            prompt_template
            .replace("{query}", query)
            .replace("{context}", context_str)
            .replace("{answer}", answer)
        ) + "\nJSON Response:"
        
        response_text = self.call_llm(prompt)
        parsed_json = self.parse_json_response(response_text)
        
        return {
            "complete": bool(parsed_json.get("complete", True)),
            "hallucination": bool(parsed_json.get("hallucination", False)),
            "feedback": parsed_json.get("feedback", "")
        }
