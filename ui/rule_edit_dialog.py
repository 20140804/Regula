# ui/rule_edit_dialog.py
"""
自定义规则编辑弹窗 - 用户添加/修改/删除规则的核心界面
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from utils.rule_storage import load_rules, save_rules

class RuleEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ 自定义规则管理")
        self.setMinimumSize(800, 600)
        
        # 加载现有规则
        self.rules = load_rules()
        self._setup_ui()
        self._refresh_table()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # ===== 顶部说明 =====
        info_label = QLabel(
            "自定义规则可以让 Regula 检测你公司特有的禁用词或句式。\n"
            "例如：禁止出现'招商加盟'、禁止'日赚'等词汇。"
        )
        info_label.setStyleSheet("color: #555; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # ===== 表格区域 =====
        table_label = QLabel("📋 当前规则列表")
        table_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "规则名称", "关键词", "相邻词", "距离", "等级", "操作"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # ===== 底部按钮 =====
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ 添加规则")
        self.btn_add.clicked.connect(self._on_add_rule)
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px;")
        btn_layout.addWidget(self.btn_add)
        
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("💾 保存并关闭")
        self.btn_save.clicked.connect(self._on_save_and_close)
        self.btn_save.setStyleSheet("background-color: #3498db; color: white; padding: 8px 24px;")
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def _refresh_table(self):
        """刷新表格显示所有规则"""
        self.table.setRowCount(len(self.rules))
        
        for row, rule in enumerate(self.rules):
            # 规则名称
            self.table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
            # 关键词
            self.table.setItem(row, 1, QTableWidgetItem(rule.get('keyword', '')))
            # 相邻词
            self.table.setItem(row, 2, QTableWidgetItem(rule.get('near_keyword', '（无）')))
            # 距离
            self.table.setItem(row, 3, QTableWidgetItem(str(rule.get('max_distance', 10))))
            # 等级
            self.table.setItem(row, 4, QTableWidgetItem(rule.get('severity', '一般')))
            
            # 操作列：删除按钮
            btn_delete = QPushButton("🗑️ 删除")
            btn_delete.clicked.connect(lambda checked, r=row: self._on_delete_rule(r))
            self.table.setCellWidget(row, 5, btn_delete)
    
    def _on_add_rule(self):
        """打开新增规则对话框"""
        dialog = RuleFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_rule = dialog.get_rule_data()
            if new_rule:
                self.rules.append(new_rule)
                self._refresh_table()
    
    def _on_delete_rule(self, row: int):
        """删除指定行规则"""
        rule_name = self.rules[row].get('name', '未命名规则')
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除规则「{rule_name}」吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.rules[row]
            self._refresh_table()
    
    def _on_save_and_close(self):
        """保存规则并关闭"""
        if save_rules(self.rules):
            self.accept()
        else:
            QMessageBox.critical(self, "保存失败", "无法保存规则文件，请检查磁盘权限。")

class RuleFormDialog(QDialog):
    """新增/编辑规则的表单对话框"""
    def __init__(self, parent=None, existing_rule=None):
        super().__init__(parent)
        self.existing_rule = existing_rule
        self.setWindowTitle("📝 编辑规则" if existing_rule else "➕ 添加新规则")
        self.setMinimumWidth(500)
        self._setup_ui()
        
        if existing_rule:
            self._load_rule_data(existing_rule)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # 规则名称
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("例如：禁止招商加盟")
        form.addRow("规则名称：", self.input_name)
        
        # 关键词
        self.input_keyword = QLineEdit()
        self.input_keyword.setPlaceholderText("例如：加盟")
        form.addRow("触发关键词：", self.input_keyword)
        
        # 相邻关键词（可选）
        self.input_near = QLineEdit()
        self.input_near.setPlaceholderText("（可选）必须同时出现的词")
        form.addRow("相邻词（可选）：", self.input_near)
        
        # 最大距离
        self.input_distance = QSpinBox()
        self.input_distance.setRange(1, 50)
        self.input_distance.setValue(10)
        form.addRow("关键词与相邻词最大距离：", self.input_distance)
        
        # 严重等级
        self.input_severity = QComboBox()
        self.input_severity.addItems(["致命", "严重", "一般"])
        form.addRow("违规严重等级：", self.input_severity)
        
        # 位置限定
        self.input_position = QComboBox()
        self.input_position.addItems(["任意", "标题", "正文"])
        form.addRow("位置限定：", self.input_position)
        
        # 修改建议
        self.input_suggestion = QTextEdit()
        self.input_suggestion.setPlaceholderText("给用户的修改建议")
        self.input_suggestion.setMaximumHeight(60)
        form.addRow("修改建议：", self.input_suggestion)
        
        layout.addLayout(form)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton("✅ 确定")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setStyleSheet("background-color: #27ae60; color: white; padding: 6px 20px;")
        btn_layout.addWidget(self.btn_ok)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def _load_rule_data(self, rule: dict):
        """编辑时回填数据"""
        self.input_name.setText(rule.get('name', ''))
        self.input_keyword.setText(rule.get('keyword', ''))
        self.input_near.setText(rule.get('near_keyword', ''))
        self.input_distance.setValue(rule.get('max_distance', 10))
        self.input_severity.setCurrentText(rule.get('severity', '一般'))
        self.input_position.setCurrentText(rule.get('position', '任意'))
        self.input_suggestion.setText(rule.get('suggestion', ''))
    
    def get_rule_data(self) -> dict:
        """获取表单数据"""
        name = self.input_name.text().strip()
        keyword = self.input_keyword.text().strip()
        near_keyword = self.input_near.text().strip()
        max_distance = self.input_distance.value()
        severity = self.input_severity.currentText()
        position = self.input_position.currentText()
        suggestion = self.input_suggestion.toPlainText().strip()
        
        if not name or not keyword:
            QMessageBox.warning(self, "信息不全", "请至少填写「规则名称」和「触发关键词」。")
            return None
        
        return {
            "name": name,
            "keyword": keyword,
            "near_keyword": near_keyword if near_keyword else "",
            "max_distance": max_distance,
            "severity": severity,
            "position": position,
            "suggestion": suggestion or f"请避免使用'{keyword}'相关表述"
        }