@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo 覆盖 GitHub 仓库的 master 分支
echo ==========================================
echo.
echo 目标仓库: https://github.com/sga-jerrylin/searxng-sga.git
echo 目标分支: master
echo 操作类型: 强制覆盖
echo.

echo 警告: 这将完全覆盖远程 master 分支的内容！
echo 请确认您要执行此操作。
echo.
set /p confirm="输入 'yes' 确认继续: "
if /i not "%confirm%"=="yes" (
    echo 操作已取消。
    pause
    exit /b
)

echo.
echo ==========================================
echo 开始覆盖 master 分支...
echo ==========================================
echo.

echo 步骤 1: 初始化 Git 仓库
git init

echo.
echo 步骤 2: 添加所有文件
git add .

echo.
echo 步骤 3: 提交更改
git commit -m "feat: 重大更新 - 完整的Windows兼容性和功能增强

🎯 主要更新:
✨ 新增功能:
- 完整的Windows兼容性支持 (pwd, uvloop, multiprocessing)
- Dify AI平台原生集成和JSON API
- 微信公众号专搜API (/wechat_search)
- Docker一键部署支持
- 多种启动方式 (简化脚本、Docker、手动)

🔧 技术改进:
- 修复Windows下pwd模块兼容性问题
- 修复uvloop模块在Windows下的问题  
- 修复multiprocessing fork兼容性问题
- 优化搜索引擎配置，禁用不稳定引擎
- 添加连接测试和故障排除工具

📚 文档完善:
- Windows兼容性指南 (WINDOWS_COMPATIBILITY_GUIDE.md)
- Docker部署指南 (DOCKER_DEPLOYMENT_GUIDE.md)
- Dify集成指南 (DIFY_INTEGRATION_GUIDE.md)
- 开源项目指南 (OPEN_SOURCE_GUIDE.md)
- Git部署指南 (GIT_DEPLOYMENT_GUIDE.md)
- 详细的API使用说明 (API_USAGE.md)

🚀 部署优化:
- 自动化启动脚本 (start_searxng_simple.py)
- Docker编排文件 (docker-compose.yml)
- Windows批处理脚本 (start_docker.bat)
- 连接测试工具 (test_connection.py)
- Git部署脚本 (git_setup.bat, git_push.bat)

🛠️ 配置优化:
- 优化searx/settings.yml配置
- Windows专用依赖文件 (requirements-windows.txt)
- Docker专用配置 (docker-settings.yml)
- 限流配置 (limiter.toml)

📊 项目特色:
- 支持200+搜索引擎
- 隐私保护和匿名搜索
- 多语言支持 (中文优化)
- 企业级部署支持
- 完整的开源生态

这个版本已经完全准备好用于生产环境和开源发布！"

echo.
echo 步骤 4: 设置远程仓库
git remote remove origin 2>nul
git remote add origin https://github.com/sga-jerrylin/searxng-sga.git

echo.
echo 步骤 5: 强制覆盖 master 分支
git branch -M master
git push -u origin master --force

echo.
echo ==========================================
echo 🎉 覆盖完成！
echo ==========================================
echo.
echo 您的 SearXNG-SGA 项目已成功覆盖到:
echo https://github.com/sga-jerrylin/searxng-sga.git
echo 分支: master
echo.
echo 🌟 项目亮点:
echo ✅ 完整的 Windows 兼容性支持
echo ✅ Dify AI 平台原生集成  
echo ✅ 微信公众号专搜 API
echo ✅ Docker 一键部署
echo ✅ 详细的文档和使用指南
echo ✅ 专业的开源项目结构
echo.
echo 🚀 现在您可以:
echo 1. 在 GitHub 上查看更新的项目
echo 2. 使用 Issues 进行问题反馈
echo 3. 接受 Pull Requests 贡献
echo 4. 发布 Release 版本
echo 5. 推广您的开源项目
echo.
echo 📱 快速启动:
echo - Windows: python start_searxng_simple.py
echo - Docker: docker-compose up -d
echo - 测试 API: python test_connection.py
echo ==========================================
pause 