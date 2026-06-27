# exporters/pdf_exporter.py
"""
PDF 风险告知书生成器
根据 Pro 状态自动选择基础版或高级版（含图表）
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
    Spacer
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

from config import PRO_ACTIVATED


# ===== 字体注册（全局共享） =====
def register_chinese_font():
    """注册中文字体，返回字体名称"""
    font_candidates = [
        ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
        ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttf"),
        ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
        ("Heiti SC", "/System/Library/Fonts/STHeiti Light.ttc"),
        ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
        ("WenQuanYi Micro Hei", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    ]

    for font_name, font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except:
                continue

    try:
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        return 'STSong-Light'
    except:
        pass

    return 'Helvetica'


CHINESE_FONT = register_chinese_font()


# ===== 基础版 PDF（免费版） =====
def export_basic_pdf(violations: List[Violation], source_file: str, output_path: str):
    """基础版 PDF 报告（免费版）"""
    is_clean = len(violations) == 0

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
        styles[style_name].fontName = CHINESE_FONT

    title_style = ParagraphStyle(
        'TitleCN',
        parent=styles['Title'],
        fontName=CHINESE_FONT,
        fontSize=22,
        alignment=1
    )
    warning_style = ParagraphStyle(
        'WarningCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        textColor=colors.red,
        fontSize=14,
        alignment=1,
        leading=20
    )
    meta_style = ParagraphStyle(
        'MetaCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=10,
        textColor=colors.grey
    )
    normal_style = styles['Normal']
    normal_style.fontName = CHINESE_FONT

    elements = []

    # 标题
    elements.append(Paragraph("🦅 合规鹰眼 · 风险告知书", title_style))
    elements.append(Spacer(1, 5*mm))

    # 元信息
    elements.append(Paragraph(f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    elements.append(Paragraph(f"源文件：{os.path.basename(source_file)}", meta_style))
    elements.append(Spacer(1, 10*mm))

    # 结论
    if is_clean:
        elements.append(Paragraph("✅ 扫描结论：未发现违规表述，内容合规。", title_style))
        elements.append(Spacer(1, 10*mm))
    else:
        fatal_count = sum(1 for v in violations if v.severity == "致命")
        serious_count = sum(1 for v in violations if v.severity == "严重")
        normal_count = sum(1 for v in violations if v.severity == "一般")

        if fatal_count > 0 or serious_count > 0:
            elements.append(Paragraph(
                f"🚨 扫描结论：发现 <font color='red'>{fatal_count + serious_count}</font> 项高风险违规（致命/严重），建议立即修改！",
                warning_style
            ))
        else:
            elements.append(Paragraph(
                f"⚠️ 扫描结论：发现 {normal_count} 项一般性建议，建议酌情优化。",
                title_style
            ))

        elements.append(Paragraph(
            f"（其中 致命: {fatal_count} 项，严重: {serious_count} 项，一般: {normal_count} 项）",
            normal_style
        ))
        elements.append(Spacer(1, 10*mm))

    # 违规详情表格
    if not is_clean:
        table_data = [['严重等级', '行号', '关键词', '位置', '修改建议']]
        for v in violations[:100]:  # 限制最多100条
            if v.severity == "致命":
                sev_display = f'<font color="red"><b>致命</b></font>'
            elif v.severity == "严重":
                sev_display = f'<font color="orange"><b>严重</b></font>'
            else:
                sev_display = f'<font color="goldenrod">一般</font>'

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
            ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10*mm))

        if len(violations) > 100:
            elements.append(Paragraph(f"（仅显示前 100 条，共 {len(violations)} 条）", meta_style))

    # 免责声明
    footer_style = ParagraphStyle(
        'FooterCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph("本报告由 Regula 合规鹰眼 自动生成，仅供内部参考。", footer_style))
    elements.append(Paragraph("最终审核以法务部门意见为准。", footer_style))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("—— 本报告为合规管理辅助工具，不构成法律意见 ——", footer_style))

    doc.build(elements)


# ===== 高级版 PDF（Pro 版，含图表） =====
def export_pro_pdf(violations: List[Violation], source_file: str, output_path: str):
    """Pro 版高级 PDF 报告（含图表）"""
    is_clean = len(violations) == 0

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
        styles[style_name].fontName = CHINESE_FONT

    title_style = ParagraphStyle(
        'TitleCN',
        parent=styles['Title'],
        fontName=CHINESE_FONT,
        fontSize=22,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'HeadingCN',
        parent=styles['Heading2'],
        fontName=CHINESE_FONT,
        fontSize=14,
        alignment=0
    )
    normal_style = styles['Normal']
    normal_style.fontName = CHINESE_FONT
    meta_style = ParagraphStyle(
        'MetaCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=10,
        textColor=colors.grey
    )

    elements = []

    # 标题
    elements.append(Paragraph("🦅 合规鹰眼 · Pro 版分析报告", title_style))
    elements.append(Spacer(1, 5*mm))

    # 元信息
    elements.append(Paragraph(f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    elements.append(Paragraph(f"源文件：{os.path.basename(source_file)}", meta_style))
    elements.append(Paragraph("📌 Pro 版 · 高级分析报告（含图表）", meta_style))
    elements.append(Spacer(1, 10*mm))

    # 统计
    fatal = sum(1 for v in violations if v.severity == "致命")
    serious = sum(1 for v in violations if v.severity == "严重")
    normal = sum(1 for v in violations if v.severity == "一般")
    total = len(violations)

    if is_clean:
        elements.append(Paragraph("✅ 扫描结论：未发现违规表述，内容完全合规。", title_style))
        elements.append(Spacer(1, 10*mm))
    else:
        elements.append(Paragraph(f"📊 违规摘要：共 {total} 项违规", heading_style))
        elements.append(Paragraph(f"  🔴 致命：{fatal} 项", normal_style))
        elements.append(Paragraph(f"  🟠 严重：{serious} 项", normal_style))
        elements.append(Paragraph(f"  🟡 一般：{normal} 项", normal_style))
        elements.append(Spacer(1, 8*mm))

        # ===== 饼图：违规分布 =====
        elements.append(Paragraph("📈 违规严重等级分布", heading_style))
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
        pie.slices[0].strokeColor = colors.white
        pie.slices[1].strokeColor = colors.white
        pie.slices[2].strokeColor = colors.white
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 10*mm))

        # ===== 违规详情表格 =====
        elements.append(Paragraph("📋 违规详情列表", heading_style))
        table_data = [['严重等级', '行号', '关键词', '位置', '修改建议']]
        for v in violations[:100]:
            if v.severity == "致命":
                sev_display = f'<font color="red"><b>致命</b></font>'
            elif v.severity == "严重":
                sev_display = f'<font color="orange"><b>严重</b></font>'
            else:
                sev_display = f'<font color="goldenrod">一般</font>'
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
            ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(table)

        if len(violations) > 100:
            elements.append(Paragraph(f"（仅显示前 100 条，共 {len(violations)} 条）", meta_style))

    # 免责声明
    footer_style = ParagraphStyle(
        'FooterCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("本报告由 Regula 合规鹰眼 Pro 版自动生成，仅供内部参考。", footer_style))
    elements.append(Paragraph("—— 本报告为合规管理辅助工具，不构成法律意见 ——", footer_style))

    doc.build(elements)


# ===== 统一入口 =====
def export_to_pdf(violations: List[Violation], source_file: str, output_path: str):
    """
    导出 PDF 报告
    根据 Pro 状态自动选择版本
    """
    if PRO_ACTIVATED:
        export_pro_pdf(violations, source_file, output_path)
    else:
        export_basic_pdf(violations, source_file, output_path)