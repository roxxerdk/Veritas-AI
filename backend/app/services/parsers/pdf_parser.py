import os
import fitz  # PyMuPDF
import pdfplumber
from typing import List
from app.services.parsers.base_parser import BaseParser, ParsedDocument, ParsedPage


class PDFParser(BaseParser):
    def parse(self, file_path: str) -> ParsedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at {file_path}")

        pages: List[ParsedPage] = []
        full_text_list = []
        metadata = {}

        # 1. Attempt parsing using PyMuPDF (fast)
        try:
            doc = fitz.open(file_path)
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "page_count": len(doc),
            }

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                # page number is 1-indexed for standard citation references
                pages.append(ParsedPage(page_number=page_num + 1, text=text))
                full_text_list.append(text)
            doc.close()
            
            full_text = "\n\n".join(full_text_list)
            return ParsedDocument(text=full_text, pages=pages, metadata=metadata)
            
        except Exception as py_exc:
            # 2. Fallback to pdfplumber
            try:
                pages.clear()
                full_text_list.clear()
                with pdfplumber.open(file_path) as pdf:
                    metadata = {
                        "page_count": len(pdf.pages),
                        **({k: str(v) for k, v in pdf.metadata.items()} if pdf.metadata else {})
                    }
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        pages.append(ParsedPage(page_number=i + 1, text=text))
                        full_text_list.append(text)
                
                full_text = "\n\n".join(full_text_list)
                return ParsedDocument(text=full_text, pages=pages, metadata=metadata)
            except Exception as plumb_exc:
                raise RuntimeError(
                    f"PDF parsing failed in both PyMuPDF and pdfplumber. "
                    f"PyMuPDF error: {str(py_exc)}. pdfplumber error: {str(plumb_exc)}"
                )
