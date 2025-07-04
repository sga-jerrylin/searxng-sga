@echo off
echo ========================================
echo SearXNG-SGA Git 推送脚本
echo ========================================

echo 请输入您的GitHub仓库URL（例如：https://github.com/username/repo.git）：
set /p REPO_URL=

echo.
echo 正在推送到仓库: %REPO_URL%
echo.

echo 1. 检查Git仓库状态...
git status

echo.
echo 2. 添加所有更改到暂存区...
git add .

echo.
echo 3. 提交更改...
git commit -m "feat: 更新SearXNG-SGA项目

✨ 新增功能:
- 完整的Windows兼容性支持
- Dify AI平台集成
- 微信公众号专搜API
- Docker一键部署
- 详细的文档和使用指南

🔧 技术改进:
- 修复Windows下pwd模块兼容性问题
- 修复uvloop模块在Windows下的问题
- 修复multiprocessing fork兼容性问题
- 优化搜索引擎配置
- 添加连接测试工具

📚 文档更新:
- Windows兼容性指南
- Docker部署指南
- Dify集成指南
- 开源项目指南
- API使用说明

🚀 部署优化:
- 支持多种启动方式
- 自动化部署脚本
- 完整的错误处理
- 性能优化建议"

echo.
echo 4. 设置远程仓库...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo 5. 推送到远程仓库...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo 推送完成！
echo.
echo 您的项目已成功推送到: %REPO_URL%
echo.
echo 🎉 现在您可以在GitHub上查看您的开源项目了！
echo.
echo 主要特性:
echo ✅ 完整的Windows兼容性支持
echo ✅ Dify AI平台原生集成
echo ✅ 微信公众号专搜API
echo ✅ Docker一键部署
echo ✅ 详细的文档和示例
echo ========================================
pause 