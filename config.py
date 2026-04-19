"""
AI 绘本生成器配置文件
"""
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'env', '.env')
print(f"[DEBUG] 加载环境变量文件: {env_path}")
print(f"[DEBUG] 文件存在: {os.path.exists(env_path)}")
load_dotenv(env_path, override=True)

# 图像生成 API 配置
IMAGE_API_BASE = os.getenv("IMAGE_API_BASE", "https://api.example.com") # 替换为你的 API 地址
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "")
IMAGE_MODEL_ID = os.getenv("IMAGE_MODEL_ID", "default-model-id") # 如果需要，可以配置模型ID


# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = "https://api.deepseek.com"

# 服务地址配置（用于生成参考图URL）
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")



# 图片生成参数默认值
DEFAULT_STEPS = 30
DEFAULT_IMG_COUNT = 1
