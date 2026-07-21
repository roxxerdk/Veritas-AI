from typing import Dict, Any
from app.services.agents.base_agent import BaseAgent


class QueryUnderstandingAgent(BaseAgent):
    def process_query(self, query: str) -> Dict[str, Any]:
        """Analyzes query to extract intent, entities, and search keywords."""
        prompt_template = self.load_prompt("query_understanding")
        
        # Inject the query parameter
        prompt = f"{prompt_template}\n\nUser Query: \"{query}\"\nJSON Response:"
        
        response_text = self.call_llm(prompt)
        parsed_json = self.parse_json_response(response_text)
        
        # Provide default values if parsing missed keys
        return {
            "intent": parsed_json.get("intent", "search_query"),
            "entities": parsed_json.get("entities", []),
            "keywords": parsed_json.get("keywords", [query])
        }
