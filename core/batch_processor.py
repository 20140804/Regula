# core/batch_processor.py
"""
批量扫描处理器 - 遍历文件夹，扫描所有 .docx 文件
"""
import os
from pathlib import Path
from typing import List, Tuple, Dict
from core.doc_parser import DocParser
from core.rule_engine import RuleEngine
from models.violation import Violation


def scan_folder(folder_path: str) -> Dict[str, List[Violation]]:
    """
    扫描文件夹内所有 .docx 文件
    返回: {文件名: [违规列表]}
    """
    results = {}
    parser = DocParser()
    engine = RuleEngine()  # 自动加载自定义规则
    
    # 递归遍历所有 .docx 文件
    for file_path in Path(folder_path).rglob("*.docx"):
        try:
            full_text, _ = parser.parse_docx(str(file_path))
            violations = engine.scan(full_text)
            results[str(file_path)] = violations
        except Exception as e:
            # 单个文件出错不影响其他文件
            print(f"[批量扫描] 跳过 {file_path}: {e}")
            results[str(file_path)] = []
    
    return results


def aggregate_stats(results: Dict[str, List[Violation]]) -> Dict[str, Dict]:
    """
    统计每个文件的违规严重等级数量
    返回: {文件名: {"fatal": n, "serious": n, "normal": n, "total": n}}
    """
    stats = {}
    for file_path, violations in results.items():
        fatal = sum(1 for v in violations if v.severity == "致命")
        serious = sum(1 for v in violations if v.severity == "严重")
        normal = sum(1 for v in violations if v.severity == "一般")
        stats[file_path] = {
            "fatal": fatal,
            "serious": serious,
            "normal": normal,
            "total": len(violations),
            "filename": os.path.basename(file_path)
        }
    return stats


def get_team_summary(stats: Dict[str, Dict]) -> Dict:
    """
    生成团队总览
    """
    total_fatal = sum(s["fatal"] for s in stats.values())
    total_serious = sum(s["serious"] for s in stats.values())
    total_normal = sum(s["normal"] for s in stats.values())
    total_files = len(stats)
    files_with_issues = sum(1 for s in stats.values() if s["total"] > 0)
    
    return {
        "total_files": total_files,
        "files_with_issues": files_with_issues,
        "total_fatal": total_fatal,
        "total_serious": total_serious,
        "total_normal": total_normal,
        "total_violations": total_fatal + total_serious + total_normal
    }