Write-Host "========================================" -ForegroundColor Green
Write-Host "推送到GitHub - 覆盖master分支" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. 检查Git状态..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "2. 添加所有更改..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "3. 提交更改..." -ForegroundColor Yellow
git commit -m "feat: 添加时间排序功能

- 新增自动时间排序功能（从最新到最旧）
- 支持sort_by_time参数配置
- 更新README文档，添加详细的时间排序说明
- 强调Dify Docker环境必须使用host.docker.internal
- 添加Python调用示例和Dify集成配置
- 创建时间排序快速参考指南
- 优化API响应格式，包含publishedDate字段"

Write-Host ""
Write-Host "4. 推送到GitHub并覆盖master分支..." -ForegroundColor Yellow
git push origin master --force

Write-Host ""
Write-Host "5. 检查推送结果..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "推送完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "按任意键继续..." 