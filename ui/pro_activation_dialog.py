# ui/pro_activation_dialog.py
"""
Pro 激活弹窗
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
from utils.license_manager import save_activation, is_pro_activated, get_machine_id


class ProActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔑 激活 Regula Pro")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("🔑 激活 Regula Pro 版")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # 说明
        info = QLabel(
            "输入您购买的激活码即可解锁 Pro 全部功能。\n"
            "激活码绑定当前设备，一机一码。"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # 机器码显示
        machine_id = get_machine_id()
        machine_label = QLabel(f"设备指纹（复制给客服购买激活码）：")
        machine_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(machine_label)
        
        machine_code = QTextEdit()
        machine_code.setPlainText(machine_id)
        machine_code.setReadOnly(True)
        machine_code.setMaximumHeight(60)
        machine_code.setStyleSheet("font-size: 10px;")
        layout.addWidget(machine_code)
        
        # 激活码输入
        input_label = QLabel("激活码：")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(input_label)
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("请输入激活码")
        layout.addWidget(self.input_code)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_activate = QPushButton("✅ 激活")
        self.btn_activate.clicked.connect(self._on_activate)
        self.btn_activate.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 24px;")
        btn_layout.addWidget(self.btn_activate)
        
        self.btn_close = QPushButton("取消")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        # 提示
        tip = QLabel("💡 购买激活码请联系作者")
        tip.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 10px;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
    
    def _on_activate(self):
        code = self.input_code.text().strip()
        if not code:
            QMessageBox.warning(self, "输入错误", "请粘贴激活码")
            return
        
        # 验证激活码（此时会调用 license_manager 验证）
        from utils.license_manager import verify_activation, get_machine_id
        if verify_activation(get_machine_id(), code):
            # 保存激活码
            if save_activation(code):
                QMessageBox.information(self, "激活成功", "🎉 Regula Pro 已成功激活！")
                self.accept()
            else:
                QMessageBox.critical(self, "保存失败", "无法保存激活码，请检查磁盘权限。")
        else:
            QMessageBox.critical(self, "激活失败", "❌ 激活码无效，请检查是否输入正确。")