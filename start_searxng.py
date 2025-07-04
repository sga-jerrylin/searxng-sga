#!/usr/bin/env python3
"""
SearXNG 启动脚本
用于快速启动SearXNG服务，支持Dify集成

使用方法:
    python start_searxng.py
    
或者指定端口:
    python start_searxng.py --port 8888
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import flask
        import werkzeug
        import requests
        print("✓ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install flask werkzeug requests")
        return False

def check_config():
    """检查配置文件"""
    config_path = Path("searx/settings.yml")
    if not config_path.exists():
        print("✗ 配置文件不存在: searx/settings.yml")
        return False
    
    print("✓ 配置文件存在")
    return True

def start_server(port=8888, host="0.0.0.0"):
    """启动SearXNG服务器"""
    print(f"启动SearXNG服务器...")
    print(f"地址: http://{host}:{port}")
    print(f"API文档: 参见 DIFY_INTEGRATION_GUIDE.md")
    print(f"微信搜索API: http://{host}:{port}/wechat_search")
    print(f"通用搜索API: http://{host}:{port}/search")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 设置环境变量
    env = os.environ.copy()
    env["SEARXNG_PORT"] = str(port)
    env["SEARXNG_BIND_ADDRESS"] = host
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, "-m", "searx.webapp"
        ], env=env, cwd=".")
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def test_connection(port=8888):
    """测试服务器连接"""
    import requests
    import time
    
    print("等待服务器启动...")
    time.sleep(2)
    
    try:
        # 测试基本连接
        response = requests.get(f"http://localhost:{port}/search?q=test&format=json", timeout=10)
        if response.status_code == 200:
            print("✓ 服务器连接正常")
            return True
        else:
            print(f"✗ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SearXNG 启动脚本")
    parser.add_argument("--port", type=int, default=8888, help="服务器端口 (默认: 8888)")
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)")
    parser.add_argument("--test", action="store_true", help="启动后测试连接")
    args = parser.parse_args()
    
    print("SearXNG 启动脚本")
    print("=" * 30)
    
    # 检查环境
    if not check_dependencies():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    # 显示配置信息
    print(f"端口: {args.port}")
    print(f"绑定地址: {args.host}")
    print(f"项目目录: {os.getcwd()}")
    
    if args.test:
        # 在后台启动服务器并测试
        import threading
        import time
        
        def start_in_background():
            start_server(args.port, args.host)
        
        # 启动后台线程
        server_thread = threading.Thread(target=start_in_background, daemon=True)
        server_thread.start()
        
        # 测试连接
        if test_connection(args.port):
            print("服务器启动成功！")
        
        # 等待用户输入
        try:
            input("按回车键停止服务器...")
        except KeyboardInterrupt:
            pass
    else:
        # 直接启动服务器
        start_server(args.port, args.host)

if __name__ == "__main__":
    main() 