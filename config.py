# config.py
"""
全局配置文件
包含：敏感词库、等级映射、授权状态、功能开关
"""
import os
from utils.license_manager import is_pro_activated


# ===== 内置敏感词库 =====
BUILTIN_SENSITIVE_WORDS = [
    "第一", "顶级", "最好", "唯一", "首选", "万能", "根治", "彻底治愈",
    "零风险", "100%", "纯天然", "无副作用", "最便宜", "全网最低"
]

# ===== 严重等级映射 =====
SEVERITY_MAP = {
    "致命": 3,
    "严重": 2,
    "一般": 1
}

# ===== 免费版字数限制 (300字) =====
FREE_TIER_LIMIT = 300

# ===== 规则存储文件名 =====
RULES_STORAGE_FILE = "custom_rules.json"

# ===== Pro 激活状态 =====
PRO_ACTIVATED = is_pro_activated()

# ===== Pro Max 激活状态 =====
PRO_MAX_ACTIVATED = os.path.exists("pro_max.key")

# ===== UI 主题配色 =====
THEME = {
    "primary": "#1a1a2e",       # 深空底色
    "secondary": "#16213e",     # 次级深蓝
    "accent": "#0f3460",        # 强调蓝
    "highlight": "#e94560",     # 活力红（点缀）
    "success": "#27ae60",       # 绿色
    "warning": "#f39c12",       # 橙色
    "danger": "#e74c3c",        # 红色
    "text_light": "#ffffff",
    "text_dark": "#2c3e50",
    "bg_light": "#f8f9fa",
    "bg_dark": "#2c3e50",
    "border_radius": "10px",
    "font_family": "Segoe UI, Microsoft YaHei, sans-serif"
}

# ===== 功能开关 =====
FEATURES = {
    "ocr": PRO_ACTIVATED,                       # OCR 图片识别
    "batch": True,                               # 批量扫描
    "heatmap": True,                             # 热力图
    "custom_rules": True,                        # 自定义规则
    "advanced_pdf": PRO_ACTIVATED,              # 高级 PDF 报告
    "ai_engine": PRO_ACTIVATED and PRO_MAX_ACTIVATED,  # AI 引擎（Pro + Pro Max）
    "multilingual": PRO_ACTIVATED,              # 多语言扫描
    "cli_mode": PRO_ACTIVATED,                  # 命令行模式
    "rule_templates": PRO_ACTIVATED,            # 规则模板库
    "debug_logging": PRO_ACTIVATED,             # 调试日志
}

# ===== 多语言支持 =====
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어"
}