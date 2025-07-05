@echo off
echo ===================================
echo 修复并重建SearXNG Docker容器
echo ===================================

echo 已修复的问题:
echo 1. SearchQuery.results_per_page 属性错误
echo 2. HTTP协议被禁用的问题
echo 3. limiter.toml 配置格式错误
echo 4. radio_browser 和 wikidata 引擎错误
echo.

echo 1. 停止现有容器...
docker-compose down

echo 2. 重新构建镜像...
docker-compose build

echo 3. 启动新容器...
docker-compose up -d

echo 4. 等待服务启动...
timeout /t 15 /nobreak >nul

echo 5. 检查容器状态...
docker-compose ps

echo 6. 显示启动日志...
docker-compose logs --tail=15 searxng

echo ===================================
echo 修复并重建完成！
echo.
echo 测试地址:
echo - 健康检查: http://localhost:8888/healthz
echo - 中文搜索: http://localhost:8888/chinese_search?q=测试&limit=3
echo - Dify调用: http://host.docker.internal:8888/chinese_search?q=测试&limit=3
echo ===================================

echo 正在测试API...
timeout /t 3 /nobreak >nul

curl -s "http://localhost:8888/healthz" >nul
if %errorlevel%==0 (
    echo ✅ 健康检查通过
) else (
    echo ❌ 健康检查失败
)

pause 