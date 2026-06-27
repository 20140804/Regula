# cli_mode.py
"""
命令行模式 - Pro 版专属
用于 CI/CD 集成，批量自动化合规检查
"""
import sys
import os
import json
from pathlib import Path
from core.doc_parser import DocParser
from core.rule_engine import RuleEngine


def run_cli():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python cli_mode.py <文件路径或文件夹路径> [--output report.json]")
        print("示例: python cli_mode.py ./docs/")
        print("示例: python cli_mode.py ./docs/ --output result.json")
        sys.exit(1)
    
    path = sys.argv[1]
    output_file = "report.json"
    
    # 解析参数
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
    
    if not os.path.exists(path):
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)
    
    print(f"🔍 扫描路径: {path}")
    print("-" * 50)
    
    parser = DocParser()
    engine = RuleEngine()
    results = {}
    
    # 扫描文件
    if os.path.isfile(path):
        files = [path]
    else:
        files = list(Path(path).rglob("*.docx"))
    
    total_violations = 0
    for file_path in files:
        try:
            full_text, _ = parser.parse_docx(str(file_path))
            violations = engine.scan(full_text)
            results[str(file_path)] = [
                {
                    "severity": v.severity,
                    "line": v.line_num,
                    "keyword": v.keyword,
                    "position": v.position,
                    "suggestion": v.suggestion
                }
                for v in violations
            ]
            total_violations += len(violations)
            print(f"✅ {os.path.basename(file_path)}: {len(violations)} 项违规")
        except Exception as e:
            print(f"❌ {os.path.basename(file_path)}: {str(e)}")
    
    print("-" * 50)
    print(f"📊 扫描完成: {len(files)} 个文件，{total_violations} 项违规")
    
    # 输出 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"📄 报告已保存: {output_file}")


if __name__ == "__main__":
    run_cli()