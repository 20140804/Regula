# ui/heatmap_widget.py
"""
热力图组件 - 用颜色网格展示每个文件的违规密度
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from typing import Dict

class HeatmapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题行
        title_layout = QHBoxLayout()
        title_label = QLabel("🔥 团队违规热力图")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "文件名", "致命 🔴", "严重 🟠", "一般 🟡", "总计"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # 底部图例
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        colors = [
            ("🟢 安全 (0项)", "#27ae60"),
            ("🟡 一般 (1-2项)", "#f1c40f"),
            ("🟠 严重 (3-5项)", "#e67e22"),
            ("🔴 高危 (≥6项)", "#e74c3c")
        ]
        for text, color in colors:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"background-color: {color}; padding: 2px 8px; border-radius: 4px; color: white;")
            legend_layout.addWidget(lbl)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
    
    def update_data(self, stats: Dict[str, Dict]):
        """更新热力图数据"""
        self.stats = stats
        self.table.setRowCount(len(stats))
        
        # 确定最大违规数，用于颜色映射
        max_total = max((s["total"] for s in stats.values()), default=0)
        
        for row, (file_path, s) in enumerate(stats.items()):
            # 文件名（只显示文件名，不显示完整路径）
            self.table.setItem(row, 0, QTableWidgetItem(s.get("filename", file_path)))
            
            # 致命
            fatal_item = QTableWidgetItem(str(s["fatal"]))
            self._color_cell(fatal_item, s["fatal"], max_total)
            self.table.setItem(row, 1, fatal_item)
            
            # 严重
            serious_item = QTableWidgetItem(str(s["serious"]))
            self._color_cell(serious_item, s["serious"], max_total)
            self.table.setItem(row, 2, serious_item)
            
            # 一般
            normal_item = QTableWidgetItem(str(s["normal"]))
            self._color_cell(normal_item, s["normal"], max_total)
            self.table.setItem(row, 3, normal_item)
            
            # 总计
            total_item = QTableWidgetItem(str(s["total"]))
            self._color_cell(total_item, s["total"], max_total)
            self.table.setItem(row, 4, total_item)
    
    def _color_cell(self, item: QTableWidgetItem, value: int, max_val: int):
        """根据违规数量给单元格上色"""
        if value == 0:
            bg = QColor("#27ae60")   # 绿色
            fg = QColor("white")
        elif value <= 2:
            bg = QColor("#f1c40f")   # 黄色
            fg = QColor("black")
        elif value <= 5:
            bg = QColor("#e67e22")   # 橙色
            fg = QColor("white")
        else:
            bg = QColor("#e74c3c")   # 红色
            fg = QColor("white")
        
        item.setBackground(QBrush(bg))
        item.setForeground(QBrush(fg))
        item.setTextAlignment(Qt.AlignCenter)