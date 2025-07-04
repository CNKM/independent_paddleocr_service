using System;
using System.Threading.Tasks;
using PaddleOCR.Client;

namespace PaddleOCR.Examples
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("🚀 PaddleOCR C# 客户端示例");
            Console.WriteLine("=" + new string('=', 40));

            using var client = new PaddleOCRClient("http://localhost:8000");

            try
            {
                // 1. 健康检查
                Console.WriteLine("\n📊 健康检查...");
                var health = await client.HealthCheckAsync();
                Console.WriteLine($"服务状态: {health.Status}");
                Console.WriteLine($"版本: {health.Version}");
                Console.WriteLine($"GPU 可用: {health.GpuAvailable}");

                // 2. 获取服务信息
                Console.WriteLine("\n📖 获取服务信息...");
                var info = await client.GetServiceInfoAsync();
                Console.WriteLine($"服务名称: {info.Name}");
                Console.WriteLine($"描述: {info.Description}");
                Console.WriteLine($"支持语言: {string.Join(", ", info.SupportedLanguages)}");

                // 3. 文件识别示例
                Console.WriteLine("\n📄 文件识别示例...");
                var imagePath = @"../demo_image.jpg"; // 请替换为实际图像路径
                
                if (System.IO.File.Exists(imagePath))
                {
                    var result = await client.RecognizeFileAsync(imagePath, "en", false);
                    if (result.Success)
                    {
                        Console.WriteLine($"识别结果: {result.Text}");
                        Console.WriteLine($"平均置信度: {result.AvgConfidence:F3}");
                        Console.WriteLine($"识别到 {result.WordCount} 个文本块");
                    }
                    else
                    {
                        Console.WriteLine($"识别失败: {result.Error}");
                    }
                }
                else
                {
                    Console.WriteLine($"图像文件不存在: {imagePath}");
                }

                // 4. Base64 识别示例
                Console.WriteLine("\n📦 Base64 识别示例...");
                if (System.IO.File.Exists(imagePath))
                {
                    var base64Data = PaddleOCRClient.FileToBase64(imagePath);
                    var result = await client.RecognizeBase64Async(base64Data, "en", false);
                    
                    if (result.Success)
                    {
                        Console.WriteLine($"Base64 识别结果: {result.Text}");
                    }
                }

                // 5. 批量处理示例
                Console.WriteLine("\n📚 批量处理示例...");
                if (System.IO.File.Exists(imagePath))
                {
                    var base64Data = PaddleOCRClient.FileToBase64(imagePath);
                    var batchResult = await client.RecognizeBatchAsync(
                        new[] { base64Data, base64Data }, "en", false);
                    
                    if (batchResult.Success)
                    {
                        Console.WriteLine($"批量处理完成，共处理 {batchResult.Total} 个图像");
                        for (int i = 0; i < batchResult.Results.Length; i++)
                        {
                            Console.WriteLine($"  图像 {i + 1}: {batchResult.Results[i].Text}");
                        }
                    }
                }

                // 6. 获取统计信息
                Console.WriteLine("\n📊 获取统计信息...");
                var stats = await client.GetStatsAsync();
                Console.WriteLine($"总请求数: {stats.TotalRequests}");
                Console.WriteLine($"成功率: {stats.SuccessRate:F1}%");
                Console.WriteLine($"已加载模型: {stats.ModelsLoaded}");

                Console.WriteLine("\n✅ 示例完成!");

            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ 示例执行失败: {ex.Message}");
                Console.WriteLine("\n请确保:");
                Console.WriteLine("1. PaddleOCR 服务已启动 (python paddleocr_service.py)");
                Console.WriteLine("2. 服务地址正确 (http://localhost:8000)");
                Console.WriteLine("3. 网络连接正常");
            }
        }
    }
}
