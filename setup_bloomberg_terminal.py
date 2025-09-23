#!/usr/bin/env python3
"""
Bloomberg Terminal Setup Script
Automatically installs and configures everything needed for Bloomberg QQQ Fetcher
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class BloombergSetup:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.python_dir = Path(sys.executable).parent
        self.is_windows = platform.system() == 'Windows'

    def print_header(self, message):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {message}")
        print("=" * 60)

    def check_python_version(self):
        """Check Python version and architecture"""
        self.print_header("Checking Python Environment")

        version = sys.version_info
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print("❌ ERROR: Python 3.6+ required")
            return False

        # Check 64-bit
        is_64bit = sys.maxsize > 2**32
        if is_64bit:
            print("✅ Python architecture: 64-bit")
        else:
            print("❌ ERROR: 64-bit Python required for Bloomberg API")
            return False

        return True

    def install_requirements(self):
        """Install all Python dependencies"""
        self.print_header("Installing Python Dependencies")

        requirements_file = self.current_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ ERROR: requirements.txt not found")
            return False

        try:
            # Upgrade pip first
            print("📦 Upgrading pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

            # Install requirements
            print("📦 Installing dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR installing dependencies: {e}")
            return False

    def install_blpapi(self):
        """Install Bloomberg Python API"""
        self.print_header("Installing Bloomberg API (blpapi)")

        # Check if blpapi wheel exists
        wheel_file = None
        for file in self.current_dir.glob("blpapi*.whl"):
            wheel_file = file
            break

        if not wheel_file:
            print("❌ ERROR: blpapi wheel file not found")
            print("   Looking for: blpapi-3.25.3-py3-none-win_amd64.whl")
            return False

        print(f"📦 Found wheel file: {wheel_file.name}")

        try:
            # Uninstall old version if exists
            print("🔧 Removing old blpapi if exists...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "blpapi", "-y"],
                         capture_output=True)

            # Install new version
            print(f"📦 Installing {wheel_file.name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", str(wheel_file), "--user"])
            print("✅ blpapi installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR installing blpapi: {e}")
            return False

    def setup_dll(self):
        """Setup Bloomberg DLL file"""
        self.print_header("Setting up Bloomberg DLL")

        dll_file = self.current_dir / "blpapi3_64.dll"
        if not dll_file.exists():
            print("❌ ERROR: blpapi3_64.dll not found")
            return False

        print(f"✅ Found DLL: {dll_file}")

        # Method 1: Copy to Python directory
        python_dll = self.python_dir / "blpapi3_64.dll"
        try:
            print(f"📋 Copying DLL to Python directory: {self.python_dir}")
            shutil.copy2(dll_file, python_dll)
            print("✅ DLL copied to Python directory")
        except Exception as e:
            print(f"⚠️  Could not copy to Python directory: {e}")
            print("   Will use PATH method instead")

        # Method 2: Add to PATH (for current session)
        os.environ['PATH'] = str(self.current_dir) + os.pathsep + os.environ.get('PATH', '')
        print(f"✅ Added {self.current_dir} to PATH")

        return True

    def test_import(self):
        """Test if blpapi can be imported"""
        self.print_header("Testing Bloomberg API Import")

        try:
            import blpapi
            print("✅ SUCCESS: blpapi imported successfully!")

            # Try to create session
            try:
                session = blpapi.Session()
                print("✅ Bloomberg session object created")
                session.stop()
            except Exception as e:
                print(f"⚠️  Session creation test: {e}")
                print("   This is normal if Bloomberg Terminal is not running")

            return True
        except ImportError as e:
            print(f"❌ ERROR importing blpapi: {e}")

            # Try to diagnose the problem
            print("\n🔍 Diagnostic Information:")
            print(f"   Python executable: {sys.executable}")
            print(f"   Python path: {sys.path[:3]}")
            print(f"   Current directory: {self.current_dir}")
            print(f"   DLL exists: {(self.current_dir / 'blpapi3_64.dll').exists()}")

            return False

    def create_batch_script(self):
        """Create batch script for easy running"""
        self.print_header("Creating Run Scripts")

        # Windows batch script
        batch_content = """@echo off
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
    pause
    exit /b 1
)

echo.
echo Available commands:
echo   1. Test Bloomberg Connection
echo   2. Run API Usage Calculator
echo   3. Run Web Interface
echo   4. Fetch Historical Data (Quick Test)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    python scripts\\historical_fetch.py --quick-test
) else if "%choice%"=="2" (
    python api_usage_calculator.py
) else if "%choice%"=="3" (
    python app.py
) else if "%choice%"=="4" (
    python scripts\\historical_fetch.py --days 7 --atm-only
) else (
    echo Invalid choice
)

pause
"""

        batch_file = self.current_dir / "run_bloomberg_fetcher.bat"
        batch_file.write_text(batch_content)
        print(f"✅ Created: {batch_file.name}")

        # PowerShell script
        ps1_content = """
Write-Host "========================================" -ForegroundColor Green
Write-Host "Bloomberg QQQ Fetcher" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Set up environment
$env:PATH += ";$(Get-Location)"
$env:PYTHONPATH = Get-Location

# Test import
python -c "import blpapi; print('✅ Bloomberg API ready')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Bloomberg API not properly installed" -ForegroundColor Red
    Write-Host "Run: python setup_bloomberg_terminal.py" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  python scripts\historical_fetch.py --quick-test" -ForegroundColor Yellow
Write-Host "  python api_usage_calculator.py" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor Yellow
Write-Host ""
"""

        ps1_file = self.current_dir / "run_bloomberg_fetcher.ps1"
        ps1_file.write_text(ps1_content)
        print(f"✅ Created: {ps1_file.name}")

        return True

    def run(self):
        """Run complete setup"""
        print("\n" + "🚀" * 30)
        print("  BLOOMBERG QQQ FETCHER - AUTOMATIC SETUP")
        print("🚀" * 30)

        # Check Python
        if not self.check_python_version():
            return False

        # Install requirements
        if not self.install_requirements():
            print("\n⚠️  Failed to install some dependencies")
            print("   You may need to install them manually")

        # Install blpapi
        if not self.install_blpapi():
            return False

        # Setup DLL
        if not self.setup_dll():
            return False

        # Test import
        if not self.test_import():
            print("\n⚠️  Import test failed, but setup is complete")
            print("   Try running this script again")

        # Create helper scripts
        self.create_batch_script()

        # Final message
        self.print_header("✅ SETUP COMPLETE!")
        print("""
You can now run:

1. Quick test:
   python scripts\\historical_fetch.py --quick-test

2. API usage calculator:
   python api_usage_calculator.py

3. Web interface:
   python app.py

4. Or use the batch file:
   run_bloomberg_fetcher.bat

Remember:
- Bloomberg Terminal must be running and logged in
- Run 'WAPI<GO>' in Bloomberg to check API status
""")

        return True

if __name__ == "__main__":
    setup = BloombergSetup()
    success = setup.run()

    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

    print("\n✅ Setup completed successfully!")
    input("\nPress Enter to exit...")