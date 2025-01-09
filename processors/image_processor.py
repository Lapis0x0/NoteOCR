import cv2
import numpy as np
import logging
from typing import List
from scipy.signal import find_peaks

class ImageProcessor:
    @staticmethod
    def detect_pages(image: np.ndarray) -> List[np.ndarray]:
        """智能检测并分割图片中的笔记页面"""
        if image is None:
            raise ValueError("无效的图片数据")

        # 获取图片尺寸
        height, width = image.shape[:2]
        
        # 预处理步骤
        # 1. 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. 自适应直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 3. 高斯模糊减少噪声
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 4. Canny边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 5. 使用霍夫变换检测直线
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        # 创建掩码用于绘制直线
        line_mask = np.zeros_like(gray)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_mask, (x1, y1), (x2, y2), 255, 2)
        
        # 6. 形态学操作强化线条
        kernel = np.ones((5,5), np.uint8)
        line_mask = cv2.dilate(line_mask, kernel, iterations=2)
        line_mask = cv2.erode(line_mask, kernel, iterations=1)
        
        # 7. 查找轮廓
        contours, _ = cv2.findContours(line_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选并排序找到的矩形区域
        page_regions = []
        min_area = width * height * 0.1  # 降低最小面积阈值到10%
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # 获取最小外接矩形
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int_(box)
            
            # 计算长宽比
            width_rect = rect[1][0]
            height_rect = rect[1][1]
            aspect_ratio = max(width_rect, height_rect) / min(width_rect, height_rect)
            
            # 更宽松的长宽比限制
            if aspect_ratio > 2.0 or aspect_ratio < 0.3:
                continue
            
            # 获取透视变换的四个顶点
            src_pts = box.astype("float32")
            # 根据矩形的方向确定目标点
            if width_rect < height_rect:
                dst_pts = np.array([[0, height_rect-1],
                                  [0, 0],
                                  [width_rect-1, 0],
                                  [width_rect-1, height_rect-1]], dtype="float32")
            else:
                dst_pts = np.array([[0, 0],
                                  [width_rect-1, 0],
                                  [width_rect-1, height_rect-1],
                                  [0, height_rect-1]], dtype="float32")
            
            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            
            # 执行透视变换
            warped = cv2.warpPerspective(image, M, (int(width_rect), int(height_rect)))
            
            # 获取边界框中心点的x坐标用于排序
            center_x = np.mean(box[:, 0])
            page_regions.append((center_x, warped))
        
        # 如果没有检测到页面，使用改进的备选方案
        if not page_regions:
            logging.info("使用备选方案：基于文本密度分析")
            return ImageProcessor._fallback_page_detection(image)
            
        # 按x坐标从左到右排序
        page_regions.sort(key=lambda x: x[0])
        pages = [region[1] for region in page_regions]
        
        logging.info(f"检测到 {len(pages)} 个页面")
        
        # 如果检测到的页面数量不是3个，使用备选方案
        if len(pages) != 3:
            logging.info("检测到的页面数量不是3个，使用备选方案")
            return ImageProcessor._fallback_page_detection(image)
        
        return pages

    @staticmethod
    def _fallback_page_detection(image: np.ndarray) -> List[np.ndarray]:
        """改进的备选方案：基于文本密度分析的页面检测"""
        height, width = image.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 自适应二值化
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # 计算水平方向的文本密度分布
        density = np.sum(binary, axis=0) / height
        
        # 使用移动平均平滑密度曲线
        window_size = width // 20
        kernel = np.ones(window_size) / window_size
        smooth_density = np.convolve(density, kernel, mode='same')
        
        # 找到密度的局部最小值作为分割点
        valleys, _ = find_peaks(-smooth_density)
        
        # 如果找到的分割点不够或太多，使用等距分割
        if len(valleys) != 2:
            page_width = width // 3
            split_points = [page_width, page_width * 2]
        else:
            split_points = sorted(valleys)
        
        # 分割图像
        pages = []
        start_x = 0
        for split_x in split_points:
            pages.append(image[:, start_x:split_x].copy())
            start_x = split_x
        pages.append(image[:, start_x:].copy())
        
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
            min_height = 1000
            height, width = image.shape[:2]
            if height < min_height:
                scale = min_height / height
                new_width = int(width * scale)
                image = cv2.resize(image, (new_width, min_height), interpolation=cv2.INTER_CUBIC)
            
            # 自适应对比度增强
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge((l,a,b))
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # 锐化处理
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            image = cv2.filter2D(image, -1, kernel)
            
            # 降噪
            image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            
            return image
            
        except Exception as e:
            logging.error(f"图片预处理失败: {str(e)}")
            return image
