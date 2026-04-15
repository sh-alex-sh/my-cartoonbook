"""
直接调用 LibLib API 生成图片
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'env', '.env'))

LIBLIB_API_KEY = os.getenv("LIBLIB_API_KEY", "")
LIBLIB_API_BASE = "https://openapi.liblibai.cloud"

def generate_image(prompt, output_path="output.png"):
    if not LIBLIB_API_KEY:
        print("请先在 env/.env 中配置 API Key")
        return None

    headers = {
        "Authorization": f"Bearer {LIBLIB_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "绘本风格模型ID",
        "prompt": prompt,
        "negative_prompt": "低质量、模糊、变形",
        "steps": 20,
        "cfg_scale": 7.0,
        "width": 1024,
        "height": 1024
    }

    print(f"正在生成图片: {prompt}")
    print(f"API: {LIBLIB_API_BASE}/v1/text2img")

    try:
        response = requests.post(
            f"{LIBLIB_API_BASE}/v1/text2img",
            headers=headers,
            json=payload,
            timeout=120
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            image_url = result.get("image_url")
            print(f"图片URL: {image_url}")

            if image_url:
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"图片已保存: {output_path}")
                    return output_path
        else:
            print(f"API 请求失败")

    except Exception as e:
        print(f"发生错误: {e}")

    return None

if __name__ == "__main__":
    generate_image("中国小男孩，绘本风格，温暖色调")