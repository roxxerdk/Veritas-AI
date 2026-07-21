from typing import List, Dict, Any
from app.services.agents.base_agent import BaseAgent


class ResponseGenerationAgent(BaseAgent):
    def generate_response(
        self,
        query: str,
        relevant_chunks: List[Dict[str, Any]],
        retry_feedback: str = ""
    ) -> str:
        """Synthesizes an answer grounded only in the provided relevant source document chunks."""
        prompt_template = self.load_prompt("response_generation")
        
        # Build context string with chunk indexes
        context_list = []
        for i, hit in enumerate(relevant_chunks):
            payload = hit.get("payload", {})
            content = payload.get("content", "")
            filename = payload.get("filename", "unknown")
            page = payload.get("page_number", 1)
            chunk_id = payload.get("chunk_id", hit.get("id"))
            
            context_list.append(
                f"[Source index: {i}] (File: {filename}, Page: {page}, Chunk ID: {chunk_id})\n"
                f"Content: {content}"
            )
            
        context_str = "\n---\n".join(context_list)
        
        # Inject variables using .replace to bypass formatting issues
        prompt = (
            prompt_template
            .replace("{query}", query)
            .replace("{context}", context_str)
        )
        
        # If running a correction retry from reflection feedback, inject it
        if retry_feedback:
            prompt += (
                f"\n\n[CRITICAL CORRECTION REQUEST FROM REFLECTION PROCESS]\n"
                f"Your previous answer failed self-correction check. Feedback:\n"
                f"\"{retry_feedback}\"\n"
                f"Please generate a new corrected response incorporating this feedback, "
                f"maintaining strict alignment with sources."
            )
            
        prompt += "\nResponse Output:"
        
        return self.call_llm(prompt)
