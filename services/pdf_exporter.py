import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))


def get_folder_name_by_time():
    """
    生成统一的输出文件夹名称
    格式：年月日时 + 顺序编号，例如：20260419131、20260419132
    """
    # 获取当前时间
    now = datetime.datetime.now()
    time_prefix = now.strftime("%Y%m%d%H")  # 格式：2026041913
    
    # 检查 outputs 目录下已有的文件夹
    base_output_dir = "outputs"
    os.makedirs(base_output_dir, exist_ok=True)
    
    # 获取所有以时间前缀开头的文件夹
    existing_folders = []
    if os.path.exists(base_output_dir):
        for item in os.listdir(base_output_dir):
            if os.path.isdir(os.path.join(base_output_dir, item)) and item.startswith(time_prefix):
                existing_folders.append(item)
    
    # 确定下一个序号
    if existing_folders:
        # 找到最大的序号
        max_num = 0
        for folder in existing_folders:
            if len(folder) > len(time_prefix):
                try:
                    num = int(folder[len(time_prefix):])
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        folder_name = f"{time_prefix}{max_num}"
    else:
        folder_name = f"{time_prefix}1"
    
    return folder_name


class PDFExporter:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, outline, images, task_id, original_name):
        # 使用与图片生成模块相同的文件夹命名逻辑
        folder_name = get_folder_name_by_time()
        folder_path = os.path.join(self.output_dir, folder_name)
        
        print(f"[DEBUG] PDF 导出文件夹: {folder_path}")
        
        images_folder = os.path.join(folder_path, "images")
        output_path = os.path.join(folder_path, f"{original_name}.pdf")

        # 确保目录存在
        os.makedirs(images_folder, exist_ok=True)

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        image_map = {}
        if images:
            for img in images:
                page_num = img.get("page_num")
                if page_num is not None:
                    image_map[page_num] = img

        # 绘制封面
        cover = outline.get("cover", {})
        title = cover.get("title", "AI 绘本")
        subtitle = cover.get("subtitle", "")

        cover_img = image_map.get(0)
        if cover_img and cover_img.get("image_url"):
            img_url = cover_img.get("image_url", "")
            img_filename = os.path.basename(img_url)
            img_path = os.path.join(images_folder, img_filename)
            print(f"[DEBUG] 绘制封面图片: {img_path}")
            if os.path.exists(img_path):
                try:
                    img_draw_height = height * 0.7
                    c.drawImage(img_path, 0, height - img_draw_height, width=width, height=img_draw_height, preserveAspectRatio=True)
                except Exception as e:
                    print(f"[DEBUG] 绘制封面图片失败: {e}")

        c.setFont('SimHei', 36)
        c.drawCentredString(width / 2, height * 0.25, title)

        if subtitle:
            c.setFont('SimSun', 16)
            c.drawCentredString(width / 2, height * 0.18, subtitle)

        c.showPage()

        # 绘制内容页
        pages = outline.get("pages", [])
        for page in pages:
            page_num = page.get("page_num", 0)
            content = page.get("content", "")

            img_data = image_map.get(page_num)
            if img_data and img_data.get("image_url"):
                img_url = img_data.get("image_url", "")
                img_filename = os.path.basename(img_url)
                img_path = os.path.join(images_folder, img_filename)
                print(f"[DEBUG] 绘制第{page_num}页图片: {img_path}")
                if os.path.exists(img_path):
                    img_draw_height = height * 0.65
                    try:
                        c.drawImage(img_path, 0, height - img_draw_height, width=width, height=img_draw_height, preserveAspectRatio=True)
                    except Exception as e:
                        print(f"[DEBUG] 绘制第{page_num}页图片失败: {e}")

            if content:
                c.setFont('SimHei', 16)
                text_y = height * 0.28
                lines = self._wrap_text(content, width - 4*cm, c)
                for line in lines[:3]:
                    c.drawCentredString(width / 2, text_y, line)
                    text_y -= 24

            c.showPage()

        # 绘制封底
        back_cover = outline.get("back_cover", {})
        final_line = back_cover.get("final_line", "")

        back_img = image_map.get(-1)
        if back_img and back_img.get("image_url"):
            img_url = back_img.get("image_url", "")
            img_filename = os.path.basename(img_url)
            img_path = os.path.join(images_folder, img_filename)
            print(f"[DEBUG] 绘制封底图片: {img_path}")
            if os.path.exists(img_path):
                try:
                    img_draw_height = height * 0.65
                    c.drawImage(img_path, 0, height - img_draw_height, width=width, height=img_draw_height, preserveAspectRatio=True)
                except Exception as e:
                    print(f"[DEBUG] 绘制封底图片失败: {e}")

        if final_line:
            c.setFont('SimHei', 16)
            c.drawCentredString(width / 2, height * 0.28, final_line)

        c.showPage()
        c.save()
        
        print(f"[DEBUG] PDF 导出完成: {output_path}")
        return output_path

    def _wrap_text(self, text, max_width, canvas):
        words = list(text)
        lines = []
        current_line = ""
        for char in words:
            test_line = current_line + char
            if canvas.stringWidth(test_line, 'SimSun', 14) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines