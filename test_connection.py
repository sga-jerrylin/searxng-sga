#!/usr/bin/env python3
"""
SearXNG 连接测试脚本
用于验证SearXNG服务是否正常运行，以及Dify是否能正常连接

使用方法:
    python test_connection.py
    python test_connection.py --host localhost --port 8888
"""

import argparse
import requests
import json
import time
import sys

def test_basic_connection(host, port):
    """测试基本连接"""
    url = f"http://{host}:{port}"
    print(f"测试基本连接: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✓ 基本连接成功")
            return True
        else:
            print(f"✗ 连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

def test_search_api(host, port):
    """测试搜索API"""
    url = f"http://{host}:{port}/search"
    params = {
        'q': 'SearXNG测试',
        'format': 'json',
        'categories': 'general'
    }
    
    print(f"测试搜索API: {url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', []))
            print(f"✓ 搜索API成功，返回 {results_count} 个结果")
            
            # 显示第一个结果（如果有）
            if results_count > 0:
                first_result = data['results'][0]
                print(f"  示例结果: {first_result.get('title', 'N/A')}")
                print(f"  URL: {first_result.get('url', 'N/A')}")
            
            return True
        else:
            print(f"✗ 搜索API失败，状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"✗ 搜索API失败: {e}")
        return False

def test_wechat_api(host, port):
    """测试微信搜索API"""
    url = f"http://{host}:{port}/wechat_search"
    params = {
        'q': '微信公众号测试'
    }
    
    print(f"测试微信搜索API: {url}")
    print(f"参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', []))
            print(f"✓ 微信搜索API成功，返回 {results_count} 个结果")
            
            # 显示第一个结果（如果有）
            if results_count > 0:
                first_result = data['results'][0]
                print(f"  示例结果: {first_result.get('title', 'N/A')}")
                print(f"  URL: {first_result.get('url', 'N/A')}")
            
            return True
        else:
            print(f"✗ 微信搜索API失败，状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"✗ 微信搜索API失败: {e}")
        return False

def test_dify_compatibility(host, port):
    """测试Dify兼容性"""
    print("测试Dify兼容性...")
    
    # 测试不同的参数组合
    test_cases = [
        {
            'name': 'Dify标准格式',
            'params': {'q': 'SearXNG', 'format': 'json'}
        },
        {
            'name': 'Dify时间范围',
            'params': {'q': 'SearXNG', 'time_range': 'day', 'format': 'json', 'categories': 'general'}
        },
        {
            'name': 'Dify POST请求',
            'method': 'POST',
            'params': {'q': 'SearXNG', 'format': 'json'}
        }
    ]
    
    success_count = 0
    for case in test_cases:
        print(f"\n  测试: {case['name']}")
        try:
            url = f"http://{host}:{port}/search"
            method = case.get('method', 'GET')
            
            if method == 'GET':
                response = requests.get(url, params=case['params'], timeout=20)
            else:
                response = requests.post(url, data=case['params'], timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    print(f"    ✓ {case['name']} 成功")
                    success_count += 1
                else:
                    print(f"    ✗ {case['name']} 响应格式异常")
            else:
                print(f"    ✗ {case['name']} 失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"    ✗ {case['name']} 异常: {e}")
    
    if success_count == len(test_cases):
        print("✓ Dify兼容性测试全部通过")
        return True
    else:
        print(f"✗ Dify兼容性测试部分失败 ({success_count}/{len(test_cases)})")
        return False

def generate_dify_config(host, port):
    """生成Dify配置建议"""
    print("\n" + "="*50)
    print("Dify配置建议:")
    print("="*50)
    
    config = {
        "工具名称": "SearXNG搜索",
        "基础URL": f"http://{host}:{port}",
        "API端点": {
            "通用搜索": "/search",
            "微信专搜": "/wechat_search"
        },
        "参数配置": {
            "q": "搜索关键词",
            "format": "json",
            "categories": "general",
            "time_range": "可选：day, week, month, year"
        },
        "请求方法": "GET 或 POST",
        "超时设置": "30秒"
    }
    
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    print("\nDify工具配置示例:")
    print(f"URL: http://{host}:{port}/search")
    print("参数: q={{{{query}}}}&format=json&categories=general")

def main():
    parser = argparse.ArgumentParser(description="SearXNG 连接测试脚本")
    parser.add_argument("--host", default="localhost", help="SearXNG主机地址")
    parser.add_argument("--port", type=int, default=8888, help="SearXNG端口")
    parser.add_argument("--skip-search", action="store_true", help="跳过搜索测试")
    args = parser.parse_args()
    
    print("SearXNG 连接测试")
    print("="*30)
    print(f"目标地址: {args.host}:{args.port}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_passed = True
    
    # 测试基本连接
    if not test_basic_connection(args.host, args.port):
        all_passed = False
        print("\n建议:")
        print("1. 确认SearXNG服务是否正在运行")
        print("2. 检查端口是否正确")
        print("3. 检查防火墙设置")
        print("4. 尝试运行: python start_searxng.py")
    
    if not args.skip_search and all_passed:
        print()
        # 测试搜索API
        if not test_search_api(args.host, args.port):
            all_passed = False
        
        print()
        # 测试微信搜索API
        if not test_wechat_api(args.host, args.port):
            print("注意: 微信搜索可能需要特定的搜索引擎配置")
        
        print()
        # 测试Dify兼容性
        if not test_dify_compatibility(args.host, args.port):
            all_passed = False
    
    # 生成配置建议
    if all_passed:
        generate_dify_config(args.host, args.port)
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ 所有测试通过！SearXNG已准备好与Dify集成")
    else:
        print("✗ 部分测试失败，请检查上述建议")
        print("详细故障排除指南: DIFY_INTEGRATION_GUIDE.md")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main() 