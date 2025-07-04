@echo off
chcp 65001 > nul

echo ======================================
echo SearXNG Docker 启动脚本
echo ======================================
echo.

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未运行，请先启动 Docker
    pause
    exit /b 1
)

echo ✅ Docker 运行正常

REM 检查docker-compose是否存在
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose 未安装
    pause
    exit /b 1
)

echo ✅ docker-compose 可用

REM 创建外部网络（如果不存在）
docker network ls | findstr "dify-network" >nul
if %errorlevel% neq 0 (
    echo 🔧 创建 dify-network 网络...
    docker network create dify-network
    echo ✅ 网络创建成功
) else (
    echo ✅ dify-network 网络已存在
)

REM 停止现有容器
echo 🛑 停止现有容器...
docker-compose down

REM 构建并启动服务
echo 🏗️  构建并启动 SearXNG 服务...
docker-compose up --build -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak > nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ SearXNG 服务启动成功！
    echo.
    echo ======================================
    echo 🎉 服务信息
    echo ======================================
    echo 🌐 SearXNG 地址: http://localhost:8888
    echo 🔍 通用搜索API: http://localhost:8888/search
    echo 📱 微信专搜API: http://localhost:8888/wechat_search
    echo.
    echo ======================================
    echo 🔧 Dify 配置
    echo ======================================
    echo 工具URL: http://localhost:8888/search
    echo 参数: q={{query}}&format=json&categories=general
    echo.
    echo 微信专搜URL: http://localhost:8888/wechat_search
    echo 参数: q={{query}}
    echo.
    echo ======================================
    echo 📋 管理命令
    echo ======================================
    echo 查看日志: docker-compose logs -f searxng
    echo 停止服务: docker-compose down
    echo 重启服务: docker-compose restart
    echo ======================================
) else (
    echo ❌ 服务启动失败，请检查日志:
    echo docker-compose logs searxng
    pause
    exit /b 1
)

pause 