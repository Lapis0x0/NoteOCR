import os
import logging
import re
from typing import List, Dict
from pathlib import Path
import markdown

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
    def save_to_markdown(text_contents: List[Dict[str, str]], output_path: str):
        """将OCR结果保存为Markdown文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for content in text_contents:
                    # 写入文件名作为标题
                    f.write(f"# {content['filename']}\n\n")
                    
                    # 处理文本内容
                    text = content['text']
                    lines = []
                    current_list = []
                    in_list = False
                    
                    for line in text.split('\n'):
                        line = line.strip()
                        if not line:
                            if in_list:
                                # 结束当前列表
                                lines.extend(current_list)
                                lines.append('')
                                current_list = []
                                in_list = False
                            lines.append('')
                            continue
                            
                        # 处理标题行（###开头的）
                        if line.startswith('###'):
                            if in_list:
                                lines.extend(current_list)
                                current_list = []
                                in_list = False
                            lines.append(f"\n## {line.lstrip('#').strip()}\n")
                            continue
                            
                        # 处理列表项（数字开头或-开头的）
                        if re.match(r'^\d+\.', line) or line.startswith('-'):
                            if not in_list:
                                if current_list:
                                    lines.extend(current_list)
                                current_list = []
                                in_list = True
                            # 确保列表项有正确的格式
                            if line.startswith('-'):
                                current_list.append(line)
                            else:
                                # 将数字列表规范化
                                text = re.sub(r'^\d+\.', '', line).strip()
                                current_list.append(f"1. {text}")
                            continue
                            
                        # 普通文本行
                        if in_list:
                            lines.extend(current_list)
                            current_list = []
                            in_list = False
                        lines.append(line)
                    
                    # 处理最后可能剩余的列表项
                    if current_list:
                        lines.extend(current_list)
                    
                    # 写入处理后的内容
                    f.write('\n'.join(lines))
                    f.write('\n\n---\n\n')  # 添加分隔线
            
            logging.info(f"Markdown文件已保存到: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"保存Markdown文件时出错: {str(e)}")
            raise

    @staticmethod
    def process_to_markdown(text_contents: List[Dict[str, str]], output_base_path: str):
        """处理OCR结果，保存为Markdown"""
        try:
            # 生成输出路径
            markdown_path = output_base_path + '.md'
            
            # 保存为Markdown
            FileHandler.save_to_markdown(text_contents, markdown_path)
            
            return markdown_path
        except Exception as e:
            logging.error(f"处理文件时出错: {str(e)}")
            raise
