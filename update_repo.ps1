Write-Host "========================================" -ForegroundColor Green
Write-Host "SearXNG-SGA 仓库更新脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "目标仓库: https://github.com/sga-jerrylin/searxng-sga.git" -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "1. 检查当前Git状态..." -ForegroundColor Cyan
    git status
    
    Write-Host ""
    Write-Host "2. 初始化Git仓库（如果需要）..." -ForegroundColor Cyan
    git init
    
    Write-Host ""
    Write-Host "3. 添加所有文件到暂存区..." -ForegroundColor Cyan
    git add .
    
    Write-Host ""
    Write-Host "4. 提交更改..." -ForegroundColor Cyan
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
    
    Write-Host ""
    Write-Host "5. 设置远程仓库..." -ForegroundColor Cyan
    git remote remove origin 2>$null
    git remote add origin https://github.com/sga-jerrylin/searxng-sga.git
    
    Write-Host ""
    Write-Host "6. 推送到远程仓库 (覆盖 master 分支)..." -ForegroundColor Cyan
    git branch -M master
    git push -u origin master --force
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "🎉 更新完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "您的SearXNG-SGA项目已成功更新到:" -ForegroundColor Yellow
    Write-Host "https://github.com/sga-jerrylin/searxng-sga.git" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🌟 项目亮点:" -ForegroundColor Yellow
    Write-Host "✅ 完整的Windows兼容性支持" -ForegroundColor Green
    Write-Host "✅ Dify AI平台原生集成" -ForegroundColor Green
    Write-Host "✅ 微信公众号专搜API" -ForegroundColor Green
    Write-Host "✅ Docker一键部署" -ForegroundColor Green
    Write-Host "✅ 详细的文档和使用指南" -ForegroundColor Green
    Write-Host "✅ 专业的开源项目结构" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 现在您可以:" -ForegroundColor Yellow
    Write-Host "1. 在GitHub上查看更新的项目" -ForegroundColor White
    Write-Host "2. 使用Issues进行问题反馈" -ForegroundColor White
    Write-Host "3. 接受Pull Requests贡献" -ForegroundColor White
    Write-Host "4. 发布Release版本" -ForegroundColor White
    Write-Host "5. 推广您的开源项目" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 快速启动:" -ForegroundColor Yellow
    Write-Host "- Windows: python start_searxng_simple.py" -ForegroundColor White
    Write-Host "- Docker: docker-compose up -d" -ForegroundColor White
    Write-Host "- 测试API: python test_connection.py" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green
}
catch {
    Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查Git配置和网络连接" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 