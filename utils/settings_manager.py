# utils/settings_manager.py
"""
全局设置管理 - 持久化存储用户偏好
"""
import os
import json
from typing import Dict, Any

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "language": "zh",           # zh / en
    "theme": "light",           # light / dark
    "font_size": "medium",      # small / medium / large
    "show_welcome": True
}


def load_settings() -> Dict[str, Any]:
    """加载设置"""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        # 合并默认值（防止新增字段缺失）
        merged = DEFAULT_SETTINGS.copy()
        merged.update(settings)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]) -> bool:
    """保存设置"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def get_language() -> str:
    """获取当前语言"""
    return load_settings().get("language", "zh")


def get_theme() -> str:
    """获取当前主题"""
    return load_settings().get("theme", "light")


def get_font_size() -> str:
    """获取当前字体大小"""
    return load_settings().get("font_size", "medium")


def get_show_welcome() -> bool:
    """是否显示引导页"""
    return load_settings().get("show_welcome", True)


def load_language_pack(lang: str) -> Dict[str, str]:
    """加载语言包"""
    locale_dir = os.path.join(os.path.dirname(__file__), "..", "locale")
    file_path = os.path.join(locale_dir, f"{lang}.json")
    
    if not os.path.exists(file_path):
        # 回退到中文
        file_path = os.path.join(locale_dir, "zh.json")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # 如果都加载失败，返回空字典
        return {}