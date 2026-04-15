"""
绘本大纲生成服务
"""
import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE

SYSTEM_PROMPT = """你是一位世界级儿童绘本设计师，曾获多项国际绘本大奖。
你的设计理念：
- 用孩子的眼睛看世界，拒绝成人化的说教
- 画面即故事，每一个细节都有意义
- 文字要像孩子说话，而不是在教孩子说话
- 节奏感比完整性更重要
- 留白是给予孩子想象的空间

你的作品特点：
- 拒绝"不仅仅是X，而是Y"这类成人思辨句式
- 拒绝"告诉我们/让我们懂得"这类说教口吻
- 拒绝过度解释和情感标签
- 封面要有视觉冲击力，第一眼就抓住注意力
- 封底要有仪式感，像一个温暖的拥抱"""

USER_PROMPT_TEMPLATE = """请将以下故事改编成{num_pages}页的儿童绘本。

【原文】
{content}

【设计要求】

一、封面设计
- 主标题：一句话抓住孩子的注意力（不是概括，是悬念或惊喜）
- 副标题/引子：1-2句话，像魔法咒语一样吸引人
- 视觉关键词：3-5个核心视觉元素

二、封底设计
- 结尾画面：根据最后一句话的总结词生成相应的视觉画面
- 情绪落点：用孩子的感受词（如"开心"、"好奇"、"安心"），不要用"成长"、"友谊"这类成人词
- 最后一句话：总结整本书

三、正文页面结构（每页包含）
1. 叙事目标：这页要让孩子感受什么/经历什么（不是学到什么）
2. 关键内容：1-2句话，孩子能听懂的口吻
3. 视觉画面：具体的场景描述，包括颜色基调、主体、氛围
4. 布局结构：跨页/单页/大特写，以及为什么这样设计

【输出格式】
必须输出有效的JSON，格式如下：
{{
    "cover": {{
        "title": "主标题",
        "subtitle": "副标题/引子",
        "visual_keywords": ["关键词1", "关键词2", "关键词3"],
        "visual_description": "封面视觉描述"
    }},
    "back_cover": {{
        "ending_image": "封底画面描述",
        "emotion": "情绪落点",
        "final_line": "最后一句话"
    }},
    "pages": [
        {{
            "page_num": 1,
            "narrative_goal": "叙事目标",
            "content": "关键内容（1-2句话）",
            "visual": "视觉画面描述",
            "layout": "布局结构"
        }}
    ]
}}

【重要提醒】
- 叙事目标写"感受什么"，不要写"学到什么"
- 关键内容是孩子能听懂的话，不是解释性语言
- 视觉画面要具体：什么颜色、什么东西、什么氛围
- 文字和画面的关系是"画外有话，话外有画"
- 不要在正文中使用"成长"、"友谊"、"道理"、"教育"这类词
- 不要说"不仅仅是"、"更重要的是"、"其实"这类转折词
- 不要用"告诉我们"、"让我们懂得"这类说教句式"""


class OutlineGenerator:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.user_prompt_template = USER_PROMPT_TEMPLATE
        self.api_base = DEEPSEEK_API_BASE
        self.api_key = DEEPSEEK_API_KEY

    def generate(self, content, num_pages=10):
        user_prompt = self.user_prompt_template.format(
            content=content,
            num_pages=num_pages
        )

        print(f"[DEBUG] API Key present: {bool(self.api_key)}")
        print(f"[DEBUG] API Base: {self.api_base}")

        if not self.api_key:
            print("[DEBUG] No API key, using sample")
            return self._generate_sample_outline(num_pages)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        try:
            print("[DEBUG] Calling DeepSeek API...")
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text[:500]}")

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0]["message"]["content"]
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                print(f"[DEBUG] Parsed text: {text[:200]}")
                outline = json.loads(text)
                return outline
            else:
                print(f"[DEBUG] DeepSeek API error: {result}")
                return self._generate_sample_outline(num_pages)

        except requests.exceptions.Timeout:
            print("[DEBUG] Request timed out")
            return self._generate_sample_outline(num_pages)
        except Exception as e:
            print(f"[DEBUG] Error calling DeepSeek API: {e}")
            return self._generate_sample_outline(num_pages)

    def _generate_sample_outline(self, num_pages):
        pages = []
        for i in range(num_pages):
            pages.append({
                "page_num": i + 1,
                "narrative_goal": "感受" + ["好奇", "惊喜", "温暖", "期待", "安心"][i % 5],
                "content": f"场景 {i+1} 的故事内容",
                "visual": f"温馨的 {['森林', '草原', '海边', '小镇', '山丘'][i % 5]} 场景",
                "layout": "跨页" if i % 2 == 0 else "单页"
            })

        return {
            "cover": {
                "title": "小兔子的奇妙旅程",
                "subtitle": "每一步都是冒险",
                "visual_keywords": ["小兔子", "森林", "彩色", "冒险"],
                "visual_description": "一只小兔子站在彩色森林入口，阳光从树叶间洒落"
            },
            "back_cover": {
                "ending_image": "小兔子在家门口，朋友们围绕身边",
                "emotion": "满足",
                "final_line": "今天真开心呀！"
            },
            "pages": pages
        }