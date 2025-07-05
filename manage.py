import logging
import os
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

# 日志配置，按天分割日志文件，控制台彩色输出
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'paddleocr_service.log'

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[41m',
    }
    RESET = '\033[0m'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_color = self._should_use_color()
    
    def _should_use_color(self):
        """检测是否应该使用颜色输出"""
        # 检查是否在 VSCode 终端
        if 'VSCODE_PID' in os.environ:
            return True
        
        # 检查是否在 Windows Terminal 或其他现代终端
        if os.name == 'nt':
            term = os.environ.get('TERM', '')
            if term or os.environ.get('WT_SESSION'):
                return True
            
            # 检查是否支持 ANSI 转义序列
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用 ANSI 转义序列支持
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        
        return True
    
    def format(self, record):
        msg = super().format(record)
        if self.use_color:
            color = self.COLORS.get(record.levelname, '')
            return f"{color}{msg}{self.RESET}" if color else msg
        return msg

# 文件日志：每天一个文件，保留30天
file_handler = TimedRotatingFileHandler(
    str(LOG_FILE), when='midnight', interval=1, backupCount=30, encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))

# 控制台日志：彩色输出
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColorFormatter('[%(asctime)s] [%(levelname)s] %(message)s'))

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
class ConsoleColor:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    def __init__(self):
        self.use_color = self._should_use_color()
    
    def _should_use_color(self):
        """检测是否应该使用颜色输出"""
        # 检查是否在 VSCode 终端
        if 'VSCODE_PID' in os.environ:
            return True
        
        # 检查是否在 Windows Terminal 或其他现代终端
        if os.name == 'nt':
            term = os.environ.get('TERM', '')
            if term or os.environ.get('WT_SESSION'):
                return True
            
            # 检查是否支持 ANSI 转义序列
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用 ANSI 转义序列支持
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        
        return True

    def color(self, text, color):
        if self.use_color:
            return f"{color}{text}{self.RESET}"
        return text

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PaddleOCR 独立服务管理脚本
提供一键安装、启动、测试等功能
"""

import os
import sys
import subprocess
import time
import platform
import json
import requests
from pathlib import Path

"""
自动切换编码，确保 Windows 控制台输出中文不乱码
"""
# 控制台编码自动切换，兼容 Windows UTF-8
if os.name == "nt":
    try:
        import ctypes
        # 设置控制台输出编码为 UTF-8
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        # 尝试启用 ANSI 转义序列支持（Windows 10+ 支持）
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.system = platform.system().lower()
        self.python_cmd = self._get_python_command()
        
    def _get_python_command(self):
        """获取 Python 命令"""
        for cmd in ['python', 'python3', 'py']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return 'python'
    
    def _run_command(self, command, shell=True, cwd=None):
        """执行命令"""
        try:
            if cwd is None:
                cwd = self.script_dir
            logging.info(f"执行命令: {command}")
            result = subprocess.run(command, shell=shell, cwd=cwd, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("命令执行成功")
                return True, result.stdout
            else:
                logging.error(f"命令执行失败: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logging.error(f"命令执行异常: {e}")
            return False, str(e)
    
    def check_dependencies(self):
        """检查依赖"""
        logging.info("检查系统依赖...")
        # 检查 Python
        success, output = self._run_command(f"{self.python_cmd} --version")
        if not success:
            logging.error("Python 未安装或不可用")
            return False
        logging.info(f"Python 版本: {output.strip()}")
        # 检查 pip
        success, output = self._run_command(f"{self.python_cmd} -m pip --version")
        if not success:
            logging.error("pip 未安装或不可用")
            return False
        logging.info(f"pip 版本: {output.strip()}")
        return True
    
    def install_dependencies(self):
        """安装依赖"""
        logging.info("安装 Python 依赖...")
        requirements_file = self.script_dir / "requirements.txt"
        if not requirements_file.exists():
            logging.error("requirements.txt 文件不存在")
            return False
        mirrors = [
            "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "https://mirrors.aliyun.com/pypi/simple/",
            "https://pypi.douban.com/simple/",
        ]
        for mirror in mirrors:
            logging.info(f"尝试使用镜像: {mirror}")
            command = f"{self.python_cmd} -m pip install -r requirements.txt -i {mirror}"
            success, output = self._run_command(command)
            if success:
                logging.info("依赖安装成功")
                return True
            else:
                logging.warning(f"镜像 {mirror} 安装失败，尝试下一个...")
        logging.info("尝试官方源...")
        command = f"{self.python_cmd} -m pip install -r requirements.txt"
        success, output = self._run_command(command)
        if success:
            logging.info("依赖安装成功")
            return True
        else:
            logging.error("依赖安装失败")
            return False
    
    def check_models_downloaded(self):
        """检查模型是否已下载"""
        logging.info("检查模型文件...")
        import os
        # 使用当前项目目录下的 models 文件夹
        model_dir = self.script_dir / "models"
        logging.info(f"检查模型目录: {model_dir}")
        
        if not model_dir.exists():
            logging.warning("模型目录不存在，首次启动需要下载模型")
            return False
        
        # 统计各种模型文件
        model_files = []
        model_count = {'pdmodel': 0, 'pdiparams': 0, 'yml': 0}
        
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                if file.endswith('.pdmodel'):
                    model_count['pdmodel'] += 1
                    model_files.append(os.path.join(root, file))
                elif file.endswith('.pdiparams'):
                    model_count['pdiparams'] += 1
                    model_files.append(os.path.join(root, file))
                elif file.endswith('.yml'):
                    model_count['yml'] += 1
                    model_files.append(os.path.join(root, file))
        
        total_files = len(model_files)
        logging.info(f"发现模型文件: {total_files} 个 (pdmodel: {model_count['pdmodel']}, pdiparams: {model_count['pdiparams']}, yml: {model_count['yml']})")
        
        # 检查是否有足够的模型文件 (至少需要一些基本模型)
        if model_count['pdmodel'] < 3 or model_count['pdiparams'] < 3:
            logging.warning("模型文件不完整，首次启动需要下载模型")
            return False
        
        logging.info("模型文件检查完成，模型已就绪")
        return True
    
    def create_directories(self):
        """创建必要的目录"""
        logging.info("创建目录...")
        directories = ['logs', 'temp', 'models']
        for directory in directories:
            dir_path = self.script_dir / directory
            dir_path.mkdir(exist_ok=True)
            logging.info(f"创建目录: {directory}")
        return True
    
    def start_service(self):
        """启动服务"""
        logging.info("启动 PaddleOCR 服务...")
        service_file = self.script_dir / "paddleocr_service.py"
        if not service_file.exists():
            logging.error("服务文件不存在")
            return False
        if self._is_port_occupied(8000):
            logging.warning("端口 8000 已被占用，服务可能已在运行")
            return False
        
        models_exist = self.check_models_downloaded()
        if not models_exist:
            logging.warning("首次启动需要下载模型文件，这可能需要几分钟时间...")
            logging.warning("   模型将从 Hugging Face 或 BOS 下载并缓存到本地")
            logging.warning("   下载完成后，后续启动将快速完成")
            wait_time = 60
        else:
            logging.info("模型文件已存在，正在启动服务...")
            wait_time = 20
        
        command = f"{self.python_cmd} {service_file}"
        if self.system == "windows":
            subprocess.Popen(command, shell=True, cwd=self.script_dir)
        else:
            subprocess.Popen(command, shell=True, cwd=self.script_dir,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        logging.info(f"等待服务启动... (预计需要 {wait_time} 秒)")
        if not models_exist:
            logging.warning("   正在下载模型文件，请耐心等待...")
        
        time.sleep(wait_time)
        
        if self._check_service_health():
            logging.info("服务启动成功")
            return True
        else:
            logging.error("服务启动失败")
            return False
    
    def _is_port_occupied(self, port):
        """检查端口是否被占用"""
        try:
            response = requests.get(f"http://localhost:{port}/api/v1/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_service_health(self):
        """检查服务健康状态"""
        for i in range(3):
            try:
                response = requests.get("http://localhost:8000/api/v1/health", timeout=3)
                if response.status_code == 200:
                    return True
            except:
                pass
            if i < 2:
                logging.info(f"   尝试连接服务中... ({i+1}/3)")
            time.sleep(1)
        return False
    

    def test_service(self):
        """仅测试 ocr/file 文件上传接口"""
        logging.info("测试服务文件识别接口...")
        if not self._check_service_health():
            logging.error("服务健康检查失败")
            return False
        logging.info("服务健康检查通过")

        # 只测 ocr/file
        test_img_path = str(self.script_dir / 'temp' / 'test.png')
        if not os.path.exists(test_img_path):
            logging.error(f"测试图片不存在: {test_img_path}")
            return False
        try:
            with open(test_img_path, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                data = {'lang': 'ch', 'use_gpu': 'false'}
                resp = requests.post("http://localhost:8000/api/v1/ocr/file", files=files, data=data, timeout=10)
            logging.info(f"[ocr/file] 状态码: {resp.status_code}, 返回: {resp.json()}")
            if resp.status_code != 200 or not resp.json().get('success'):
                logging.error("ocr/file 接口测试失败")
                return False
        except Exception as e:
            logging.error(f"ocr/file 接口异常: {e}")
            return False

        logging.info("文件识别接口测试通过")
        return True
    
    def stop_service(self):
        """停止服务"""
        logging.info("停止服务...")
        if self.system == "windows":
            # 只杀掉 paddleocr_service.py 进程
            try:
                result = subprocess.run(
                    'wmic process where "CommandLine like \'%paddleocr_service.py%\' and not CommandLine like \'%manage.py%\'" get ProcessId,CommandLine /FORMAT:LIST',
                    shell=True, capture_output=True, text=True)
                pids = []
                for line in result.stdout.splitlines():
                    if line.startswith("ProcessId="):
                        pid = line.split("=", 1)[1].strip()
                        if pid:
                            pids.append(pid)
                if pids:
                    for pid in pids:
                        logging.info(f"终止进程 PID: {pid}")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                else:
                    logging.info("未找到 paddleocr_service.py 进程，无需终止")
                    logging.info("服务已停止")
                    return True
            except Exception as e:
                logging.error(f"终止进程时出错: {e}")
        else:
            command = "pkill -f paddleocr_service.py"
            self._run_command(command)
        time.sleep(2)
        # 优化：如果服务已停，不再尝试连接
        if not self._check_service_health():
            logging.info("服务已停止")
            return True
        # 若还在运行，再尝试重试
        for i in range(3):
            time.sleep(5)
            logging.info(f"    尝试连接服务中... ({i+1}/3)")
            if not self._check_service_health():
                logging.info("服务已停止")
                return True
        logging.warning("服务可能仍在运行")
        return False
    
    def show_status(self):
        """显示服务状态"""
        logging.info("检查服务状态...")
        if self._check_service_health():
            logging.info("服务正在运行")
            try:
                response = requests.get("http://localhost:8000/api/v1/info", timeout=5)
                if response.status_code == 200:
                    info = response.json()
                    data = info.get('data', {})
                    logging.info(f"   服务地址: http://localhost:8000")
                    logging.info(f"   版本: {data.get('version', 'N/A')}")
                    logging.info(f"   状态: {data.get('status', 'N/A')}")
                    logging.info(f"   支持语言: {data.get('supported_languages', [])}")
            except:
                pass
        else:
            logging.error("服务未运行")
    
    def full_setup(self):
        """完整安装流程"""
        logging.info("开始完整安装流程...")
        logging.info("=" * 50)
        steps = [
            ("检查系统依赖", self.check_dependencies),
            ("创建目录", self.create_directories),
            ("安装 Python 依赖", self.install_dependencies),
            ("启动服务", self.start_service),
            ("测试服务", self.test_service),
        ]
        for step_name, step_func in steps:
            logging.info(f"\n{step_name}...")
            if not step_func():
                logging.error(f"{step_name} 失败，安装中止")
                return False
        logging.info("\n" + "=" * 50)
        logging.info("PaddleOCR 独立服务安装完成！")
        logging.info("\n使用说明：")
        logging.info("   • 服务地址: http://localhost:8000")
        logging.info("   • 健康检查: http://localhost:8000/api/v1/health")
        logging.info("   • 服务信息: http://localhost:8000/api/v1/info")
        logging.info("   • API 文档: 请查看 DEPLOYMENT_GUIDE.md")
        logging.info("\n管理命令：")
        logging.info(f"   • 启动服务: {self.python_cmd} manage.py start")
        logging.info(f"   • 停止服务: {self.python_cmd} manage.py stop")
        logging.info(f"   • 查看状态: {self.python_cmd} manage.py status")
        logging.info(f"   • 测试服务: {self.python_cmd} manage.py test")
        return True

def main():
    """主函数"""
    manager = ServiceManager()
    
    if len(sys.argv) < 2:
        logging.info("PaddleOCR 独立服务管理脚本")
        logging.info("\n用法:")
        logging.info("  python manage.py <command>")
        logging.info("\n可用命令:")
        logging.info("  setup   - 完整安装配置")
        logging.info("  start   - 启动服务")
        logging.info("  stop    - 停止服务")
        logging.info("  restart - 重启服务")
        logging.info("  status  - 查看状态")
        logging.info("  test    - 测试服务")
        logging.info("  install - 安装依赖")
        logging.info("\n示例:")
        logging.info("  python manage.py setup    # 完整安装")
        logging.info("  python manage.py start    # 启动服务")
        logging.info("  python manage.py status   # 查看状态")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        manager.full_setup()
    elif command == "start":
        if not manager.check_dependencies():
            logging.error("依赖检查失败")
            return
        manager.create_directories()
        manager.start_service()
    elif command == "stop":
        manager.stop_service()
    elif command == "restart":
        manager.stop_service()
        time.sleep(2)
        if not manager.check_dependencies():
            logging.error("依赖检查失败")
            return
        manager.create_directories()
        manager.start_service()
    elif command == "status":
        manager.show_status()
    elif command == "test":
        manager.test_service()
    elif command == "install":
        if not manager.check_dependencies():
            logging.error("依赖检查失败")
            return
        manager.install_dependencies()
    else:
        logging.error(f"未知命令: {command}")
        logging.warning("使用 'python manage.py' 查看帮助")

if __name__ == "__main__":
    main()
