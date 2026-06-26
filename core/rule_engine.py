# core/rule_engine.py
from typing import List, Dict
from models.violation import Violation
from core.text_splitter import TextSplitter
from config import BUILTIN_SENSITIVE_WORDS
from utils.rule_storage import load_rules  # 【新增】导入规则加载

class RuleEngine:
    def __init__(self, custom_rules: List[Dict] = None):
        # 如果传入了自定义规则则使用，否则从文件加载
        if custom_rules is not None:
            self.custom_rules = custom_rules
        else:
            self.custom_rules = load_rules()  # 【新增】从 JSON 加载
        self.splitter = TextSplitter()
    
    def scan(self, full_text: str) -> List[Violation]:
        findings = []
        sentences = self.splitter.split_by_sentences(full_text)
        
        for line_num, line_text, is_title in sentences:
            # 1. 内置词库匹配
            for word in BUILTIN_SENSITIVE_WORDS:
                if word in line_text:
                    severity = "一般"
                    if word == "第一" and is_title and len(line_text) < 20:
                        severity = "严重"
                    if word in ["根治", "彻底治愈", "零风险"]:
                        severity = "致命"
                    
                    context = self.splitter.extract_context(full_text, word)
                    findings.append(Violation(
                        keyword=word,
                        context=context,
                        line_num=line_num,
                        severity=severity,
                        position="标题" if is_title else "正文",
                        suggestion="避免绝对化表述" if severity != "一般" else "建议替换为客观描述"
                    ))
            
            # 2. 【修改】使用从文件加载的自定义规则
            for rule in self.custom_rules:
                if self._matches_rule(line_text, is_title, rule):
                    findings.append(Violation(
                        keyword=rule.get('name', '自定义规则'),
                        context=self.splitter.extract_context(full_text, rule.get('keyword', '')),
                        line_num=line_num,
                        severity=rule.get('severity', '严重'),
                        position="标题" if is_title else "正文",
                        suggestion=rule.get('suggestion', '请修改此项')
                    ))
        
        # 去重
        unique = {}
        for f in findings:
            key = (f.line_num, f.keyword)
            if key not in unique:
                unique[key] = f
        return list(unique.values())
    
    def _matches_rule(self, line_text: str, is_title: bool, rule: Dict) -> bool:
        keyword = rule.get('keyword', '')
        if keyword and keyword not in line_text:
            return False
        
        pos_rule = rule.get('position', '任意')
        if pos_rule == '标题' and not is_title:
            return False
        if pos_rule == '正文' and is_title:
            return False
        
        neighbor = rule.get('near_keyword', '')
        if neighbor:
            idx_k = line_text.find(keyword)
            idx_n = line_text.find(neighbor)
            if idx_k == -1 or idx_n == -1:
                return False
            if abs(idx_k - idx_n) > rule.get('max_distance', 10):
                return False
        return True