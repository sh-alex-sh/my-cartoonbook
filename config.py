"""
AI 绘本生成器配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'env', '.env'))

# LibLib API 配置
LIBLIB_API_BASE = "https://openapi.liblibai.cloud"
LIBLIB_ACCESS_KEY = os.getenv("LIBLIB_ACCESS_KEY", "")
LIBLIB_SECRET_KEY = os.getenv("LIBLIB_SECRET_KEY", "")

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# 默认模型配置
DEFAULT_TEMPLATE_UUID = "5d7e67009b344550bc1aa6ccbfa1d7f4"

# 图片生成参数默认值
DEFAULT_STEPS = 30
DEFAULT_IMG_COUNT = 1