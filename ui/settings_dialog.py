# ui/settings_dialog.py
"""
设置页面 - 全局偏好设置
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QRadioButton, QButtonGroup,
    QCheckBox, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from utils.settings_manager import load_settings, save_settings, load_language_pack


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.settings = load_settings()
        self.lang_pack = load_language_pack(self.settings.get("language", "zh"))
        
        self._setup_ui()
        self._load_current_settings()
    
    def _tr(self, key: str) -> str:
        return self.lang_pack.get(key, key)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # ===== 标题 =====
        title = QLabel("⚙️ " + self._tr("settings_title"))
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        # ===== 语言 =====
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self._tr("settings_language"))
        lang_label.setMinimumWidth(120)
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setMinimumWidth(150)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # 重启提示
        self.restart_hint = QLabel(self._tr("settings_restart_hint"))
        self.restart_hint.setStyleSheet("color: #e67e22; font-size: 11px; margin-left: 120px;")
        self.restart_hint.setWordWrap(True)
        layout.addWidget(self.restart_hint)
        
        layout.addSpacing(10)
        
        # ===== 主题 =====
        theme_layout = QHBoxLayout()
        theme_label = QLabel(self._tr("settings_theme"))
        theme_label.setMinimumWidth(120)
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
        
        layout.addSpacing(10)
        
        # ===== 字体大小 =====
        font_layout = QHBoxLayout()
        font_label = QLabel(self._tr("settings_font_size"))
        font_label.setMinimumWidth(120)
        font_layout.addWidget(font_label)
        
        self.font_combo = QComboBox()
        self.font_combo.addItem(self._tr("font_small"), "small")
        self.font_combo.addItem(self._tr("font_medium"), "medium")
        self.font_combo.addItem(self._tr("font_large"), "large")
        self.font_combo.setMinimumWidth(150)
        font_layout.addWidget(self.font_combo)
        font_layout.addStretch()
        layout.addLayout(font_layout)
        
        layout.addSpacing(15)
        
        # ===== 启动引导页 =====
        welcome_layout = QHBoxLayout()
        self.welcome_check = QCheckBox(self._tr("settings_show_welcome"))
        self.welcome_check.setChecked(True)
        welcome_layout.addWidget(self.welcome_check)
        welcome_layout.addStretch()
        layout.addLayout(welcome_layout)
        
        layout.addStretch()
        
        # ===== 底部按钮 =====
        btn_layout = QHBoxLayout()
        
        self.btn_restore = QPushButton(self._tr("settings_restore_default"))
        self.btn_restore.clicked.connect(self._on_restore_default)
        self.btn_restore.setStyleSheet("padding: 8px 16px;")
        btn_layout.addWidget(self.btn_restore)
        
        btn_layout.addStretch()
        
        self.btn_save = QPushButton(self._tr("settings_save"))
        self.btn_save.clicked.connect(self._on_save)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 24px; border-radius: 6px;")
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton(self._tr("settings_close"))
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("padding: 8px 16px;")
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def _load_current_settings(self):
        """加载当前设置到界面"""
        lang = self.settings.get("language", "zh")
        index = self.lang_combo.findData(lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        theme = self.settings.get("theme", "light")
        if theme == "dark":
            self.theme_dark.setChecked(True)
        else:
            self.theme_light.setChecked(True)
        
        font_size = self.settings.get("font_size", "medium")
        index = self.font_combo.findData(font_size)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        
        self.welcome_check.setChecked(self.settings.get("show_welcome", True))
    
    def _on_restore_default(self):
        """恢复默认设置"""
        from utils.settings_manager import DEFAULT_SETTINGS
        reply = QMessageBox.question(
            self,
            "确认恢复",
            "确定要恢复所有设置为默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings = DEFAULT_SETTINGS.copy()
            self._load_current_settings()
            QMessageBox.information(self, "已恢复", "设置已恢复为默认值。")
    
    def _on_save(self):
        """保存设置"""
        old_lang = self.settings.get("language", "zh")
        new_lang = self.lang_combo.currentData()
        
        self.settings["language"] = new_lang
        self.settings["theme"] = "dark" if self.theme_dark.isChecked() else "light"
        self.settings["font_size"] = self.font_combo.currentData()
        self.settings["show_welcome"] = self.welcome_check.isChecked()
        
        save_settings(self.settings)
        
        # 如果语言改变了，提示重启
        if old_lang != new_lang:
            QMessageBox.information(
                self,
                "语言已更改",
                "语言设置已更改，重启软件后完全生效。\n建议关闭并重新打开 Regula。"
            )
        else:
            QMessageBox.information(self, "已保存", "设置已保存。")
        
        self.accept()