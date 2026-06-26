# core/text_splitter.py
import re
from typing import List, Tuple

class TextSplitter:
    @staticmethod
    def split_by_sentences(text: str) -> List[Tuple[int, str, bool]]:
        raw_lines = re.split(r'(?<=[。！？.!?])\s*|\n', text)
        raw_lines = [line.strip() for line in raw_lines if line.strip()]
        
        result = []
        for idx, line in enumerate(raw_lines, start=1):
            # 如果行首有# 或 字数很少且无标点，视为标题
            is_title = line.startswith('#') or (len(line) < 12 and not any(p in line for p in '。，,.'))
            result.append((idx, line, is_title))
        return result

    @staticmethod
    def extract_context(full_text: str, keyword: str, window: int = 30) -> str:
        pos = full_text.find(keyword)
        if pos == -1:
            return ""
        start = max(0, pos - window)
        end = min(len(full_text), pos + len(keyword) + window)
        return full_text[start:end].replace('\n', ' ')