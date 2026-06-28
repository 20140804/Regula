# core/ai_classifier.py
"""
违规自动分类器 - Pro Max 专属
自动将违规归类到预定义类别
"""
from typing import List, Dict, Tuple
from core.ai_engine import ai_engine
from models.violation import Violation


class AIClassifier:
    """AI 违规分类器"""
    
    @staticmethod
    def classify_violation(violation: Violation) -> Tuple[str, float]:
        """
        对单条违规进行分类
        返回: (分类名称, 置信度)
        """
        if not ai_engine or not ai_engine.is_available():
            return "未分类", 0.0
        
        return ai_engine.classify_violation(
            violation.keyword,
            violation.context
        )
    
    @staticmethod
    def classify_batch(violations: List[Violation]) -> Dict[str, List[Violation]]:
        """
        批量分类违规
        返回: {分类名: [违规列表]}
        """
        result = {}
        for v in violations:
            category, _ = AIClassifier.classify_violation(v)
            if category not in result:
                result[category] = []
            result[category].append(v)
        return result
    
    @staticmethod
    def get_category_stats(violations: List[Violation]) -> Dict[str, int]:
        """
        获取分类统计
        返回: {分类名: 数量}
        """
        classified = AIClassifier.classify_batch(violations)
        return {cat: len(v_list) for cat, v_list in classified.items()}