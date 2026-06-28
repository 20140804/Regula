# core/ai_suggester.py
"""
智能修改建议器 - Pro Max 专属
提供违规的智能修改建议
"""
from typing import List, Dict, Optional
from core.ai_engine import ai_engine
from models.violation import Violation


class AISuggester:
    """AI 智能修改建议器"""
    
    @staticmethod
    def suggest_for_violation(violation: Violation) -> str:
        """
        为单条违规生成修改建议
        """
        if not ai_engine or not ai_engine.is_available():
            return violation.suggestion  # 回退到原建议
        
        return ai_engine.suggest_fix(
            violation.keyword,
            violation.context
        )
    
    @staticmethod
    def enhance_violation(violation: Violation) -> Violation:
        """
        增强违规记录（添加 AI 分类和增强建议）
        """
        # 获取分类
        category, confidence = AIClassifier.classify_violation(violation)
        
        # 获取增强建议
        enhanced_suggestion = AISuggester.suggest_for_violation(violation)
        
        # 创建增强后的违规记录（保留原有字段，增强建议和分类信息）
        enhanced = Violation(
            keyword=violation.keyword,
            context=violation.context,
            line_num=violation.line_num,
            severity=violation.severity,
            position=violation.position,
            suggestion=f"[AI] {enhanced_suggestion}"
        )
        # 添加分类信息（通过额外属性）
        enhanced.category = category
        enhanced.confidence = confidence
        
        return enhanced
    
    @staticmethod
    def enhance_batch(violations: List[Violation]) -> List[Violation]:
        """
        批量增强违规记录
        """
        return [AISuggester.enhance_violation(v) for v in violations]