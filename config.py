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