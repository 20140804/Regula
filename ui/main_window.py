# ui/main_window.py
"""
主窗口 - 完整版
支持：单文件/文件夹/图片拖拽、扫描、热力图、PDF导出、规则管理、Pro激活、规则模板库、设置
PRO MAX 版额外支持：AI 智能语义理解、违规自动分类、智能修改建议
"""
import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFileDialog, QMessageBox,
    QDialog, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from utils.async_runner import ScanWorker, BatchScanWorker, OCRScanWorker
from models.violation import Violation
from exporters.pdf_exporter import export_to_pdf
from ui.heatmap_widget import HeatmapWidget
from config import THEME, PRO_ACTIVATED, PRO_MAX_ACTIVATED
from utils.settings_manager import load_settings, load_language_pack
from utils.logger import log_exception, log_info, log_error
from core.ai_engine import is_ai_available
from core.ai_suggester import AISuggester


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regula - 合规鹰眼扫描器")
        self.setMinimumSize(1100, 750)

        # 加载设置和语言包
        self.settings = load_settings()
        self.lang_pack = load_language_pack(self.settings.get("language", "zh"))
        
        self.current_file_path = None
        self.current_violations = []
        self.current_batch_stats = {}
        self.is_batch_mode = False
        self.is_image_mode = False

        # Pro Max 状态
        self.is_pro_max = PRO_ACTIVATED and PRO_MAX_ACTIVATED
        self.ai_available = is_ai_available()
        self.ai_enhanced_violations = []

        self._setup_ui()
        self.setAcceptDrops(True)
        
        log_info("主窗口初始化完成")

    def _tr(self, key: str) -> str:
        """获取当前语言的翻译"""
        return self.lang_pack.get(key, key)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)

        # ===== 标题 =====
        title_label = QLabel("🦅 Regula 合规鹰眼")
        title_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {THEME['primary']}; padding: 5px 0;")
        main_layout.addWidget(title_label)

        # ===== Pro 状态栏 =====
        pro_layout = QHBoxLayout()

        # Pro 状态
        self.pro_status_label = QLabel(
            self._tr("pro_activated") if PRO_ACTIVATED else self._tr("pro_free")
        )
        self.pro_status_label.setStyleSheet(
            f"color: {'#27ae60' if PRO_ACTIVATED else '#e67e22'}; font-weight: bold; font-size: 14px;"
        )
        pro_layout.addWidget(self.pro_status_label)

        # Pro Max 状态（仅在 Pro 已激活时显示）
        if self.is_pro_max:
            self.promax_status_label = QLabel(" 👑 PRO MAX")
            self.promax_status_label.setStyleSheet("color: #8e44ad; font-weight: bold; font-size: 14px;")
            pro_layout.addWidget(self.promax_status_label)

        pro_layout.addStretch()

        if not PRO_ACTIVATED:
            self.btn_upgrade = QPushButton(self._tr("btn_upgrade"))
            self.btn_upgrade.clicked.connect(self._on_upgrade)
            self.btn_upgrade.setStyleSheet("background-color: #e67e22; color: white; padding: 4px 16px; border-radius: 4px; font-weight: bold;")
            pro_layout.addWidget(self.btn_upgrade)
        elif PRO_ACTIVATED and not PRO_MAX_ACTIVATED:
            self.btn_promax_upgrade = QPushButton("👑 升级 Pro Max")
            self.btn_promax_upgrade.clicked.connect(self._on_upgrade_promax)
            self.btn_promax_upgrade.setStyleSheet("background-color: #8e44ad; color: white; padding: 4px 16px; border-radius: 4px; font-weight: bold;")
            pro_layout.addWidget(self.btn_promax_upgrade)

        main_layout.addLayout(pro_layout)

        # ===== 拖拽区 + 按钮 =====
        top_layout = QHBoxLayout()

        self.drop_label = QLabel(self._tr("hint_drop"))
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setObjectName("drop_area")
        self.drop_label.setMinimumHeight(120)
        top_layout.addWidget(self.drop_label, 3)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        self.btn_open = QPushButton(self._tr("btn_open"))
        self.btn_open.clicked.connect(self._on_open_file)
        button_layout.addWidget(self.btn_open)

        self.btn_scan = QPushButton(self._tr("btn_scan"))
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.clicked.connect(self._on_start_scan)
        self.btn_scan.setEnabled(False)
        button_layout.addWidget(self.btn_scan)

        self.btn_export = QPushButton(self._tr("btn_export"))
        self.btn_export.setObjectName("btn_export")
        self.btn_export.clicked.connect(self._on_export_pdf)
        self.btn_export.setEnabled(False)
        button_layout.addWidget(self.btn_export)

        self.btn_rules = QPushButton(self._tr("btn_rules"))
        self.btn_rules.setObjectName("btn_rules")
        self.btn_rules.clicked.connect(self._on_manage_rules)
        button_layout.addWidget(self.btn_rules)

        self.btn_templates = QPushButton(self._tr("btn_templates"))
        self.btn_templates.clicked.connect(self._on_manage_templates)
        self.btn_templates.setStyleSheet("padding: 12px; font-size: 14px; background-color: #8e44ad; color: white; border-radius: 6px;")
        button_layout.addWidget(self.btn_templates)

        self.btn_clear = QPushButton(self._tr("btn_clear"))
        self.btn_clear.clicked.connect(self._on_clear_results)
        button_layout.addWidget(self.btn_clear)

        self.btn_settings = QPushButton(self._tr("btn_settings"))
        self.btn_settings.clicked.connect(self._on_open_settings)
        self.btn_settings.setStyleSheet("padding: 12px; font-size: 14px; background-color: #95a5a6; color: white; border-radius: 6px;")
        button_layout.addWidget(self.btn_settings)

        button_layout.addStretch()
        top_layout.addLayout(button_layout, 1)
        main_layout.addLayout(top_layout)

        # ===== 进度条 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # ===== 状态栏 =====
        self.status_label = QLabel(self._tr("status_ready"))
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        main_layout.addWidget(self.status_label)

        # ===== Tab切换 =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #dcdde1; border-radius: 8px; }
            QTabBar::tab { padding: 8px 16px; }
        """)

        # 表格：动态列数（Pro Max 多一列 AI 分类）
        self.table = QTableWidget()
        if self.is_pro_max:
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                self._tr("table_severity"), self._tr("table_line"), self._tr("table_keyword"),
                self._tr("table_position"), self._tr("table_context"), self._tr("table_suggestion"),
                "AI 分类"
            ])
        else:
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                self._tr("table_severity"), self._tr("table_line"), self._tr("table_keyword"),
                self._tr("table_position"), self._tr("table_context"), self._tr("table_suggestion")
            ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        if self.is_pro_max:
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.tab_widget.addTab(self.table, self._tr("tab_details"))

        self.heatmap_widget = HeatmapWidget()
        self.tab_widget.addTab(self.heatmap_widget, self._tr("tab_heatmap"))

        main_layout.addWidget(self.tab_widget)

        self.stats_label = QLabel("共 0 项违规 | 0 个文件")
        self.stats_label.setStyleSheet(f"color: {THEME['text_dark']}; font-weight: bold; padding: 5px; background: #ecf0f1; border-radius: 5px;")
        main_layout.addWidget(self.stats_label)

    # ===== 拖拽事件 =====
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                path = urls[0].toLocalFile()
                is_docx = path.endswith('.docx')
                is_image = path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'))
                is_folder = os.path.isdir(path)
                if is_docx or is_image or is_folder:
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
            try:
                if path.endswith('.docx'):
                    self._load_file(path)
                elif path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                    self._load_image(path)
                elif os.path.isdir(path):
                    self._load_folder(path)
                else:
                    QMessageBox.warning(self, self._tr("error_invalid_format"), 
                                       self._tr("error_invalid_format"))
            except Exception as e:
                log_exception(e, f"拖拽文件: {path}")
                QMessageBox.critical(self, self._tr("error_scan_failed"), str(e))

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
        self.is_image_mode = False
        self.current_file_path = file_path
        self.drop_label.setText(f"📄 {os.path.basename(file_path)}\n点击「开始扫描」进行分析")
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"{self._tr('status_loading')}: {file_path}")
        self.tab_widget.setCurrentIndex(0)
        log_info(f"加载文件: {file_path}")

    def _load_image(self, image_path: str):
        self.is_batch_mode = False
        self.is_image_mode = True
        self.current_file_path = image_path
        self.drop_label.setText(f"🖼️ {os.path.basename(image_path)}\n点击「开始扫描」进行 OCR 文字识别")
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"{self._tr('status_loading')}: {image_path}")
        self.tab_widget.setCurrentIndex(0)
        self.stats_label.setText("🖼️ OCR 识别将提取图片中的所有文字进行合规扫描")
        log_info(f"加载图片: {image_path}")

    def _load_folder(self, folder_path: str):
        self.is_batch_mode = True
        self.is_image_mode = False
        self.current_file_path = folder_path
        self.drop_label.setText(f"📁 {os.path.basename(folder_path)}\n包含所有 .docx 文件，点击「开始扫描」批量分析")
        self.btn_scan.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.status_label.setText(f"{self._tr('status_loading')}: {folder_path}")
        self.tab_widget.setCurrentIndex(0)
        log_info(f"加载文件夹: {folder_path}")

    def _on_open_file(self):
        reply = QMessageBox.question(
            self,
            "选择模式",
            "点击「是」选择单个文件，点击「否」选择文件夹（批量扫描）",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply == QMessageBox.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择文件",
                "",
                "所有支持 (*.docx *.png *.jpg *.jpeg *.bmp);;Word文档 (*.docx);;图片 (*.png *.jpg *.jpeg *.bmp)"
            )
            if file_path:
                if file_path.endswith('.docx'):
                    self._load_file(file_path)
                else:
                    self._load_image(file_path)
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
        self.ai_enhanced_violations = []

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)

        try:
            if self.is_image_mode:
                self.status_label.setText("⏳ OCR 识别中，请稍候...")
                self.worker = OCRScanWorker(self.current_file_path)
                self.worker.finished.connect(self._on_scan_finished)
                self.worker.error.connect(self._on_scan_error)
                self.worker.start()
            elif self.is_batch_mode:
                self.status_label.setText("⏳ 批量扫描中，请稍候...")
                self.worker = BatchScanWorker(self.current_file_path)
                self.worker.finished.connect(self._on_batch_finished)
                self.worker.error.connect(self._on_scan_error)
                self.worker.start()
            else:
                self.status_label.setText("⏳ 扫描中，请稍候...")
                self.worker = ScanWorker(self.current_file_path)
                self.worker.finished.connect(self._on_scan_finished)
                self.worker.error.connect(self._on_scan_error)
                self.worker.start()
        except Exception as e:
            log_exception(e, "启动扫描线程")
            self._on_scan_error(str(e))

    def _on_scan_finished(self, violations: list, file_path: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)

        # 如果是 Pro Max 且有违规，进行 AI 增强
        if self.is_pro_max and violations and self.ai_available:
            self.status_label.setText("🧠 AI 智能分析中...")
            try:
                self.ai_enhanced_violations = AISuggester.enhance_batch(violations)
                self.current_violations = self.ai_enhanced_violations
                log_info(f"AI 增强完成，处理了 {len(violations)} 条违规")
            except Exception as e:
                log_exception(e, "AI 增强失败")
                self.current_violations = violations
                self.ai_enhanced_violations = []
        else:
            self.current_violations = violations
            self.ai_enhanced_violations = []

        self.btn_export.setEnabled(True)
        self.status_label.setText(f"✅ {self._tr('status_complete')}: {os.path.basename(file_path)}")
        self._populate_table(self.current_violations)
        self._update_stats(self.current_violations, is_batch=False)

        if not violations:
            QMessageBox.information(self, self._tr("success_scan_clean"), 
                                   self._tr("success_scan_clean"))

    def _on_batch_finished(self, stats: dict, summary: dict):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.current_batch_stats = stats

        all_violations = []
        for v_list in stats.values():
            all_violations.extend(v_list)
        self.current_violations = all_violations

        # 如果是 Pro Max，对批量结果进行 AI 增强
        if self.is_pro_max and all_violations and self.ai_available:
            try:
                self.ai_enhanced_violations = AISuggester.enhance_batch(all_violations)
                self.current_violations = self.ai_enhanced_violations
                log_info(f"AI 批量增强完成，处理了 {len(all_violations)} 条违规")
            except Exception as e:
                log_exception(e, "AI 批量增强失败")
                self.current_violations = all_violations
                self.ai_enhanced_violations = []

        self._populate_table(self.current_violations)
        self._update_stats(self.current_violations, is_batch=True, summary=summary)

        self.heatmap_widget.update_data(stats)
        self.tab_widget.setCurrentIndex(1)

        self.btn_export.setEnabled(True)
        self.status_label.setText(f"✅ 批量扫描完成: 共扫描 {summary['total_files']} 个文件")
        log_info(f"批量扫描完成: {summary['total_files']} 个文件, {summary['total_violations']} 项违规")

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
        self.status_label.setText(f"❌ {self._tr('status_error')}: {error_msg}")
        log_error(f"扫描错误: {error_msg}")
        QMessageBox.critical(self, self._tr("error_scan_failed"), 
                            f"{self._tr('error_scan_failed')}：\n{error_msg}")

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

            # Pro Max 专属：AI 分类列
            if self.is_pro_max and hasattr(v, 'category'):
                category_text = v.category if v.category else "未分类"
                category_item = QTableWidgetItem(category_text)
                # 根据置信度着色
                if hasattr(v, 'confidence') and v.confidence > 0.7:
                    category_item.setForeground(Qt.GlobalColor.darkGreen)
                elif hasattr(v, 'confidence') and v.confidence > 0.4:
                    category_item.setForeground(Qt.GlobalColor.darkYellow)
                else:
                    category_item.setForeground(Qt.GlobalColor.darkGray)
                self.table.setItem(row, 6, category_item)

            # 颜色标记（原有逻辑）
            for col in range(self.table.columnCount()):
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
            self.stats_label.setText(
                self._tr("stats_batch").format(
                    total=len(violations),
                    fatal=fatal,
                    serious=serious,
                    normal=normal,
                    files=summary['total_files'],
                    issues=summary['files_with_issues']
                )
            )
        else:
            self.stats_label.setText(
                self._tr("stats_template").format(
                    total=len(violations),
                    fatal=fatal,
                    serious=serious,
                    normal=normal
                )
            )

    def _on_clear_results(self):
        self.table.setRowCount(0)
        self.heatmap_widget.update_data({})
        self.current_violations = []
        self.current_batch_stats = {}
        self.ai_enhanced_violations = []
        self.stats_label.setText("共 0 项违规 | 0 个文件")
        self.status_label.setText("已清空结果")
        self.current_file_path = None
        self.drop_label.setText(self._tr("hint_drop"))
        self.btn_scan.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.is_batch_mode = False
        self.is_image_mode = False
        log_info("清空结果")

    # ===== PDF导出 =====
    def _on_export_pdf(self):
        if not self.current_violations and not self.current_batch_stats:
            QMessageBox.warning(self, "无数据", "请先扫描文档再导出报告。")
            return

        try:
            if self.is_batch_mode and self.current_batch_stats:
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存批量报告 PDF",
                    "批量合规报告.pdf",
                    "PDF 文件 (*.pdf)"
                )
                if not save_path:
                    return
                all_v = self.current_violations
                export_to_pdf(
                    violations=all_v,
                    source_file=f"批量扫描: {os.path.basename(self.current_file_path)}",
                    output_path=save_path
                )
                QMessageBox.information(self, self._tr("success_pdf_exported"), 
                                       f"✅ {self._tr('success_pdf_exported')}：\n{save_path}")
                self.status_label.setText(f"✅ PDF已导出: {os.path.basename(save_path)}")
                log_info(f"PDF导出: {save_path}")
            else:
                if not self.current_file_path:
                    QMessageBox.warning(self, "无数据", "请先扫描文档再导出报告。")
                    return
                base = os.path.basename(self.current_file_path)
                if self.is_image_mode:
                    base = base.replace('.png', '_OCR报告.pdf').replace('.jpg', '_OCR报告.pdf')
                else:
                    base = base.replace('.docx', '_合规报告.pdf')
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存 PDF 报告",
                    base,
                    "PDF 文件 (*.pdf)"
                )
                if not save_path:
                    return
                export_to_pdf(
                    violations=self.current_violations,
                    source_file=self.current_file_path,
                    output_path=save_path
                )
                QMessageBox.information(self, self._tr("success_pdf_exported"), 
                                       f"✅ {self._tr('success_pdf_exported')}：\n{save_path}")
                self.status_label.setText(f"✅ PDF已导出: {os.path.basename(save_path)}")
                log_info(f"PDF导出: {save_path}")
        except Exception as e:
            log_exception(e, "PDF导出")
            QMessageBox.critical(self, "导出失败", f"生成 PDF 时出错：\n{str(e)}")

    # ===== 规则管理 =====
    def _on_manage_rules(self):
        try:
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
        except Exception as e:
            log_exception(e, "打开规则管理")
            QMessageBox.critical(self, "错误", f"打开规则管理失败：{str(e)}")

    def _on_manage_templates(self):
        try:
            from ui.rule_template_dialog import RuleTemplateDialog
            dialog = RuleTemplateDialog(self)
            if dialog.exec() == QDialog.Accepted:
                self.status_label.setText("✅ 规则模板已导入，请重新扫描以应用新规则")
                if self.current_file_path:
                    QMessageBox.information(
                        self,
                        "模板已导入",
                        "规则模板已导入并合并到当前规则列表。点击「开始扫描」重新分析当前内容以应用新规则。"
                    )
        except Exception as e:
            log_exception(e, "打开规则模板库")
            QMessageBox.critical(self, "错误", f"打开规则模板库失败：{str(e)}")

    # ===== 设置 =====
    def _on_open_settings(self):
        try:
            from ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            if dialog.exec() == QDialog.Accepted:
                # 设置已保存，提示重启
                pass
        except Exception as e:
            log_exception(e, "打开设置")
            QMessageBox.critical(self, "错误", f"打开设置失败：{str(e)}")

    # ===== Pro 激活 =====
    def _on_upgrade(self):
        try:
            from ui.pro_activation_dialog import ProActivationDialog
            dialog = ProActivationDialog(self)
            if dialog.exec() == QDialog.Accepted:
                # 激活成功，更新UI状态
                self.pro_status_label.setText(self._tr("pro_activated"))
                self.pro_status_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
                self.btn_upgrade.setVisible(False)
                log_info("Pro 激活成功")
                QMessageBox.information(
                    self,
                    "激活成功",
                    "Pro 功能已解锁，部分功能需要重启软件后完全生效。\n（建议关闭并重新启动 Regula）"
                )
        except Exception as e:
            log_exception(e, "Pro 激活")
            QMessageBox.critical(self, "错误", f"激活失败：{str(e)}")

    # ===== Pro Max 升级 =====
    def _on_upgrade_promax(self):
        try:
            from ui.promax_activation_dialog import ProMaxActivationDialog
            dialog = ProMaxActivationDialog(self)
            if dialog.exec() == QDialog.Accepted:
                # 激活成功，更新UI
                self.promax_status_label = QLabel(" 👑 PRO MAX")
                self.promax_status_label.setStyleSheet("color: #8e44ad; font-weight: bold; font-size: 14px;")
                # 隐藏升级按钮
                self.btn_promax_upgrade.setVisible(False)
                self.is_pro_max = True
                self.ai_available = is_ai_available()
                log_info("Pro Max 激活成功")
                QMessageBox.information(
                    self,
                    "激活成功",
                    "Pro Max 已激活，AI 智能功能已解锁！\n建议重启软件以完全生效。"
                )
        except Exception as e:
            log_exception(e, "Pro Max 激活")
            QMessageBox.critical(self, "错误", f"激活失败：{str(e)}")