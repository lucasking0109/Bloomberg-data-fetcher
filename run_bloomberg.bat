@echo off
title Bloomberg QQQ Options Fetcher
color 0A

echo.
echo ============================================================
echo           BLOOMBERG QQQ OPTIONS FETCHER
echo ============================================================
echo.
echo This tool helps you fetch QQQ options data from Bloomberg
echo.
echo Prerequisites:
echo   - Bloomberg Terminal running and logged in
echo   - Bloomberg API library installed
echo.
echo ============================================================
echo.

:menu
echo Available Commands:
echo.
echo   1. Test Bloomberg Connection
echo   2. Fetch Daily Options Data
echo   3. Fetch Historical Data (60 days)
echo   4. Run All Operations
echo   5. Show Data Status
echo   6. Setup Bloomberg API
echo   0. Exit
echo.
set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto daily
if "%choice%"=="3" goto historical
if "%choice%"=="4" goto all
if "%choice%"=="5" goto status
if "%choice%"=="6" goto setup
if "%choice%"=="0" goto exit
echo Invalid choice. Please try again.
echo.
goto menu

:test
echo.
echo Testing Bloomberg API connection...
echo ============================================================
python scripts/run_all.py --test
echo.
pause
goto menu

:daily
echo.
echo Fetching daily QQQ options data...
echo ============================================================
python scripts/run_all.py --daily
echo.
pause
goto menu

:historical
echo.
echo Fetching historical QQQ options data...
echo ============================================================
python scripts/run_all.py --historical
echo.
pause
goto menu

:all
echo.
echo Running complete workflow...
echo ============================================================
python scripts/run_all.py --all
echo.
pause
goto menu

:status
echo.
echo Current data status:
echo ============================================================
python scripts/run_all.py --status
echo.
pause
goto menu

:setup
echo.
echo Bloomberg API Setup...
echo ============================================================
python scripts/setup_bloomberg.py
echo.
pause
goto menu

:exit
echo.
echo Thank you for using Bloomberg QQQ Options Fetcher!
echo.
pause
exit
