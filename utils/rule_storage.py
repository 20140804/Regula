# utils/rule_storage.py
"""
规则的本地存储 - 将自定义规则保存为 JSON 文件
"""
import os
import json
from typing import List, Dict

RULES_FILE = "custom_rules.json"

def load_rules() -> List[Dict]:
    """
    从 JSON 文件加载自定义规则
    """
    if not os.path.exists(RULES_FILE):
        # 返回默认示例规则
        return [{
            "name": "竞品拉踩",
            "keyword": "隔壁",
            "near_keyword": "老王",
            "max_distance": 10,
            "severity": "严重",
            "position": "任意",
            "suggestion": "不要点名竞品，改用'同行'或'其他品牌'"
        }]
    
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_rules(rules: List[Dict]) -> bool:
    """
    保存规则到 JSON 文件
    """
    try:
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def get_rules_summary(rules: List[Dict]) -> str:
    """
    生成规则的简短描述，用于在界面中显示
    """
    if not rules:
        return "（无自定义规则）"
    
    summaries = []
    for r in rules[:5]:  # 只显示前5条
        name = r.get('name', '未命名规则')
        keyword = r.get('keyword', '')
        summaries.append(f"· {name}（含'{keyword}'）")
    
    if len(rules) > 5:
        summaries.append(f"· …… 等共 {len(rules)} 条规则")
    
    return "\n".join(summaries)