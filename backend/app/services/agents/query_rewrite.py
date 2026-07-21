from typing import Dict, Any
from app.services.agents.base_agent import BaseAgent


class QueryRewriteAgent(BaseAgent):
    def rewrite_query(self, original_query: str, current_query: str) -> Dict[str, Any]:
        """Reformulates a search query to optimize hybrid retrieval performance."""
        prompt_template = self.load_prompt("query_rewrite")
        
        # Inject the query parameters
        prompt = prompt_template.format(
            original_query=original_query,
            current_query=current_query
        ) + "\nJSON Response:"
        
        response_text = self.call_llm(prompt)
        parsed_json = self.parse_json_response(response_text)
        
        return {
            "rewritten_query": parsed_json.get("rewritten_query", original_query),
            "rationale": parsed_json.get("rationale", "Standard query bypass")
        }
