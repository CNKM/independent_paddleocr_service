/**
 * PaddleOCR 独立服务 Node.js 客户端
 * 适配独立服务的 API 接口
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
            const response = await this.client.post('/api/v1/ocr/batch', {
                images: base64Images,
                lang: lang
            });path = require('path');

class PaddleOCRClient {
    constructor(baseURL = 'http://localhost:8000', timeout = 60000) {
        this.baseURL = baseURL.replace(/\/$/, ''); // 移除尾部斜杠
        this.timeout = timeout;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'User-Agent': 'PaddleOCR-NodeJS-Client/1.0.0'
            }
        });
        
        console.log(`PaddleOCR 客户端初始化完成，服务地址: ${this.baseURL}`);
    }

    /**
     * 检查服务健康状态
     * @returns {Promise<boolean>} 服务是否正常
     */
    async checkHealth() {
        try {
            const response = await this.client.get('/api/v1/health');
            return response.status === 200;
        } catch (error) {
            console.error('健康检查失败:', error.message);
            return false;
        }
    }

    /**
     * 获取服务信息
     * @returns {Promise<Object>} 服务信息
     */
    async getInfo() {
        try {
            const response = await this.client.get('/api/v1/info');
            return response.data;
        } catch (error) {
            throw new Error(`获取服务信息失败: ${error.message}`);
        }
    }

    /**
     * 从本地文件识别文字
     * @param {string} filePath - 图像文件路径
     * @param {string} lang - 语言代码 (ch, en, french, german, etc.)
     * @returns {Promise<Object>} OCR 识别结果
     */
    async ocrFromFile(filePath, lang = 'ch') {
        try {
            // 检查文件是否存在
            if (!fs.existsSync(filePath)) {
                throw new Error(`文件不存在: ${filePath}`);
            }

            // 创建 FormData
            const formData = new FormData();
            formData.append('file', fs.createReadStream(filePath));
            formData.append('lang', lang);

            const response = await axios.post(`${this.baseURL}/api/v1/ocr/file`, formData, {
                headers: {
                    ...formData.getHeaders(),
                },
                timeout: this.timeout
            });

            return response.data;
        } catch (error) {
            throw new Error(`文件识别失败: ${error.message}`);
        }
    }

    /**
     * 从 Base64 数据识别文字
     * @param {string} base64Data - Base64 编码的图像数据
     * @param {string} lang - 语言代码
     * @returns {Promise<Object>} OCR 识别结果
     */
    async ocrFromBase64(base64Data, lang = 'ch') {
        try {
            const response = await this.client.post('/api/v1/ocr/base64', {
                image: base64Data,
                lang: lang
            });

            return response.data;
        } catch (error) {
            throw new Error(`Base64 识别失败: ${error.message}`);
        }
    }

    /**
     * 从 URL 识别文字
     * @param {string} imageUrl - 图像 URL
     * @param {string} lang - 语言代码
     * @returns {Promise<Object>} OCR 识别结果
     */
    async ocrFromUrl(imageUrl, lang = 'ch') {
        try {
            const response = await this.client.post('/api/v1/ocr/url', {
                url: imageUrl,
                lang: lang
            });

            return response.data;
        } catch (error) {
            throw new Error(`URL 识别失败: ${error.message}`);
        }
    }

    /**
     * 批量识别文件
     * @param {Array<string>} filePaths - 图像文件路径数组
     * @param {string} lang - 语言代码
     * @returns {Promise<Object>} 批量识别结果
     */
    async ocrBatchFiles(filePaths, lang = 'ch') {
        try {
            // 检查所有文件是否存在
            for (const filePath of filePaths) {
                if (!fs.existsSync(filePath)) {
                    throw new Error(`文件不存在: ${filePath}`);
                }
            }

            // 创建 FormData
            const formData = new FormData();
            for (const filePath of filePaths) {
                formData.append('files', fs.createReadStream(filePath));
            }
            formData.append('lang', lang);

            const response = await axios.post(`${this.baseURL}/api/v1/ocr/batch`, formData, {
                headers: {
                    ...formData.getHeaders(),
                },
                timeout: this.timeout
            });

            return response.data;
        } catch (error) {
            throw new Error(`批量文件识别失败: ${error.message}`);
        }
    }

    /**
     * 批量识别 Base64 数据
     * @param {Array<string>} base64List - Base64 编码的图像数据数组
     * @param {string} lang - 语言代码
     * @returns {Promise<Object>} 批量识别结果
     */
    async ocrBatchBase64(base64List, lang = 'ch') {
        try {
            const response = await this.client.post('/api/v1/ocr/batch', {
                images: base64List,
                lang: lang
            });

            return response.data;
        } catch (error) {
            throw new Error(`批量 Base64 识别失败: ${error.message}`);
        }
    }

    /**
     * 将图像文件转换为 Base64 编码
     * @param {string} filePath - 图像文件路径
     * @returns {string} Base64 编码的图像数据
     */
    imageToBase64(filePath) {
        try {
            if (!fs.existsSync(filePath)) {
                throw new Error(`文件不存在: ${filePath}`);
            }

            const fileBuffer = fs.readFileSync(filePath);
            return fileBuffer.toString('base64');
        } catch (error) {
            throw new Error(`文件转换失败: ${error.message}`);
        }
    }

    /**
     * 保存 Base64 图像数据到文件
     * @param {string} base64Data - Base64 编码的图像数据
     * @param {string} filePath - 保存的文件路径
     */
    saveBase64Image(base64Data, filePath) {
        try {
            const imageBuffer = Buffer.from(base64Data, 'base64');
            fs.writeFileSync(filePath, imageBuffer);
        } catch (error) {
            throw new Error(`保存图像失败: ${error.message}`);
        }
    }

    /**
     * 从 OCR 结果中提取纯文本
     * @param {Object} ocrResult - OCR 识别结果
     * @returns {Array<string>} 文本数组
     */
    extractTextOnly(ocrResult) {
        if (!ocrResult.success) {
            return [];
        }

        const texts = [];
        for (const item of ocrResult.data || []) {
            if (Array.isArray(item) && item.length >= 2) {
                const textInfo = item[1];
                if (Array.isArray(textInfo) && textInfo.length >= 1) {
                    texts.push(textInfo[0]);
                } else if (typeof textInfo === 'string') {
                    texts.push(textInfo);
                }
            }
        }
        return texts;
    }

    /**
     * 获取带置信度的文本结果
     * @param {Object} ocrResult - OCR 识别结果
     * @returns {Array<Object>} 包含文本和置信度的数组
     */
    getTextWithConfidence(ocrResult) {
        if (!ocrResult.success) {
            return [];
        }

        const results = [];
        for (const item of ocrResult.data || []) {
            if (Array.isArray(item) && item.length >= 2) {
                const bbox = item[0];
                const textInfo = item[1];

                if (Array.isArray(textInfo) && textInfo.length >= 2) {
                    results.push({
                        text: textInfo[0],
                        confidence: textInfo[1],
                        bbox: bbox
                    });
                } else if (typeof textInfo === 'string') {
                    results.push({
                        text: textInfo,
                        confidence: 1.0,
                        bbox: bbox
                    });
                }
            }
        }
        return results;
    }

    /**
     * 获取文件的 MIME 类型
     * @param {string} filePath - 文件路径
     * @returns {string} MIME 类型
     */
    getMimeType(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        const mimeTypes = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        };
        return mimeTypes[ext] || 'image/jpeg';
    }

    /**
     * 检查文件是否为支持的图像格式
     * @param {string} filePath - 文件路径
     * @returns {boolean} 是否支持
     */
    isSupportedImageFormat(filePath) {
        const ext = path.extname(filePath).toLowerCase();
        const supportedFormats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'];
        return supportedFormats.includes(ext);
    }
}

/**
 * 创建 PaddleOCR 客户端实例
 * @param {string} baseURL - 服务地址
 * @param {number} timeout - 超时时间
 * @returns {PaddleOCRClient} 客户端实例
 */
function createClient(baseURL = 'http://localhost:8000', timeout = 60000) {
    return new PaddleOCRClient(baseURL, timeout);
}

/**
 * 快速识别图像中的文字
 * @param {string} filePath - 图像文件路径
 * @param {string} lang - 语言代码
 * @param {string} baseURL - 服务地址
 * @returns {Promise<string>} 识别的文本
 */
async function quickOCR(filePath, lang = 'ch', baseURL = 'http://localhost:8000') {
    const client = createClient(baseURL);
    try {
        const result = await client.ocrFromFile(filePath, lang);
        const texts = client.extractTextOnly(result);
        return texts.join('\n');
    } catch (error) {
        throw new Error(`快速识别失败: ${error.message}`);
    }
}

module.exports = {
    PaddleOCRClient,
    createClient,
    quickOCR
};
