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
    else:
        print(f"\n⚠️  示例图片不存在: {sample_image}")
        print("请将测试图片放在项目根目录下，命名为 demo_image.jpg")
    print("\n=" * 50)
    print("示例完成")

if __name__ == "__main__":
    main()
