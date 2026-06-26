# export_icon.py
"""从代码导出 .ico 图标文件"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QColor, QFont, QPolygon
from PySide6.QtCore import Qt, QRect, QPoint

def create_app_icon() -> QIcon:
    """直接从 main.py 复制的绘图逻辑"""
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 1. 盾牌背景
    painter.setBrush(QBrush(QColor("#1a1a2e")))
    painter.setPen(QPen(QColor("#e94560"), 4))
    painter.drawRoundedRect(10, 10, 108, 108, 24, 24)

    # 2. 红色飞翼
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

    # 4. 字母 R
    painter.setPen(QPen(QColor("#1a1a2e"), 2))
    painter.setFont(QFont("Arial", 48, QFont.Weight.Bold))
    painter.drawText(QRect(28, 28, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")
    painter.setPen(QPen(QColor("#ffffff"), 2))
    painter.drawText(QRect(30, 30, 72, 72), Qt.AlignmentFlag.AlignCenter, "R")

    painter.end()
    return QIcon(pixmap)


if __name__ == "__main__":
    # 必须先创建 QApplication 才能使用 QPixmap
    app = QApplication(sys.argv)

    # 生成图标
    icon = create_app_icon()
    pixmap = icon.pixmap(256, 256)
    pixmap.save("Regula.ico", "ICO")
    print("✅ 已生成 Regula.ico")

    # 退出应用
    sys.exit()