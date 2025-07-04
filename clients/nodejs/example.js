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
            
            // Base64 识别
            console.log('\n3.2 Base64 识别...');
            try {
                const base64Data = client.imageToBase64(sampleImage);
                const result = await client.ocrFromBase64(base64Data, 'ch');
                if (result.success) {
                    console.log('✅ Base64 识别成功');
                    const texts = client.extractTextOnly(result);
                    console.log(`识别到 ${texts.length} 行文本`);
                } else {
                    console.log(`❌ Base64 识别失败: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.log(`❌ Base64 识别异常: ${error.message}`);
            }
            
            // 批量处理示例
            console.log('\n3.3 批量处理示例...');
            try {
                // 假设有多个相同的图片文件
                const imageFiles = [sampleImage];
                
                const result = await client.ocrBatchFiles(imageFiles, 'ch');
                if (result.success) {
                    console.log('✅ 批量处理成功');
                    result.data.forEach((fileResult, index) => {
                        const filename = path.basename(imageFiles[index]);
                        console.log(`\n文件: ${filename}`);
                        if (fileResult.success) {
                            const texts = client.extractTextOnly(fileResult);
                            texts.forEach((text, textIndex) => {
                                console.log(`  ${textIndex + 1}. ${text}`);
                            });
                        } else {
                            console.log(`  ❌ 识别失败: ${fileResult.error || 'Unknown error'}`);
                        }
                    });
                } else {
                    console.log(`❌ 批量处理失败: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.log(`❌ 批量处理异常: ${error.message}`);
            }
            
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

async function demoBatchProcessing() {
    console.log('\n批量处理示例');
    console.log('-'.repeat(30));
    
    const client = createClient();
    
    // 假设有多个图片文件
    const imageFiles = [
        'image1.jpg',
        'image2.jpg',
        'image3.jpg'
    ];
    
    // 过滤存在的文件
    const existingFiles = imageFiles.filter(file => fs.existsSync(file));
    
    if (existingFiles.length > 0) {
        console.log(`批量处理 ${existingFiles.length} 个文件...`);
        try {
            const result = await client.ocrBatchFiles(existingFiles, 'ch');
            if (result.success) {
                console.log('✅ 批量处理成功');
                result.data.forEach((fileResult, index) => {
                    const filename = existingFiles[index];
                    console.log(`\n文件: ${filename}`);
                    if (fileResult.success) {
                        const texts = client.extractTextOnly(fileResult);
                        texts.forEach((text, textIndex) => {
                            console.log(`  ${textIndex + 1}. ${text}`);
                        });
                    } else {
                        console.log(`  ❌ 识别失败: ${fileResult.error || 'Unknown error'}`);
                    }
                });
            } else {
                console.log(`❌ 批量处理失败: ${result.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.log(`❌ 批量处理异常: ${error.message}`);
        }
    } else {
        console.log('没有找到可处理的图片文件');
    }
}

async function demoUrlRecognition() {
    console.log('\nURL 识别示例');
    console.log('-'.repeat(30));
    
    const client = createClient();
    
    // 示例图片 URL
    const imageUrl = 'https://example.com/sample-image.jpg';
    
    try {
        console.log(`识别 URL: ${imageUrl}`);
        const result = await client.ocrFromUrl(imageUrl, 'ch');
        if (result.success) {
            console.log('✅ URL 识别成功');
            const texts = client.extractTextOnly(result);
            texts.forEach((text, index) => {
                console.log(`  ${index + 1}. ${text}`);
            });
        } else {
            console.log(`❌ URL 识别失败: ${result.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.log(`❌ URL 识别异常: ${error.message}`);
    }
}

async function demoMultiLanguage() {
    console.log('\n多语言识别示例');
    console.log('-'.repeat(30));
    
    const client = createClient();
    
    // 假设有不同语言的图片
    const languageTests = [
        { file: 'chinese.jpg', lang: 'ch', name: '中文' },
        { file: 'english.jpg', lang: 'en', name: '英文' },
        { file: 'french.jpg', lang: 'french', name: '法文' },
        { file: 'german.jpg', lang: 'german', name: '德文' }
    ];
    
    for (const test of languageTests) {
        if (fs.existsSync(test.file)) {
            try {
                console.log(`\n识别${test.name}图片: ${test.file}`);
                const result = await client.ocrFromFile(test.file, test.lang);
                if (result.success) {
                    console.log(`✅ ${test.name}识别成功`);
                    const texts = client.extractTextOnly(result);
                    texts.forEach((text, index) => {
                        console.log(`  ${index + 1}. ${text}`);
                    });
                } else {
                    console.log(`❌ ${test.name}识别失败: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.log(`❌ ${test.name}识别异常: ${error.message}`);
            }
        }
    }
}

// 主函数
if (require.main === module) {
    main().then(() => {
        // 运行其他示例
        demoBatchProcessing();
        demoUrlRecognition();
        demoMultiLanguage();
    }).catch(console.error);
}

module.exports = {
    main,
    demoBatchProcessing,
    demoUrlRecognition,
    demoMultiLanguage
};
