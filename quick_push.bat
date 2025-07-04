@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo 正在推送到 GitHub 仓库...
echo ==========================================
echo.

echo 步骤 1: 初始化 Git 仓库
git init

echo.
echo 步骤 2: 添加所有文件
git add .

echo.
echo 步骤 3: 提交更改
git commit -m "feat: 重大更新 - 完整的Windows兼容性和功能增强"

echo.
echo 步骤 4: 设置远程仓库
git remote remove origin 2>nul
git remote add origin https://github.com/sga-jerrylin/searxng-sga.git

echo.
echo 步骤 5: 推送到 GitHub
git branch -M main
git push -u origin main --force

echo.
echo ==========================================
echo 推送完成！
echo 仓库地址: https://github.com/sga-jerrylin/searxng-sga.git
echo ==========================================
pause 