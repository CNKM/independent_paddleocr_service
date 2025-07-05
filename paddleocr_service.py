# -*- coding: utf-8 -*-
"""
PaddleOCR 独立服务
提供高性能、多语言的 OCR 服务

支持特性:
- 多种输入格式 (文件、Base64、URL)
- 多语言识别
- 模型缓存和预加载
- 详细的错误处理和日志
- 性能监控
"""

import os
import sys
import json
import time
import logging
import tempfile
import uuid
import base64
import yaml
from datetime import datetime
from pathlib import Path
from threading import Lock
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import requests
import paddle
from paddleocr import PaddleOCR

# 设置模型目录环境变量
current_dir = Path(__file__).parent
model_dir = current_dir / 'models'
model_dir.mkdir(exist_ok=True)

# 设置 PaddleOCR 相关环境变量
os.environ['PADDLEOCR_MODEL_PATH'] = str(model_dir)
os.environ['PADDLE_OCR_MODEL_PATH'] = str(model_dir)
# 设置 PaddleX 模型路径（这是关键）
os.environ['PADDLEX_MODEL_PATH'] = str(model_dir)

logger = logging.getLogger(__name__)
logger.info(f"设置模型目录: {model_dir}")

# 配置日志，日志文件强制写入 logs 目录
LOG_DIR = current_dir / 'logs'
LOG_DIR.mkdir(exist_ok=True)
from logging.handlers import TimedRotatingFileHandler
LOG_FILE = LOG_DIR / 'paddleocr_service.log'
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
# 按天分割日志文件，保留30天
file_handler = TimedRotatingFileHandler(
    str(LOG_FILE), when='midnight', interval=1, backupCount=30, encoding='utf-8'
)
file_handler.suffix = "%Y-%m-%d.log"
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

