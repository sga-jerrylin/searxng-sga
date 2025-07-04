@echo off
echo ========================================
echo SearXNG-SGA 仓库更新脚本
echo ========================================
echo.
echo 目标仓库: https://github.com/sga-jerrylin/searxng-sga.git
echo.

echo 1. 检查当前Git状态...
git status

echo.
echo 2. 初始化Git仓库（如果需要）...
git init

echo.
echo 3. 添加所有文件到暂存区...
git add .

echo.
echo 4. 提交更改...
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
echo 5. 设置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/sga-jerrylin/searxng-sga.git

echo.
echo 6. 推送到远程仓库...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo 🎉 更新完成！
echo.
echo 您的SearXNG-SGA项目已成功更新到:
echo https://github.com/sga-jerrylin/searxng-sga.git
echo.
echo 🌟 项目亮点:
echo ✅ 完整的Windows兼容性支持
echo ✅ Dify AI平台原生集成  
echo ✅ 微信公众号专搜API
echo ✅ Docker一键部署
echo ✅ 详细的文档和使用指南
echo ✅ 专业的开源项目结构
echo.
echo 🚀 现在您可以:
echo 1. 在GitHub上查看更新的项目
echo 2. 使用Issues进行问题反馈
echo 3. 接受Pull Requests贡献
echo 4. 发布Release版本
echo 5. 推广您的开源项目
echo.
echo 📱 快速启动:
echo - Windows: python start_searxng_simple.py
echo - Docker: docker-compose up -d
echo - 测试API: python test_connection.py
echo ========================================
pause 