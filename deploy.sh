#!/bin/bash

# SearXNG 部署脚本 - 包含微信搜索功能
# 使用方法: ./deploy.sh

echo "开始部署 SearXNG（包含微信搜索功能）..."

# 创建必要的目录结构
echo "创建目录结构..."
mkdir -p searx

# 复制配置文件
echo "复制配置文件..."
cp docker-settings.yml searx/settings.yml
cp limiter.toml searx/limiter.toml

# 创建 engines 目录并复制微信搜索引擎
echo "设置微信搜索引擎..."
mkdir -p searx/engines
cp searx/engines/wechat.py searx/engines/wechat.py

# 生成随机密钥
echo "生成随机密钥..."
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/your-custom-secret-key-here/$SECRET_KEY/g" searx/settings.yml

echo "配置完成！"
echo "生成的密钥: $SECRET_KEY"
echo ""
echo "接下来请执行以下命令启动服务："
echo "docker-compose down"
echo "docker-compose up -d"
echo ""
echo "服务启动后，访问 http://localhost:8081 即可使用"
echo "使用 !wx 前缀可以专门搜索微信公众号内容"
echo ""
echo "如需查看日志，执行: docker-compose logs -f searxng" 