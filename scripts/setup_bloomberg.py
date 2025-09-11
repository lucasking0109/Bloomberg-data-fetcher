#!/usr/bin/env python3
"""
Bloomberg API Setup Script
Automates the installation and testing of Bloomberg API
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("\n" + "="*60)
    print("BLOOMBERG API SETUP SCRIPT")
    print("="*60)
    print("This script will help you set up Bloomberg API for Python")
    print("="*60 + "\n")

def check_python():
    """Check Python installation"""
    print("1. Checking Python installation...")
    
    python_path = r"C:\Users\cchunan\AppData\Local\Programs\Python\Python313\python.exe"
    
    if os.path.exists(python_path):
        print(f"✅ Python found at: {python_path}")
        return python_path
    else:
        print("❌ Python not found at expected location")
        print("Please ensure Python 3.8+ is installed")
        return None

def check_bloomberg_terminal():
    """Check if Bloomberg Terminal is running"""
    print("\n2. Checking Bloomberg Terminal...")
    
    # Check for Bloomberg processes
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Bloomberg.exe'], 
                              capture_output=True, text=True)
        if 'Bloomberg.exe' in result.stdout:
            print("✅ Bloomberg Terminal is running")
            return True
        else:
            print("⚠️ Bloomberg Terminal not detected")
            print("Please ensure Bloomberg Terminal is running and logged in")
            return False
    except Exception as e:
        print(f"⚠️ Could not check Bloomberg Terminal: {e}")
        return False

def check_blpapi():
    """Check if blpapi is installed"""
    print("\n3. Checking Bloomberg API library...")
    
    python_path = check_python()
    if not python_path:
        return False
    
    try:
        result = subprocess.run([python_path, '-c', 'import blpapi; print("blpapi version:", blpapi.__version__)'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Bloomberg API library is installed")
            print(f"   {result.stdout.strip()}")
            return True
        else:
            print("❌ Bloomberg API library not found")
            return False
    except Exception as e:
        print(f"❌ Error checking blpapi: {e}")
        return False

def install_blpapi_guide():
    """Provide installation guide for blpapi"""
    print("\n" + "="*60)
    print("BLOOMBERG API INSTALLATION REQUIRED")
    print("="*60)
    print("The Bloomberg API library (blpapi) needs to be installed manually.")
    print("\n📋 INSTALLATION STEPS:")
    print("1. Open Bloomberg Terminal")
    print("2. Type: API<GO> and press Enter")
    print("3. Select 'API Library' from the menu")
    print("4. Choose 'Python' version")
    print("5. Download the installer")
    print("6. Run installer as Administrator")
    print("7. Choose Python path: C:\\Users\\cchunan\\AppData\\Local\\Programs\\Python\\Python313\\")
    print("\n🔄 After installation, run this script again to test the connection.")
    print("="*60)

def test_connection(python_path):
    """Test Bloomberg API connection"""
    print("\n4. Testing Bloomberg API connection...")
    
    try:
        result = subprocess.run([python_path, 'scripts/quick_test.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Bloomberg API connection test PASSED!")
            print("✅ All systems ready for data fetching")
            return True
        else:
            print("❌ Bloomberg API connection test FAILED")
            print("Error output:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running connection test: {e}")
        return False

def create_convenience_scripts():
    """Create convenience scripts for easy usage"""
    print("\n5. Creating convenience scripts...")
    
    # Create run_all.py script
    run_all_script = '''#!/usr/bin/env python3
"""
Convenience script to run all Bloomberg data fetchers
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_quick_test():
    """Run quick connection test"""
    print("\\n🔍 Running Bloomberg API connection test...")
    os.system("python scripts/quick_test.py")

def run_daily_fetch():
    """Run daily options fetch"""
    print("\\n📊 Running daily QQQ options fetch...")
    os.system("python scripts/daily_fetch.py --save-db --export-csv")

