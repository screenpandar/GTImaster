@echo off
chcp 65001 >nul

REM 若未以管理员运行，则请求提升权限后重新启动
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

set "ROOT=%~dp0"
set "TARGET=%USERPROFILE%\.EasyOCR"

echo ========== GTImaster 一键部署 ==========

REM 1. 复制 .EasyOCR 到用户目录
set "SOURCE=%ROOT%.EasyOCR"
if exist "%SOURCE%" (
    echo [1/3] 正在复制 .EasyOCR 到用户目录...
    xcopy "%SOURCE%" "%TARGET%\" /E /I /Y /Q >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo       .EasyOCR 已复制到：%TARGET%
    ) else (
        echo       复制 .EasyOCR 时出错，请检查权限。
    )
) else (
    echo [1/3] 未找到 .EasyOCR 文件夹，跳过。若需 OCR 请将 .EasyOCR 放在本脚本同目录后重新运行。
)

REM 2. 安装依赖
echo [2/3] 正在安装 Python 依赖...
if exist "%ROOT%requirements.txt" (
    pip install -r "%ROOT%requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo       pip 安装失败，请检查网络或 Python 环境。
        pause
        exit /b 1
    )
) else (
    echo       未找到 requirements.txt，跳过依赖安装。
)

echo [3/3] 启动 GTImaster...
cd /d "%ROOT%"
python GTImaster.py
if %ERRORLEVEL% neq 0 (
    echo 启动失败，请确认已安装 Python 及依赖。
)
pause
