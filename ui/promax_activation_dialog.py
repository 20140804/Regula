# ui/promax_activation_dialog.py
"""
Pro Max 激活弹窗
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
from utils.promax_license_manager import (
    get_machine_id,
    verify_promax_activation,
    save_promax_activation,
    is_promax_activated
)


class ProMaxActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👑 激活 Regula Pro Max")
        self.setMinimumWidth(550)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("👑 激活 Regula Pro Max")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #8e44ad;")
        layout.addWidget(title)
        
        # 说明
        info = QLabel(
            "Pro Max 是 Regula 的终极版本，包含 AI 智能语义理解、\n"
            "违规自动分类、智能修改建议等强大功能。\n\n"
            "请输入您的 Pro Max 激活码。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555;")
        layout.addWidget(info)
        
        # 机器码显示
        machine_id = get_machine_id()
        machine_label = QLabel("设备指纹（发送给开发者以获取 Pro Max 激活码）：")
        machine_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(machine_label)
        
        machine_code = QTextEdit()
        machine_code.setPlainText(machine_id)
        machine_code.setReadOnly(True)
        machine_code.setMaximumHeight(50)
        machine_code.setStyleSheet("font-size: 10px;")
        layout.addWidget(machine_code)
        
        # 激活码输入
        input_label = QLabel("Pro Max 激活码：")
        input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(input_label)
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("粘贴 Pro Max 激活码")
        layout.addWidget(self.input_code)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_activate = QPushButton("👑 激活 Pro Max")
        self.btn_activate.clicked.connect(self._on_activate)
        self.btn_activate.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 10px 28px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #732d91;
            }
        """)
        btn_layout.addWidget(self.btn_activate)
        
        self.btn_close = QPushButton("取消")
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("padding: 10px 20px;")
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        # 底部提示
        tip = QLabel("💡 购买 Pro Max 激活码请联系：Regula_Official@outlook.com")
        tip.setStyleSheet("color: #7f8c8d; font-size: 11px; margin-top: 15px;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
    
    def _on_activate(self):
        code = self.input_code.text().strip()
        if not code:
            QMessageBox.warning(self, "输入错误", "请粘贴 Pro Max 激活码")
            return
        
        if verify_promax_activation(get_machine_id(), code):
            if save_promax_activation(code):
                QMessageBox.information(self, "激活成功", "🎉 Pro Max 已成功激活！AI 智能功能已解锁。")
                self.accept()
            else:
                QMessageBox.critical(self, "保存失败", "无法保存激活码，请检查磁盘权限。")
        else:
            QMessageBox.critical(self, "激活失败", "❌ 激活码无效，请检查是否输入正确。")