def run_historical_fetch(days=60):
    """Run historical options fetch"""
    print(f"\\n📈 Running historical QQQ options fetch ({days} days)...")
    os.system(f"python scripts/historical_fetch.py --days {days} --save-db")

def main():
    parser = argparse.ArgumentParser(description='Bloomberg QQQ Options Fetcher')
    parser.add_argument('--test', action='store_true', help='Run connection test only')
    parser.add_argument('--daily', action='store_true', help='Run daily fetch')
    parser.add_argument('--historical', action='store_true', help='Run historical fetch')
    parser.add_argument('--days', type=int, default=60, help='Days of historical data')
    parser.add_argument('--all', action='store_true', help='Run all fetches')
    
    args = parser.parse_args()
    
    print("\\n" + "="*60)
    print("BLOOMBERG QQQ OPTIONS FETCHER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if args.test:
        run_quick_test()
    elif args.daily:
        run_daily_fetch()
    elif args.historical:
        run_historical_fetch(args.days)
    elif args.all:
        run_quick_test()
        run_daily_fetch()
        run_historical_fetch(args.days)
    else:
        print("\\nUsage examples:")
        print("  python scripts/run_all.py --test          # Test connection")
        print("  python scripts/run_all.py --daily         # Daily fetch")
        print("  python scripts/run_all.py --historical    # Historical fetch")
        print("  python scripts/run_all.py --all           # Run everything")
        print("  python scripts/run_all.py --days 30      # 30 days historical")

if __name__ == "__main__":
    main()
'''
    
    with open('scripts/run_all.py', 'w') as f:
        f.write(run_all_script)
    
    print("✅ Created scripts/run_all.py")
    
    # Create batch file for Windows
    batch_script = '''@echo off
echo Bloomberg QQQ Options Fetcher
echo =============================
echo.
echo Available commands:
echo   test        - Test Bloomberg connection
echo   daily       - Fetch daily options data
echo   historical  - Fetch historical data (60 days)
echo   all         - Run all fetches
echo.
set /p choice="Enter command (test/daily/historical/all): "

if "%choice%"=="test" (
    python scripts/run_all.py --test
) else if "%choice%"=="daily" (
    python scripts/run_all.py --daily
) else if "%choice%"=="historical" (
    python scripts/run_all.py --historical
) else if "%choice%"=="all" (
    python scripts/run_all.py --all
) else (
    echo Invalid choice. Please run again.
)

pause
'''
    
    with open('run_bloomberg.bat', 'w') as f:
        f.write(batch_script)
    
    print("✅ Created run_bloomberg.bat")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python
    python_path = check_python()
    if not python_path:
        print("\n❌ Setup failed: Python not found")
        return 1
    
    # Check Bloomberg Terminal
    bloomberg_running = check_bloomberg_terminal()
    
    # Check blpapi
    blpapi_installed = check_blpapi()
    
    if not blpapi_installed:
        install_blpapi_guide()
        return 1
    
    # Test connection
    if bloomberg_running:
        connection_ok = test_connection(python_path)
        if connection_ok:
            create_convenience_scripts()
            
            print("\n" + "="*60)
            print("🎉 SETUP COMPLETE!")
            print("="*60)
            print("✅ Python: Ready")
            print("✅ Bloomberg Terminal: Running")
            print("✅ Bloomberg API: Installed")
            print("✅ Connection: Working")
            print("✅ Convenience scripts: Created")
            print("\n🚀 Ready to fetch QQQ options data!")
            print("\nQuick commands:")
            print("  python scripts/run_all.py --daily      # Daily fetch")
            print("  python scripts/run_all.py --historical # Historical fetch")
            print("  run_bloomberg.bat                      # Windows batch menu")
            print("="*60)
            return 0
        else:
            print("\n❌ Setup incomplete: Connection test failed")
            return 1
    else:
        print("\n⚠️ Setup incomplete: Bloomberg Terminal not running")
        print("Please start Bloomberg Terminal and run this script again")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)
