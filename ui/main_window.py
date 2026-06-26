# ui/main_window.py
"""
主窗口 - 支持单文件/文件夹拖拽、扫描、热力图、PDF导出、规则管理
"""
import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFileDialog, QMessageBox,
    QDialog, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from utils.async_runner import ScanWorker, BatchScanWorker
from models.violation import Violation
from exporters.pdf_exporter import export_to_pdf
from ui.heatmap_widget import HeatmapWidget
from config import THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regula - 合规鹰眼扫描器")
        self.setMinimumSize(1100, 750)

        self.current_file_path = None
        self.current_violations = []
        self.current_batch_stats = {}  # 批量扫描统计

        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)

        # ===== 标题 =====
        title_label = QLabel("🦅 Regula 合规鹰眼")
        title_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {THEME['primary']}; padding: 5px 0;")
        main_layout.addWidget(title_label)

        # ===== 拖拽区 + 按钮 =====
        top_layout = QHBoxLayout()

        self.drop_label = QLabel(
            "📂 拖拽 Word 文档 (.docx) 或文件夹到此处\n"
            "（支持批量扫描整个文件夹）"
        )
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setObjectName("drop_area")
        self.drop_label.setMinimumHeight(120)
        top_layout.addWidget(self.drop_label, 3)

        # 按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        self.btn_open = QPushButton("📁 选择文件/文件夹")
        self.btn_open.clicked.connect(self._on_open_file)
        button_layout.addWidget(self.btn_open)

        self.btn_scan = QPushButton("🚀 开始扫描")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self._on_start_scan)
        self.btn_scan.setEnabled(False)
        button_layout.addWidget(self.btn_scan)

        self.btn_export = QPushButton("📄 导出PDF报告")
        self.btn_export.setObjectName("btn_export")
        self.btn_export.clicked.connect(self._on_export_pdf)
        self.btn_export.setEnabled(False)
        button_layout.addWidget(self.btn_export)

        self.btn_rules = QPushButton("⚙️ 规则管理")
        self.btn_rules.setObjectName("btn_rules")
        self.btn_rules.clicked.connect(self._on_manage_rules)
        button_layout.addWidget(self.btn_rules)

        self.btn_clear = QPushButton("🗑️ 清空结果")
        self.btn_clear.clicked.connect(self._on_clear_results)
        button_layout.addWidget(self.btn_clear)

        button_layout.addStretch()
        top_layout.addLayout(button_layout, 1)
        main_layout.addLayout(top_layout)

        # ===== 进度条 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # ===== 状态栏 =====
        self.status_label = QLabel("就绪，请拖入文档或文件夹")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        main_layout.addWidget(self.status_label)

        # ===== Tab切换：详情列表 / 热力图 =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #dcdde1; border-radius: 8px; }
            QTabBar::tab { padding: 8px 16px; }
        """)

        # Tab1: 违规列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["严重等级", "行号", "关键词", "位置", "上下文", "修改建议"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.tab_widget.addTab(self.table, "📋 违规详情")

        # Tab2: 热力图
        self.heatmap_widget = HeatmapWidget()
        self.tab_widget.addTab(self.heatmap_widget, "🔥 热力图")

        main_layout.addWidget(self.tab_widget)

        # ===== 底部统计 =====
        self.stats_label = QLabel("共 0 项违规 | 0 个文件")
        self.stats_label.setStyleSheet(f"color: {THEME['text_dark']}; font-weight: bold; padding: 5px; background: #ecf0f1; border-radius: 5px;")
        main_layout.addWidget(self.stats_label)

        # 默认识别当前模式
        self.is_batch_mode = False

    # ===== 拖拽事件 =====
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                path = urls[0].toLocalFile()
                if path.endswith('.docx') or os.path.isdir(path):
                    event.acceptProposedAction()
                    self.drop_label.setStyleSheet("""
                        QLabel#drop_area {
                            border: 3px dashed #27ae60;
                            border-radius: 10px;
                            background-color: #d5f5e3;
                            padding: 30px;
                            font-size: 16px;
                            color: #1e8449;
                        }
                    """)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._reset_drop_style()

    def dropEvent(self, event: QDropEvent):
        self._reset_drop_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.endswith('.docx'):
                self._load_file(path)
            elif os.path.isdir(path):
                self._load_folder(path)
            else:
                QMessageBox.warning(self, "格式错误", "请拖入 .docx 文件或文件夹")

    def _reset_drop_style(self):
        self.drop_label.setStyleSheet("""
            QLabel#drop_area {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
                padding: 30px;
                font-size: 16px;
                color: #2c3e50;
            }
            QLabel#drop_area:hover {
                background-color: #d5dbdb;
            }
        """)

    # ===== 加载逻辑 =====
    def _load_file(self, file_path: str):
        self.is_batch_mode = False
        self.current_file_path = file_path
        self.drop_label.setText(f"📄 {os.path.basename(file_path)}\n点击「开始扫描」进行分析")
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"已加载文件: {file_path}")
        # 切换到详情Tab
        self.tab_widget.setCurrentIndex(0)

    def _load_folder(self, folder_path: str):
        self.is_batch_mode = True
        self.current_file_path = folder_path
        self.drop_label.setText(f"📁 {os.path.basename(folder_path)}\n包含所有 .docx 文件，点击「开始扫描」批量分析")
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"已加载文件夹: {folder_path}")
        self.tab_widget.setCurrentIndex(0)

    def _on_open_file(self):
        # 让用户选择文件或文件夹
        import shutil
        reply = QMessageBox.question(
            self,
            "选择模式",
            "点击「是」选择单个文件，点击「否」选择文件夹（批量扫描）",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply == QMessageBox.Yes:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择 Word 文档", "", "Word 文档 (*.docx)")
            if file_path:
                self._load_file(file_path)
        elif reply == QMessageBox.No:
            folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
            if folder_path:
                self._load_folder(folder_path)

    # ===== 扫描 =====
    def _on_start_scan(self):
        if not self.current_file_path:
            return

        self.table.setRowCount(0)
        self.heatmap_widget.update_data({})
        self.current_violations = []
        self.current_batch_stats = {}

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)

        if self.is_batch_mode:
            # 批量扫描
            self.status_label.setText("⏳ 批量扫描中，请稍候...")
            self.worker = BatchScanWorker(self.current_file_path)
            self.worker.finished.connect(self._on_batch_finished)
            self.worker.error.connect(self._on_scan_error)
            self.worker.start()
        else:
            # 单文件扫描
            self.status_label.setText("⏳ 扫描中，请稍候...")
            self.worker = ScanWorker(self.current_file_path)
            self.worker.finished.connect(self._on_scan_finished)
            self.worker.error.connect(self._on_scan_error)
            self.worker.start()

    def _on_scan_finished(self, violations: list, file_path: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.current_violations = violations
        self.btn_export.setEnabled(True)

        self.status_label.setText(f"✅ 扫描完成: {os.path.basename(file_path)}")
        self._populate_table(violations)
        self._update_stats(violations, is_batch=False)

        if not violations:
            QMessageBox.information(self, "扫描结果", "🎉 恭喜！未发现任何违规表述！")

    def _on_batch_finished(self, stats: dict, summary: dict):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.current_batch_stats = stats

        # 把第一个文件的结果展示在详情页（或汇总所有）
        all_violations = []
        for v_list in stats.values():
            all_violations.extend(v_list)
        self.current_violations = all_violations

        self._populate_table(all_violations)
        self._update_stats(all_violations, is_batch=True, summary=summary)

        # 更新热力图
        self.heatmap_widget.update_data(stats)

        # 切换到热力图Tab
        self.tab_widget.setCurrentIndex(1)

        self.btn_export.setEnabled(True)
        self.status_label.setText(f"✅ 批量扫描完成: 共扫描 {summary['total_files']} 个文件")

        QMessageBox.information(
            self,
            "批量扫描完成",
            f"扫描了 {summary['total_files']} 个文件\n"
            f"发现违规文件: {summary['files_with_issues']} 个\n"
            f"违规总数: {summary['total_violations']} 项"
        )

    def _on_scan_error(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"❌ 扫描失败: {error_msg}")
        QMessageBox.critical(self, "扫描错误", f"读取失败：\n{error_msg}")

    # ===== 表格填充 =====
    def _populate_table(self, violations: list):
        self.table.setRowCount(len(violations))
        for row, v in enumerate(violations):
            self.table.setItem(row, 0, QTableWidgetItem(v.severity))
            self.table.setItem(row, 1, QTableWidgetItem(str(v.line_num)))
            self.table.setItem(row, 2, QTableWidgetItem(v.keyword))
            self.table.setItem(row, 3, QTableWidgetItem(v.position))
            ctx = v.context[:80] + ("..." if len(v.context) > 80 else "")
            self.table.setItem(row, 4, QTableWidgetItem(ctx))
            self.table.setItem(row, 5, QTableWidgetItem(v.suggestion))

            for col in range(6):
                item = self.table.item(row, col)
                if item:
                    if v.severity == "致命":
                        item.setForeground(Qt.GlobalColor.red)
                    elif v.severity == "严重":
                        item.setForeground(Qt.GlobalColor.darkYellow)

    def _update_stats(self, violations: list, is_batch: bool = False, summary: dict = None):
        fatal = sum(1 for v in violations if v.severity == "致命")
        serious = sum(1 for v in violations if v.severity == "严重")
        normal = sum(1 for v in violations if v.severity == "一般")

        if is_batch and summary:
            total_files = summary['total_files']
            files_with_issues = summary['files_with_issues']
            self.stats_label.setText(
                f"📊 共 {len(violations)} 项违规 | "
                f"致命: {fatal} | 严重: {serious} | 一般: {normal} | "
                f"扫描文件: {total_files} 个 (含违规: {files_with_issues} 个)"
            )
        else:
            self.stats_label.setText(
                f"共 {len(violations)} 项违规  |  🔴致命: {fatal}  |  🟠严重: {serious}  |  🟡一般: {normal}"
            )

    # ===== 清空 =====
    def _on_clear_results(self):
        self.table.setRowCount(0)
        self.heatmap_widget.update_data({})
        self.current_violations = []
        self.current_batch_stats = {}
        self.stats_label.setText("共 0 项违规 | 0 个文件")
        self.status_label.setText("已清空结果")
        self.current_file_path = None
        self.drop_label.setText(
            "📂 拖拽 Word 文档 (.docx) 或文件夹到此处\n"
            "（支持批量扫描整个文件夹）"
        )
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.is_batch_mode = False

    # ===== PDF导出（支持批量模式） =====
    def _on_export_pdf(self):
        if not self.current_violations and not self.current_batch_stats:
            QMessageBox.warning(self, "无数据", "请先扫描文档再导出报告。")
            return

        if self.is_batch_mode and self.current_batch_stats:
            # 批量模式：导出汇总报告
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存批量报告 PDF",
                "批量合规报告.pdf",
                "PDF 文件 (*.pdf)"
            )
            if not save_path:
                return

            try:
                # 合并所有违规
                all_v = self.current_violations
                export_to_pdf(
                    violations=all_v,
                    source_file=f"批量扫描: {os.path.basename(self.current_file_path)}",
                    output_path=save_path
                )
                QMessageBox.information(self, "导出成功", f"✅ 批量报告已保存至：\n{save_path}")
                self.status_label.setText(f"✅ 批量PDF已导出")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"生成 PDF 时出错：\n{str(e)}")
        else:
            # 单文件模式
            if not self.current_file_path:
                QMessageBox.warning(self, "无数据", "请先扫描文档再导出报告。")
                return
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存 PDF 报告",
                os.path.basename(self.current_file_path).replace('.docx', '_合规报告.pdf'),
                "PDF 文件 (*.pdf)"
            )
            if not save_path:
                return

            try:
                export_to_pdf(
                    violations=self.current_violations,
                    source_file=self.current_file_path,
                    output_path=save_path
                )
                QMessageBox.information(self, "导出成功", f"✅ PDF 报告已保存至：\n{save_path}")
                self.status_label.setText(f"✅ PDF 已导出: {os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"生成 PDF 时出错：\n{str(e)}")

    # ===== 规则管理 =====
    def _on_manage_rules(self):
        from ui.rule_edit_dialog import RuleEditDialog
        dialog = RuleEditDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.status_label.setText("✅ 规则已更新，请重新扫描以应用新规则")
            if self.current_file_path:
                QMessageBox.information(
                    self,
                    "规则已更新",
                    "自定义规则已保存。点击「开始扫描」重新分析当前内容以应用新规则。"
                )