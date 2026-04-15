"""
Flask 路由
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import uuid

api = Blueprint('api', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


@api.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    if file and allowed_file(file.filename):
        task_id = str(uuid.uuid4())
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{task_id}_{secure_filename(file.filename)}")
        file.save(filepath)
        return jsonify({'task_id': task_id, 'filepath': filepath})
    return jsonify({'error': '不支持的文件类型'}), 400


@api.route('/parse', methods=['POST'])
def parse_pdf():
    from services.pdf_parser import PDFParser
    data = request.json
    filepath = data.get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 400
    content = PDFParser().extract_text(filepath)
    return jsonify({'content': content})


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
    result = ImageGenerator().generate_all(data.get('outline'))
    return jsonify(result)


@api.route('/image/<path:filename>', methods=['GET'])
def get_image(filename):
    filepath = os.path.join('outputs', 'images', filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    return jsonify({'error': '图片不存在'}), 404


@api.route('/export', methods=['POST'])
def export_pdf():
    from services.pdf_exporter import PDFExporter
    data = request.json
    path = PDFExporter().export(data.get('outline'), data.get('images'), data.get('task_id'))
    return jsonify({'output_path': path, 'download_url': f'/api/download/{data.get("task_id")}'})


@api.route('/download/<task_id>', methods=['GET'])
def download_pdf(task_id):
    filepath = os.path.join(current_app.config['OUTPUT_FOLDER'], f"storybook_{task_id}.pdf")
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404