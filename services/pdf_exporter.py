"""
PDF 导出服务
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))


def get_safe_folder_name(base_name):
    return base_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')


class PDFExporter:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, outline, images, task_id, original_name):
        folder_name = get_safe_folder_name(f"{original_name}_{task_id[:8]}")
        folder_path = os.path.join(self.output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        images_folder = os.path.join(folder_path, "images")
        os.makedirs(images_folder, exist_ok=True)

        output_path = os.path.join(folder_path, f"{original_name}.pdf")

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        image_map = {}
        if images:
            for img in images:
                page_num = img.get("page_num")
                if page_num is not None:
                    image_map[page_num] = img

        cover = outline.get("cover", {})
        title = cover.get("title", "AI 绘本")
        subtitle = cover.get("subtitle", "")

        cover_img = image_map.get(0)
        if cover_img and cover_img.get("image_url") and not cover_img.get("image_url", "").startswith("http"):
            img_url = cover_img.get("image_url", "")
            img_filename = os.path.basename(img_url)
            img_path = os.path.join(images_folder, img_filename)
            print(f"[DEBUG] 绘制封面图片: {img_path}")
            if os.path.exists(img_path):
                try:
                    img_draw_height = height * 0.7
                    c.drawImage(img_path, 0, height - img_draw_height, width=width, height=img_draw_height, preserveAspectRatio=False)
                except Exception as e:
                    print(f"[DEBUG] 绘制封面图片失败: {e}")

        c.setFont('SimHei', 36)
        c.drawCentredString(width / 2, height * 0.25, title)

        if subtitle:
            c.setFont('SimSun', 16)
            c.drawCentredString(width / 2, height * 0.18, subtitle)

        c.showPage()

        pages = outline.get("pages", [])
        for page in pages:
            page_num = page.get("page_num", 0)
            content = page.get("content", "")
            visual = page.get("visual", "")

            img_data = image_map.get(page_num)
            if img_data and img_data.get("image_url") and not img_data.get("image_url", "").startswith("http"):
                img_url = img_data.get("image_url", "")
                img_filename = os.path.basename(img_url)
                img_path = os.path.join(images_folder, img_filename)
                print(f"[DEBUG] 查找 PDF 图片 page_{page_num}: {img_path}")
                if os.path.exists(img_path):
                    img_width = width * 0.85
                    img_height = height * 0.5
                    x = (width - img_width) / 2
                    y = height * 0.42
                    try:
                        c.drawImage(img_path, x, y, width=img_width, height=img_height, preserveAspectRatio=True)
                    except Exception as e:
                        print(f"[DEBUG] 绘制图片失败: {e}")

            if content:
                c.setFont('SimSun', 14)
                text_y = height * 0.35
                lines = self._wrap_text(content, width - 4*cm, c)
                for line in lines[:3]:
                    c.drawString(2*cm, text_y, line)
                    text_y -= 20

            c.showPage()

        back_cover = outline.get("back_cover", {})
        final_line = back_cover.get("final_line", "")

        back_img = image_map.get(-1)
        if back_img and back_img.get("image_url") and not back_img.get("image_url", "").startswith("http"):
            img_url = back_img.get("image_url", "")
            img_filename = os.path.basename(img_url)
            img_path = os.path.join(images_folder, img_filename)
            print(f"[DEBUG] 绘制封底图片: {img_path}")
            if os.path.exists(img_path):
                try:
                    img_draw_height = height * 0.7
                    c.drawImage(img_path, 0, height - img_draw_height, width=width, height=img_draw_height, preserveAspectRatio=False)
                except Exception as e:
                    print(f"[DEBUG] 绘制封底图片失败: {e}")

        if final_line:
            c.setFont('SimSun', 16)
            c.drawCentredString(width / 2, height * 0.15, final_line)

        c.showPage()
        c.save()
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