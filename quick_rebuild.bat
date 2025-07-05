@echo off
echo ===================================
echo 快速重建SearXNG Docker容器
echo ===================================

echo 1. 停止现有容器...
docker-compose down

echo 2. 重新构建镜像...
docker-compose build

echo 3. 启动新容器...
docker-compose up -d

echo 4. 等待服务启动...
timeout /t 10 /nobreak >nul

echo 5. 检查容器状态...
docker-compose ps

echo 6. 显示启动日志...
docker-compose logs --tail=10 searxng

echo ===================================
echo 快速重建完成！
echo 测试地址:
echo - 健康检查: http://localhost:8888/healthz
echo - 中文搜索: http://localhost:8888/chinese_search?q=测试
echo ===================================
pause 