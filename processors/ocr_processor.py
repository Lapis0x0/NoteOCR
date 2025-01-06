import base64
import logging
from typing import Optional
from openai import OpenAI
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

class OCRProcessor:
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def process_image(self, image: np.ndarray) -> str:
        """处理单张图片并返回OCR结果"""
        try:
            # 将OpenCV图片转换为bytes
            success, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            if not success:
                raise ValueError("图片编码失败")
            
            # 转换为base64
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 准备API请求
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                        "min_pixels": 28 * 28 * 4,
                        "max_pixels": 28 * 28 * 1280
                    },
                    {"type": "text", "text": "Read all the text in the image."}
                ]
            }]
            
            # 调用API
            completion = self.client.chat.completions.create(
                model="qwen-vl-ocr",
                messages=messages
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OCR处理失败: {str(e)}")
            return ""
