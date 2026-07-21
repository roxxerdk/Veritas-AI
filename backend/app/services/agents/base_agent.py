import json
import logging
import os
import re
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from app.config.settings import settings

logger = logging.getLogger("veritas-ai.agents")
PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts"))


class BaseAgent:
    _prompt_cache: Dict[str, str] = {}
    _llm_instance: Optional[Any] = None

    def __init__(self, model_name: str = "gemini-flash-latest"):
        self.model_name = model_name
        self._init_llm()

    def _init_llm(self):
        """Initializes the LLM client based on the selected provider."""
        if BaseAgent._llm_instance is None:
            if settings.LLM_PROVIDER == "ollama":
                logger.info(f"Initializing local Ollama driver with model '{settings.OLLAMA_MODEL}'...")
                BaseAgent._llm_instance = ChatOllama(
                    model=settings.OLLAMA_MODEL,
                    base_url=settings.OLLAMA_BASE_URL,
                    temperature=0.0
                )
            else:
                # Leverage settings api key, fallback to env variable
                api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    logger.warning("GEMINI_API_KEY is not defined. LLM operations will fail.")
                
                logger.info(f"Initializing Gemini driver with model '{self.model_name}'...")
                BaseAgent._llm_instance = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=api_key,
                    temperature=0.0, # low temperature for predictable evaluation & responses
                    max_tokens=2048
                )

    def load_prompt(self, prompt_filename: str) -> str:
        """Loads a prompt template from disk, supporting hot-reloading during debug mode."""
        if not prompt_filename.endswith(".txt"):
            prompt_filename += ".txt"
            
        file_path = os.path.join(PROMPTS_DIR, prompt_filename)
        
        # Read from disk directly if debug mode is active (enabling hot-reloading)
        if settings.DEBUG or prompt_filename not in BaseAgent._prompt_cache:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                BaseAgent._prompt_cache[prompt_filename] = content
            except Exception as e:
                logger.error(f"Failed to load prompt template at {file_path}: {str(e)}")
                raise e
                
        return BaseAgent._prompt_cache[prompt_filename]

    def call_llm(self, prompt: str) -> str:
        """Helper to invoke the Gemini LLM with a given prompt."""
        try:
            response = BaseAgent._llm_instance.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error calling Gemini LLM: {str(e)}")
            raise e

    def parse_json_response(self, text: str) -> Dict[str, Any]:
        """Cleans and extracts JSON strings wrapped in Markdown code fences."""
        if not text:
            return {}
        
        # Clean markdown code block wraps (```json ... ```)
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # Remove leading ```json or ```
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            # Remove trailing ```
            cleaned = re.sub(r"\n```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response. Raw output:\n{text}\nError: {str(e)}")
            # Attempt to extract any substring bounded by curly braces
            try:
                matches = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if matches:
                    return json.loads(matches.group(0))
            except Exception:
                pass
            raise e
