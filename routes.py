"""
Flask 路由
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import urllib.parse

api = Blueprint('api', __name__)

task_files = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'docx', 'txt']


def get_safe_folder_name(original_name, task_id):
    safe_name = original_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    return f"{safe_name}_{task_id[:8]}"


@api.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.txt']:
        return jsonify({'error': '不支持的文件类型'}), 400
    task_id = str(uuid.uuid4())
    filename = f"{task_id}{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    safe_filename = os.path.splitext(secure_filename(file.filename))[0]
    if not safe_filename:
        safe_filename = "story"
    task_files[task_id] = {
        'filepath': filepath,
        'original_name': safe_filename
    }

    return jsonify({'task_id': task_id, 'filepath': filepath, 'original_name': safe_filename})


@api.route('/parse', methods=['POST'])
def parse_document():
    from services.pdf_parser import DocumentParser
    data = request.json
    filepath = data.get('filepath')
    print(f"收到 filepath: {repr(filepath)}")
    if not filepath:
        return jsonify({'error': '文件路径为空'}), 400
    filepath = os.path.abspath(filepath)
    print(f"实际路径: {filepath}")
    if not os.path.exists(filepath):
        return jsonify({'error': f'文件不存在: {filepath}'}), 400
    try:
        parser = DocumentParser()
        content = parser.extract_text(filepath)
        return jsonify({'content': content})
    except Exception as e:
        import sys
        import traceback
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()
        return jsonify({'error': f'解析失败: {str(e)}', 'details': traceback.format_exc()}), 500


@api.route('/outline', methods=['POST'])
def generate_outline():
    from services.outline_generator import OutlineGenerator
    data = request.json
    outline = OutlineGenerator().generate(data.get('content'), data.get('num_pages', 10))
    return jsonify({'outline': outline})


@api.route('/images', methods=['POST'])
def generate_images():
    from services.image_generator import ImageGenerator
    data = request.json
    task_id = data.get('task_id')
    original_name = data.get('original_name', 'story')

    print(f"[DEBUG] /api/images called - task_id: {task_id}, original_name: {original_name}")
    print(f"[DEBUG] task_files keys: {list(task_files.keys())}")
    print(f"[DEBUG] task_files[{task_id}]: {task_files.get(task_id)}")

    task_info = task_files.get(task_id, {})
    original_name = task_info.get('original_name', original_name)

    print(f"[DEBUG] Using original_name: {original_name}")

    try:
        result = ImageGenerator().generate_all(data.get('outline'), task_id, original_name)
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[DEBUG] /api/images error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api.route('/image/<path:folder>/<path:filename>', methods=['GET'])
def get_image(folder, filename):
    folder_decoded = urllib.parse.unquote(folder)
    filename_decoded = urllib.parse.unquote(filename)
    filepath = os.path.join('outputs', folder_decoded, 'images', filename_decoded)
    print(f"[DEBUG] 查找图片: {filepath}")
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    return jsonify({'error': '图片不存在'}), 404


@api.route('/export', methods=['POST'])
def export_pdf():
    from services.pdf_exporter import PDFExporter
    data = request.json
    task_id = data.get('task_id')
    original_name = data.get('original_name', 'story')

    task_info = task_files.get(task_id, {})
    original_name = task_info.get('original_name', original_name)

    print(f"[DEBUG] 导出 PDF - task_id: {task_id}, original_name: {original_name}")

    path = PDFExporter().export(data.get('outline'), data.get('images'), task_id, original_name)
    folder_name = os.path.basename(os.path.dirname(path))
    download_url = f'/api/download/{urllib.parse.quote(folder_name)}/{urllib.parse.quote(original_name)}.pdf'
    print(f"[DEBUG] PDF 路径: {path}, 下载URL: {download_url}")
    return jsonify({'output_path': path, 'download_url': download_url})


@api.route('/download/<path:folder>/<path:filename>', methods=['GET'])
def download_pdf(folder, filename):
    folder_decoded = urllib.parse.unquote(folder)
    filename_decoded = urllib.parse.unquote(filename)
    filepath = os.path.join('outputs', folder_decoded, filename_decoded)
    print(f"[DEBUG] 下载 PDF: {filepath}")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename_decoded)
    return jsonify({'error': '文件不存在'}), 404