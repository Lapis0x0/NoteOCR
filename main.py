import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import concurrent.futures
from tqdm import tqdm
import cv2
import time
from dotenv import load_dotenv

from processors.image_processor import ImageProcessor
from processors.ocr_processor import OCRProcessor
from processors.text_processor import TextProcessor
from utils.file_handler import FileHandler
from config import config

class NoteOCR:
    def __init__(self):
        """初始化NoteOCR"""
        # 加载环境变量
        load_dotenv()
        
        # 初始化处理器
        self.ocr_processor = OCRProcessor(
            api_key=config.OCR_API['KEY'],
            base_url=config.OCR_API['BASE_URL']
        )
        
        self.text_processor = TextProcessor(
            api_key=config.TEXT_API['KEY'],
            base_url=config.TEXT_API['BASE_URL'],
            model=config.TEXT_API['MODEL']
        )
        
        self.file_handler = FileHandler()
        self.image_processor = ImageProcessor()

    def process_single_page(self, page_image: cv2.Mat, filename: str, page_num: int, total_pages: int) -> Optional[Dict[str, str]]:
        """处理单个页面"""
        try:
            # 预处理图片
            processed_image = self.image_processor.preprocess_image(page_image)
            
            # OCR识别
            raw_text = self.ocr_processor.process_image(processed_image)
            if raw_text:
                # 使用文本处理器优化内容
                enhanced_text = self.text_processor.format_and_enhance(raw_text)
                
                page_info = f"{filename} (Page {page_num}/{total_pages})"
                return {
                    'filename': page_info,
                    'text': enhanced_text
                }
            
            return None
        except Exception as e:
            logging.error(f"处理页面时出错 {filename} Page {page_num}: {str(e)}")
            return None

    def process_single_image(self, image_path: str) -> List[Dict[str, str]]:
        """处理单张图片"""
        try:
            # 获取文件名（不带扩展名）作为标题
            filename = Path(image_path).stem
            
            # 读取图片
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"无法读取图片: {image_path}")
            
            # 检测并分割页面
            pages = self.image_processor.detect_pages(image)
            logging.info(f"检测到 {len(pages)} 个页面")
            
            text_contents = []
            
            # 使用线程池并发处理页面
            with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
                # 提交所有页面处理任务
                futures = []
                for i, page_image in enumerate(pages):
                    future = executor.submit(
                        self.process_single_page,
                        page_image,
                        filename,
                        i + 1,
                        len(pages)
                    )
                    futures.append(future)
                
                # 按顺序获取结果
                for future in futures:
                    try:
                        result = future.result()
                        if result:
                            text_contents.append(result)
                    except Exception as e:
                        logging.error(f"处理页面时出错: {str(e)}")
            
            return text_contents
        except Exception as e:
            logging.error(f"处理图片时出错 {image_path}: {str(e)}")
            return []

    def process_directory(self):
        """处理整个目录的图片"""
        # 获取所有图片文件
        image_files = []
        for ext in config.IMAGE_EXTENSIONS:
            image_files.extend(Path(config.INPUT_DIR).glob(f"*{ext}"))
        image_files = sorted(image_files)
        
        if not image_files:
            logging.warning(f"在目录 {config.INPUT_DIR} 中没有找到图片文件")
            return
        
        text_contents = []
        
        # 使用线程池并发处理图片
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_image = {
                executor.submit(self.process_single_image, str(image_path)): image_path
                for image_path in image_files
            }
            
            # 使用tqdm显示进度
            with tqdm(total=len(image_files), desc="处理图片") as pbar:
                # 获取结果
                for future in concurrent.futures.as_completed(future_to_image):
                    image_path = future_to_image[future]
                    try:
                        results = future.result()
                        if results:
                            text_contents.extend(results)
                    except Exception as e:
                        logging.error(f"处理图片时出错 {image_path}: {str(e)}")
                    finally:
                        pbar.update(1)
        
        if text_contents:
            try:
                # 处理OCR结果
                output_base_path = os.path.join(config.OUTPUT_DIR, 'notes')
                markdown_path = self.file_handler.process_to_markdown(text_contents, output_base_path)
                
                logging.info("文件处理完成！")
                logging.info(f"Markdown文件：{markdown_path}")
            except Exception as e:
                logging.error(f"保存文件时出错: {str(e)}")
        else:
            logging.error("没有成功处理任何图片")

def main():
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 检查输入目录
        if not os.path.isdir(config.INPUT_DIR):
            logging.error(f"输入目录不存在: {config.INPUT_DIR}")
            return
        
        # 创建NoteOCR实例并处理目录
        ocr = NoteOCR()
        ocr.process_directory()
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()
