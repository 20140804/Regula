# ui/welcome_dialog.py
"""
引导页 - 首次启动时显示
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QRadioButton, QButtonGroup,
    QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from utils.settings_manager import load_settings, save_settings, load_language_pack


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Regula - 欢迎")
        self.setMinimumSize(550, 450)
        self.setModal(True)
        
        # 加载当前设置
        self.settings = load_settings()
        self.lang_pack = load_language_pack(self.settings.get("language", "zh"))
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # ===== 标题 =====
        title = QLabel("🦅 Regula")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a2e;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(self._tr("welcome_subtitle"))
        subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # ===== 描述 =====
        desc = QLabel(self._tr("welcome_desc"))
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 13px; color: #555; line-height: 1.6;")
        layout.addWidget(desc)
        
        layout.addSpacing(15)
        
        # ===== 语言选择 =====
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self._tr("welcome_language"))
        lang_label.setMinimumWidth(80)
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setMinimumWidth(150)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # ===== 主题选择 =====
        theme_layout = QHBoxLayout()
        theme_label = QLabel(self._tr("welcome_theme"))
        theme_label.setMinimumWidth(80)
        theme_layout.addWidget(theme_label)
        
        self.theme_group = QButtonGroup()
        theme_widget = QWidget()
        theme_inner = QHBoxLayout(theme_widget)
        theme_inner.setContentsMargins(0, 0, 0, 0)
        
        self.theme_light = QRadioButton(self._tr("theme_light"))
        self.theme_dark = QRadioButton(self._tr("theme_dark"))
        self.theme_group.addButton(self.theme_light, 0)
        self.theme_group.addButton(self.theme_dark, 1)
        theme_inner.addWidget(self.theme_light)
        theme_inner.addWidget(self.theme_dark)
        theme_inner.addStretch()
        
        theme_layout.addWidget(theme_widget)
        layout.addLayout(theme_layout)
        
        # ===== 字体大小选择 =====
        font_layout = QHBoxLayout()
        font_label = QLabel(self._tr("welcome_font_size"))
        font_label.setMinimumWidth(80)
        font_layout.addWidget(font_label)
        
        self.font_combo = QComboBox()
        self.font_combo.addItem(self._tr("font_small"), "small")
        self.font_combo.addItem(self._tr("font_medium"), "medium")
        self.font_combo.addItem(self._tr("font_large"), "large")
        self.font_combo.setMinimumWidth(150)
        font_layout.addWidget(self.font_combo)
        font_layout.addStretch()
        layout.addLayout(font_layout)
        
        layout.addStretch()
        
        # ===== 按钮 =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_start = QPushButton(self._tr("btn_start"))
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 36px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_layout.addWidget(self.btn_start)
        
        layout.addLayout(btn_layout)
    
    def _tr(self, key: str) -> str:
        """获取当前语言的翻译"""
        return self.lang_pack.get(key, key)
    
    def _load_current_settings(self):
        """加载当前设置到界面"""
        # 语言
        lang = self.settings.get("language", "zh")
        index = self.lang_combo.findData(lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        # 主题
        theme = self.settings.get("theme", "light")
        if theme == "dark":
            self.theme_dark.setChecked(True)
        else:
            self.theme_light.setChecked(True)
        
        # 字体
        font_size = self.settings.get("font_size", "medium")
        index = self.font_combo.findData(font_size)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
    
    def _on_start(self):
        """点击开始按钮"""
        # 保存设置
        self.settings["language"] = self.lang_combo.currentData()
        self.settings["theme"] = "dark" if self.theme_dark.isChecked() else "light"
        self.settings["font_size"] = self.font_combo.currentData()
        save_settings(self.settings)
        self.accept()
    
    def get_settings(self):
        """获取设置（供外部使用）"""
        return self.settings