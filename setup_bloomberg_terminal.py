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

    def install_blpapi_official(self):
        """Install Bloomberg API using official pip repository (preferred method)"""
        self.print_header("Installing Bloomberg API (Official Method)")

        bloomberg_index = "https://blpapi.bloomberg.com/repository/releases/python/simple/"
        print(f"📦 Using Bloomberg's official repository: {bloomberg_index}")

        try:
            # Uninstall old version if exists
            print("🔧 Removing old blpapi if exists...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "blpapi", "-y"],
                         capture_output=True)

            # Install from official repository
            print("📦 Installing blpapi from Bloomberg's official repository...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--index-url", bloomberg_index,
                "blpapi", "--user"
            ])
            print("✅ Bloomberg API installed successfully from official repository!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Official installation failed: {e}")
            print("   Falling back to local wheel method...")
            return False

    def install_blpapi_wheel(self):
        """Install Bloomberg Python API from local wheel file (fallback method)"""
        self.print_header("Installing Bloomberg API (Local Wheel Method)")

        # Check if blpapi wheel exists
        wheel_file = None
        for file in self.current_dir.glob("blpapi*.whl"):
            wheel_file = file
            break

        if not wheel_file:
            print("❌ ERROR: blpapi wheel file not found")
            print("   Looking for: blpapi-3.25.3-py3-none-win_amd64.whl")
            print("   Download from: Bloomberg Terminal API<GO> or")
            print("   https://www.bloomberg.com/professional/support/api-library/")
            return False

        print(f"📦 Found wheel file: {wheel_file.name}")

        try:
            # Install wheel
            print(f"📦 Installing {wheel_file.name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", str(wheel_file), "--user", "--force-reinstall"])
            print("✅ blpapi installed successfully from wheel")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR installing blpapi: {e}")
            return False

    def setup_dll(self):
        """Setup Bloomberg DLL file with multiple fallback methods"""
        self.print_header("Setting up Bloomberg DLL")

        dll_file = self.current_dir / "blpapi3_64.dll"
        if not dll_file.exists():
            print("❌ ERROR: blpapi3_64.dll not found")
            print("   Please ensure blpapi3_64.dll is in the project directory")
            return False

        print(f"✅ Found DLL: {dll_file}")

        # Get DLL size for verification
        dll_size = dll_file.stat().st_size / (1024 * 1024)  # Convert to MB
        print(f"   DLL size: {dll_size:.1f} MB")

        success_count = 0

        # Method 1: Copy to Python directory
        python_dll = self.python_dir / "blpapi3_64.dll"
        try:
            print(f"📋 Method 1: Copying to Python directory: {self.python_dir}")
            shutil.copy2(dll_file, python_dll)
            print("✅ DLL copied to Python directory")
            success_count += 1
        except Exception as e:
            print(f"⚠️  Method 1 failed: {e}")

        # Method 2: Copy to Scripts directory
        scripts_dir = self.python_dir / "Scripts"
        if scripts_dir.exists():
            try:
                scripts_dll = scripts_dir / "blpapi3_64.dll"
                print(f"📋 Method 2: Copying to Scripts directory: {scripts_dir}")
                shutil.copy2(dll_file, scripts_dll)
                print("✅ DLL copied to Scripts directory")
                success_count += 1
            except Exception as e:
                print(f"⚠️  Method 2 failed: {e}")

        # Method 3: Copy to site-packages directory
        try:
            import site
            site_packages = Path(site.getusersitepackages()) if hasattr(site, 'getusersitepackages') else None
            if site_packages and site_packages.exists():
                site_dll = site_packages / "blpapi3_64.dll"
                print(f"📋 Method 3: Copying to site-packages: {site_packages}")
                shutil.copy2(dll_file, site_dll)
                print("✅ DLL copied to site-packages directory")
                success_count += 1
        except Exception as e:
            print(f"⚠️  Method 3 failed: {e}")

        # Method 4: Try System32 directory (requires admin)
        if self.is_windows:
            try:
                import os
                system32 = Path(os.environ.get('WINDIR', 'C:\\Windows')) / "System32"
                if system32.exists():
                    system32_dll = system32 / "blpapi3_64.dll"
                    print(f"📋 Method 4: Copying to System32: {system32}")
                    shutil.copy2(dll_file, system32_dll)
                    print("✅ DLL copied to System32 directory")
                    success_count += 1
            except Exception as e:
                print(f"⚠️  Method 4 failed (may need admin rights): {e}")

        # Method 5: Add to PATH (for current session)
        os.environ['PATH'] = str(self.current_dir) + os.pathsep + os.environ.get('PATH', '')
        print(f"✅ Added {self.current_dir} to PATH")

        # Method 6: Check common Bloomberg installation paths
        bloomberg_paths = [
            "C:\\blp\\DAPI",
            "C:\\Program Files (x86)\\blp\\DAPI",
            "C:\\Program Files\\Bloomberg\\blp\\DAPI"
        ]

        for bloomberg_path in bloomberg_paths:
            try:
                path_obj = Path(bloomberg_path)
                if path_obj.exists():
                    bloomberg_dll = path_obj / "blpapi3_64.dll"
                    print(f"📋 Method 6: Copying to Bloomberg path: {bloomberg_path}")
                    shutil.copy2(dll_file, bloomberg_dll)
                    print(f"✅ DLL copied to Bloomberg directory: {bloomberg_path}")
                    success_count += 1
                    # Add to PATH too
                    os.environ['PATH'] = bloomberg_path + os.pathsep + os.environ.get('PATH', '')
                    break
            except Exception as e:
                print(f"⚠️  Bloomberg path {bloomberg_path} failed: {e}")

        print(f"\n📊 DLL Setup Summary:")
        print(f"   Successful installations: {success_count}")
        print(f"   Current PATH includes project directory: ✅")

        return success_count > 0

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
python -c "import blpapi; print('OK Bloomberg API ready')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR Bloomberg API not properly installed" -ForegroundColor Red
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
        ps1_file.write_text(ps1_content, encoding='utf-8')
        print(f"✅ Created: {ps1_file.name}")

        return True

    def setup_environment_variables(self):
        """Setup Bloomberg environment variables"""
        self.print_header("Setting up Environment Variables")

        # Set BLPAPI_ROOT to current directory
        os.environ['BLPAPI_ROOT'] = str(self.current_dir)
        print(f"✅ Set BLPAPI_ROOT = {self.current_dir}")

        # Add current directory to PATH
        current_path = os.environ.get('PATH', '')
        if str(self.current_dir) not in current_path:
            os.environ['PATH'] = str(self.current_dir) + os.pathsep + current_path
            print(f"✅ Added {self.current_dir} to PATH")

        return True

    def run(self):
        """Run complete setup with official method preferred"""
        print("\n" + "🚀" * 30)
        print("  BLOOMBERG QQQ FETCHER - AUTOMATIC SETUP")
        print("🚀" * 30)
        print("  Using Bloomberg's official installation methods")

        # Check Python
        if not self.check_python_version():
            return False

        # Setup environment variables
        if not self.setup_environment_variables():
            return False

        # Install requirements
        if not self.install_requirements():
            print("\n⚠️  Failed to install some dependencies")
            print("   You may need to install them manually")

        # Try official Bloomberg installation first
        blpapi_success = self.install_blpapi_official()

        # If official fails, try local wheel
        if not blpapi_success:
            print("\n🔄 Trying fallback installation method...")
            blpapi_success = self.install_blpapi_wheel()

            # If wheel method succeeds, setup DLL
            if blpapi_success:
                if not self.setup_dll():
                    print("\n⚠️  DLL setup failed, but pip installation may still work")

        if not blpapi_success:
            print("\n❌ All Bloomberg API installation methods failed!")
            print("\nTroubleshooting:")
            print("1. Check internet connection for official method")
            print("2. Download wheel file from Bloomberg Terminal: API<GO>")
            print("3. Run: python bloomberg_diagnostics.py")
            return False

        # Test import
        if not self.test_import():
            print("\n⚠️  Import test failed, but installation may still work")
            print("   Check if Bloomberg Terminal is running")

        # Create helper scripts
        self.create_batch_script()

        # Final message
        self.print_header("✅ SETUP COMPLETE!")
        print("""
Bloomberg API installed successfully!

Next steps:
1. Ensure Bloomberg Terminal is running and logged in
2. Test: python -c "import blpapi; print('Success!')"

Available commands:
- python scripts\\historical_fetch.py --quick-test
- python app.py
- run_bloomberg_fetcher.bat

For new command sessions, run: setup_environment.bat

Note: Use API<GO> in Bloomberg Terminal (not WAPI<GO>)
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