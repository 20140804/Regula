# main.py
"""
Regula - 合规鹰眼扫描器
入口文件：启动图形界面（含引导页、设置、Pro 日志记录）
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QColor, QFont, QPolygon
from PySide6.QtCore import Qt, QRect, QPoint

from ui.main_window import MainWindow
from ui.welcome_dialog import WelcomeDialog
from utils.settings_manager import load_settings, save_settings
from utils.logger import log_exception, log_info, log_error


# ============================================================
# 1. 全局样式表（根据设置动态生成）
# ============================================================
def get_style_sheet(settings: dict) -> str:
    """根据用户设置生成 QSS 样式表"""
    theme = settings.get("theme", "light")
    font_size_map = {"small": 12, "medium": 14, "large": 16}
    font_size = font_size_map.get(settings.get("font_size", "medium"), 14)

    if theme == "dark":
        return f"""
        /* ===== 暗色主题 ===== */
        QWidget {{
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-size: {font_size}px;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        }}
        QMainWindow {{ background-color: #1e1e2e; }}
        QDialog {{ background-color: #1e1e2e; }}
        
        QPushButton {{
            background-color: #313244;
            color: #cdd6f4;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: #45475a; }}
        QPushButton:pressed {{ background-color: #585b70; }}
        QPushButton:disabled {{ opacity: 0.5; }}
        
        QPushButton#btn_scan {{
            background-color: #27ae60;
            color: white;
        }}
        QPushButton#btn_scan:hover {{ background-color: #2ecc71; }}
        
        QPushButton#btn_export {{
            background-color: #0f3460;
            color: white;
        }}
        QPushButton#btn_export:hover {{ background-color: #1a4a7a; }}
        
        QPushButton#btn_rules {{
            background-color: #8e44ad;
            color: white;
        }}
        QPushButton#btn_rules:hover {{ background-color: #a569bd; }}
        
        QTableWidget {{
            background-color: #1e1e2e;
            gridline-color: #313244;
            alternate-background-color: #313244;
            border: 1px solid #313244;
            border-radius: 6px;
        }}
        QTableWidget::item {{
            padding: 6px;
            color: #cdd6f4;
        }}
        QHeaderView::section {{
            background-color: #313244;
            color: #cdd6f4;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        
        QProgressBar {{
            border: none;
            border-radius: 5px;
            background-color: #313244;
            height: 12px;
            text-align: center;
            color: #cdd6f4;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #0f3460, stop:1 #e94560);
            border-radius: 5px;
        }}
        
        QLabel#drop_area {{
            border: 3px dashed #89b4fa;
            border-radius: 10px;
            background-color: #313244;
            padding: 30px;
            font-size: 16px;
            color: #cdd6f4;
        }}
        QLabel#drop_area:hover {{
            background-color: #45475a;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #313244;
            border-radius: 8px;
            background-color: #1e1e2e;
        }}
        QTabBar::tab {{
            padding: 8px 16px;
            background-color: #313244;
            color: #cdd6f4;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: #45475a;
        }}
        QTabBar::tab:hover {{
            background-color: #585b70;
        }}
        
        QScrollBar:vertical {{
            background: #313244;
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: #585b70;
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #6c7086;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QComboBox, QLineEdit, QTextEdit {{
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 4px;
            padding: 4px 8px;
        }}
        QComboBox:hover, QLineEdit:hover, QTextEdit:hover {{
            border-color: #89b4fa;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: #313244;
            color: #cdd6f4;
            selection-background-color: #45475a;
        }}
        
        QRadioButton {{
            color: #cdd6f4;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QCheckBox {{
            color: #cdd6f4;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QMessageBox QPushButton {{
            background-color: #313244;
            color: #cdd6f4;
            padding: 6px 16px;
            border-radius: 4px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: #45475a;
        }}
        """
    else:
        return f"""
        /* ===== 浅色主题 ===== */
        QWidget {{
            font-size: {font_size}px;
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            color: #2c3e50;
        }}
        QMainWindow, QDialog {{ background-color: #f8f9fa; }}
        
        QPushButton {{
            background-color: #e0e0e0;
            color: #2c3e50;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: #d0d0d0; }}
        QPushButton:pressed {{ background-color: #c0c0c0; }}
        QPushButton:disabled {{ opacity: 0.5; }}
        
        QPushButton#btn_scan {{
            background-color: #27ae60;
            color: white;
        }}
        QPushButton#btn_scan:hover {{ background-color: #219a52; }}
        
        QPushButton#btn_export {{
            background-color: #0f3460;
            color: white;
        }}
        QPushButton#btn_export:hover {{ background-color: #1a4a7a; }}
        
        QPushButton#btn_rules {{
            background-color: #8e44ad;
            color: white;
        }}
        QPushButton#btn_rules:hover {{ background-color: #732d91; }}
        
        QTableWidget {{
            background-color: white;
            alternate-background-color: #f8f9fa;
            border: 1px solid #dcdde1;
            border-radius: 6px;
            gridline-color: #dcdde1;
        }}
        QTableWidget::item {{ padding: 6px; }}
        QHeaderView::section {{
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        
        QProgressBar {{
            border: none;
            border-radius: 5px;
            background-color: #ecf0f1;
            height: 12px;
            text-align: center;
            color: #2c3e50;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #0f3460, stop:1 #e94560);
            border-radius: 5px;
        }}
        
        QLabel#drop_area {{
            border: 3px dashed #3498db;
            border-radius: 10px;
            background-color: #ecf0f1;
            padding: 30px;
            font-size: 16px;
            color: #2c3e50;
        }}
        QLabel#drop_area:hover {{
            background-color: #d5dbdb;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #dcdde1;
            border-radius: 8px;
            background-color: white;
        }}
        QTabBar::tab {{
            padding: 8px 16px;
            background-color: #ecf0f1;
            color: #2c3e50;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: white;
        }}
        QTabBar::tab:hover {{
            background-color: #d5dbdb;
        }}
        
        QScrollBar:vertical {{
            background: #ecf0f1;
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: #bdc3c7;
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #95a5a6;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QComboBox, QLineEdit, QTextEdit {{
            background-color: white;
            color: #2c3e50;
            border: 1px solid #dcdde1;
            border-radius: 4px;
            padding: 4px 8px;
        }}
        QComboBox:hover, QLineEdit:hover, QTextEdit:hover {{
            border-color: #3498db;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: white;
            color: #2c3e50;
            selection-background-color: #3498db;
            selection-color: white;
        }}
        
        QRadioButton {{
            color: #2c3e50;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QCheckBox {{
            color: #2c3e50;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        
        QMessageBox QPushButton {{
            background-color: #e0e0e0;
            color: #2c3e50;
            padding: 6px 16px;
            border-radius: 4px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: #d0d0d0;
        }}
        """


# ============================================================
# 2. 程序图标（纯代码绘制）
# ============================================================
def create_app_icon() -> QIcon:
    """用 QPainter 绘制 128x128 程序图标"""
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 深蓝盾牌 + 红色描边
    painter.setBrush(QBrush(QColor("#1a1a2e")))
    painter.setPen(QPen(QColor("#e94560"), 4))
    painter.drawRoundedRect(10, 10, 108, 108, 24, 24)

    # 红色飞翼（V形）
    painter.setBrush(QBrush(QColor("#e94560")))
    painter.setPen(Qt.PenStyle.NoPen)
    points = [
        QPoint(64, 28),
        QPoint(20, 78),
        QPoint(45, 78),
        QPoint(64, 52),
        QPoint(83, 78),
        QPoint(108, 78)
    ]
    painter.drawPolygon(QPolygon(points))

    # 白色中心圆环
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.setPen(QPen(QColor("#1a1a2e"), 2))
    painter.drawEllipse(30, 30, 68, 68)

    # 字母 "R"
    painter.setPen(QPen(QColor("#1a1a2e"), 2))
    painter.setFont(QFont("Arial", 48, QFont.Weight.Bold))
    painter.drawText(QRect(28, 28, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")
    painter.setPen(QPen(QColor("#ffffff"), 2))
    painter.drawText(QRect(30, 30, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")

    painter.end()
    return QIcon(pixmap)


# ============================================================
# 3. 主入口
# ============================================================
def main():
    """程序入口"""
    try:
        # 创建 QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Regula")
        app.setOrganizationName("Regula")

        # 加载用户设置
        settings = load_settings()
        log_info(f"软件启动 | 语言: {settings.get('language')}, 主题: {settings.get('theme')}")

        # 应用样式表
        app.setStyleSheet(get_style_sheet(settings))

        # 设置程序图标
        icon = create_app_icon()
        app.setWindowIcon(icon)

        # ===== 判断是否显示引导页 =====
        show_welcome = settings.get("show_welcome", True)

        if show_welcome:
            welcome = WelcomeDialog()
            # 如果用户关闭了引导页（未点「开始使用」），仍然进入主界面
            welcome.exec()
            # 重新加载设置（可能被引导页修改）
            settings = load_settings()
            # 重新应用样式表（主题可能变了）
            app.setStyleSheet(get_style_sheet(settings))
            log_info("引导页已显示")

        # ===== 创建主窗口 =====
        window = MainWindow()
        window.setWindowIcon(icon)
        window.show()

        log_info("主窗口已显示，软件启动完成")

        # 运行事件循环
        sys.exit(app.exec())

    except Exception as e:
        # 捕获启动过程中的异常并记录到 debug.txt
        log_exception(e, "软件启动过程发生异常")
        # 如果异常太严重，可能无法显示 GUI，直接打印到控制台
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()