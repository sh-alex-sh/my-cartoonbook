# AI 绘本生成器

一个基于 AI 的儿童绘本自动生成工具，能够将文档或故事大纲转换为完整的绘本。

## 功能特色

- 📄 **多格式文档解析**：支持 PDF、Word、TXT 格式，支持 PDF 中的图片 OCR 识别
- 📝 **智能故事大纲**：基于 DeepSeek API 自动生成专业的儿童绘本结构
- 🎨 **AI 图片生成**：基于 Gemini-2.5-flash-image 模型生成绘本风格的插画
- 📖 **专业 PDF 导出**：生成可打印的绘本书籍格式
- 🔄 **角色一致性**：通过角色设定参考图保持图片中角色的一致性

## 项目结构

```
├── app.py                 # Flask 应用主入口
├── routes.py              # Web API 路由定义
├── config.py              # 应用配置（API 密钥、模型设置等）
├── services/              # 核心服务模块
│   ├── pdf_parser.py      # 文档解析服务
│   ├── outline_generator.py # 故事大纲生成服务
│   ├── image_generator.py   # 图片生成服务（基于 Gemini API）
│   └── pdf_exporter.py    # PDF 导出服务
├── templates/             # 前端模板
│   └── index.html         # 主界面
├── env/                   # 环境配置
│   └── .env.example       # 环境变量模板
└── outputs/               # 生成文件输出目录（自动创建）
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask PyPDF2 python-docx pdf2image pytesseract Pillow requests reportlab python-dotenv
```

### 2. 配置环境变量

复制 `env/.env.example` 为 `env/.env`，填入以下配置：

```env
# 图像生成 API 配置（必填）
IMAGE_API_BASE=https://www.packyapi.com
IMAGE_API_KEY=你的API密钥
IMAGE_MODEL_ID=gemini-2.5-flash-image

# DeepSeek API 配置（用于故事大纲生成）
DEEPSEEK_API_KEY=你的DeepSeek密钥

# 服务地址配置
API_BASE_URL=http://127.0.0.1:5000
```

### 3. 安装 OCR 支持（可选，用于 PDF 文字识别）

**Windows 用户：**
1. 下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. 下载中文语言包 `chi_sim.traineddata`
3. 默认路径：`C:\Program Files\Tesseract-OCR\tesseract.exe`

### 4. 安装 PDF 渲染支持（可选，用于 PDF 图片提取）

**Windows 用户：**
下载 [Poppler](https://github.com/oschwartz10612/poppler-windows/releases)，解压到 `C:\poppler`

### 5. 运行应用

```bash
python app.py
```

启动后访问：`http://localhost:5000`

## 使用流程

1. **上传文档**：点击"上传并解析"导入 PDF/Word/TXT 文件
2. **编辑内容**：在文本框中编辑或直接输入故事内容
3. **生成大纲**：点击"生成大纲"，AI 自动设计绘本结构（封面、内容页、封底）
4. **生成图片**：选择要生成的页面，点击"生成图片"
5. **导出 PDF**：点击"导出 PDF"下载完成的绘本

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传文档文件 |
| `/api/parse` | POST | 解析文档内容 |
| `/api/outline` | POST | 生成绘本大纲 |
| `/api/images` | POST | 批量生成图片 |
| `/api/export` | POST | 导出 PDF 绘本 |

## 技术栈

- **Web 框架**：Flask
- **AI 故事大纲**：DeepSeek API
- **AI 图片生成**：Gemini-2.5-flash-image（通过 packyapi.com）
- **文档处理**：PyPDF2, python-docx
- **OCR 识别**：Tesseract
- **PDF 生成**：ReportLab
- **版本控制**：Git

## 项目状态

- ✅ **基础功能**：文档解析、大纲生成、图片生成、PDF 导出
- ✅ **角色一致性**：通过参考图保持角色特征一致
- ✅ **Git 管理**：代码已推送到 GitHub 远程仓库
- 🔄 **持续优化**：根据实际使用反馈不断改进

## 注意事项

- 图片生成依赖于第三方 AI 服务，请确保 API 密钥有效
- 生成图片时请避免使用可能触发内容安全审核的描述
- 中文文字渲染可能存在字体兼容性问题
- 建议在生成前先测试单张图片的生成效果

## 许可证

本项目仅供学习和研究使用。