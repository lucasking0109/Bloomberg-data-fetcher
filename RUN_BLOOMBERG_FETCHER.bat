@echo off
echo ============================================================
echo     Bloomberg QQQ Options Fetcher - 一鍵執行
echo ============================================================
echo.

REM 執行Python腳本
python run_bloomberg_fetcher.py

REM 如果Python執行失敗，嘗試python3
if errorlevel 1 (
    echo.
    echo 嘗試使用 python3...
    python3 run_bloomberg_fetcher.py
)

pause