"""
PDF 导出服务
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import requests
import os


class PDFExporter:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export(self, outline, images, task_id):
        output_path = os.path.join(self.output_dir, f"storybook_{task_id}.pdf")
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width / 2, height / 2, outline.get("title", "AI 绘本"))
        c.showPage()

        for page in outline.get("pages", []):
            c.drawString(2*cm, height - 2*cm, page.get("text", ""))
            c.showPage()

        c.save()
        return output_path