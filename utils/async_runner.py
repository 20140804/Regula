# utils/async_runner.py
"""
后台线程扫描器 - 单文件、批量、OCR 识别
"""
from PySide6.QtCore import QThread, Signal
from core.doc_parser import DocParser
from core.rule_engine import RuleEngine
from models.violation import Violation
from typing import List
from core.batch_processor import scan_folder, aggregate_stats, get_team_summary
from core.ocr_engine import ocr_engine


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


class OCRScanWorker(QThread):
    """OCR 图片扫描工作线程（Pro 功能）"""
    finished = Signal(list, str)  # (违规列表, 图片路径)
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            # 1. 从图片提取文字
            full_text, text_details = ocr_engine.extract_text(self.image_path)

            if not full_text.strip():
                self.finished.emit([], self.image_path)
                return

            # 2. 用规则引擎扫描提取的文字
            engine = RuleEngine()
            violations = engine.scan(full_text)

            # 3. 在违规记录中添加 OCR 特有信息（图片来源标识）
            for v in violations:
                v.context = f"[图片OCR] {v.context}"

            self.finished.emit(violations, self.image_path)

        except Exception as e:
            self.error.emit(str(e))