# models/violation.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Violation:
    """单条违规记录"""
    keyword: str
    context: str
    line_num: int
    severity: str
    position: str
    suggestion: str
    # AI 扩展字段
    category: Optional[str] = field(default="")  # 违规分类
    confidence: Optional[float] = field(default=0.0)  # 分类置信度