# models/violation.py
from dataclasses import dataclass

@dataclass
class Violation:
    """单条违规记录"""
    keyword: str           # 触发的敏感词
    context: str           # 所在原文片段
    line_num: int          # 段落/行号
    severity: str          # "致命", "严重", "一般"
    position: str          # "标题", "正文"
    suggestion: str        # 修改建议