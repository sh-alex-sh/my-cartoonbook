"""
PDF 文档解析服务
"""
import PyPDF2


class PDFParser:
    def extract_text(self, filepath):
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def extract_pages(self, filepath):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)