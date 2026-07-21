from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RecursiveChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_text(self, text: str) -> List[str]:
        """Splits a string of text recursively into chunks based on characters."""
        if not text:
            return []
        return self.splitter.split_text(text)
