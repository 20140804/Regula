# core/rule_templates.py
"""
预设规则模板库 - Pro 版专属
按行业分类，用户可一键导入
"""
from typing import List, Dict

# ===== 电商行业规则 =====
E_COMMERCE_RULES = [
    {
        "name": "禁止绝对化用语_销量",
        "keyword": "销量第一",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请使用'销量领先'、'热销'等客观表述"
    },
    {
        "name": "禁止绝对化用语_全网最低",
        "keyword": "全网最低",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请使用'价格优惠'、'超值'等客观表述"
    },
    {
        "name": "禁止绝对化用语_最好",
        "keyword": "最好",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请使用'品质优良'、'口碑良好'等客观表述"
    },
    {
        "name": "禁止绝对化用语_顶级",
        "keyword": "顶级",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请使用'高端'、'精品'等客观表述"
    },
    {
        "name": "禁止绝对化用语_唯一",
        "keyword": "唯一",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请使用'独特'、'特色'等客观表述"
    },
    {
        "name": "禁止虚假促销_永久有效",
        "keyword": "永久有效",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "一般",
        "position": "任意",
        "suggestion": "请明确促销有效期"
    },
    {
        "name": "禁止虚假促销_限时",
        "keyword": "限时",
        "near_keyword": "最后一天",
        "max_distance": 15,
        "severity": "一般",
        "position": "任意",
        "suggestion": "请确认是否真的限时，避免虚假促销"
    },
    {
        "name": "禁止误导性比较_竞品",
        "keyword": "竞品",
        "near_keyword": "差",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "避免贬低竞品，改用'对比'、'参考'等中性表述"
    },
    {
        "name": "禁止误导性比较_其他品牌",
        "keyword": "其他品牌",
        "near_keyword": "不如",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "避免贬低竞品，改用'对比'、'参考'等中性表述"
    },
    {
        "name": "禁止虚假承诺_无效退款",
        "keyword": "无效退款",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "请确认是否有无效退款政策，否则不要使用"
    },
]

# ===== 金融行业规则 =====
FINANCE_RULES = [
    {
        "name": "禁止保本承诺_保本",
        "keyword": "保本",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "金融产品不得承诺保本保息，违反监管规定"
    },
    {
        "name": "禁止保本承诺_零风险",
        "keyword": "零风险",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "金融产品不得承诺零风险，违反监管规定"
    },
    {
        "name": "禁止保本承诺_稳赚",
        "keyword": "稳赚",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "金融产品不得承诺稳赚，违反监管规定"
    },
    {
        "name": "禁止收益承诺_年化",
        "keyword": "年化收益率",
        "near_keyword": "保证",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "年化收益率不得保证，应注明'预期'、'历史'等字样"
    },
    {
        "name": "禁止收益承诺_预期收益",
        "keyword": "预期收益",
        "near_keyword": "保证",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "预期收益不得保证，应注明'不构成承诺'"
    },
    {
        "name": "禁止误导_低风险",
        "keyword": "低风险",
        "near_keyword": "保本",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "低风险不等于保本，请勿混淆概念"
    },
    {
        "name": "禁止误导_高收益",
        "keyword": "高收益",
        "near_keyword": "低风险",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "高收益与低风险通常不能并存，请客观描述"
    },
    {
        "name": "禁止内幕_内幕消息",
        "keyword": "内幕消息",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得利用内幕消息进行宣传，违反证券法"
    },
    {
        "name": "禁止承诺_绝对收益",
        "keyword": "绝对收益",
        "near_keyword": "保证",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得承诺绝对收益，违反监管规定"
    },
]

# ===== 医药/健康行业规则 =====
MEDICAL_RULES = [
    {
        "name": "禁止医疗功效_根治",
        "keyword": "根治",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得使用'根治'等绝对化表述，违反广告法"
    },
    {
        "name": "禁止医疗功效_彻底治愈",
        "keyword": "彻底治愈",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得使用'彻底治愈'等绝对化表述，违反广告法"
    },
    {
        "name": "禁止医疗功效_治愈率",
        "keyword": "治愈率",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得宣传治愈率，违反广告法"
    },
    {
        "name": "禁止医疗功效_100%",
        "keyword": "100%",
        "near_keyword": "有效",
        "max_distance": 5,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得承诺100%有效，违反广告法"
    },
    {
        "name": "禁止医疗功效_无副作用",
        "keyword": "无副作用",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "任何药物都有副作用，不得宣传无副作用"
    },
    {
        "name": "禁止医疗功效_天然",
        "keyword": "纯天然",
        "near_keyword": "无毒",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "纯天然不等于无毒，请勿误导消费者"
    },
    {
        "name": "禁止医疗功效_速效",
        "keyword": "速效",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "不得宣传'速效'，应客观描述效果"
    },
    {
        "name": "禁止医疗功效_特效",
        "keyword": "特效",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "严重",
        "position": "任意",
        "suggestion": "不得宣传'特效'，应客观描述效果"
    },
    {
        "name": "禁止医疗功效_万能",
        "keyword": "万能",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得宣传'万能'，违反广告法"
    },
]

# ===== 通用规则 =====
GENERAL_RULES = [
    {
        "name": "禁止歧视_性别",
        "keyword": "性别歧视",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及性别歧视内容"
    },
    {
        "name": "禁止歧视_种族",
        "keyword": "种族歧视",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及种族歧视内容"
    },
    {
        "name": "禁止歧视_年龄",
        "keyword": "年龄歧视",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及年龄歧视内容"
    },
    {
        "name": "禁止违法_赌博",
        "keyword": "赌博",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及赌博相关内容"
    },
    {
        "name": "禁止违法_毒品",
        "keyword": "毒品",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及毒品相关内容"
    },
    {
        "name": "禁止违法_暴力",
        "keyword": "暴力",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及暴力相关内容"
    },
    {
        "name": "禁止违法_淫秽",
        "keyword": "淫秽",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "致命",
        "position": "任意",
        "suggestion": "不得涉及淫秽相关内容"
    },
    {
        "name": "禁止虚假宣传_最",
        "keyword": "最",
        "near_keyword": "之一",
        "max_distance": 5,
        "severity": "一般",
        "position": "任意",
        "suggestion": "避免使用'最'字，可用'领先'、'优选'等替代"
    },
    {
        "name": "禁止虚假宣传_第一",
        "keyword": "第一",
        "near_keyword": "品牌",
        "max_distance": 5,
        "severity": "严重",
        "position": "任意",
        "suggestion": "'第一'需有权威数据支撑"
    },
    {
        "name": "禁止虚假宣传_首选",
        "keyword": "首选",
        "near_keyword": "",
        "max_distance": 10,
        "severity": "一般",
        "position": "任意",
        "suggestion": "'首选'需有依据"
    },
]


def get_all_templates() -> Dict[str, List[Dict]]:
    """获取所有规则模板"""
    return {
        "电商": E_COMMERCE_RULES,
        "金融": FINANCE_RULES,
        "医药": MEDICAL_RULES,
        "通用": GENERAL_RULES
    }


def get_template_names() -> List[str]:
    """获取所有模板名称列表"""
    return list(get_all_templates().keys())


def get_template_by_name(name: str) -> List[Dict]:
    """按名称获取模板"""
    templates = get_all_templates()
    return templates.get(name, [])