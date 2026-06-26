# exporters/pdf_exporter.py
"""
PDF 风险告知书生成器 - 把违规扫描结果导出为正式报告
支持中文字体（自动检测系统字体）
"""
import os
import sys
from datetime import datetime
from typing import List
from models.violation import Violation

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ===== 自动检测并注册中文字体 =====
def register_chinese_font():
    """
    注册中文字体，按优先级尝试不同字体
    返回注册后的字体名称，如果都不支持则返回 'Helvetica'
    """
    # 系统字体路径（按优先级）
    font_candidates = [
        # Windows
        ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
        ("Microsoft YaHei", "C:/Windows/Fonts/msyh.ttf"),
        ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
        # Mac
        ("Heiti SC", "/System/Library/Fonts/STHeiti Light.ttc"),
        ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
        # Linux
        ("WenQuanYi Micro Hei", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        ("Noto Sans CJK SC", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ]

    for font_name, font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"[PDF] 已注册中文字体: {font_name} ({font_path})")
                return font_name
            except Exception as e:
                print(f"[PDF] 注册字体 {font_name} 失败: {e}")
                continue

    # 如果所有本地字体都失败，尝试使用内置的 CID 字体（适用于中文）
    try:
        # reportlab 内置了 Adobe 的 CID 字体，支持中文
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        print("[PDF] 使用内置 CID 字体 STSong-Light")
        return 'STSong-Light'
    except:
        pass

    # 最后回退到默认字体（会乱码，但至少不报错）
    print("[PDF] 警告：未找到中文字体，PDF 中文可能显示异常")
    return 'Helvetica'

CHINESE_FONT = register_chinese_font()


def export_to_pdf(violations: List[Violation], source_file: str, output_path: str):
    """
    导出合规扫描报告为 PDF
    :param violations: 违规列表
    :param source_file: 被扫描的原始文档路径
    :param output_path: PDF 保存路径
    """
    is_clean = len(violations) == 0

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # 自定义样式，全部使用中文字体
    styles = getSampleStyleSheet()
    
    # 修改所有现有样式为中文
    for style_name in styles.byName.keys():
        styles[style_name].fontName = CHINESE_FONT

    # 新建一个标题样式（大号）
    title_style = ParagraphStyle(
        'TitleCN',
        parent=styles['Title'],
        fontName=CHINESE_FONT,
        fontSize=22,
        alignment=1  # 居中
    )
    # 新建红色警告样式
    warning_style = ParagraphStyle(
        'WarningCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        textColor=colors.red,
        fontSize=14,
        alignment=1,
        leading=20
    )
    # 新建灰色小字样式
    meta_style = ParagraphStyle(
        'MetaCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=10,
        textColor=colors.grey
    )
    # 新建表头样式（居中加粗）
    header_style = ParagraphStyle(
        'HeaderCN',
        parent=styles['Normal'],
        fontName=CHINESE_FONT,
        fontSize=10,
        alignment=1,
        textColor=colors.whitesmoke,
        backColor=colors.HexColor('#2c3e50')
    )
    # 普通正文样式（使用中文）
    normal_style = styles['Normal']
    normal_style.fontName = CHINESE_FONT

    elements = []

    # ===== 1. 标题 =====
    elements.append(Paragraph("🦅 合规鹰眼 · 风险告知书", title_style))
    elements.append(Spacer(1, 5*mm))

    # ===== 2. 报告元信息 =====
    elements.append(Paragraph(f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    elements.append(Paragraph(f"源文件：{os.path.basename(source_file)}", meta_style))
    elements.append(Spacer(1, 10*mm))

    # ===== 3. 总体结论 =====
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

    # ===== 4. 违规详情表格 =====
    if not is_clean:
        table_data = [
            ['严重等级', '行号', '关键词', '位置', '修改建议']
        ]
        
        for v in violations:
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

    # ===== 5. 免责声明 =====
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

    # ===== 6. 构建 PDF =====
    doc.build(elements)