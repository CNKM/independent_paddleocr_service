using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace PaddleOCR.Client
{
    /// <summary>
    /// PaddleOCR 服务客户端
    /// </summary>
    public class PaddleOCRClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        public PaddleOCRClient(string baseUrl = "http://localhost:8000")
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromMinutes(2)
            };
        }

        /// <summary>
        /// 健康检查
        /// </summary>
        public async Task<HealthResponse> HealthCheckAsync()
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/api/v1/health");
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<HealthResponse>(json, GetJsonOptions());
        }

        /// <summary>
        /// 获取服务信息
        /// </summary>
        public async Task<ServiceInfo> GetServiceInfoAsync()
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/api/v1/info");
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<ServiceInfo>(json, GetJsonOptions());
        }

        /// <summary>
        /// 识别本地文件
        /// </summary>
        public async Task<OCRResult> RecognizeFileAsync(string filePath, string lang = "ch", bool useGpu = false)
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException($"文件不存在: {filePath}");

            using var form = new MultipartFormDataContent();
            using var fileStream = File.OpenRead(filePath);
            using var fileContent = new StreamContent(fileStream);
            
            form.Add(fileContent, "file", Path.GetFileName(filePath));
            form.Add(new StringContent(lang), "lang");
            form.Add(new StringContent(useGpu.ToString().ToLower()), "use_gpu");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/ocr/file", form);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<OCRResult>(json, GetJsonOptions());
        }

        /// <summary>
        /// 识别 Base64 编码的图像
        /// </summary>
        public async Task<OCRResult> RecognizeBase64Async(string base64Data, string lang = "ch", bool useGpu = false)
        {
            var request = new Base64Request
            {
                Image = base64Data,
                Lang = lang,
                UseGpu = useGpu
            };

            var json = JsonSerializer.Serialize(request, GetJsonOptions());
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/ocr/base64", content);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<OCRResult>(responseJson, GetJsonOptions());
        }

        /// <summary>
        /// 识别 URL 图像
        /// </summary>
        public async Task<OCRResult> RecognizeUrlAsync(string imageUrl, string lang = "ch", bool useGpu = false)
        {
            var request = new UrlRequest
            {
                Url = imageUrl,
                Lang = lang,
                UseGpu = useGpu
            };

            var json = JsonSerializer.Serialize(request, GetJsonOptions());
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/ocr/url", content);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<OCRResult>(responseJson, GetJsonOptions());
        }

        /// <summary>
        /// 批量处理图像
        /// </summary>
        public async Task<BatchResult> RecognizeBatchAsync(string[] base64Images, string lang = "ch", bool useGpu = false)
        {
            var request = new BatchRequest
            {
                Images = base64Images,
                Lang = lang,
                UseGpu = useGpu
            };

            var json = JsonSerializer.Serialize(request, GetJsonOptions());
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}/api/v1/ocr/batch", content);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<BatchResult>(responseJson, GetJsonOptions());
        }

        /// <summary>
        /// 将文件转换为 Base64
        /// </summary>
        public static string FileToBase64(string filePath)
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException($"文件不存在: {filePath}");

            var bytes = File.ReadAllBytes(filePath);
            var base64 = Convert.ToBase64String(bytes);
            
            var extension = Path.GetExtension(filePath).ToLower();
            var mimeType = extension switch
            {
                ".png" => "image/png",
                ".gif" => "image/gif",
                ".webp" => "image/webp",
                _ => "image/jpeg"
            };

            return $"data:{mimeType};base64,{base64}";
        }

        /// <summary>
        /// 获取统计信息
        /// </summary>
        public async Task<StatsResponse> GetStatsAsync()
        {
            var response = await _httpClient.GetAsync($"{_baseUrl}/api/v1/stats");
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<StatsResponse>(json, GetJsonOptions());
        }

        private static JsonSerializerOptions GetJsonOptions()
        {
            return new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                PropertyNameCaseInsensitive = true
            };
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }

    // 数据模型
    public class HealthResponse
    {
        public string Status { get; set; }
        public string Timestamp { get; set; }
        public string Version { get; set; }
        public string PaddleVersion { get; set; }
        public bool GpuAvailable { get; set; }
        public double Uptime { get; set; }
    }

    public class ServiceInfo
    {
        public string Name { get; set; }
        public string Version { get; set; }
        public string Description { get; set; }
        public string Author { get; set; }
        public string[] SupportedLanguages { get; set; }
        public string[] SupportedFormats { get; set; }
        public Dictionary<string, string> ApiEndpoints { get; set; }
    }

    public class OCRResult
    {
        public bool Success { get; set; }
        public string Timestamp { get; set; }
        public string Lang { get; set; }
        public string Text { get; set; }
        public int WordCount { get; set; }
        public double AvgConfidence { get; set; }
        public OCRDetail[] Details { get; set; }
        public string Message { get; set; }
        public string Error { get; set; }
        public string ErrorType { get; set; }
    }

    public class OCRDetail
    {
        public string Text { get; set; }
        public double Confidence { get; set; }
        public double[][] Bbox { get; set; }
    }

    public class BatchResult
    {
        public bool Success { get; set; }
        public string Timestamp { get; set; }
        public int Total { get; set; }
        public OCRResult[] Results { get; set; }
        public string Error { get; set; }
    }

    public class StatsResponse
    {
        public int ModelsLoaded { get; set; }
        public int TotalRequests { get; set; }
        public int SuccessfulRequests { get; set; }
        public int FailedRequests { get; set; }
        public double StartTime { get; set; }
        public double Uptime { get; set; }
        public double SuccessRate { get; set; }
    }

    // 请求模型
    public class Base64Request
    {
        public string Image { get; set; }
        public string Lang { get; set; }
        public bool UseGpu { get; set; }
    }

    public class UrlRequest
    {
        public string Url { get; set; }
        public string Lang { get; set; }
        public bool UseGpu { get; set; }
    }

    public class BatchRequest
    {
        public string[] Images { get; set; }
        public string Lang { get; set; }
        public bool UseGpu { get; set; }
    }
}
