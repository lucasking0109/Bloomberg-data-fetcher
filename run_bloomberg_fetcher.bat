@echo off
title Bloomberg QQQ Fetcher - One-Click Setup
color 0A

echo.
echo =====================================================================
echo                  BLOOMBERG QQQ FETCHER v2.0
echo =====================================================================
echo     Professional Options Data Fetcher for Bloomberg Terminal
echo =====================================================================
echo.

REM Set up environment
set PATH=%PATH%;%CD%
set PYTHONPATH=%CD%

REM Check if we're in the right directory
if not exist "setup_bloomberg_terminal.py" (
    echo ❌ ERROR: Not in the correct directory!
    echo Please navigate to the bloomberg-qqq-fetcher directory first.
    echo.
    echo Current directory: %CD%
    echo Expected files: setup_bloomberg_terminal.py, run_bloomberg_fetcher.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Project directory confirmed
echo.

REM Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo 📥 PYTHON INSTALLATION REQUIRED
    echo.
    echo Please install Python 3.8+ (64-bit) from:
    echo 🌐 https://www.python.org/downloads/
    echo.
    echo IMPORTANT SETTINGS when installing:
    echo   ✅ Check "Add Python to PATH"
    echo   ✅ Choose "Install for all users" (if possible)
    echo   ✅ Make sure it's 64-bit version
    echo.
    echo After installation, restart this script.
    echo.
    echo Alternative: See BLOOMBERG_TERMINAL_SETUP.md for detailed guide
    echo.
    pause
    exit /b 1
)

REM Get Python version and check if it's 64-bit
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
python -c "import sys; exit(0 if sys.maxsize > 2**32 else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Python must be 64-bit for Bloomberg API!
    echo   Current: 32-bit Python %PYTHON_VERSION%
    echo   Required: 64-bit Python 3.8+
    echo.
    echo Please install 64-bit Python from:
    echo 🌐 https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python %PYTHON_VERSION% (64-bit) detected

REM Test Bloomberg API
echo 🔍 Checking Bloomberg API...
python -c "import blpapi" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Bloomberg API not found - running automatic setup...
    echo.
    python setup_bloomberg_terminal.py
    echo.
    echo 🔄 Testing Bloomberg API again...
    python -c "import blpapi" >nul 2>&1
    if errorlevel 1 (
        echo ❌ Bloomberg API setup failed!
        echo.
        echo Please check:
        echo   1. Python is 64-bit
        echo   2. blpapi wheel file exists in directory
        echo   3. No permission issues
        echo.
        echo See BLOOMBERG_TERMINAL_SETUP.md for troubleshooting
        pause
        exit /b 1
    )
)

echo ✅ Bloomberg API ready!

REM Check Bloomberg Terminal connection
echo 🔍 Checking Bloomberg Terminal...
python -c "import blpapi; session = blpapi.Session(); connected = session.start(); session.stop(); print('Connected' if connected else 'Not Connected')" 2>nul | findstr "Connected" >nul
if errorlevel 1 (
    echo ⚠️  Cannot connect to Bloomberg Terminal
    echo.
    echo Please ensure:
    echo   ✅ Bloomberg Terminal is running
    echo   ✅ You are logged in
    echo   ✅ Type WAPI^<GO^> in Bloomberg to check API status
    echo.
    echo You can still use the calculator and setup tools.
    echo.
) else (
    echo ✅ Bloomberg Terminal connection verified!
)

echo.
echo =====================================================================
echo                        READY TO USE!
echo =====================================================================
echo.
echo Available operations:
echo.
echo   1. 🧪 Test Bloomberg Connection (Quick Test)
echo   2. 📊 API Usage Calculator (Plan your data fetch)
echo   3. 🌐 Launch Web Interface (Full dashboard)
echo   4. 📈 Fetch Historical Data - Quick Test (7 days)
echo   5. 📊 Fetch Historical Data - Standard (30 days)
echo   6. 🔧 Re-run Setup (If something went wrong)
echo   7. 📖 View Documentation
echo   0. ❌ Exit
echo.
set /p choice="👉 Enter your choice (0-7): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Running Bloomberg connection test...
    echo =====================================================================
    python scripts\historical_fetch.py --quick-test
) else if "%choice%"=="2" (
    echo.
    echo 📊 Launching API usage calculator...
    echo =====================================================================
    python api_usage_calculator.py
) else if "%choice%"=="3" (
    echo.
    echo 🌐 Starting web interface...
    echo =====================================================================
    echo 🌐 Open your browser and go to: http://localhost:8501
    echo 🔄 Starting Streamlit server...
    python app.py
) else if "%choice%"=="4" (
    echo.
    echo 📈 Running quick historical test (7 days, ATM only)...
    echo =====================================================================
    python scripts\historical_fetch.py --days 7 --atm-only --export-format csv
) else if "%choice%"=="5" (
    echo.
    echo 📊 Fetching 30 days historical data...
    echo =====================================================================
    echo ⏰ This may take 10-15 minutes depending on API speed
    python scripts\historical_fetch.py --days 30 --export-format parquet
) else if "%choice%"=="6" (
    echo.
    echo 🔧 Re-running setup...
    echo =====================================================================
    python setup_bloomberg_terminal.py
) else if "%choice%"=="7" (
    echo.
    echo 📖 Available documentation:
    echo =====================================================================
    echo   📋 QUICK_START.md - Quick start guide
    echo   🔧 SETUP_GUIDE.md - Detailed setup instructions
    echo   🏢 BLOOMBERG_TERMINAL_SETUP.md - Bloomberg Terminal specific guide
    echo   🤖 AI_ASSISTANT_GUIDE.md - AI assistant reference
    echo   📊 README.md - Complete documentation
    echo.
    echo 💡 Open these files in any text editor to read them
) else if "%choice%"=="0" (
    echo.
    echo 👋 Thank you for using Bloomberg QQQ Fetcher!
    echo.
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Please select 0-7.
)

echo.
echo =====================================================================
echo ✅ Operation completed!
echo =====================================================================
echo.
echo 💡 Tips:
echo   - Run after market close (4:30 PM ET) for best data
echo   - Check API usage with option 2 before large fetches
echo   - Data is saved to the 'data' directory
echo   - Use web interface (option 3) for the best experience
echo.
pause