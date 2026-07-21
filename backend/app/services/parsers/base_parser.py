from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel


class ParsedPage(BaseModel):
    page_number: int
    text: str


class ParsedDocument(BaseModel):
    text: str
    pages: List[ParsedPage]
    metadata: Dict[str, Any]


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """Parses a document file on disk and returns a unified ParsedDocument."""
        pass
