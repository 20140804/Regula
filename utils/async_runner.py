# utils/async_runner.py
"""
后台线程扫描器 - 防止 GUI 界面卡死
"""
from PySide6.QtCore import QThread, Signal  # ← 添加这行
from core.doc_parser import DocParser
from core.rule_engine import RuleEngine
from models.violation import Violation
from typing import List
from core.batch_processor import scan_folder, aggregate_stats, get_team_summary


class ScanWorker(QThread):
    """单文件扫描工作线程"""
    finished = Signal(list, str)
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            parser = DocParser()
            full_text, paragraphs = parser.parse_docx(self.file_path)
            engine = RuleEngine()
            violations = engine.scan(full_text)
            self.finished.emit(violations, self.file_path)
        except Exception as e:
            self.error.emit(str(e))


class BatchScanWorker(QThread):
    """批量扫描工作线程"""
    finished = Signal(dict, dict)  # (stats, summary)
    progress = Signal(int, str)    # (当前文件数, 文件名)
    error = Signal(str)

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            results = scan_folder(self.folder_path)
            stats = aggregate_stats(results)
            summary = get_team_summary(stats)
            self.finished.emit(stats, summary)
        except Exception as e:
            self.error.emit(str(e))