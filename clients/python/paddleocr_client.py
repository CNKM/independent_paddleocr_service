# -*- coding: utf-8 -*-
"""
PaddleOCR 服务 Python 客户端
支持文件、Base64、URL 等多种输入方式的 OCR 识别
"""

import os
import base64
import json
import time
import logging
from typing import List, Dict, Union, Optional
from pathlib import Path
import requests
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PaddleOCRClient:
    """PaddleOCR 服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 60):
        """
        初始化客户端
        
        Args:
            base_url: 服务地址
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'PaddleOCR-Python-Client/1.0.0'
        })
        
        logger.info(f"PaddleOCR 客户端初始化完成，服务地址: {self.base_url}")
    
    def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False
    
    def get_info(self) -> Dict:
        """获取服务信息"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/info", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取服务信息失败: {e}")
            raise
    
    def ocr_from_file(self, file_path: str, lang: str = "ch") -> Dict:
        """
        从文件识别文字
        
        Args:
            file_path: 图片文件路径
            lang: 语言代码 (ch, en, french, german, etc.)
        
        Returns:
            OCR 识别结果
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/*')}
            data = {'lang': lang}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ocr/file",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    def ocr_from_base64(self, base64_data: str, lang: str = "ch") -> Dict:
        """
        从 Base64 数据识别文字
        
        Args:
            base64_data: Base64 编码的图片数据
            lang: 语言代码
        
        Returns:
            OCR 识别结果
        """
        payload = {
            'image': base64_data,
            'lang': lang
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/ocr/base64",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def ocr_from_url(self, image_url: str, lang: str = "ch") -> Dict:
        """
        从 URL 识别文字
        
        Args:
            image_url: 图片 URL
            lang: 语言代码
        
        Returns:
            OCR 识别结果
        """
        payload = {
            'url': image_url,
            'lang': lang
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/ocr/url",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def ocr_batch_files(self, file_paths: List[str], lang: str = "ch") -> Dict:
        """
        批量识别文件
        
        Args:
            file_paths: 图片文件路径列表
            lang: 语言代码
        
        Returns:
            批量识别结果
        """
        files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            files.append(('files', (os.path.basename(file_path), open(file_path, 'rb'), 'image/*')))
        
        try:
            data = {'lang': lang}
            response = self.session.post(
                f"{self.base_url}/api/v1/ocr/batch",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        finally:
            # 关闭文件
            for _, (_, file_obj, _) in files:
                file_obj.close()
    
    def ocr_batch_base64(self, base64_list: List[str], lang: str = "ch") -> Dict:
        """
        批量识别 Base64 数据
        
        Args:
            base64_list: Base64 编码的图片数据列表
            lang: 语言代码
        
        Returns:
            批量识别结果
        """
        payload = {
            'images': base64_list,
            'lang': lang
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/ocr/batch",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def image_to_base64(self, file_path: str) -> str:
        """
        将图片文件转换为 Base64 编码
        
        Args:
            file_path: 图片文件路径
        
        Returns:
            Base64 编码的图片数据
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def save_base64_image(self, base64_data: str, file_path: str) -> None:
        """
        保存 Base64 图片数据到文件
        
        Args:
            base64_data: Base64 编码的图片数据
            file_path: 保存的文件路径
        """
        image_data = base64.b64decode(base64_data)
        with open(file_path, 'wb') as f:
            f.write(image_data)
    
    def extract_text_only(self, ocr_result: Dict) -> List[str]:
        """
        从 OCR 结果中提取纯文本
        
        Args:
            ocr_result: OCR 识别结果
        
        Returns:
            文本列表
        """
        if not ocr_result.get('success', False):
            return []
        
        texts = []
        for item in ocr_result.get('data', []):
            if isinstance(item, list) and len(item) >= 2:
                text = item[1]
                if isinstance(text, list) and len(text) >= 1:
                    texts.append(text[0])
                elif isinstance(text, str):
                    texts.append(text)
        
        return texts
    
    def get_text_with_confidence(self, ocr_result: Dict) -> List[Dict]:
        """
        获取带置信度的文本结果
        
        Args:
            ocr_result: OCR 识别结果
        
        Returns:
            包含文本和置信度的列表
        """
        if not ocr_result.get('success', False):
            return []
        
        results = []
        for item in ocr_result.get('data', []):
            if isinstance(item, list) and len(item) >= 2:
                bbox = item[0]
                text_info = item[1]
                
                if isinstance(text_info, list) and len(text_info) >= 2:
                    text = text_info[0]
                    confidence = text_info[1]
                    results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
                elif isinstance(text_info, str):
                    results.append({
                        'text': text_info,
                        'confidence': 1.0,
                        'bbox': bbox
                    })
        
        return results
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.session.close()

# 便捷函数
def create_client(base_url: str = "http://localhost:8000", timeout: int = 60) -> PaddleOCRClient:
    """创建 PaddleOCR 客户端"""
    return PaddleOCRClient(base_url, timeout)

def quick_ocr(file_path: str, lang: str = "ch", base_url: str = "http://localhost:8000") -> str:
    """快速识别图片中的文字"""
    with create_client(base_url) as client:
        result = client.ocr_from_file(file_path, lang)
        texts = client.extract_text_only(result)
        return '\n'.join(texts)

if __name__ == "__main__":
    # 示例用法
    client = PaddleOCRClient()
    
    # 检查服务状态
    if client.check_health():
        print("服务运行正常")
        
        # 获取服务信息
        info = client.get_info()
        print(f"服务信息: {info}")
    else:
        print("服务未运行或不可访问")
