"""
图片后处理服务 - 解决中文乱码问题
"""
import os
from PIL import Image, ImageDraw, ImageFont

class ImageProcessor:
    def __init__(self):
        # 尝试加载系统字体，如果找不到则使用默认字体
        self.font_paths = [
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
        self.font = None
        self.font_size = 24
        
        # 尝试加载字体
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                try:
                    self.font = ImageFont.truetype(font_path, self.font_size)
                    print(f"[DEBUG] 使用字体: {font_path}")
                    break
                except Exception as e:
                    print(f"[DEBUG] 加载字体失败 {font_path}: {e}")
        
        if self.font is None:
            print("[DEBUG] 未找到系统字体，使用默认字体")
            self.font = ImageFont.load_default()

    def add_text_to_image(self, image_path, text, position=(10, 10), color=(0, 0, 0)):
        """
        在图片上添加文字
        
        Args:
            image_path: 图片文件路径
            text: 要添加的文字
            position: 文字位置 (x, y)
            color: 文字颜色 (R, G, B)
        
        Returns:
            str: 处理后的图片路径
        """
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 创建绘图对象
            draw = ImageDraw.Draw(image)
            
            # 添加文字
            draw.text(position, text, font=self.font, fill=color)
            
            # 保存图片
            processed_path = image_path.replace('.png', '_processed.png')
            image.save(processed_path)
            
            print(f"[DEBUG] 文字添加完成: {processed_path}")
            return processed_path
            
        except Exception as e:
            print(f"[DEBUG] 图片文字处理失败: {e}")
            return image_path  # 如果失败，返回原图路径

    def process_all_images(self, images_info, output_dir):
        """
        批量处理图片，添加文字
        
        Args:
            images_info: 图片信息列表
            output_dir: 输出目录
        
        Returns:
            list: 处理后的图片信息
        """
        processed_images = []
        
        for img_info in images_info:
            image_path = img_info.get('local_path')
            if image_path and os.path.exists(image_path):
                # 根据图片类型添加不同的文字
                text = self._get_text_for_image(img_info)
                if text:
                    # 根据图片类型设置不同的位置
                    position = self._get_position_for_image(img_info)
                    processed_path = self.add_text_to_image(image_path, text, position)
                    img_info['processed_path'] = processed_path
                else:
                    img_info['processed_path'] = image_path
            
            processed_images.append(img_info)
        
        return processed_images

    def _get_text_for_image(self, img_info):
        """根据图片类型返回要添加的文字"""
        img_type = img_info.get('type', '')
        
        if img_type == 'cover':
            return "封面"
        elif img_type == 'back_cover':
            return "封底"
        elif img_type == 'character_ref':
            return "角色设定图"
        elif img_type == 'content':
            page_num = img_info.get('page_num', 0)
            if page_num > 0:
                return f"第{page_num}页"
        
        return ""

    def _get_position_for_image(self, img_info):
        """根据图片类型返回文字位置"""
        img_type = img_info.get('type', '')
        
        # 默认居中底部位置
        if img_type in ['cover', 'back_cover', 'content']:
            return (20, 20)  # 左上角位置，与其他图片一致
        elif img_type == 'character_ref':
            return (20, 20)  # 角色设定图也使用相同位置
        
        return (20, 20)  # 默认位置

# 单例实例
image_processor = ImageProcessor()