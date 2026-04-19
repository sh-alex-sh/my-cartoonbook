"""
图片生成服务
"""
import requests
import os
import uuid
import base64
import time
from config import IMAGE_API_BASE, IMAGE_API_KEY, IMAGE_MODEL_ID

class ImageGenerator:
    def __init__(self):
        self.api_base = IMAGE_API_BASE
        self.api_key = IMAGE_API_KEY
        self.model_id = IMAGE_MODEL_ID

    def _get_output_dir(self, task_id, original_name):
        safe_name = ''.join(c for c in original_name if c.isalnum() or c in (' ', '_')).rstrip()
        folder_name = f"{safe_name}_{task_id[:8]}"
        output_dir = os.path.join("outputs", folder_name, "images")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir, folder_name

    def _get_headers(self):
        """构造请求头，包含认证信息"""
        return {
            "Content-Type": "application/json"
        }

    def generate_one(self, scene_description, output_dir, folder_name, ref_image_path=None):
        """
        生成单张图片。
        注意：这是一个示例实现，你需要根据你的新API文档来调整 payload 结构。
        """
        # 假设新API的端点是 /v1/images/generations
        endpoint = f"/v1beta/models/{self.model_id}:generateContent" 
        full_url = f"{self.api_base}{endpoint}?key={self.api_key}"
        
        print(f"[DEBUG] 完整请求URL: {full_url}")

        # 这是一个通用的 payload 结构，请根据你的新API文档进行修改
        payload = {
            "contents": [{
                "parts": [{
                    "text": scene_description
                }]
            }]
        }

        if ref_image_path and os.path.exists(ref_image_path):
            # 这里需要根据新API的文档来处理参考图
            # 可能是上传图片获取URL，也可能是直接发送base64
            print(f"[DEBUG] 使用参考图: {ref_image_path} (注意: 当前未实现参考图逻辑)")
            # payload['image_url'] = ref_image_path # 示例

        print(f"[DEBUG] 开始生成图片，prompt: {scene_description[:80]}...")
        
        try:
            response = requests.post(full_url, headers=self._get_headers(), json=payload, timeout=60)
            response.raise_for_status() # 如果状态码不是 2xx，则抛出异常
            
            result = response.json()
            print(f"[DEBUG] 生成请求响应: {response.status_code} - {str(result)[:200]}")

            # 解析内联的 base64 数据
            parts = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])
            base64_data = None
            for part in parts:
                if 'inlineData' in part:
                    base64_data = part['inlineData'].get('data')
                    break
            
            if not base64_data:
                print(f"[DEBUG] 完整API响应: {result}")
                raise Exception("API响应中未找到图片 base64 数据")

            return self._save_base64_image(base64_data, str(uuid.uuid4()), output_dir, folder_name)

        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] API 请求失败: {e}")
            if e.response:
                print(f"[DEBUG] 错误响应: {e.response.text}")
            raise Exception(f"图片生成请求失败: {e}")


    def _save_base64_image(self, base64_data, generate_uuid, output_dir, folder_name):
        """将 base64 编码的字符串解码并保存为图片文件"""
        try:
            image_data = base64.b64decode(base64_data)
            filename = f"{generate_uuid}.png"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            print(f"[DEBUG] 图片保存到: {filepath}")
            return f"/api/image/{folder_name}/{filename}"
        except Exception as e:
            print(f"[DEBUG] 保存 base64 图片失败: {e}")
            raise Exception(f"保存 base64 图片失败: {e}")

    def _build_character_prompt(self, character):
        name = character.get('name', '')
        appearance = character.get('appearance', '')
        outfit = character.get('outfit', '')
        personality = character.get('personality', '')

        prompt_parts = []
        if name:
            prompt_parts.append(f"角色名称: {name}")
        if appearance:
            prompt_parts.append(f"外貌特征: {appearance}")
        if outfit:
            prompt_parts.append(f"服装配饰: {outfit}")
        if personality:
            prompt_parts.append(f"性格特点: {personality}")

        base_prompt = "，".join(prompt_parts) if prompt_parts else ""

        ref_prompt = f"""{base_prompt}

请画出这个角色的完整设定图，展示以下内容：

【全身姿势】
- 站立姿势（正面展示整体外观）
- 挥手打招呼
- 行走姿势
- 坐下/休息姿势

【面部表情】
- 开心/微笑
- 好奇/疑问
- 惊讶/惊叹
- 坚定/认真

【关键特征标注】
- 发型样式和颜色
- 眼睛形状和眼神
- 服装细节和颜色
- 配饰（如有）

儿童绘本风格，所有姿势和表情保持角色一致性，背景简单留白，特征清晰可见"""
        return ref_prompt

    def generate_all(self, outline, task_id, original_name):
        character = outline.get('character', {})
        char_description = self._build_character_description(character)
        char_name = character.get('name', '') if character else ''
        output_dir, folder_name = self._get_output_dir(task_id, original_name)

        images = []

        print(f"[DEBUG] === 开始角色一致性优化流程 ===")
        print(f"[DEBUG] 1. 先生成角色设定参考图...")
        char_ref_local = None
        char_ref_api_path = None
        try:
            ref_prompt = self._build_character_prompt(character)
            char_ref_api_path = self.generate_one(ref_prompt, output_dir, folder_name)
            char_ref_filename = os.path.basename(char_ref_api_path)
            char_ref_local = os.path.join(output_dir, char_ref_filename)
            print(f"[DEBUG] 角色设定图生成成功: {char_ref_api_path}")
            print(f"[DEBUG] 角色设定图本地路径: {char_ref_local}")
        except Exception as e:
            print(f"[DEBUG] 角色设定图生成失败（将继续生成，但角色可能不一致）: {e}")

        images.append({
            "page_num": -2,
            "image_url": char_ref_api_path,
            "type": "character_ref"
        })

        print(f"[DEBUG] 2. 生成封面图片（使用角色设定图参考）...")
        cover_data = outline.get('cover', {})
        if cover_data.get('visual_description'):
            cover_prompt = self._build_page_prompt(cover_data['visual_description'], char_description, char_name, "封面")
            try:
                image_path = self.generate_one(cover_prompt, output_dir, folder_name, char_ref_local)
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

        print(f"[DEBUG] 3. 生成内容页图片（共{len(outline.get('pages', []))}页，使用角色设定图参考）...")
        pages = outline.get('pages', [])
        for page in pages:
            page_num = page.get('page_num')
            visual = page.get('visual', '')
            full_prompt = self._build_page_prompt(visual, char_description, char_name, f"第{page_num}页")
            try:
                image_path = self.generate_one(full_prompt, output_dir, folder_name, char_ref_local)
                images.append({
                    "page_num": page_num,
                    "image_url": image_path,
                    "type": "content"
                })
                print(f"[DEBUG] 第{page_num}页图片生成成功: {image_path}")
            except Exception as e:
                print(f"[DEBUG] 第{page_num}页图片生成失败: {e}")
                images.append({
                    "page_num": page_num,
                    "error": str(e),
                    "type": "content"
                })

        print(f"[DEBUG] 4. 生成封底图片（使用角色设定图参考）...")
        back_cover_data = outline.get('back_cover', {})
        if back_cover_data.get('ending_image'):
            back_prompt = self._build_page_prompt(back_cover_data['ending_image'], char_description, char_name, "封底")
            try:
                image_path = self.generate_one(back_prompt, output_dir, folder_name, char_ref_local)
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

        print(f"[DEBUG] === 图片生成完成 ===")
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

    def _build_page_prompt(self, scene_description, character_description, char_name, page_label=""):
        base = f"{character_description}，" if character_description else ""
        return f"""{base}{scene_description}，{page_label}，儿童绘本风格

【角色一致性强制要求 - 必须严格遵守】
- 角色名称：{char_name}
- 角色外貌特征：{character_description}
- 保持相同：脸型、眼睛颜色、发型、服装细节
- 只可改变：姿势、表情、与场景的互动
- 画风统一，色彩协调

【文字渲染强制要求 - 必须严格遵守】
- 如果图片中需要出现任何文字，必须使用支持中文的、清晰的黑体字。
- 确保所有中文字符都完整显示，不能出现乱码或方框。"""
