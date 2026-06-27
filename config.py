# config.py
# 内置敏感词库（后期可导入自定义）
BUILTIN_SENSITIVE_WORDS = [
    "第一", "顶级", "最好", "唯一", "首选", "万能", "根治", "彻底治愈",
    "零风险", "100%", "纯天然", "无副作用", "最便宜", "全网最低"
]

# 严重等级映射
SEVERITY_MAP = {
    "致命": 3,
    "严重": 2,
    "一般": 1
}

# 免费版字数限制 (300字)
FREE_TIER_LIMIT = 300

# 规则存储文件名
RULES_STORAGE_FILE = "custom_rules.json"
# config.py (追加以下内容)

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
# config.py (追加)

# ===== Pro 版本功能开关 =====
PRO_FEATURES = {
    "ocr_enabled": True,        # OCR 功能（Pro 专属）
    "max_rules_free": 3,         # 免费版最大规则数（留作以后用）
    "batch_limit_free": 5,       # 免费版最大批量文件数（留作以后用）
}
# config.py (追加)
from utils.license_manager import is_pro_activated

# ===== Pro 状态 =====
PRO_ACTIVATED = is_pro_activated()

# 功能开关
FEATURES = {
    "ocr": PRO_ACTIVATED,      # OCR 图片识别
    "batch": True,             # 批量扫描（免费版已有）
    "heatmap": True,           # 热力图（免费版已有）
    "custom_rules": True,      # 自定义规则（免费版已有）
    "advanced_pdf": PRO_ACTIVATED,  # 高级 PDF 报告
}
# config.py (追加)
# ===== 多语言支持 =====
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "英文",
    "ja": "日文",
    "ko": "韩文"
}