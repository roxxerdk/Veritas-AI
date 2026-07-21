import os
from typing import List
from app.services.parsers.base_parser import BaseParser, ParsedDocument, ParsedPage


class TextParser(BaseParser):
    def parse(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TXT file not found at {file_path}")

        # Attempt UTF-8 decoding, with fallback to latin-1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                full_text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                full_text = f.read()

        pages = [ParsedPage(page_number=1, text=full_text)]
        metadata = {
            "page_count": 1,
            "char_count": len(full_text),
            "word_count": len(full_text.split())
        }

        return ParsedDocument(text=full_text, pages=pages, metadata=metadata)
