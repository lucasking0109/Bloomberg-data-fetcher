@echo off
chcp 65001 > nul
echo ══════════════════════════════════════════════════════════
echo       🛡️ Safe Bloomberg Fetcher - 防錯版執行器
echo ══════════════════════════════════════════════════════════
echo.

REM 執行防錯版腳本
python safe_run.py

REM 如果失敗，嘗試 python3
if errorlevel 1 (
    echo.
    echo 嘗試使用 python3...
    python3 safe_run.py
)

REM 如果還是失敗，嘗試 py
if errorlevel 1 (
    echo.
    echo 嘗試使用 py...
    py safe_run.py
)

pause