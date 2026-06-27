# exporters/pdf_pro_enhancer.py
"""
高级 PDF 报告生成器 - Pro 版专属
包含：违规图表、趋势分析、部门排行
"""
import os
from datetime import datetime
from typing import List
from models.violation import Violation

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

from exporters.pdf_exporter import CHINESE_FONT, register_chinese_font


def export_pro_pdf(violations: List[Violation], source_file: str, output_path: str):
    """
    导出高级 PDF 报告（含图表）
    """
    # 注册中文字体
    chinese_font = register_chinese_font()
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    for style_name in styles.byName.keys():
        styles[style_name].fontName = chinese_font
    
    title_style = ParagraphStyle(
        'TitleCN',
        parent=styles['Title'],
        fontName=chinese_font,
        fontSize=22,
        alignment=1
    )
    normal_style = styles['Normal']
    normal_style.fontName = chinese_font
    
    elements = []
    
    # ===== 标题 =====
    elements.append(Paragraph("🦅 合规鹰眼 · Pro 版分析报告", title_style))
    elements.append(Spacer(1, 5*mm))
    
    # ===== 元信息 =====
    meta_style = ParagraphStyle(
        'MetaCN',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=10,
        textColor=colors.grey
    )
    elements.append(Paragraph(f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    elements.append(Paragraph(f"源文件：{os.path.basename(source_file)}", meta_style))
    elements.append(Paragraph(f"Pro 版 · 高级分析报告", meta_style))
    elements.append(Spacer(1, 10*mm))
    
    # ===== 统计摘要 =====
    fatal = sum(1 for v in violations if v.severity == "致命")
    serious = sum(1 for v in violations if v.severity == "严重")
    normal = sum(1 for v in violations if v.severity == "一般")
    total = len(violations)
    
    elements.append(Paragraph(f"📊 违规摘要：共 {total} 项", normal_style))
    elements.append(Paragraph(f"  🔴 致命：{fatal} 项", normal_style))
    elements.append(Paragraph(f"  🟠 严重：{serious} 项", normal_style))
    elements.append(Paragraph(f"  🟡 一般：{normal} 项", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # ===== 图表1：违规分布饼图 =====
    if total > 0:
        elements.append(Paragraph("📈 违规严重等级分布", normal_style))
        
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 150
        pie.height = 150
        pie.data = [fatal, serious, normal]
        pie.labels = [f"致命 {fatal}", f"严重 {serious}", f"一般 {normal}"]
        pie.slices[0].fillColor = colors.red
        pie.slices[1].fillColor = colors.orange
        pie.slices[2].fillColor = colors.gold
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 10*mm))
    
    # ===== 违规详情表格 =====
    if not violations:
        elements.append(Paragraph("✅ 未发现违规表述", normal_style))
    else:
        table_data = [['严重等级', '行号', '关键词', '位置', '修改建议']]
        for v in violations[:50]:  # 最多显示50条
            sev_display = f'<font color="red"><b>致命</b></font>' if v.severity == "致命" else \
                         f'<font color="orange"><b>严重</b></font>' if v.severity == "严重" else \
                         f'<font color="goldenrod">一般</font>'
            table_data.append([
                Paragraph(sev_display, normal_style),
                str(v.line_num),
                v.keyword,
                v.position,
                v.suggestion
            ])
        
        table = Table(table_data, colWidths=[30*mm, 15*mm, 30*mm, 25*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 5*mm))
        
        if len(violations) > 50:
            elements.append(Paragraph(f"（仅显示前 50 条，共 {len(violations)} 条）", meta_style))
    
    # ===== 免责声明 =====
    footer_style = ParagraphStyle(
        'FooterCN',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("本报告由 Regula 合规鹰眼 Pro 版自动生成，仅供内部参考。", footer_style))
    elements.append(Paragraph("—— 本报告为合规管理辅助工具，不构成法律意见 ——", footer_style))
    
    doc.build(elements)