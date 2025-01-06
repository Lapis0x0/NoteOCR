import os
import logging
from typing import List, Dict
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

class FileHandler:
    @staticmethod
    def save_to_txt(text_contents: List[Dict[str, str]], output_path: str):
        """将OCR结果保存为TXT文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for content in text_contents:
                    # 写入文件名作为标题
                    f.write(f"\n{'='*50}\n")
                    f.write(f"Source: {content['filename']}\n")
                    f.write(f"{'='*50}\n\n")
                    
                    # 写入识别的文本
                    f.write(content['text'])
                    f.write('\n\n')
            
            logging.info(f"TXT文件已保存到: {output_path}")
        except Exception as e:
            logging.error(f"保存TXT文件时出错: {str(e)}")
            raise

    @staticmethod
    def create_pdf(text_contents: List[Dict[str, str]], output_path: str):
        """将OCR结果创建为PDF文件"""
        try:
            # 注册中文字体
            font_path = '/Library/Fonts/Arial Unicode.ttf'
            font_name = 'ArialUnicode'
            pdfmetrics.registerFont(TTFont(font_name, font_path))

            # 创建文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title='OCR Notes'
            )

            # 创建样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=16,
                spaceAfter=30,
                spaceBefore=20
            )
            text_style = ParagraphStyle(
                'CustomText',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=12,
                leading=16,
                spaceAfter=12,
                firstLineIndent=24  # 首行缩进
            )

            # 构建内容
            story = []
            for i, content in enumerate(text_contents):
                # 添加标题
                title = Paragraph(f"Source: {content['filename']}", title_style)
                story.append(title)
                
                # 添加分隔线（使用空格）
                story.append(Spacer(1, 0.1 * inch))
                
                # 添加文本内容
                paragraphs = content['text'].split('\n')
                for para in paragraphs:
                    if para.strip():  # 只添加非空段落
                        p = Paragraph(para, text_style)
                        story.append(p)
                
                # 在每个文档之间添加分页符（除了最后一个文档）
                if i < len(text_contents) - 1:
                    story.append(PageBreak())

            # 生成PDF
            doc.build(story)
            logging.info(f"PDF已保存到: {output_path}")
        except Exception as e:
            logging.error(f"创建PDF时出错: {str(e)}")
            raise
