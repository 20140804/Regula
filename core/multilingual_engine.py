# core/multilingual_engine.py
"""
多语言扫描引擎 - Pro 版专属
支持英文、日文、韩文
"""
from typing import List, Tuple
import re

# ===== 各语言内置敏感词库 =====
ENGLISH_WORDS = [
    "best", "first", "top", "perfect", "ultimate", "guaranteed",
    "risk-free", "100%", "safe", "no side effects",
    "cure", "heal", "permanent", "forever"
]

JAPANESE_WORDS = [
    "最高", "第一", "完璧", "絶対", "永久", "リスクフリー",
    "副作用なし", "完全治癒", "100%", "保証"
]

KOREAN_WORDS = [
    "최고", "첫째", "완벽한", "영원한", "위험 없는",
    "부작용 없음", "완전 치료", "100%", "보장"
]


class MultilingualEngine:
    """多语言扫描引擎"""
    
    def __init__(self):
        self.lang_map = {
            "en": ENGLISH_WORDS,
            "ja": JAPANESE_WORDS,
            "ko": KOREAN_WORDS
        }
    
    def scan(self, text: str, lang: str = "en") -> List[Tuple[str, str]]:
        """
        扫描指定语言的文本
        返回: [(关键词, 严重等级), ...]
        """
        if lang not in self.lang_map:
            return []
        
        words = self.lang_map[lang]
        results = []
        
        for word in words:
            if word.lower() in text.lower():
                # 简单等级判定
                if word in ["best", "first", "top", "最高", "第一", "최고", "첫째"]:
                    severity = "严重"
                elif word in ["cure", "heal", "permanent", "根治", "完全治癒"]:
                    severity = "致命"
                else:
                    severity = "一般"
                results.append((word, severity))
        
        # 去重
        seen = set()
        unique_results = []
        for word, severity in results:
            if word not in seen:
                seen.add(word)
                unique_results.append((word, severity))
        
        return unique_results
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ["en", "ja", "ko"]