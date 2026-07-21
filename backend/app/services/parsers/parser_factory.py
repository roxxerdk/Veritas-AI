import os
from app.services.parsers.base_parser import BaseParser
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.text_parser import TextParser
from app.services.parsers.markdown_parser import MarkdownParser


class ParserFactory:
    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        """Determines the file extension and returns the appropriate parser instance."""
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        
        if ext == "pdf":
            return PDFParser()
        elif ext == "docx":
            return DOCXParser()
        elif ext == "txt":
            return TextParser()
        elif ext in ["md", "markdown"]:
            return MarkdownParser()
        else:
            raise ValueError(f"No parser available for file format extension: '.{ext}'")
