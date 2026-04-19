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

【重要】页数分配：封面1页 + 内容页（{content_pages}页） + 封底1页 = 共{num_pages}页

【原文】
{content}

【设计要求】

一、角色设计（极其重要！）
请详细描述故事中的主要角色特征，这些描述将用于保证每页图片的角色一致性：
- 角色名称：
- 外貌特征：（具体描述，如：一只4岁的小鹿，深棕色皮毛，白色斑点，大眼睛，长睫毛，善良的表情）
- 服装/配饰：（如果有的话）
- 性格特点：（简述）

二、封面设计
- 主标题：一句话抓住孩子的注意力（不是概括，是悬念或惊喜）
- 副标题/引子：1-2句话，像魔法咒语一样吸引人
- 视觉关键词：3-5个核心视觉元素
- 封面视觉描述：（包含角色在内的具体画面描述）

三、封底设计
- 结尾画面：根据故事结局生成相应的视觉画面
- 情绪落点：根据故事实际选择最贴切的感受词：开心/惊讶/好奇/温暖/感动/安心/治愈/兴奋/满足/回味 等，不要都用"安心"
- 最后一句话：故事内容的总结，要具体概括故事发生了什么，不要只写情绪感受

四、正文页面结构（每页包含）
1. 叙事目标：这页要让孩子感受什么/经历什么（不是学到什么）
2. 关键内容：1-2句话，孩子能听懂的口吻
3. 视觉画面：具体的场景描述，包括颜色基调、主体、氛围
4. 布局结构：跨页/单页/大特写，以及为什么这样设计

【输出格式】
必须输出有效的JSON，格式如下：
{{
    "character": {{
        "name": "角色名称",
        "appearance": "外貌特征描述",
        "outfit": "服装/配饰描述",
        "personality": "性格特点"
    }},
    "cover": {{
        "title": "主标题",
        "subtitle": "副标题/引子",
        "visual_keywords": ["关键词1", "关键词2", "关键词3"],
        "visual_description": "封面视觉描述（必须包含角色）"
    }},
    "back_cover": {{
        "ending_image": "封底画面描述（包含角色）",
        "emotion": "情绪落点",
        "final_line": "最后一句话"
    }},
    "pages": [
        {{
            "page_num": 1,
            "narrative_goal": "叙事目标",
            "content": "关键内容（1-2句话）",
            "visual": "视觉画面描述（必须包含角色：描述角色在这一页的动作、表情和位置）",
            "layout": "布局结构"
        }}
    ]
}}

【重要提醒】
- 叙事目标写"感受什么"，不要写"学到什么"
- 关键内容是孩子能听懂的话，不是解释性语言
- 视觉画面要具体：什么颜色、什么东西、什么氛围
- 每页的 visual 描述中必须明确描述角色的动作、表情和位置
- 文字和画面的关系是"画外有话，话外有画"
- 不要在正文中使用"成长"、"友谊"、"道理"、"教育"这类词
- 不要说"不仅仅是"、"更重要的是"、"其实"这类转折词
- 不要用"告诉我们"、"让我们懂得"这类说教句式
- 角色外貌必须在每页描述中保持一致（使用相同的角色描述词）"""


class OutlineGenerator:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.user_prompt_template = USER_PROMPT_TEMPLATE
        self.api_base = DEEPSEEK_API_BASE
        self.api_key = DEEPSEEK_API_KEY

    def generate(self, content, num_pages=10):
        content_pages = max(1, num_pages - 2)
        user_prompt = self.user_prompt_template.format(
            content=content,
            num_pages=num_pages,
            content_pages=content_pages
        )

        print(f"[DEBUG] API Key present: {bool(self.api_key)}")
        print(f"[DEBUG] API Base: {self.api_base}")

        if not self.api_key:
            raise Exception("未配置 DeepSeek API 密钥，请检查 .env 文件中的 DEEPSEEK_API_KEY")

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
            print(f"[DEBUG] Response text length: {len(response.text)}")
            print(f"[DEBUG] Response text (first 1000 chars): {response.text[:1000]}")

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0]["message"]["content"]
                text = text.strip()
                
                # 更智能地提取 JSON 内容
                if "```json" in text:
                    # 提取 ```json 块中的内容
                    start_idx = text.find("```json") + 7
                    end_idx = text.find("```", start_idx)
                    if end_idx != -1:
                        text = text[start_idx:end_idx].strip()
                elif text.startswith("```"):
                    # 提取普通 ``` 块中的内容
                    start_idx = text.find("```") + 3
                    end_idx = text.find("```", start_idx)
                    if end_idx != -1:
                        text = text[start_idx:end_idx].strip()
                
                print(f"[DEBUG] Parsed text length: {len(text)}")
                print(f"[DEBUG] Parsed text (first 500 chars): {text[:500]}")
                
                # 尝试解析 JSON
                try:
                    outline = json.loads(text)
                    return outline
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] JSON 解析失败: {e}")
                    print(f"[DEBUG] 尝试解析的文本: {text}")
                    # 如果解析失败，尝试修复常见的 JSON 格式问题
                    text = self._fix_json_format(text)
                    try:
                        outline = json.loads(text)
                        print("[DEBUG] 修复后的 JSON 解析成功")
                        return outline
                    except json.JSONDecodeError as e2:
                        print(f"[DEBUG] 修复后仍然失败: {e2}")
                        raise Exception(f"DeepSeek API 返回的 JSON 格式错误: {str(e2)}")
            else:
                error_msg = result.get("error", {}).get("message", str(result))
                print(f"[DEBUG] DeepSeek API error: {error_msg}")
                raise Exception(f"DeepSeek API 错误: {error_msg}")

        except requests.exceptions.Timeout:
            print("[DEBUG] Request timed out")
            raise Exception("DeepSeek API 请求超时，请重试")
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON decode error: {e}")
            print(f"[DEBUG] Raw response text: {response.text}")
            raise Exception(f"DeepSeek API 返回格式错误: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Error calling DeepSeek API: {e}")
            raise Exception(f"调用 DeepSeek API 失败: {str(e)}")

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