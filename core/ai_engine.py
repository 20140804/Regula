# core/ai_engine.py
"""
AI 智能增强引擎 - Pro Max 专属
基于 sentence-transformers 实现本地语义理解
"""
import os
import numpy as np
from typing import List, Tuple, Dict, Optional
from sentence_transformers import SentenceTransformer, util
from config import PRO_ACTIVATED, PRO_MAX_ACTIVATED


# ===== 违规预设示例库（用于语义匹配） =====
VIOLATION_EXAMPLES = {
    "虚假宣传": [
        "销量第一", "全网最低", "最好", "顶级", "唯一", "首选",
        "永久有效", "100%有效", "零风险", "保本", "稳赚"
    ],
    "医疗违规": [
        "根治", "彻底治愈", "无副作用", "治愈率", "速效", "特效", "万能"
    ],
    "歧视言论": [
        "性别歧视", "种族歧视", "年龄歧视"
    ],
    "违法内容": [
        "赌博", "毒品", "暴力", "淫秽"
    ],
    "绝对化用语": [
        "最", "第一", "唯一", "绝对", "永远"
    ]
}


class AIEngine:
    """AI 语义理解引擎（Pro Max 专属）"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 检查 Pro 授权（必须先有 Pro）
        if not PRO_ACTIVATED:
            raise RuntimeError("Pro Max 功能需要 Pro 授权，请先激活 Pro 版。")
        
        # 检查 Pro Max 授权
        if not PRO_MAX_ACTIVATED:
            raise RuntimeError("Pro Max 功能需要额外授权，请激活 Pro Max。")
        
        if self._model is None:
            try:
                # 使用轻量级中文模型（适合 CPU 运行）
                self._model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                print("[AI] 语义模型加载成功")
            except Exception as e:
                print(f"[AI] 模型加载失败: {e}")
                self._model = None
    
    def is_available(self) -> bool:
        """检查 AI 引擎是否可用"""
        return self._model is not None
    
    def semantic_similarity(self, text: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """
        计算文本与候选列表的语义相似度
        返回: [(候选文本, 相似度), ...] 按相似度降序排列
        """
        if not self.is_available():
            return []
        
        # 编码
        text_embedding = self._model.encode(text, convert_to_tensor=True)
        candidate_embeddings = self._model.encode(candidates, convert_to_tensor=True)
        
        # 计算余弦相似度
        similarities = util.cos_sim(text_embedding, candidate_embeddings)[0]
        
        # 排序
        results = []
        for i, score in enumerate(similarities):
            results.append((candidates[i], float(score)))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def classify_violation(self, keyword: str, context: str) -> Tuple[str, float]:
        """
        智能分类违规类型
        返回: (分类名称, 置信度)
        """
        if not self.is_available():
            return "未知", 0.0
        
        # 构建分类候选
        categories = list(VIOLATION_EXAMPLES.keys())
        # 为每个分类生成一个代表性描述
        category_descriptions = []
        for cat in categories:
            examples = VIOLATION_EXAMPLES.get(cat, [])
            # 用"关键词"组合作为该类的表示
            desc = f"{cat}: {', '.join(examples[:5])}"
            category_descriptions.append(desc)
        
        # 用违规关键词和上下文组合进行匹配
        combined = f"{keyword} {context[:50]}"
        
        results = self.semantic_similarity(combined, category_descriptions)
        
        if results:
            # 提取原始分类名
            top_desc = results[0][0]
            top_score = results[0][1]
            # 找到对应的分类名
            for cat in categories:
                if cat in top_desc:
                    return cat, top_score
        
        return "通用违规", 0.0
    
    def suggest_fix(self, keyword: str, context: str) -> str:
        """
        智能生成修改建议
        """
        suggestions = {
            "第一": "请使用'销量领先'、'品质优良'等客观表述",
            "最好": "请使用'品质优良'、'口碑良好'等客观表述",
            "顶级": "请使用'高端'、'精品'等客观表述",
            "唯一": "请使用'独特'、'特色'等客观表述",
            "根治": "请使用'缓解'、'改善'等客观表述",
            "彻底治愈": "请使用'有效缓解'、'显著改善'等客观表述",
            "零风险": "请使用'风险可控'、'信息充分披露'等表述",
            "保本": "请使用'风险较低'、'稳健'等客观表述",
            "全网最低": "请使用'价格优惠'、'超值'等客观表述",
            "永久有效": "请明确说明有效期，避免使用'永久'",
            "100%": "请避免承诺100%，使用'高'、'显著'等表述",
        }
        
        # 精确匹配
        for key, suggestion in suggestions.items():
            if key in keyword:
                return suggestion
        
        # 语义匹配
        if self.is_available():
            keys = list(suggestions.keys())
            results = self.semantic_similarity(keyword, keys)
            if results and results[0][1] > 0.5:
                return suggestions.get(results[0][0], "请使用客观、准确的表述")
        
        return "请使用客观、准确的表述，避免绝对化用语"


# 全局单例
try:
    ai_engine = AIEngine()
except RuntimeError as e:
    print(f"[AI] {e}")
    ai_engine = None


def is_ai_available() -> bool:
    return ai_engine is not None and ai_engine.is_available()