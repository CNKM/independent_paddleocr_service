package com.paddleocr.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * PaddleOCR 服务 Java 客户端
 * 
 * @author PaddleOCR
 * @version 1.0.0
 */
public class PaddleOCRClient {
    
    private static final Logger logger = LoggerFactory.getLogger(PaddleOCRClient.class);
    
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final String baseUrl;
    
    /**
     * 构造函数
     * 
     * @param baseUrl 服务地址
     * @param timeout 超时时间（秒）
     */
    public PaddleOCRClient(String baseUrl, int timeout) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.objectMapper = new ObjectMapper();
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(timeout, TimeUnit.SECONDS)
                .readTimeout(timeout, TimeUnit.SECONDS)
                .writeTimeout(timeout, TimeUnit.SECONDS)
                .build();
        
        logger.info("PaddleOCR Java 客户端初始化完成，服务地址: {}", this.baseUrl);
    }
    
    /**
     * 构造函数（默认超时 60 秒）
     * 
     * @param baseUrl 服务地址
     */
    public PaddleOCRClient(String baseUrl) {
        this(baseUrl, 60);
    }
    
    /**
     * 构造函数（默认本地服务）
     */
    public PaddleOCRClient() {
        this("http://localhost:8000");
    }
    
    /**
     * 检查服务健康状态
     * 
     * @return 服务是否正常
     */
    public boolean checkHealth() {
        try {
            Request request = new Request.Builder()
                    .url(baseUrl + "/api/v1/health")
                    .build();
            
            Response response = httpClient.newCall(request).execute();
            return response.isSuccessful();
        } catch (Exception e) {
            logger.error("健康检查失败", e);
            return false;
        }
    }
    
    /**
     * 获取服务信息
     * 
     * @return 服务信息
     * @throws IOException 请求异常
     */
    public JsonNode getInfo() throws IOException {            Request request = new Request.Builder()
                .url(baseUrl + "/api/v1/info")
                .build();
        
        Response response = httpClient.newCall(request).execute();
        if (!response.isSuccessful()) {
            throw new IOException("获取服务信息失败: " + response.code());
        }
        
        String responseBody = response.body().string();
        return objectMapper.readTree(responseBody);
    }
    
    /**
     * 从文件识别文字
     * 
     * @param filePath 图片文件路径
     * @param lang 语言代码
     * @return OCR 识别结果
     * @throws IOException 请求异常
     */
    public JsonNode ocrFromFile(String filePath, String lang) throws IOException {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new IOException("文件不存在: " + filePath);
        }
        
        RequestBody fileBody = RequestBody.create(file, MediaType.parse("image/*"));
        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", file.getName(), fileBody)
                .addFormDataPart("lang", lang)
                .build();            Request request = new Request.Builder()
                .url(baseUrl + "/api/v1/ocr/file")
                .post(requestBody)
                .build();
        
        Response response = httpClient.newCall(request).execute();
        if (!response.isSuccessful()) {
            throw new IOException("文件识别失败: " + response.code());
        }
        
        String responseBody = response.body().string();
        return objectMapper.readTree(responseBody);
    }
    
    /**
     * 从文件识别文字（默认中文）
     * 
     * @param filePath 图片文件路径
     * @return OCR 识别结果
     * @throws IOException 请求异常
     */
    public JsonNode ocrFromFile(String filePath) throws IOException {
        return ocrFromFile(filePath, "ch");
    }
    
    }
    
    /**
     * 从 URL 识别文字
     * 
     * @param imageUrl 图片 URL
     * @param lang 语言代码
     * @return OCR 识别结果
     * @throws IOException 请求异常
     */
    public JsonNode ocrFromUrl(String imageUrl, String lang) throws IOException {
        String jsonPayload = String.format("{\"url\":\"%s\",\"lang\":\"%s\"}", imageUrl, lang);
        
        RequestBody requestBody = RequestBody.create(jsonPayload, MediaType.parse("application/json"));
        Request request = new Request.Builder()
                .url(baseUrl + "/api/v1/ocr/url")
                .post(requestBody)
                .build();
        
        Response response = httpClient.newCall(request).execute();
        if (!response.isSuccessful()) {
            throw new IOException("URL 识别失败: " + response.code());
        }
        
        String responseBody = response.body().string();
        return objectMapper.readTree(responseBody);
    }
    
    /**
     * 从 URL 识别文字（默认中文）
     * 
     * @param imageUrl 图片 URL
     * @return OCR 识别结果
     * @throws IOException 请求异常
     */
    public JsonNode ocrFromUrl(String imageUrl) throws IOException {
        return ocrFromUrl(imageUrl, "ch");
    }
    
    // ...已移除 base64 和批量相关方法...
    
    /**
     * 关闭客户端
     */
    public void close() {
        if (httpClient != null) {
            httpClient.dispatcher().executorService().shutdown();
            httpClient.connectionPool().evictAll();
        }
    }
}
