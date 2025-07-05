@echo off
echo ========================================
echo 推送到GitHub - 覆盖master分支
echo ========================================

echo.
echo 1. 检查Git状态...
git status

echo.
echo 2. 添加所有更改...
git add .

echo.
echo 3. 提交更改...
git commit -m "feat: 添加时间排序功能

- 新增自动时间排序功能（从最新到最旧）
- 支持sort_by_time参数配置
- 更新README文档，添加详细的时间排序说明
- 强调Dify Docker环境必须使用host.docker.internal
- 添加Python调用示例和Dify集成配置
- 创建时间排序快速参考指南
- 优化API响应格式，包含publishedDate字段"

echo.
echo 4. 推送到GitHub并覆盖master分支...
git push origin master --force

echo.
echo 5. 检查推送结果...
git status

echo.
echo ========================================
echo 推送完成！
echo ========================================
pause 