@echo off
title Bloomberg QQQ Fetcher - Quick Setup
color 0A

echo.
echo =====================================================================
echo                   BLOOMBERG QQQ FETCHER - QUICK SETUP
echo =====================================================================
echo         Using Bloomberg's Official Installation Methods
echo =====================================================================
echo.

REM Set up environment
set BLPAPI_ROOT=%CD%
set PATH=%PATH%;%CD%
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Function to find Python executable
set PYTHON_EXE=

REM Try common Python commands
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    goto :python_found
)

REM Try Windows Store Python
"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :python_found
)

REM Try common installation paths
for %%i in (39 310 311 312 313) do (
    if exist "C:\Python%%i\python.exe" (
        set PYTHON_EXE="C:\Python%%i\python.exe"
        goto :python_found
    )
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%i\python.exe" (
        set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python%%i\python.exe"
        goto :python_found
    )
)

REM Python not found
echo ❌ Python not found!
echo.
echo Please install Python 3.8+ from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:python_found
echo ✅ Found Python: %PYTHON_EXE%
%PYTHON_EXE% --version
echo.

REM Check if we're in the correct directory
if not exist "bloomberg_official_setup.py" (
    echo ❌ ERROR: Not in the correct directory!
    echo Please navigate to the Bloomberg-data-fetcher directory first.
    echo.
    echo Current directory: %CD%
    echo Expected files: bloomberg_official_setup.py
    echo.
    pause
    exit /b 1
)

echo ✅ Project directory confirmed
echo.

REM Show setup options
echo Available setup methods:
echo.
echo   1. 🚀 Official Setup (Recommended) - Uses Bloomberg's pip repository
echo   2. 🔧 Enhanced Setup - Includes fallback methods and diagnostics
echo   3. 🧪 Test Only - Check existing installation
echo   4. 📊 Run Diagnostics - Comprehensive system check
echo   0. ❌ Exit
echo.
set /p choice="👉 Enter your choice (0-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Running Official Bloomberg Setup...
    echo =====================================================================
    %PYTHON_EXE% bloomberg_official_setup.py
) else if "%choice%"=="2" (
    echo.
    echo 🔧 Running Enhanced Setup...
    echo =====================================================================
    %PYTHON_EXE% setup_bloomberg_terminal.py
) else if "%choice%"=="3" (
    echo.
    echo 🧪 Testing Bloomberg API...
    echo =====================================================================
    echo Testing import...
    %PYTHON_EXE% -c "import blpapi; print('✅ Bloomberg API import successful')"
    if not errorlevel 1 (
        echo.
        echo Testing connection...
        %PYTHON_EXE% -c "import blpapi; session = blpapi.Session(); print('✅ Connection test passed' if session.start() else '⚠️  Connection failed - check Terminal'); session.stop() if 'session' in locals() else None"
    )
) else if "%choice%"=="4" (
    echo.
    echo 📊 Running Bloomberg Diagnostics...
    echo =====================================================================
    %PYTHON_EXE% bloomberg_diagnostics.py
) else if "%choice%"=="0" (
    echo.
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Please select 0-4.
    pause
    goto :main_menu
)

:after_setup
echo.
echo =====================================================================
echo                          NEXT STEPS
echo =====================================================================
echo.
echo If setup was successful:
echo   1. Ensure Bloomberg Terminal is running and logged in
echo   2. In Bloomberg Terminal, type: API^<GO^> (not WAPI^<GO^>)
echo   3. Test connection: %PYTHON_EXE% -c "import blpapi; print('Success!')"
echo.
echo Available applications:
echo   🧪 Quick Test: %PYTHON_EXE% scripts\historical_fetch.py --quick-test
echo   🌐 Web App: %PYTHON_EXE% app.py
echo   📊 Full Menu: run_bloomberg_fetcher.bat
echo.
echo For new command sessions, run: setup_environment.bat
echo.
echo 💡 Troubleshooting:
echo   - Run diagnostics: %PYTHON_EXE% bloomberg_diagnostics.py
echo   - Check MANUAL_FIX_GUIDE.md for detailed help
echo.

:main_menu
echo Would you like to:
echo   1. Run another setup option
echo   2. Test Bloomberg API now
echo   3. Launch application menu
echo   0. Exit
echo.
set /p next_choice="👉 Enter your choice (0-3): "

if "%next_choice%"=="1" (
    cls
    goto :python_found
) else if "%next_choice%"=="2" (
    echo.
    echo Testing Bloomberg API...
    %PYTHON_EXE% -c "import blpapi; print('✅ Success!'); session = blpapi.Session(); print('✅ Terminal connected!' if session.start() else '⚠️  Terminal not connected'); session.stop() if 'session' in locals() else None"
    pause
    goto :main_menu
) else if "%next_choice%"=="3" (
    echo.
    echo Launching Bloomberg Fetcher...
    call run_bloomberg_fetcher.bat
) else (
    echo.
    echo 👋 Thank you for using Bloomberg QQQ Fetcher!
    echo.
)

pause