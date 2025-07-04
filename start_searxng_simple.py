#!/usr/bin/env python3
"""
SearXNG 简化启动脚本 - Windows 版本
"""
import os
import sys
import subprocess

def main():
    print("SearXNG 简化启动脚本")
    print("=" * 30)
    
    # 设置 Python 路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = current_dir
    os.environ['FLASK_APP'] = 'searx.webapp'
    os.environ['FLASK_ENV'] = 'development'
    
    print(f"当前目录: {current_dir}")
    print(f"Python路径: {sys.path[0]}")
    
    try:
        # 测试模块导入
        import searx
        print("✓ SearXNG 模块导入成功")
        
        # 启动Flask应用
        print("\n启动 SearXNG 服务...")
        print("地址: http://localhost:8888")
        print("按 Ctrl+C 停止服务")
        print("-" * 30)
        
        # 直接导入并运行
        from searx.webapp import app
        app.run(host='0.0.0.0', port=8888, debug=True)
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        print("请确保已安装所有依赖包")
        return 1
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 