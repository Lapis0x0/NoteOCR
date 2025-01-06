import cv2
import numpy as np
import logging
from typing import List

class ImageProcessor:
    @staticmethod
    def detect_pages(image: np.ndarray) -> List[np.ndarray]:
        """智能检测并分割图片中的笔记页面"""
        if image is None:
            raise ValueError("无效的图片数据")

        # 获取图片尺寸
        height, width = image.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用Otsu's二值化方法
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 使用形态学操作清理噪声
        kernel = np.ones((5,5), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=2)
        binary = cv2.erode(binary, kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选并排序找到的矩形区域
        page_regions = []
        min_area = width * height * 0.15  # 调整最小区域面积（图片面积的15%）
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 计算长宽比
            aspect_ratio = w / h
            # 调整长宽比阈值，笔记通常是竖直的矩形
            if aspect_ratio > 1.5 or aspect_ratio < 0.5:  # 更严格的长宽比限制
                continue
            
            # 添加边距
            margin = 10
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(width, x + w + margin)
            y2 = min(height, y + h + margin)
            
            # 提取页面图像
            page_image = image[y1:y2, x1:x2].copy()  # 使用copy()避免引用问题
            # 保存坐标信息用于排序
            page_regions.append((x1, page_image))
        
        # 如果没有检测到页面，尝试简单的三等分
        if not page_regions:
            logging.info("使用备选方案：按宽度三等分")
            page_width = width // 3
            pages = []
            for i in range(3):
                start_x = i * page_width
                end_x = (i + 1) * page_width if i < 2 else width
                page_image = image[:, start_x:end_x].copy()
                pages.append(page_image)
            return pages
            
        # 按x坐标从左到右排序
        page_regions.sort(key=lambda x: x[0])
        pages = [region[1] for region in page_regions]
        
        logging.info(f"检测到 {len(pages)} 个页面")
        
        # 如果检测到的页面数量不是3个，也使用三等分方案
        if len(pages) != 3:
            logging.info("检测到的页面数量不是3个，使用备选方案：按宽度三等分")
            page_width = width // 3
            pages = []
            for i in range(3):
                start_x = i * page_width
                end_x = (i + 1) * page_width if i < 2 else width
                page_image = image[:, start_x:end_x].copy()
                pages.append(page_image)
        
        return pages

    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """预处理图片以提高OCR效果"""
        try:
            # 转换为RGB格式
            if len(image.shape) == 2:  # 如果是灰度图
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 3:  # 如果是BGR格式
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 调整大小确保图片不会太小
            min_size = 1000
            height, width = image.shape[:2]
            if width < min_size or height < min_size:
                scale = min_size / min(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 增强对比度
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge((l,a,b))
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return image
            
        except Exception as e:
            logging.error(f"图片预处理失败: {str(e)}")
            return image
