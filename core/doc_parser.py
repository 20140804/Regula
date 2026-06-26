# core/doc_parser.py
import os
from typing import List, Tuple
from docx import Document

class DocParser:
    @staticmethod
    def parse_docx(file_path: str) -> Tuple[str, List[Tuple[int, str]]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        doc = Document(file_path)
        paragraphs = []
        full_text = []
        for idx, para in enumerate(doc.paragraphs, start=1):
            text = para.text.strip()
            if text:
                paragraphs.append((idx, text))
                full_text.append(text)
        return "\n".join(full_text), paragraphs