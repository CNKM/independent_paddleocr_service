# -*- coding: utf-8 -*-
"""
PaddleOCR Python 客户端使用示例
"""

import os
import sys
import json
from pathlib import Path

# 添加客户端路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paddleocr_client import PaddleOCRClient, quick_ocr

def main():
    """主函数"""
    print("PaddleOCR Python 客户端示例")
    print("=" * 50)
    
    # 创建客户端
    client = PaddleOCRClient(base_url="http://localhost:8000")
    
    # 检查服务状态
    print("1. 检查服务状态...")
    if not client.check_health():
        print("❌ 服务未运行，请先启动 PaddleOCR 服务")
        return
    
    print("✅ 服务运行正常")
    
    # 获取服务信息
    print("\n2. 获取服务信息...")
    try:
        info = client.get_info()
        print(f"服务版本: {info.get('version', 'N/A')}")
        print(f"支持的语言: {info.get('supported_languages', [])}")
        print(f"服务状态: {info.get('status', 'N/A')}")
    except Exception as e:
        print(f"获取服务信息失败: {e}")
    
    # 示例图片路径（需要根据实际情况修改）
    sample_image = Path(__file__).parent.parent.parent.parent / "demo_image.jpg"
    
    if sample_image.exists():
        print(f"\n3. 使用示例图片进行识别: {sample_image}")
        
        # 文件识别
        print("\n3.1 文件识别...")
        try:
            result = client.ocr_from_file(str(sample_image), lang="ch")
            if result.get('success'):
                print("✅ 识别成功")
                texts = client.extract_text_only(result)
                print("识别结果:")
                for i, text in enumerate(texts, 1):
                    print(f"  {i}. {text}")
                
                # 显示详细信息
                print("\n详细信息:")
                details = client.get_text_with_confidence(result)
                for i, detail in enumerate(details, 1):
                    print(f"  {i}. 文本: {detail['text']}")
                    print(f"     置信度: {detail['confidence']:.3f}")
                    print(f"     边界框: {detail['bbox']}")
            else:
                print(f"❌ 识别失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 文件识别异常: {e}")
        
        # Base64 识别
        print("\n3.2 Base64 识别...")
        try:
            base64_data = client.image_to_base64(str(sample_image))
            result = client.ocr_from_base64(base64_data, lang="ch")
            if result.get('success'):
                print("✅ Base64 识别成功")
                texts = client.extract_text_only(result)
                print(f"识别到 {len(texts)} 行文本")
            else:
                print(f"❌ Base64 识别失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Base64 识别异常: {e}")
    
    else:
        print(f"\n⚠️  示例图片不存在: {sample_image}")
        print("请将测试图片放在项目根目录下，命名为 demo_image.jpg")
    
    # 快速识别示例
    print("\n4. 快速识别示例...")
    if sample_image.exists():
        try:
            text = quick_ocr(str(sample_image), lang="ch")
            print("快速识别结果:")
            print(text)
        except Exception as e:
            print(f"❌ 快速识别失败: {e}")
    
    print("\n=" * 50)
    print("示例完成")

def demo_batch_processing():
    """批量处理示例"""
    print("\n批量处理示例")
    print("-" * 30)
    
    client = PaddleOCRClient()
    
    # 假设有多个图片文件
    image_files = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
    ]
    
    # 过滤存在的文件
    existing_files = [f for f in image_files if os.path.exists(f)]
    
    if existing_files:
        print(f"批量处理 {len(existing_files)} 个文件...")
        try:
            result = client.ocr_batch_files(existing_files, lang="ch")
            if result.get('success'):
                print("✅ 批量处理成功")
                for i, file_result in enumerate(result.get('data', [])):
                    filename = existing_files[i]
                    print(f"\n文件: {filename}")
                    if file_result.get('success'):
                        texts = client.extract_text_only(file_result)
                        for j, text in enumerate(texts, 1):
                            print(f"  {j}. {text}")
                    else:
                        print(f"  ❌ 识别失败: {file_result.get('error', 'Unknown error')}")
            else:
                print(f"❌ 批量处理失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 批量处理异常: {e}")
    else:
        print("没有找到可处理的图片文件")

if __name__ == "__main__":
    main()
    demo_batch_processing()
