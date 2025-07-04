#!/bin/bash

echo "======================================"
echo "SearXNG Docker 启动脚本"
echo "======================================"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "✅ Docker 运行正常"

# 检查docker-compose是否存在
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装"
    exit 1
fi

echo "✅ docker-compose 可用"

# 创建外部网络（如果不存在）
if ! docker network ls | grep -q "dify-network"; then
    echo "🔧 创建 dify-network 网络..."
    docker network create dify-network
    echo "✅ 网络创建成功"
else
    echo "✅ dify-network 网络已存在"
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建并启动服务
echo "🏗️  构建并启动 SearXNG 服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ SearXNG 服务启动成功！"
    echo ""
    echo "======================================"
    echo "🎉 服务信息"
    echo "======================================"
    echo "🌐 SearXNG 地址: http://localhost:8888"
    echo "🔍 通用搜索API: http://localhost:8888/search"
    echo "📱 微信专搜API: http://localhost:8888/wechat_search"
    echo ""
    echo "======================================"
    echo "🔧 Dify 配置"
    echo "======================================"
    echo "工具URL: http://localhost:8888/search"
    echo "参数: q={{query}}&format=json&categories=general"
    echo ""
    echo "微信专搜URL: http://localhost:8888/wechat_search"
    echo "参数: q={{query}}"
    echo ""
    echo "======================================"
    echo "📋 管理命令"
    echo "======================================"
    echo "查看日志: docker-compose logs -f searxng"
    echo "停止服务: docker-compose down"
    echo "重启服务: docker-compose restart"
    echo "======================================"
else
    echo "❌ 服务启动失败，请检查日志:"
    echo "docker-compose logs searxng"
    exit 1
fi 