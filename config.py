import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 项目根目录
    ROOT_DIR = Path(__file__).parent.absolute()
    
    # 输入输出目录
    INPUT_DIR = os.path.join(ROOT_DIR, os.getenv('INPUT_DIR', 'input'))
    OUTPUT_DIR = os.path.join(ROOT_DIR, os.getenv('OUTPUT_DIR', 'output'))
    
    # 支持的图片格式
    IMAGE_EXTENSIONS = os.getenv('IMAGE_EXTENSIONS', '.jpg,.jpeg,.png').split(',')
    
    # OCR API配置
    OCR_API = {
        'KEY': os.getenv('DASHSCOPE_API_KEY'),
        'BASE_URL': os.getenv('DASHSCOPE_API_BASE_URL'),
        'MODEL': os.getenv('DASHSCOPE_MODEL'),
    }
    
    # 文本处理API配置
    TEXT_API = {
        'KEY': os.getenv('DEEPSEEK_API_KEY'),
        'BASE_URL': os.getenv('DEEPSEEK_API_BASE_URL'),
        'MODEL': os.getenv('DEEPSEEK_MODEL'),
    }
    
    # 图像处理配置
    IMAGE_CONFIG = {
        'MIN_PAGE_AREA_RATIO': float(os.getenv('MIN_PAGE_AREA_RATIO', '0.15')),
        'PAGE_MARGIN': int(os.getenv('PAGE_MARGIN', '10')),
        'MIN_ASPECT_RATIO': float(os.getenv('MIN_ASPECT_RATIO', '0.5')),
        'MAX_ASPECT_RATIO': float(os.getenv('MAX_ASPECT_RATIO', '1.5')),
        'MIN_IMAGE_SIZE': int(os.getenv('MIN_IMAGE_SIZE', '1000')),
    }
    
    # OCR配置
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))
    
    # 并发配置
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '1'))

    def __post_init__(self):
        """配置后处理"""
        # 验证必要的配置
        if not self.OCR_API['KEY']:
            raise ValueError("必须在.env中设置DASHSCOPE_API_KEY")
        if not self.TEXT_API['KEY']:
            raise ValueError("必须在.env中设置DEEPSEEK_API_KEY")

# 创建配置实例
config = Config()

# 创建必要的目录
os.makedirs(config.INPUT_DIR, exist_ok=True)
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
