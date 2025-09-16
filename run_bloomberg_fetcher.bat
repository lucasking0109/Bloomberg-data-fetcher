@echo off
echo ========================================
echo Bloomberg QQQ Fetcher
echo ========================================

REM Set up environment
set PATH=%PATH%;%CD%
set PYTHONPATH=%CD%

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.6+ (64-bit)
    pause
    exit /b 1
)

REM Test Bloomberg API
python -c "import blpapi" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Bloomberg API not found
    echo Running setup script...
    python setup_bloomberg_terminal.py
    echo.
    echo Please run this script again after setup
    pause
    exit /b 1
)

echo Bloomberg API ready!
echo.
echo Available commands:
echo   1. Test Bloomberg Connection
echo   2. Run API Usage Calculator
echo   3. Run Web Interface
echo   4. Fetch Historical Data (Quick Test)
echo   5. Fetch 30 days historical data
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Running Bloomberg connection test...
    python scripts\historical_fetch.py --quick-test
) else if "%choice%"=="2" (
    echo Running API usage calculator...
    python api_usage_calculator.py
) else if "%choice%"=="3" (
    echo Starting web interface...
    echo Open http://localhost:8501 in your browser
    python app.py
) else if "%choice%"=="4" (
    echo Running quick test (7 days, ATM only)...
    python scripts\historical_fetch.py --days 7 --atm-only --export-format csv
) else if "%choice%"=="5" (
    echo Fetching 30 days historical data...
    python scripts\historical_fetch.py --days 30 --export-format parquet
) else (
    echo Invalid choice. Please select 1-5.
)

echo.
echo Operation completed!
pause