# AI 绘本生成器

将文档自动转换为儿童绘本的工具。

## 功能

- 📄 **文档解析**：支持 PDF、Word、TXT 格式，PDF 中的图片自动 OCR 识别
- 📝 **智能大纲**：基于 DeepSeek API 生成专业的儿童绘本结构
- 🎨 **图片生成**：基于 liblib API 生成绘本风格的插画
- 📖 **PDF 导出**：生成可打印的绘本书籍

## 项目结构

```
├── app.py                 # Flask 应用入口
├── routes.py              # API 路由定义
├── config.py              # 配置（API 密钥等）
├── services/
│   ├── pdf_parser.py      # 文档解析服务
│   ├── outline_generator.py # 大纲生成服务
│   ├── image_generator.py   # 图片生成服务
│   └── pdf_exporter.py    # PDF 导出服务
├── templates/
│   └── index.html         # 前端界面
└── env/
    └── .env.example       # 环境变量模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask PyPDF2 python-docx pdf2image pytesseract Pillow requests reportlab
```

### 2. 配置环境变量

复制 `env/.env.example` 为 `.env`，填入以下密钥：

```
DEEPSEEK_API_KEY=你的DeepSeek密钥
LIBLIB_ACCESS_KEY=你的liblib AccessKey
LIBLIB_SECRET_KEY=你的liblib SecretKey
```

### 3. 安装 OCR（Windows）

1. 下载 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. 安装并下载中文语言包 `chi_sim.traineddata`
3. 配置路径（代码中默认：`C:\Program Files\Tesseract-OCR\tesseract.exe`）

### 4. 安装 PDF 渲染（Windows）

下载 [Poppler](https://github.com/oschwartz10612/poppler-windows/releases)，解压到 `C:\poppler`

### 5. 运行

```bash
python app.py
```

打开浏览器访问 `http://localhost:5000`

## 使用流程

1. **上传文档**：点击"上传并解析"导入 PDF/Word/TXT 文件
2. **编辑内容**：在文本框中编辑或直接输入故事内容
3. **生成大纲**：点击"生成大纲"，AI 自动设计绘本结构
4. **生成图片**：选择要生成的页面，点击"生成图片"
5. **导出 PDF**：点击"导出 PDF"下载完成的绘本

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传文件 |
| `/api/parse` | POST | 解析文档 |
| `/api/outline` | POST | 生成大纲 |
| `/api/generate` | POST | 生成图片 |
| `/api/export` | POST | 导出 PDF |

## 技术栈

- **后端**：Flask
- **AI 大纲**：DeepSeek API
- **图片生成**：liblib AI API
- **OCR**：Tesseract
- **PDF 处理**：PyPDF2, pdf2image, ReportLab
