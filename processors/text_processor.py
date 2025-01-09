import logging
from typing import Optional
from openai import OpenAI

class TextProcessor:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "deepseek-chat", temperature: float = 0.3, max_tokens: int = 2000):
        """初始化文本处理器
        
        Args:
            api_key: API密钥，如果不指定则从配置文件读取
            base_url: API基础URL，如果不指定则从配置文件读取
            model: 使用的模型名称
            temperature: 生成的随机性（0-1）
            max_tokens: 最大生成token数
        """
        if not api_key:
            raise ValueError("必须提供api_key")
        if not base_url:
            raise ValueError("必须提供base_url")
            
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def format_and_enhance(self, text: str) -> str:
        """格式化和增强OCR的文本内容"""
        try:
            # 准备提示词
            messages = [
                {"role": "system", "content": "你是一个专业的笔记整理助手。你需要帮助整理和优化OCR识别出的课堂笔记内容，使其更加清晰、结构化，并保持原有的重点标记。请注意，你应该只输出整理后的笔记内容，不要包含任何其他信息。"},
                {"role": "user", "content": f"""请帮我整理以下课堂笔记内容，要求：
1. 保持原有的结构和格式
2. 保留所有重点标记
3. 修正明显的OCR错误（比如不合理的人名、称呼和名词等）
4. 优化段落和缩进
5. 确保数学公式和符号的正确性

笔记内容：
{text}"""}
            ]

            # 调用API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return completion.choices[0].message.content

        except Exception as e:
            logging.error(f"文本处理失败: {str(e)}")
            return text  # 如果处理失败，返回原文本
