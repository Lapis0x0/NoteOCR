import os
import time
import logging
from pathlib import Path
from tqdm import tqdm
import cv2
from dotenv import load_dotenv

from processors.image_processor import ImageProcessor
from processors.ocr_processor import OCRProcessor
from processors.text_processor import TextProcessor
from utils.file_handler import FileHandler
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NoteOCR:
    def __init__(self):
        """初始化NoteOCR系统"""
        # 加载环境变量
        load_dotenv()
        
        # OCR API配置
        ocr_api_key = os.getenv('DASHSCOPE_API_KEY')
        if not ocr_api_key:
            raise ValueError("请在.env文件中设置DASHSCOPE_API_KEY")
            
        # 文本处理API配置
        text_api_key = os.getenv('DEEPSEEK_API_KEY')
        text_base_url = os.getenv('DEEPSEEK_API_BASE_URL')
        if not text_api_key:
            raise ValueError("请在.env文件中设置DEEPSEEK_API_KEY")

        # 初始化处理器
        self.ocr_processor = OCRProcessor(api_key=config.OCR_API['KEY'])
        self.text_processor = TextProcessor(
            api_key=config.TEXT_API['KEY'],
            base_url=config.TEXT_API['BASE_URL']
        )
        self.file_handler = FileHandler()

    def process_directory(self):
        """处理整个目录的图片"""
        image_files = []
        for ext in config.SUPPORTED_FORMATS:
            image_files.extend(Path(config.INPUT_DIR).glob(f"*{ext}"))
        
        if not image_files:
            logging.warning(f"在 {config.INPUT_DIR} 目录中没有找到支持的图片文件")
            return
        
        text_contents = []
        for image_file in tqdm(image_files, desc="处理图片"):
            logging.info(f"正在处理: {image_file.name}")
            
            try:
                # 读取图片
                image = cv2.imread(str(image_file))
                if image is None:
                    raise ValueError(f"无法读取图片: {image_file}")
                
                # 检测并分割页面
                pages = ImageProcessor.detect_pages(image)
                logging.info(f"检测到 {len(pages)} 个页面")
                
                # 处理每个页面
                for i, page_image in enumerate(pages, 1):
                    # 预处理图片
                    processed_image = ImageProcessor.preprocess_image(page_image)
                    
                    # OCR识别
                    raw_text = self.ocr_processor.process_image(processed_image)
                    if raw_text:
                        # 使用文本处理器优化内容
                        enhanced_text = self.text_processor.format_and_enhance(raw_text)
                        
                        page_info = f"{image_file.name} (Page {i}/{len(pages)})"
                        text_contents.append({
                            'filename': page_info,
                            'text': enhanced_text
                        })
                        # 立即将当前结果写入文件
                        with open(config.TXT_OUTPUT, 'a', encoding='utf-8') as f:
                            f.write(f"\n{'='*50}\n")
                            f.write(f"Source: {page_info}\n")
                            f.write(f"{'='*50}\n\n")
                            f.write(enhanced_text)
                            f.write('\n\n')
                    
                    # 避免API调用过于频繁
                    time.sleep(1)
                    
            except Exception as e:
                logging.error(f"处理图片 {image_file.name} 时出错: {str(e)}")
                continue
        
        if text_contents:
            try:
                self.file_handler.create_pdf(text_contents, config.PDF_OUTPUT)
                self.file_handler.save_to_txt(text_contents, config.TXT_OUTPUT)
            except Exception as e:
                logging.error(f"保存文件时出错: {str(e)}")
                logging.info("文件保存失败，但OCR结果已经处理完成")
        else:
            logging.warning("没有成功处理任何图片")

def main():
    try:
        ocr = NoteOCR()
        ocr.process_directory()
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
