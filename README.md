# NoteOCR - 智能笔记处理系统

NoteOCR 是一个专门用于处理和优化手写笔记的 OCR 系统。它能够自动检测页面、识别文字内容，并生成结构化的 Markdown 文件。

## 主要特性

- 🔍 智能页面检测：使用 Otsu 阈值和轮廓检测自动识别笔记页面
- 📝 高质量 OCR：使用阿里 Qwen VL-OCR API 进行中文手写文本识别
- 🎨 智能文本优化：使用 Deepseek API 进行文本整理和优化
- ⚡️ 并发处理：支持多线程并发处理多个页面
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
   复制 `.env.example` 并重命名为 `.env` ，然后填写以下必要配置：
   - `DASHSCOPE_API_KEY`: OCR API 密钥
   - `DEEPSEEK_API_KEY`: 文本处理 API 密钥
   
   其他配置项可以保持默认值或根据需要调整。

## 使用方法

1. 将需要处理的笔记图片放入 `input` 目录

2. 运行程序：
   ```bash
   python main.py
   ```

3. 处理完成后，可以在 `output` 目录中找到生成的 Markdown 文件

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
- 并发处理使用 Python 的 `concurrent.futures`

## 配置说明

所有配置项都集中在 `.env` 文件中，主要包括：

- API 配置（OCR 和文本处理）
- 图像处理参数
- 并发处理参数
- 输入输出目录设置

详细的配置说明请参考 `.env.example` 文件。

## 注意事项

- 确保输入图片清晰可读
- 图片背景最好是纯色的
- 支持的图片格式：JPG、JPEG、PNG
- 处理速度受并发设置和 API 限制影响

## 未来计划

- [ ] 支持更多的 OCR API 选项
- [ ] 提高图片检测处理的鲁棒性
- [ ] 优化页面检测算法
- [ ] 添加更多文本优化选项
