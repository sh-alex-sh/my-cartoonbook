"""
AI 绘本生成器
基于 Gradio + LibLib API 的图片生成应用
"""
import gradio as gr
import requests
import hmac
import hashlib
import base64
import time
import uuid
import os
from config import (
    LIBLIB_API_BASE, LIBLIB_ACCESS_KEY, LIBLIB_SECRET_KEY,
    DEFAULT_TEMPLATE_UUID, DEFAULT_STEPS, DEFAULT_IMG_COUNT
)


def make_signature(uri, timestamp, signature_nonce):
    content = f"{uri}&{timestamp}&{signature_nonce}"
    digest = hmac.new(
        LIBLIB_SECRET_KEY.encode(),
        content.encode(),
        hashlib.sha1
    ).digest()
    sign = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return sign


def make_auth_params(uri):
    timestamp = str(int(time.time() * 1000))
    signature_nonce = str(uuid.uuid4())
    signature = make_signature(uri, timestamp, signature_nonce)
    return {
        "AccessKey": LIBLIB_ACCESS_KEY,
        "Signature": signature,
        "Timestamp": timestamp,
        "SignatureNonce": signature_nonce
    }


def submit_generation(prompt, steps, img_count):
    if not prompt:
        return None, "请输入图片描述", None

    if not LIBLIB_ACCESS_KEY or not LIBLIB_SECRET_KEY:
        return None, "请先在 env/.env 中配置 AccessKey 和 SecretKey", None

    uri = "/api/generate/webui/text2img/ultra"
    auth_params = make_auth_params(uri)
    full_url = f"{LIBLIB_API_BASE}{uri}"

    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "templateUuid": DEFAULT_TEMPLATE_UUID,
            "generateParams": {
                "prompt": prompt,
                "promptMagic": 1,
                "aspectRatio": "square",
                "imgCount": img_count,
                "steps": steps
            }
        }

        response = requests.post(
            full_url,
            headers=headers,
            params=auth_params,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return None, f"API 请求失败: {response.status_code}", None

        result = response.json()
        if not isinstance(result, dict):
            return None, f"响应格式错误: {response.text[:100]}", None

        generate_uuid = result.get("data", {}).get("generateUuid")
        if not generate_uuid:
            return None, f"未获取到生成UUID: {response.text[:200]}", None

        return None, "已提交任务，正在等待生成（请稍候1-3分钟）...", generate_uuid

    except requests.exceptions.Timeout:
        return None, "请求超时", None
    except Exception as e:
        return None, f"网络错误: {str(e)}", None


def poll_status(generate_uuid):
    uri = "/api/generate/webui/status"
    full_url = f"{LIBLIB_API_BASE}{uri}"

    for i in range(120):
        print(f"[调试] 第 {i+1} 次轮询...")
        if not generate_uuid:
            return None, None, "任务已取消"

        try:
            auth_params = make_auth_params(uri)
            print(f"[调试] 发送请求到 {full_url}")
            response = requests.post(
                full_url,
                params=auth_params,
                json={"generateUuid": generate_uuid},
                timeout=30
            )
            print(f"[调试] 响应状态码: {response.status_code}")

            if response.status_code == 200:
                print(f"[调试] 开始解析响应...")
                result = response.json()
                print(f"[调试] 响应内容: {result}")
                if not isinstance(result, dict):
                    return None, None, "响应格式错误"

                data = result.get("data", {}) or {}
                generate_status = data.get("generateStatus")
                print(f"[调试] generateStatus: {generate_status}")

                if generate_status == 6 or (generate_status == 5 and data.get("percentCompleted", 0) == 1.0):
                    print(f"[调试] 生成成功，准备下载图片...")
                    images = data.get("images", [])
                    if images:
                        image_url = images[0].get("imageUrl")
                        if image_url:
                            print(f"[调试] 图片URL: {image_url}")
                            local_path = download_image(image_url)
                            print(f"[调试] 本地路径: {local_path}")
                            if local_path:
                                return local_path, "生成成功！", None
                    return None, None, "生成成功但无图片"

                elif generate_status == 7:
                    error_msg = data.get("generateMsg", "未知错误")
                    return None, None, f"生成失败: {error_msg}"

                elif generate_status in (1, 2, 3, 4):
                    progress = int((data.get("percentCompleted", 0) or 0) * 100)
                    print(f"[调试] 生成进度: {progress}%")

        except Exception as e:
            print(f"[调试] 查询异常: {str(e)}")
            return None, None, f"查询失败: {str(e)}"

        print(f"[调试] 等待3秒...")
        time.sleep(3)

    return None, None, "生成超时"


def download_image(image_url, save_dir="outputs"):
    os.makedirs(save_dir, exist_ok=True)
    try:
        response = requests.get(image_url, timeout=60)
        if response.status_code == 200:
            filename = f"{save_dir}/storybook_{int(time.time())}.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception:
        pass
    return None


def generate_image(prompt, negative_prompt, steps, img_count):
    print(f"[调试] 开始生成图片: {prompt}")
    err, status, uuid = submit_generation(prompt, steps, img_count)
    if err:
        print(f"[调试] 提交失败: {err}")
        return None, err

    print(f"[调试] 任务已提交，UUID: {uuid}")
    yield None, status

    if uuid:
        print(f"[调试] 开始轮询状态...")
        image, final_status, _ = poll_status(uuid)
        print(f"[调试] 轮询完成，image={image}, status={final_status}")
        yield image, final_status


def main():
    with gr.Blocks(title="AI 绘本生成器") as demo:
        gr.Markdown("# 🎨 AI 绘本生成器\n输入文字描述，AI 将为你生成精美的绘本风格图片")

        with gr.Row():
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(
                    label="图片描述",
                    placeholder="例如：一只小兔子在森林里采蘑菇，宫崎骏动画风格",
                    lines=4
                )

                negative_prompt = gr.Textbox(
                    label="负面提示词（可选）",
                    placeholder="例如：低质量、模糊、变形",
                    lines=2
                )

                with gr.Accordion("高级设置", open=False):
                    steps = gr.Slider(
                        minimum=10, maximum=50, value=DEFAULT_STEPS,
                        step=1, label="生成步数"
                    )
                    img_count = gr.Slider(
                        minimum=1, maximum=4, value=DEFAULT_IMG_COUNT,
                        step=1, label="生图数量"
                    )

                generate_btn = gr.Button("生成绘本图片", variant="primary")

            with gr.Column(scale=1):
                output_image = gr.Image(label="生成的图片", type="filepath")
                status_text = gr.Textbox(label="状态信息", lines=2)

        generate_btn.click(
            fn=generate_image,
            inputs=[prompt_input, negative_prompt, steps, img_count],
            outputs=[output_image, status_text]
        )

    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()