"""
AI 绘本生成器配置文件
"""
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'env', '.env')
print(f"[DEBUG] 加载环境变量文件: {env_path}")
print(f"[DEBUG] 文件存在: {os.path.exists(env_path)}")
load_dotenv(env_path, override=True)

# LibLib API 配置
LIBLIB_API_BASE = "https://openapi.liblibai.cloud"
LIBLIB_ACCESS_KEY = os.getenv("LIBLIB_ACCESS_KEY", "")
LIBLIB_SECRET_KEY = os.getenv("LIBLIB_SECRET_KEY", "")
print(f"[DEBUG] LIBLIB_ACCESS_KEY: {LIBLIB_ACCESS_KEY}")
print(f"[DEBUG] LIBLIB_SECRET_KEY: {LIBLIB_SECRET_KEY[:4] if LIBLIB_SECRET_KEY else 'None'}...")

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# 服务地址配置（用于生成参考图URL）
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

# 默认模型配置
DEFAULT_TEMPLATE_UUID = "5d7e67009b344550bc1aa6ccbfa1d7f4"

# 图片生成参数默认值
DEFAULT_STEPS = 30
DEFAULT_IMG_COUNT = 1