class OCRServiceConfig:
    """服务配置类"""
    
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'debug': False,
                'max_content_length': 50 * 1024 * 1024  # 50MB
            },
            'ocr': {
                'default_lang': 'ch',
                'use_textline_orientation': True,
                'use_gpu': False,
                'max_image_size': 4096,
                'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            },
            'performance': {
                'preload_models': ['ch', 'en'],
                'max_batch_size': 10,
                'request_timeout': 60,
                'cleanup_temp_files': True
            },
            'logging': {
                'level': 'INFO',
                'max_log_size': 10 * 1024 * 1024,  # 10MB
                'backup_count': 5
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                self._deep_update(default_config, user_config)
        
        self.config = default_config
        logger.info(f"配置加载完成: {self.config}")
    
    def _deep_update(self, base_dict, update_dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

class OCRModelManager:
    """OCR 模型管理器"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.model_lock = Lock()
        self.stats = {
            'models_loaded': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': time.time()
        }
        
    def get_model(self, lang='ch', use_gpu=None):
        """获取 OCR 模型实例"""
        if use_gpu is None:
            use_gpu = self.config['ocr']['use_gpu']
            
        model_key = f"{lang}_{use_gpu}"
        
        with self.model_lock:
            if model_key not in self.models:
                logger.info(f"加载 OCR 模型: {model_key}")
                
                # 设置设备
                if use_gpu and paddle.device.is_compiled_with_cuda():
                    paddle.device.set_device('gpu')
                    logger.info("使用 GPU 加速")
                else:
                    paddle.device.set_device('cpu')
                    logger.info("使用 CPU 推理")
                
                # 创建模型
                model_dir = self.config['ocr'].get('model_dir', './models')
                # 转换为绝对路径
                if not os.path.isabs(model_dir):
                    model_dir = os.path.join(os.path.dirname(__file__), model_dir)
                # 确保模型目录存在
                os.makedirs(model_dir, exist_ok=True)
                logger.info(f"使用模型目录: {model_dir}")
                
                self.models[model_key] = PaddleOCR(
                    use_textline_orientation=self.config['ocr']['use_textline_orientation'],
                    lang=lang,
                    det_model_dir=None,  # 让 PaddleOCR 自动下载到指定目录
                    rec_model_dir=None,
                    cls_model_dir=None
                )
                
                self.stats['models_loaded'] += 1
                logger.info(f"OCR 模型加载完成: {model_key}")
        
        return self.models[model_key]
    
    def preload_models(self):
        """预加载模型"""
        preload_models = self.config['performance']['preload_models']
        logger.info(f"开始预加载模型: {preload_models}")
        
        for lang in preload_models:
            try:
                self.get_model(lang)
                logger.info(f"模型预加载成功: {lang}")
            except Exception as e:
                logger.error(f"模型预加载失败 {lang}: {e}")
        
        logger.info("模型预加载完成")
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            'loaded_models': list(self.models.keys()),
            'stats': self.stats
        }

class OCRService:
    """OCR 服务类"""
    
    def __init__(self, config):
        self.config = config
        self.model_manager = OCRModelManager(config)
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"临时目录: {self.temp_dir}")
        
    def process_image_file(self, file_path, lang='ch', use_gpu=None):
        """处理图像文件"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 检查文件格式
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.config['ocr']['supported_formats']:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 检查图像大小
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("无法读取图像文件")
            
            h, w = image.shape[:2]
            max_size = self.config['ocr']['max_image_size']
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_h, new_w = int(h * scale), int(w * scale)
                image = cv2.resize(image, (new_w, new_h))
                temp_path = os.path.join(self.temp_dir, f"resized_{uuid.uuid4().hex}.jpg")
                cv2.imwrite(temp_path, image)
                file_path = temp_path
            
            # 获取模型并进行识别
            model = self.model_manager.get_model(lang, use_gpu)
            result = model.predict(file_path)
            
            self.model_manager.stats['total_requests'] += 1
            
            if result and len(result) > 0:
                ocr_result = result[0]
                texts = ocr_result.get('rec_texts', [])
                scores = ocr_result.get('rec_scores', [])
                polys = ocr_result.get('rec_polys', [])
                
                formatted_result = {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'lang': lang,
                    'text': ' '.join(texts),
                    'word_count': len(texts),
                    'avg_confidence': sum(scores) / len(scores) if scores else 0,
                    'details': []
                }
                
                for i, (text, score) in enumerate(zip(texts, scores)):
                    bbox = polys[i].tolist() if i < len(polys) else []
                    formatted_result['details'].append({
                        'text': text,
                        'confidence': float(score),
                        'bbox': bbox
                    })
                
                self.model_manager.stats['successful_requests'] += 1
                return formatted_result
            else:
                self.model_manager.stats['successful_requests'] += 1
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'lang': lang,
                    'text': '',
                    'word_count': 0,
                    'avg_confidence': 0,
                    'details': [],
                    'message': '未识别到文字'
                }
                
        except Exception as e:
            import traceback
            self.model_manager.stats['failed_requests'] += 1
            logger.error(f"图像处理失败: {e}\n{traceback.format_exc()}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
    
    
    def process_url_image(self, image_url, lang='ch', use_gpu=None):
        """处理 URL 图像"""
        try:
            # 下载图像
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 保存临时文件
            temp_filename = f"{uuid.uuid4().hex}.jpg"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            # 处理图像
            result = self.process_image_file(temp_path, lang, use_gpu)
            
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
            
        except Exception as e:
            self.model_manager.stats['failed_requests'] += 1
            logger.error(f"URL 图像处理失败: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def process_batch_images(self, images, lang='ch', use_gpu=None):
        """批量处理图像"""
        max_batch_size = self.config['performance']['max_batch_size']
        if len(images) > max_batch_size:
            return {
                'success': False,
                'error': f'批量大小超过限制: {len(images)} > {max_batch_size}'
            }
        
        results = []
        for i, image_data in enumerate(images):
            logger.info(f"处理批量图像 {i+1}/{len(images)}")
            result = self.process_base64_image(image_data, lang, use_gpu)
            results.append(result)
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total': len(images),
            'results': results
        }

# 创建 Flask 应用
def create_app():
    """创建 Flask 应用"""
    
    # 加载配置
    config = OCRServiceConfig()
    
    # 创建应用
    app = Flask(__name__)
    CORS(app)
    
    # 设置最大文件大小
    app.config['MAX_CONTENT_LENGTH'] = config.config['server']['max_content_length']
    
    # 创建 OCR 服务
    ocr_service = OCRService(config.config)
    
    # 预加载模型
    ocr_service.model_manager.preload_models()
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'status': 'healthy',
                'version': '1.0.0',
                'paddle_version': paddle.__version__,
                'gpu_available': paddle.device.is_compiled_with_cuda(),
                'uptime': time.time() - ocr_service.model_manager.stats['start_time']
            }
        })

    @app.route('/api/v1/info', methods=['GET'])
    def get_info():
        """获取服务信息"""
        status = 'running'
        try:
            status_check = True
        except Exception:
            status = 'error'
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'name': 'PaddleOCR Service',
                'version': '1.0.0',
                'description': '高性能多语言 OCR 服务',
                'author': 'PaddleOCR Team',
                'status': status,
                'supported_languages': ['ch', 'en'],
                'supported_formats': config.config['ocr']['supported_formats'],
                'api_endpoints': {
                    'GET /api/v1/health': '健康检查',
                    'GET /api/v1/info': '服务信息',
                    'POST /api/v1/ocr/file': '文件上传识别',
                    'POST /api/v1/ocr/url': 'URL 图像识别',
                    'GET /api/v1/models': '模型信息',
                    'GET /api/v1/stats': '统计信息'
                }
            }
        })

    @app.route('/api/v1/ocr/file', methods=['POST'])
    def ocr_file():
        """文件上传识别"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': '未找到文件', 'error_type': 'FileNotFound'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': '未选择文件', 'error_type': 'FileNotSelected'}), 400
            lang = request.form.get('lang', config.config['ocr']['default_lang'])
            use_gpu = request.form.get('use_gpu', '').lower() == 'true'
            temp_filename = f"{uuid.uuid4().hex}_{file.filename}"
            temp_path = os.path.join(ocr_service.temp_dir, temp_filename)
            file.save(temp_path)
            # 新增详细调试日志
            if not os.path.exists(temp_path):
                logger.error(f"文件保存失败: {temp_path}")
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': '文件保存失败', 'error_type': 'FileSaveError'}), 500
            import cv2
            img = cv2.imread(temp_path)
            if img is None:
                logger.error(f"cv2 无法读取上传的图片: {temp_path}")
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': '图片格式不被支持或已损坏', 'error_type': 'ImageReadError'}), 500
            result = ocr_service.process_image_file(temp_path, lang, use_gpu)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if result.get('success', False):
                return jsonify({'success': True, 'timestamp': datetime.now().isoformat(), 'data': result})
            else:
                logger.error(f"OCR 识别失败: {result}")
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': result.get('error', '识别失败'), 'error_type': result.get('error_type', 'Unknown')}), 500
        except Exception as e:
            import traceback
            logger.error(f"文件上传处理失败: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': str(e), 'error_type': type(e).__name__}), 500

   
    @app.route('/api/v1/ocr/url', methods=['POST'])
    def ocr_url():
        """URL 图像识别"""
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': '缺少图像 URL', 'error_type': 'NoURL'}), 400
            image_url = data['url']
            lang = data.get('lang', config.config['ocr']['default_lang'])
            use_gpu = data.get('use_gpu', False)
            result = ocr_service.process_url_image(image_url, lang, use_gpu)
            if result.get('success', False):
                return jsonify({'success': True, 'timestamp': datetime.now().isoformat(), 'data': result})
            else:
                return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': result.get('error', '识别失败'), 'error_type': result.get('error_type', 'Unknown')}), 500
        except Exception as e:
            logger.error(f"URL 处理失败: {e}")
            return jsonify({'success': False, 'timestamp': datetime.now().isoformat(), 'error': str(e), 'error_type': type(e).__name__}), 500



    @app.route('/api/v1/models', methods=['GET'])
    def get_models():
        """获取模型信息"""
        return jsonify({'success': True, 'timestamp': datetime.now().isoformat(), 'data': ocr_service.model_manager.get_model_info()})

    @app.route('/api/v1/stats', methods=['GET'])
    def get_stats():
        """获取统计信息"""
        stats = ocr_service.model_manager.stats.copy()
        stats['uptime'] = time.time() - stats['start_time']
        stats['success_rate'] = (
            stats['successful_requests'] / max(stats['total_requests'], 1) * 100
        )
        return jsonify({'success': True, 'timestamp': datetime.now().isoformat(), 'data': stats})
    
    return app, config

if __name__ == '__main__':
    print("🚀 启动 PaddleOCR 独立服务")
    print("=" * 50)
    
    app, config = create_app()
    
    server_config = config.config['server']
    
    print(f"📡 服务地址: http://{server_config['host']}:{server_config['port']}")
    print(f"📖 API 文档: http://{server_config['host']}:{server_config['port']}/api/v1/info")
    print("✅ 服务启动完成!")
    
    app.run(
        host=server_config['host'],
        port=server_config['port'],
        debug=server_config['debug']
    )
