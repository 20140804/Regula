# main.py
"""
Regula - 合规鹰眼扫描器
入口文件：启动图形界面（含纯代码绘制的程序图标）
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import (
    QIcon, QPixmap, QPainter, QBrush, QPen, 
    QColor, QFont, QPolygon
)
from PySide6.QtCore import Qt, QRect, QPoint  # ← 关键修正：QPoint 从 QtCore 导入
from ui.main_window import MainWindow
from config import THEME


# ===== 全局样式表（QSS） =====
def get_style_sheet():
    return f"""
    QWidget {{
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 13px;
        color: {THEME['text_dark']};
    }}
    QMainWindow, QDialog {{
        background-color: {THEME['bg_light']};
    }}
    QPushButton {{
        border: none;
        border-radius: {THEME['border_radius']};
        padding: 10px 18px;
        font-weight: bold;
        background-color: #e0e0e0;
        color: {THEME['text_dark']};
    }}
    QPushButton:hover {{ background-color: #d0d0d0; }}
    QPushButton:pressed {{ background-color: #c0c0c0; }}
    QPushButton:disabled {{ opacity: 0.5; }}
    
    QPushButton#btn_scan {{
        background-color: {THEME['success']};
        color: white;
    }}
    QPushButton#btn_scan:hover {{ background-color: #219a52; }}
    
    QPushButton#btn_export {{
        background-color: {THEME['accent']};
        color: white;
    }}
    QPushButton#btn_export:hover {{ background-color: #0a2647; }}
    
    QPushButton#btn_rules {{
        background-color: #8e44ad;
        color: white;
    }}
    QPushButton#btn_rules:hover {{ background-color: #732d91; }}
    
    QTableWidget {{
        background-color: white;
        alternate-background-color: {THEME['bg_light']};
        border: 1px solid #dcdde1;
        border-radius: {THEME['border_radius']};
        gridline-color: #dcdde1;
    }}
    QTableWidget::item {{ padding: 6px; }}
    QHeaderView::section {{
        background-color: {THEME['secondary']};
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
        color: {THEME['text_dark']};
    }}
    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {THEME['accent']}, stop:1 {THEME['highlight']});
        border-radius: 5px;
    }}
    QLabel#drop_area {{
        border: 3px dashed {THEME['accent']};
        border-radius: {THEME['border_radius']};
        background-color: #ecf0f1;
        padding: 30px;
        font-size: 16px;
        color: {THEME['text_dark']};
    }}
    QLabel#drop_area:hover {{ background-color: #d5dbdb; }}
    
    QScrollBar:vertical {{
        background: #f0f0f0;
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: #c0c0c0;
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: #a0a0a0; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    """


# ===== 🎨 纯代码绘制程序图标 =====
def create_app_icon() -> QIcon:
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 1. 盾牌背景（深蓝圆角矩形 + 红色描边）
    painter.setBrush(QBrush(QColor("#1a1a2e")))
    painter.setPen(QPen(QColor("#e94560"), 4))
    painter.drawRoundedRect(10, 10, 108, 108, 24, 24)

    # 2. 红色飞翼（V 形）
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

    # 3. 中心白色圆环
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.setPen(QPen(QColor("#1a1a2e"), 2))
    painter.drawEllipse(30, 30, 68, 68)

    # 4. 字母 "R"（深色描边 + 白色填充）
    painter.setPen(QPen(QColor("#1a1a2e"), 2))
    painter.setFont(QFont("Arial", 48, QFont.Weight.Bold))
    painter.drawText(QRect(28, 28, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")
    painter.setPen(QPen(QColor("#ffffff"), 2))
    painter.drawText(QRect(30, 30, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")

    painter.end()
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Regula")
    app.setOrganizationName("Regula")
    app.setStyleSheet(get_style_sheet())

    # 设置全局图标
    icon = create_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)  # 确保窗口也使用相同图标
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()