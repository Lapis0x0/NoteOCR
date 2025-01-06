import os
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_supported_formats() -> List[str]:
    """从环境变量获取支持的图片格式列表"""
    formats_str = os.getenv('SUPPORTED_FORMATS', '.jpg,.jpeg,.png')
    return formats_str.split(',')

# API配置
OCR_API = {
    'KEY': os.getenv('DASHSCOPE_API_KEY'),
    'BASE_URL': os.getenv('DASHSCOPE_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
    'MODEL': os.getenv('DASHSCOPE_MODEL', 'qwen-vl-ocr'),
}

TEXT_API = {
    'KEY': os.getenv('DEEPSEEK_API_KEY'),
    'BASE_URL': os.getenv('DEEPSEEK_API_BASE_URL', 'https://api.lapis.cafe/v1'),
    'MODEL': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
    'TEMPERATURE': float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3')),
    'MAX_TOKENS': int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000')),
}

# 文件路径配置
INPUT_DIR = os.getenv('INPUT_DIR', 'input')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
PDF_OUTPUT = os.path.join(OUTPUT_DIR, os.getenv('PDF_FILENAME', 'notes.pdf'))
TXT_OUTPUT = os.path.join(OUTPUT_DIR, os.getenv('TXT_FILENAME', 'notes.txt'))

# 图像处理配置
IMAGE_CONFIG = {
    'MIN_PAGE_AREA_RATIO': float(os.getenv('MIN_PAGE_AREA_RATIO', '0.15')),
    'PAGE_MARGIN': int(os.getenv('PAGE_MARGIN', '10')),
    'MIN_ASPECT_RATIO': float(os.getenv('MIN_ASPECT_RATIO', '0.5')),
    'MAX_ASPECT_RATIO': float(os.getenv('MAX_ASPECT_RATIO', '1.5')),
    'MIN_IMAGE_SIZE': int(os.getenv('MIN_IMAGE_SIZE', '1000')),
}

# OCR配置
SUPPORTED_FORMATS = get_supported_formats()
MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))

# 创建必要的目录
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
