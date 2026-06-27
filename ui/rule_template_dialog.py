# ui/rule_template_dialog.py
"""
规则模板库弹窗 - Pro 版专属
一键导入行业预设规则
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QTextEdit, QMessageBox,
    QListWidgetItem
)
from PySide6.QtCore import Qt
from core.rule_templates import get_all_templates, get_template_by_name
from utils.rule_storage import load_rules, save_rules


class RuleTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 规则模板库")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self._load_templates()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("📚 规则模板库（Pro 版）")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QLabel(
            "选择行业模板，一键导入预设规则。导入后将合并到当前规则列表中。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(info)
        
        # 主布局：左侧列表 + 右侧预览
        main_layout = QHBoxLayout()
        
        # 左侧模板列表
        left_layout = QVBoxLayout()
        left_label = QLabel("行业模板")
        left_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(left_label)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_selected)
        left_layout.addWidget(self.template_list)
        
        # 右侧预览
        right_layout = QVBoxLayout()
        right_label = QLabel("规则预览")
        right_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(right_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        right_layout.addWidget(self.preview_text)
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        layout.addLayout(main_layout)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_import = QPushButton("✅ 导入选中模板")
        self.btn_import.clicked.connect(self._on_import)
        self.btn_import.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 24px;")
        btn_layout.addWidget(self.btn_import)
        
        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
    
    def _load_templates(self):
        """加载模板列表"""
        templates = get_all_templates()
        for name in templates.keys():
            self.template_list.addItem(name)
        
        # 默认选中第一个
        if self.template_list.count() > 0:
            self.template_list.setCurrentRow(0)
            self._on_template_selected(self.template_list.item(0))
    
    def _on_template_selected(self, item):
        """模板选中时更新预览"""
        template_name = item.text()
        rules = get_template_by_name(template_name)
        
        if not rules:
            self.preview_text.setText("该模板暂无规则")
            return
        
        # 生成预览文本
        preview = f"📋 {template_name} 行业规则 ({len(rules)} 条)\n"
        preview += "=" * 50 + "\n\n"
        
        for i, rule in enumerate(rules[:20], 1):  # 最多显示20条
            preview += f"{i}. {rule.get('name', '未命名')}\n"
            preview += f"   关键词: {rule.get('keyword', '')}\n"
            preview += f"   等级: {rule.get('severity', '一般')}\n"
            preview += f"   建议: {rule.get('suggestion', '')[:50]}...\n\n"
        
        if len(rules) > 20:
            preview += f"... 共 {len(rules)} 条规则，预览仅显示前 20 条"
        
        self.preview_text.setText(preview)
    
    def _on_import(self):
        """导入选中的模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "未选择", "请先选择一个模板")
            return
        
        template_name = current_item.text()
        new_rules = get_template_by_name(template_name)
        
        if not new_rules:
            QMessageBox.warning(self, "模板为空", "该模板没有规则")
            return
        
        # 确认导入
        reply = QMessageBox.question(
            self,
            "确认导入",
            f"将导入 {len(new_rules)} 条规则到当前规则列表，确认继续？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 加载现有规则
        current_rules = load_rules()
        
        # 合并（去重：按 name 和 keyword 去重）
        existing_keys = {(r.get('name', ''), r.get('keyword', '')) for r in current_rules}
        added_count = 0
        
        for rule in new_rules:
            key = (rule.get('name', ''), rule.get('keyword', ''))
            if key not in existing_keys:
                current_rules.append(rule)
                existing_keys.add(key)
                added_count += 1
        
        # 保存
        if save_rules(current_rules):
            QMessageBox.information(
                self,
                "导入成功",
                f"✅ 成功导入 {added_count} 条新规则\n"
                f"（{len(new_rules) - added_count} 条规则已存在，已跳过）"
            )
            self.accept()
        else:
            QMessageBox.critical(self, "保存失败", "无法保存规则，请检查磁盘权限")