# NoteOCR - 智能笔记处理系统

NoteOCR 是一个专门用于处理和优化手写笔记的 OCR 系统。它能够自动检测页面、识别文字内容，并生成结构化的 PDF 和 TXT 输出文件。

## 主要特性

- 🔍 智能页面检测：使用 Otsu 阈值和轮廓检测自动识别笔记页面
- 📝 高质量 OCR：使用阿里 Qwen VL-OCR API 进行中文手写文本识别
- 🎨 智能文本优化：使用 Deepseek API 进行文本整理和优化
- 📄 多格式输出：同时生成 PDF 和 TXT 格式的文件
- 🎯 保持原有格式：保留笔记中的重点标记和结构

## 系统要求

- Python 3.8+
- OpenCV
- 阿里 Qwen VL-OCR API 密钥
- Deepseek API 密钥

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/NoteOCR.git
   cd NoteOCR
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   .\venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   创建 `.env` 文件并添加以下内容：
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key
   DEEPSEEK_API_BASE_URL=your_deepseek_api_base_url
   ALI_QWEN_VL_OCR_API_KEY=your_ali_qwen_vl_ocr_api_key
   INPUT_DIR=input
   OUTPUT_DIR=output
   PDF_FILENAME=notes.pdf
   TXT_FILENAME=notes.txt
   ```

## 使用方法

1. 将需要处理的笔记图片放入 `input` 目录

2. 运行程序：
   ```bash
   python main.py
   ```

3. 处理完成后，可以在 `output` 目录中找到生成的 PDF 和 TXT 文件

## 项目结构

```
NoteOCR/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── processors/          # 处理器模块
│   ├── image_processor.py   # 图像处理
│   ├── ocr_processor.py     # OCR 处理
│   └── text_processor.py    # 文本处理
├── utils/              # 工具模块
│   └── file_handler.py     # 文件处理
├── input/              # 输入目录
└── output/             # 输出目录
```

## 开发说明

- 图像处理使用 OpenCV 进行页面检测和预处理
- OCR 使用阿里 Qwen VL-OCR API 进行文字识别
- 文本优化使用 Deepseek API
- PDF 生成使用 ReportLab，支持中文显示

## 注意事项

- 确保输入图片清晰可读
- 图片背景最好是纯色的
- 建议使用 JPG 或 PNG 格式的图片
- 处理大量图片时可能需要较长时间

## 未来计划

- [ ] 添加批量处理功能
- [ ] 提高图片检测处理的鲁棒性
- [ ] 优化页面检测算法
- [ ] 提供更多输出格式选项
