"""
AI 绘本生成器 - Flask 主程序
"""
from flask import Flask, render_template, jsonify, request
from routes import api
import os

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['OUTPUT_FOLDER'] = 'outputs'
    app.register_blueprint(api, url_prefix='/api')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        err_msg = str(e)
        err_trace = traceback.format_exc()
        if request.is_json:
            return jsonify({'error': err_msg, 'details': err_trace}), 500
        return jsonify({'error': err_msg, 'details': err_trace}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)