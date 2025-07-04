# PaddleOCR 独立服务统一文档

---

## 1. 项目简介

PaddleOCR 独立服务是一个高性能、易部署的 OCR 服务包，提供 RESTful API 接口，支持多种编程语言客户端调用。

---

## 2. 特性
- 高性能：基于 PaddleOCR 引擎，支持多种语言识别
- 易部署：支持 Docker、脚本一键部署
- 多语言：支持中、英、法、德等
- 批量处理、多种输入方式
- 跨平台：Windows、Linux、macOS
- 客户端库：Python、Java、C#、Node.js
- 日志、监控、健康检查

---

## 3. 目录结构

```
independent_service/
├── paddleocr_service.py      # 主服务程序
├── config.yaml               # 配置文件
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker Compose
├── start.sh / start.bat      # 启动脚本
├── clients/                  # 客户端库
│   ├── python/ java/ csharp/ nodejs/
├── logs/ temp/ models/       # 日志、临时、模型目录
```

---

## 4. 快速开始

### 4.1 脚本一键安装（推荐）
```bash
cd independent_service
python manage.py setup
```

### 4.2 手动安装
```bash
pip install -r requirements.txt
python paddleocr_service.py
```

### 4.3 Docker 部署
```bash
cd independent_service
docker build -t paddleocr-service .
docker run -d -p 8000:8000 paddleocr-service
# 或 docker-compose up -d
```

---

## 5. 配置说明

编辑 `config.yaml` 可自定义服务端口、模型、语言等参数。

---

## 6. API 说明

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/info` | GET | 服务信息 |
| `/api/v1/ocr/file` | POST | 文件识别 |
| `/api/v1/ocr/base64` | POST | Base64 识别 |
| `/api/v1/ocr/url` | POST | URL 识别 |
| `/api/v1/ocr/batch` | POST | 批量识别 |
| `/api/v1/models` | GET | 模型信息 |
| `/api/v1/stats` | GET | 统计信息 |

---

## 7. 客户端使用

### Python
详见 `clients/python/README.md` 和 `example.py`

### Java
详见 `clients/java/README.md` 和 `PaddleOCRExample.java`

### C#
详见 `clients/csharp/README.md` 和 `Example.cs`

### Node.js
详见 `clients/nodejs/README.md` 和 `example.js`

---

## 8. 常见问题
- 首次启动需联网下载模型，后续本地缓存
- 端口冲突请检查 8000 端口占用
- 详细日志见 logs 目录

---

## 9. 维护与贡献
欢迎 issue、PR 反馈与贡献！

---

## 10. 版本与许可证
- PaddleOCR >=2.7
- Python >=3.7
- License: Apache 2.0
