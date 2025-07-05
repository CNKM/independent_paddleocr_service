/**
 * PaddleOCR Node.js 客户端使用示例
 */

const { PaddleOCRClient, createClient, quickOCR } = require('./paddleocr_client');
const fs = require('fs');
const path = require('path');

async function main() {
    console.log('PaddleOCR Node.js 客户端示例');
    console.log('='.repeat(50));
    
    // 创建客户端
    const client = new PaddleOCRClient('http://localhost:8000');
    
    try {
        // 检查服务状态
        console.log('1. 检查服务状态...');
        const isHealthy = await client.checkHealth();
        if (!isHealthy) {
            console.log('❌ 服务未运行，请先启动 PaddleOCR 服务');
            return;
        }
        console.log('✅ 服务运行正常');
        
        // 获取服务信息
        console.log('\n2. 获取服务信息...');
        try {
            const info = await client.getInfo();
            console.log(`服务版本: ${info.version || 'N/A'}`);
            console.log(`支持的语言: ${info.supported_languages || []}`);
            console.log(`服务状态: ${info.status || 'N/A'}`);
        } catch (error) {
            console.log(`获取服务信息失败: ${error.message}`);
        }
        
        // 示例图片路径（需要根据实际情况修改）
        const sampleImage = path.join(__dirname, '..', '..', '..', 'demo_image.jpg');
        
        if (fs.existsSync(sampleImage)) {
            console.log(`\n3. 使用示例图片进行识别: ${sampleImage}`);
            
            // 文件识别
            console.log('\n3.1 文件识别...');
            try {
                const result = await client.ocrFromFile(sampleImage, 'ch');
                if (result.success) {
                    console.log('✅ 识别成功');
                    const texts = client.extractTextOnly(result);
                    console.log('识别结果:');
                    texts.forEach((text, index) => {
                        console.log(`  ${index + 1}. ${text}`);
                    });
                    
                    // 显示详细信息
                    console.log('\n详细信息:');
                    const details = client.getTextWithConfidence(result);
                    details.forEach((detail, index) => {
                        console.log(`  ${index + 1}. 文本: ${detail.text}`);
                        console.log(`     置信度: ${detail.confidence.toFixed(3)}`);
                        console.log(`     边界框: ${JSON.stringify(detail.bbox)}`);
                    });
                } else {
                    console.log(`❌ 识别失败: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.log(`❌ 文件识别异常: ${error.message}`);
            }
            
            // ...仅保留文件识别演示...
            
        } else {
            console.log(`\n⚠️  示例图片不存在: ${sampleImage}`);
            console.log('请将测试图片放在项目根目录下，命名为 demo_image.jpg');
        }
        
        // 快速识别示例
        console.log('\n4. 快速识别示例...');
        if (fs.existsSync(sampleImage)) {
            try {
                const text = await quickOCR(sampleImage, 'ch');
                console.log('快速识别结果:');
                console.log(text);
            } catch (error) {
                console.log(`❌ 快速识别失败: ${error.message}`);
            }
        }
        
    } catch (error) {
        console.log(`❌ 示例运行异常: ${error.message}`);
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('示例完成');
}

// 主函数
if (require.main === module) {
    main().catch(console.error);
}
