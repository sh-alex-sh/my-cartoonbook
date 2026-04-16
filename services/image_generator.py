"""
图片生成服务
"""
import requests
import hmac
import hashlib
import base64
import time
import uuid
import os
import json


class ImageGenerator:
    def __init__(self):
        from config import LIBLIB_API_BASE, LIBLIB_ACCESS_KEY, LIBLIB_SECRET_KEY
        self.api_base = LIBLIB_API_BASE
        self.access_key = LIBLIB_ACCESS_KEY
        self.secret_key = LIBLIB_SECRET_KEY

    def _get_output_dir(self, task_id, original_name):
        safe_name = original_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        folder_name = f"{safe_name}_{task_id[:8]}"
        output_dir = os.path.join("outputs", folder_name, "images")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir, folder_name

    def make_signature(self, uri, timestamp, signature_nonce):
        content = f"{uri}&{timestamp}&{signature_nonce}"
        digest = hmac.new(self.secret_key.encode(), content.encode(), hashlib.sha1).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    def make_auth_params(self, uri):
        timestamp = str(int(time.time() * 1000))
        signature_nonce = str(uuid.uuid4())
        signature = self.make_signature(uri, timestamp, signature_nonce)
        print(f"[DEBUG] 签名参数 - URI: {uri}, Timestamp: {timestamp}, SignatureNonce: {signature_nonce}, Signature: {signature}")
        return {
            "AccessKey": self.access_key,
            "Signature": signature,
            "Timestamp": timestamp,
            "SignatureNonce": signature_nonce
        }

    def generate_one(self, scene_description, output_dir, folder_name):
        uri = "/api/generate/webui/text2img/ultra"
        auth_params = self.make_auth_params(uri)
        full_url = f"{self.api_base}{uri}"
        print(f"[DEBUG] 完整请求URL: {full_url}")
        print(f"[DEBUG] 请求参数: {auth_params}")
        payload = {
            "templateUuid": "5d7e67009b344550bc1aa6ccbfa1d7f4",
            "generateParams": {
                "prompt": scene_description,
                "promptMagic": 1,
                "aspectRatio": "square",
                "imgCount": 1
            }
        }
        print(f"[DEBUG] 开始生成图片，prompt: {scene_description[:80]}...")
        response = requests.post(full_url, headers={"Content-Type": "application/json"}, params=auth_params, json=payload, timeout=30)
        print(f"[DEBUG] 生成请求响应: {response.status_code} - {response.text[:200]}")
        result = response.json()
        generate_uuid = result.get("data", {}).get("generateUuid")
        if not generate_uuid:
            error_msg = result.get("msg", result.get("message", str(result)))
            print(f"[DEBUG] 生成失败: {error_msg}")
            raise Exception(f"图片生成请求失败: {error_msg}")
        return self._wait_for_image(generate_uuid, output_dir, folder_name)

    def _wait_for_image(self, generate_uuid, output_dir, folder_name, max_retries=60):
        uri = "/api/generate/webui/status"
        for i in range(max_retries):
            auth_params = self.make_auth_params(uri)
            response = requests.post(f"{self.api_base}{uri}", params=auth_params, json={"generateUuid": generate_uuid}, timeout=30)
            result = response.json()
            data = result.get("data")
            if data is None:
                print(f"[DEBUG] 状态轮询 {i+1}: data为空, 响应: {response.text[:100]}")
                time.sleep(3)
                continue
            status = data.get("generateStatus")
            print(f"[DEBUG] 状态轮询 {i+1}: status={status}")
            if status == 6 or (status == 5 and data.get("percentCompleted") == 1.0):
                images = data.get("images")
                if images and len(images) > 0:
                    image_url = images[0].get("imageUrl")
                    if image_url:
                        local_path = self._download_image(image_url, generate_uuid, output_dir, folder_name)
                        return local_path
            time.sleep(3)
        raise Exception("生成超时（60秒内未完成）")

    def _download_image(self, image_url, generate_uuid, output_dir, folder_name):
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                filename = f"{generate_uuid}.png"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"[DEBUG] 图片保存到: {filepath}")
                return f"/api/image/{folder_name}/{filename}"
        except Exception as e:
            print(f"[DEBUG] 下载图片失败: {e}")
            pass
        return image_url

    def generate_all(self, outline, task_id, original_name):
        character = outline.get('character', {})
        char_description = self._build_character_description(character)
        output_dir, folder_name = self._get_output_dir(task_id, original_name)

        images = []

        cover_data = outline.get('cover', {})
        if cover_data.get('visual_description'):
            cover_prompt = self._build_prompt(cover_data['visual_description'], char_description, is_cover=True)
            try:
                image_path = self.generate_one(cover_prompt, output_dir, folder_name)
                images.append({
                    "page_num": 0,
                    "image_url": image_path,
                    "type": "cover"
                })
                print(f"[DEBUG] 封面图片生成成功: {image_path}")
            except Exception as e:
                print(f"[DEBUG] 封面图片生成失败: {e}")
                images.append({
                    "page_num": 0,
                    "error": str(e),
                    "type": "cover"
                })

        pages = outline.get('pages', [])
        for page in pages:
            page_num = page.get('page_num')
            visual = page.get('visual', '')
            full_prompt = self._build_prompt(visual, char_description)
            try:
                image_path = self.generate_one(full_prompt, output_dir, folder_name)
                images.append({
                    "page_num": page_num,
                    "image_url": image_path,
                    "type": "content"
                })
            except Exception as e:
                images.append({
                    "page_num": page_num,
                    "error": str(e),
                    "type": "content"
                })

        back_cover_data = outline.get('back_cover', {})
        if back_cover_data.get('ending_image'):
            back_prompt = self._build_prompt(back_cover_data['ending_image'], char_description, is_cover=True)
            try:
                image_path = self.generate_one(back_prompt, output_dir, folder_name)
                images.append({
                    "page_num": -1,
                    "image_url": image_path,
                    "type": "back_cover"
                })
                print(f"[DEBUG] 封底图片生成成功: {image_path}")
            except Exception as e:
                print(f"[DEBUG] 封底图片生成失败: {e}")
                images.append({
                    "page_num": -1,
                    "error": str(e),
                    "type": "back_cover"
                })

        return {"images": images, "folder_name": folder_name}

    def _build_character_description(self, character):
        parts = []
        if character.get('name'):
            parts.append(f"角色：{character['name']}")
        if character.get('appearance'):
            parts.append(f"外貌：{character['appearance']}")
        if character.get('outfit'):
            parts.append(f"服装：{character['outfit']}")
        if character.get('personality'):
            parts.append(f"性格：{character['personality']}")
        return "，".join(parts) if parts else ""

    def _build_prompt(self, scene_description, character_description, is_cover=False):
        style = "儿童绘本风格，封面大图，视觉冲击力强" if is_cover else "儿童绘本风格"
        if character_description:
            return f"{character_description}，{scene_description}，{style}，角色在所有画面中保持一致"
        return scene_description + f"，{style}"