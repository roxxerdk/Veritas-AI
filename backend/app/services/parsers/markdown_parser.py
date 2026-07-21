import os
from typing import List
from app.services.parsers.base_parser import BaseParser, ParsedDocument, ParsedPage


class MarkdownParser(BaseParser):
    def parse(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found at {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                full_text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                full_text = f.read()

        pages = [ParsedPage(page_number=1, text=full_text)]
        
        # Capture basic structural metadata from MD syntax
        headers_count = sum(1 for line in full_text.splitlines() if line.strip().startswith("#"))
        metadata = {
            "page_count": 1,
            "char_count": len(full_text),
            "headers_count": headers_count,
        }

        return ParsedDocument(text=full_text, pages=pages, metadata=metadata)
