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
        self.output_dir = "outputs/images"
        os.makedirs(self.output_dir, exist_ok=True)

    def make_signature(self, uri, timestamp, signature_nonce):
        content = f"{uri}&{timestamp}&{signature_nonce}"
        digest = hmac.new(self.secret_key.encode(), content.encode(), hashlib.sha1).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    def make_auth_params(self, uri):
        timestamp = str(int(time.time() * 1000))
        signature_nonce = str(uuid.uuid4())
        return {
            "AccessKey": self.access_key,
            "Signature": self.make_signature(uri, timestamp, signature_nonce),
            "Timestamp": timestamp,
            "SignatureNonce": signature_nonce
        }

    def generate_one(self, scene_description):
        uri = "/api/generate/webui/text2img/ultra"
        auth_params = self.make_auth_params(uri)
        payload = {
            "templateUuid": "5d7e67009b344550bc1aa6ccbfa1d7f4",
            "generateParams": {
                "prompt": scene_description + "，儿童绘本风格",
                "promptMagic": 1,
                "aspectRatio": "square",
                "imgCount": 1
            }
        }
        response = requests.post(f"{self.api_base}{uri}", headers={"Content-Type": "application/json"}, params=auth_params, json=payload, timeout=30)
        result = response.json()
        generate_uuid = result.get("data", {}).get("generateUuid")
        return self._wait_for_image(generate_uuid)

    def _wait_for_image(self, generate_uuid, max_retries=60):
        uri = "/api/generate/webui/status"
        for _ in range(max_retries):
            auth_params = self.make_auth_params(uri)
            response = requests.post(f"{self.api_base}{uri}", params=auth_params, json={"generateUuid": generate_uuid}, timeout=30)
            result = response.json()
            data = result.get("data")
            if data is None:
                time.sleep(3)
                continue
            status = data.get("generateStatus")
            if status == 6 or (status == 5 and data.get("percentCompleted") == 1.0):
                images = data.get("images")
                if images and len(images) > 0:
                    image_url = images[0].get("imageUrl")
                    if image_url:
                        local_path = self._download_image(image_url, generate_uuid)
                        return local_path
            time.sleep(3)
        raise Exception("生成超时")

    def _download_image(self, image_url, generate_uuid):
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                filename = f"{generate_uuid}.png"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return f"/api/image/{filename}"
        except Exception:
            pass
        return image_url

    def generate_all(self, outline):
        pages = outline.get('pages', [])
        images = []
        for page in pages:
            page_num = page.get('page_num')
            visual = page.get('visual', '')
            try:
                image_path = self.generate_one(visual)
                images.append({
                    "page_num": page_num,
                    "image_url": image_path
                })
            except Exception as e:
                images.append({
                    "page_num": page_num,
                    "error": str(e)
                })
        return {"images": images}