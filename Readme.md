# PaddleOCR 独立服务统一文档


## 1. 项目简介

PaddleOCR 独立服务是一个高性能、易部署的 OCR 服务包，提供 RESTful API 接口，支持多种编程语言客户端调用。

---

## 2. 特性

- 高性能：基于 PaddleOCR 引擎，支持多种语言识别
- 易部署：支持 Docker、脚本一键部署
- 多语言：支持中、英、法、德等
- 文件和 URL 输入方式
- 跨平台：Windows、Linux、macOS
- 客户端库：Python、Java、C#、Node.js
- 日志、监控、健康检查

---

## 3. 目录结构

```
├── paddleocr_service.py      # 主服务程序
├── config.yaml               # 配置文件
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker Compose
├── manage.py                 # 管理脚本（安装/启动/测试等）
├── clients/                  # 多语言客户端示例
│   ├── python/               # Python 客户端与示例
│   ├── java/                 # Java 客户端与示例
│   ├── csharp/               # C# 客户端与示例
│   └── nodejs/               # Node.js 客户端与示例
```

---

## 4. 快速开始

### 4.1 脚本一键安装（推荐）

```bash
python manage.py setup
```

### 4.2 手动安装

```bash
pip install -r requirements.txt
python paddleocr_service.py
```

### 4.3 Docker 部署

```bash
docker build -t paddleocr-service .
docker run -d -p 8000:8000 paddleocr-service
# 或 docker-compose up -d
```

---

## 5. 配置说明

编辑 `config.yaml` 可自定义服务端口、模型、语言等参数。

---

## 6. API 说明


| 路径               | 方法 | 说明     |
| ------------------ | ---- | -------- |
| `/api/v1/health`   | GET  | 健康检查 |
| `/api/v1/info`     | GET  | 服务信息 |
| `/api/v1/ocr/file` | POST | 文件识别 |
| `/api/v1/ocr/url`  | POST | URL 识别 |
| `/api/v1/models`   | GET  | 模型信息 |
| `/api/v1/stats`    | GET  | 统计信息 |

---

## 7. 客户端使用

### Python

详见 `clients/python/example.py`

### Java

详见 `clients/java/PaddleOCRExample.java`

### C#

详见 `clients/csharp/Example.cs`

### Node.js

详见 `clients/nodejs/example.js`

---

## 8. 常见问题

- 首次启动需联网下载模型，后续本地缓存
- 端口冲突请检查 8000 端口占用
- 详细日志见 logs 目录（首次运行后自动生成）

---

## 9. 维护与贡献

欢迎 issue、PR 反馈与贡献！

---

## 10. 版本与许可证

- PaddleOCR >=2.7
- Python >=3.7
- License: Apache 2.0
