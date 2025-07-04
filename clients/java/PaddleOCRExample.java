package com.paddleocr.client;

import com.fasterxml.jackson.databind.JsonNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

/**
 * PaddleOCR Java 客户端使用示例
 * 
 * @author PaddleOCR
 * @version 1.0.0
 */
public class PaddleOCRExample {
    
    private static final Logger logger = LoggerFactory.getLogger(PaddleOCRExample.class);
    
    public static void main(String[] args) {
        System.out.println("PaddleOCR Java 客户端示例");
        System.out.println("=" + "=".repeat(50));
        
        // 创建客户端
        PaddleOCRClient client = new PaddleOCRClient("http://localhost:8000");
        
        try {
            // 检查服务状态
            System.out.println("1. 检查服务状态...");
            if (!client.checkHealth()) {
                System.out.println("❌ 服务未运行，请先启动 PaddleOCR 服务");
                return;
            }
            System.out.println("✅ 服务运行正常");
            
            // 获取服务信息
            System.out.println("\n2. 获取服务信息...");
            try {
                JsonNode info = client.getInfo();
                System.out.println("服务版本: " + info.get("version").asText());
                System.out.println("服务状态: " + info.get("status").asText());
                if (info.has("supported_languages")) {
                    System.out.println("支持的语言: " + info.get("supported_languages").toString());
                }
            } catch (Exception e) {
                System.out.println("获取服务信息失败: " + e.getMessage());
            }
            
            // 示例图片路径（需要根据实际情况修改）
            String sampleImage = "demo_image.jpg";
            
            // 检查示例图片是否存在
            if (new java.io.File(sampleImage).exists()) {
                System.out.println("\n3. 使用示例图片进行识别: " + sampleImage);
                
                // 文件识别
                System.out.println("\n3.1 文件识别...");
                try {
                    JsonNode result = client.ocrFromFile(sampleImage, "ch");
                    if (result.get("success").asBoolean()) {
                        System.out.println("✅ 识别成功");
                        
                        // 提取文本
                        JsonNode data = result.get("data");
                        if (data.isArray()) {
                            System.out.println("识别结果:");
                            int index = 1;
                            for (JsonNode item : data) {
                                if (item.isArray() && item.size() >= 2) {
                                    JsonNode textInfo = item.get(1);
                                    if (textInfo.isArray() && textInfo.size() >= 1) {
                                        String text = textInfo.get(0).asText();
                                        System.out.println("  " + index + ". " + text);
                                        index++;
                                    }
                                }
                            }
                        }
                    } else {
                        System.out.println("❌ 识别失败: " + result.get("error").asText());
                    }
                } catch (Exception e) {
                    System.out.println("❌ 文件识别异常: " + e.getMessage());
                }
                
                // Base64 识别
                System.out.println("\n3.2 Base64 识别...");
                try {
                    String base64Data = client.imageToBase64(sampleImage);
                    JsonNode result = client.ocrFromBase64(base64Data, "ch");
                    if (result.get("success").asBoolean()) {
                        System.out.println("✅ Base64 识别成功");
                        JsonNode data = result.get("data");
                        if (data.isArray()) {
                            System.out.println("识别到 " + data.size() + " 行文本");
                        }
                    } else {
                        System.out.println("❌ Base64 识别失败: " + result.get("error").asText());
                    }
                } catch (Exception e) {
                    System.out.println("❌ Base64 识别异常: " + e.getMessage());
                }
                
                // 批量处理示例
                System.out.println("\n3.3 批量处理示例...");
                try {
                    // 假设有多个相同的图片文件
                    List<String> imageFiles = Arrays.asList(sampleImage);
                    
                    JsonNode result = client.ocrBatchFiles(imageFiles, "ch");
                    if (result.get("success").asBoolean()) {
                        System.out.println("✅ 批量处理成功");
                        JsonNode data = result.get("data");
                        if (data.isArray()) {
                            for (int i = 0; i < data.size(); i++) {
                                System.out.println("文件 " + imageFiles.get(i) + ":");
                                JsonNode fileResult = data.get(i);
                                if (fileResult.get("success").asBoolean()) {
                                    JsonNode fileData = fileResult.get("data");
                                    if (fileData.isArray()) {
                                        int textIndex = 1;
                                        for (JsonNode item : fileData) {
                                            if (item.isArray() && item.size() >= 2) {
                                                JsonNode textInfo = item.get(1);
                                                if (textInfo.isArray() && textInfo.size() >= 1) {
                                                    String text = textInfo.get(0).asText();
                                                    System.out.println("  " + textIndex + ". " + text);
                                                    textIndex++;
                                                }
                                            }
                                        }
                                    }
                                } else {
                                    System.out.println("  ❌ 识别失败: " + fileResult.get("error").asText());
                                }
                            }
                        }
                    } else {
                        System.out.println("❌ 批量处理失败: " + result.get("error").asText());
                    }
                } catch (Exception e) {
                    System.out.println("❌ 批量处理异常: " + e.getMessage());
                }
                
            } else {
                System.out.println("\n⚠️  示例图片不存在: " + sampleImage);
                System.out.println("请将测试图片放在项目根目录下，命名为 demo_image.jpg");
            }
            
        } finally {
            // 关闭客户端
            client.close();
        }
        
        System.out.println("\n" + "=".repeat(50));
        System.out.println("示例完成");
    }
    
    /**
     * 提取纯文本的工具方法
     * 
     * @param ocrResult OCR 识别结果
     * @return 文本列表
     */
    public static String[] extractTextOnly(JsonNode ocrResult) {
        if (!ocrResult.get("success").asBoolean()) {
            return new String[0];
        }
        
        JsonNode data = ocrResult.get("data");
        if (!data.isArray()) {
            return new String[0];
        }
        
        return StreamSupport.stream(data.spliterator(), false)
                .filter(item -> item.isArray() && item.size() >= 2)
                .map(item -> item.get(1))
                .filter(textInfo -> textInfo.isArray() && textInfo.size() >= 1)
                .map(textInfo -> textInfo.get(0).asText())
                .toArray(String[]::new);
    }
}
