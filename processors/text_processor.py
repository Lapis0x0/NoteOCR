import logging
from typing import Optional
from openai import OpenAI
import config

class TextProcessor:
    def __init__(self, api_key: str = None, base_url: str = None):
        """初始化文本处理器
        
        Args:
            api_key: API密钥，如果不指定则从配置文件读取
            base_url: API基础URL，如果不指定则从配置文件读取
        """
        self.client = OpenAI(
            api_key=api_key or config.TEXT_API['KEY'],
            base_url=base_url or config.TEXT_API['BASE_URL']
        )

    def format_and_enhance(self, text: str) -> str:
        """格式化和增强OCR的文本内容"""
        try:
            # 准备提示词
            messages = [
                {"role": "system", "content": "你是一个专业的笔记整理助手。你需要帮助整理和优化OCR识别出的课堂笔记内容，使其更加清晰、结构化，并保持原有的重点标记。请注意，你应该只输出整理后的笔记内容，不要包含任何其他信息。"},
                {"role": "user", "content": f"""请帮我整理以下课堂笔记内容，要求：
1. 保持原有的结构和格式
2. 保留所有重点标记（如：红色字体的部分）
3. 修正明显的OCR错误
4. 优化段落和缩进
5. 确保数学公式和符号的正确性

笔记内容：
{text}"""}
            ]

            # 调用API
            completion = self.client.chat.completions.create(
                model=config.TEXT_API['MODEL'],
                messages=messages,
                temperature=config.TEXT_API['TEMPERATURE'],
                max_tokens=config.TEXT_API['MAX_TOKENS']
            )

            return completion.choices[0].message.content

        except Exception as e:
            logging.error(f"文本处理失败: {str(e)}")
            return text  # 如果处理失败，返回原文本
