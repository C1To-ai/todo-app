@echo off
chcp 65001 >nul
title 待办事项管理器

echo ========================================
echo   待办事项管理器 - 桌面版
echo ========================================
echo.

cd /d "D:\桌面\Code\todo-app"

echo 🚀  正在启动...
python desktop_app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败，请检查 Python 安装
    echo.
    pause
)
