@echo off
set REMOTE_URL=https://github.com/sga-jerrylin/searxng-sga.git

echo ========================================
echo 推送到GitHub - 覆盖master分支
echo ========================================

echo.
echo 1. 设置远程仓库地址...
git remote set-url origin %REMOTE_URL%

echo.
echo 2. 拉取最新master分支，避免冲突...
git pull origin master --rebase

echo.
echo 3. 添加所有更改...
git add .

echo.
echo 4. 提交更改...
git commit -m "feat: 添加时间排序功能\n\n- 新增自动时间排序功能（从最新到最旧）\n- 支持sort_by_time参数配置\n- 更新README文档，添加详细的时间排序说明\n- 强调Dify Docker环境必须使用host.docker.internal\n- 添加Python调用示例和Dify集成配置\n- 创建时间排序快速参考指南\n- 优化API响应格式，包含publishedDate字段"

echo.
echo 5. 强制推送到GitHub master分支...
git push origin master --force

echo.
echo 6. 检查推送结果...
git status

echo.
echo ========================================
echo 推送完成！
echo ========================================
pause 