#!/usr/bin/env python3
"""
Bloomberg Official Setup Script
Uses Bloomberg's official pip repository for clean, reliable installation
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class BloombergOfficialSetup:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.python_exe = sys.executable
        self.python_dir = Path(self.python_exe).parent
        self.is_windows = platform.system() == 'Windows'

    def print_header(self, message):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {message}")
        print("=" * 70)

    def print_step(self, step, message):
        """Print step with number"""
        print(f"\n[{step}] {message}")

    def check_python_environment(self):
        """Check Python installation"""
        self.print_header("Checking Python Environment")

        version = sys.version_info
        print(f"✅ Python executable: {self.python_exe}")
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")

        # Check version compatibility
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ ERROR: Python 3.8+ required for Bloomberg API")
            return False

        # Check architecture
        is_64bit = sys.maxsize > 2**32
        arch = "64-bit" if is_64bit else "32-bit"
        print(f"✅ Python architecture: {arch}")

        if not is_64bit:
            print("⚠️  WARNING: 64-bit Python recommended for Bloomberg API")

        return True

    def setup_environment_variables(self):
        """Setup Bloomberg environment variables"""
        self.print_header("Setting up Environment Variables")

        # Set BLPAPI_ROOT to current directory
        blpapi_root = str(self.current_dir)
        os.environ['BLPAPI_ROOT'] = blpapi_root
        print(f"✅ Set BLPAPI_ROOT = {blpapi_root}")

        # Add current directory to PATH
        current_path = os.environ.get('PATH', '')
        if str(self.current_dir) not in current_path:
            os.environ['PATH'] = str(self.current_dir) + os.pathsep + current_path
            print(f"✅ Added {self.current_dir} to PATH")

        # Set PYTHONPATH
        pythonpath = os.environ.get('PYTHONPATH', '')
        if str(self.current_dir) not in pythonpath:
            os.environ['PYTHONPATH'] = str(self.current_dir) + os.pathsep + pythonpath
            print(f"✅ Added {self.current_dir} to PYTHONPATH")

        return True

    def install_pip_requirements(self):
        """Install regular pip requirements"""
        self.print_header("Installing Standard Dependencies")

        requirements_file = self.current_dir / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️  requirements.txt not found, skipping standard dependencies")
            return True

        try:
            self.print_step(1, "Upgrading pip")
            subprocess.check_call([
                self.python_exe, "-m", "pip", "install", "--upgrade", "pip"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print("✅ pip upgraded successfully")

            self.print_step(2, "Installing requirements.txt")
            subprocess.check_call([
                self.python_exe, "-m", "pip", "install",
                "-r", str(requirements_file), "--user"
            ])
            print("✅ Standard dependencies installed")
            return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Some standard dependencies failed to install: {e}")
            print("   This may not affect Bloomberg API functionality")
            return True  # Don't fail the whole setup

    def install_blpapi_official(self):
        """Install Bloomberg API using official pip repository"""
        self.print_header("Installing Bloomberg API (Official Method)")

        bloomberg_index = "https://blpapi.bloomberg.com/repository/releases/python/simple/"

        try:
            self.print_step(1, "Uninstalling any existing blpapi")
            subprocess.run([
                self.python_exe, "-m", "pip", "uninstall", "blpapi", "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.print_step(2, "Installing blpapi from Bloomberg's official repository")
            print(f"   Repository: {bloomberg_index}")

            subprocess.check_call([
                self.python_exe, "-m", "pip", "install",
                "--index-url", bloomberg_index,
                "blpapi", "--user"
            ])

            print("✅ Bloomberg API installed successfully from official repository!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Official installation failed: {e}")
            return False

    def install_blpapi_fallback(self):
        """Fallback: Install from local wheel file if available"""
        self.print_header("Bloomberg API Fallback Installation")

        # Look for wheel file
        wheel_files = list(self.current_dir.glob("blpapi*.whl"))
        if not wheel_files:
            print("❌ No local wheel file found for fallback installation")
            return False

        wheel_file = wheel_files[0]
        print(f"📦 Found local wheel: {wheel_file.name}")

        try:
            subprocess.check_call([
                self.python_exe, "-m", "pip", "install",
                str(wheel_file), "--user", "--force-reinstall"
            ])
            print("✅ Fallback installation successful!")

            # Handle DLL if present
            dll_file = self.current_dir / "blpapi3_64.dll"
            if dll_file.exists():
                print("🔧 Setting up DLL file...")
                self._setup_dll_fallback(dll_file)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Fallback installation failed: {e}")
            return False

    def _setup_dll_fallback(self, dll_file):
        """Setup DLL for fallback installation"""
        try:
            # Copy to site-packages if possible
            import site
            if hasattr(site, 'getusersitepackages'):
                site_packages = Path(site.getusersitepackages())
                if site_packages.exists():
                    blpapi_dir = site_packages / "blpapi"
                    blpapi_dir.mkdir(exist_ok=True)
                    shutil.copy2(dll_file, blpapi_dir / "blpapi3_64.dll")
                    print("✅ DLL copied to site-packages")
        except Exception as e:
            print(f"⚠️  DLL setup warning: {e}")

    def test_installation(self):
        """Test Bloomberg API installation"""
        self.print_header("Testing Bloomberg API Installation")

        try:
            self.print_step(1, "Testing import")
            subprocess.check_call([
                self.python_exe, "-c", "import blpapi; print('✅ blpapi import successful')"
            ])

            self.print_step(2, "Testing basic functionality")
            test_code = """
import blpapi
try:
    # Test session creation
    options = blpapi.SessionOptions()
    options.setServerHost('localhost')
    options.setServerPort(8194)
    session = blpapi.Session(options)
    print('✅ Bloomberg session object created successfully')

    # Test version info
    version = blpapi.versionInfo()
    print(f'✅ Bloomberg API version: {version}')

except Exception as e:
    print(f'⚠️  Session test warning: {e}')
    print('   This is normal if Bloomberg Terminal is not running')
"""

            subprocess.check_call([self.python_exe, "-c", test_code])
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Installation test failed: {e}")
            return False

    def create_environment_batch_file(self):
        """Create batch file to set environment variables"""
        if not self.is_windows:
            return

        self.print_header("Creating Environment Setup Files")

        # Create batch file for environment setup
        batch_content = f"""@echo off
REM Bloomberg API Environment Setup
echo Setting up Bloomberg API environment...

REM Set environment variables
set BLPAPI_ROOT={self.current_dir}
set PATH=%PATH%;{self.current_dir}
set PYTHONPATH=%PYTHONPATH%;{self.current_dir}

echo ✅ Environment variables set:
echo    BLPAPI_ROOT = %BLPAPI_ROOT%
echo    PATH includes project directory
echo    PYTHONPATH includes project directory

REM Test Bloomberg API
echo.
echo Testing Bloomberg API...
"{self.python_exe}" -c "import blpapi; print('✅ Bloomberg API ready!')"

if errorlevel 1 (
    echo ❌ Bloomberg API test failed
    echo Please check installation or run bloomberg_official_setup.py again
) else (
    echo.
    echo 🎉 Bloomberg API is ready to use!
    echo.
    echo Available commands:
    echo   "{self.python_exe}" scripts\\historical_fetch.py --quick-test
    echo   "{self.python_exe}" app.py
    echo   run_bloomberg_fetcher.bat
)

pause
"""

        batch_file = self.current_dir / "setup_environment.bat"
        batch_file.write_text(batch_content, encoding='utf-8')
        print(f"✅ Created: {batch_file.name}")

    def run_setup(self):
        """Run complete setup process"""
        print("🚀 Bloomberg Official Setup")
        print("=" * 70)
        print("Using Bloomberg's official pip repository for clean installation")

        # Check Python environment
        if not self.check_python_environment():
            return False

        # Setup environment variables
        if not self.setup_environment_variables():
            return False

        # Install standard requirements
        self.install_pip_requirements()

        # Try official installation first
        success = self.install_blpapi_official()

        if not success:
            print("\n⚠️  Official installation failed, trying fallback method...")
            success = self.install_blpapi_fallback()

        if not success:
            print("\n❌ All installation methods failed!")
            print("\nTroubleshooting:")
            print("1. Ensure you have internet connection")
            print("2. Try running as administrator")
            print("3. Check if corporate firewall blocks pip repositories")
            print("4. Run: python bloomberg_diagnostics.py")
            return False

        # Test installation
        if not self.test_installation():
            print("\n⚠️  Installation completed but testing failed")
            print("Bloomberg API may still work - check Bloomberg Terminal is running")

        # Create helper files
        self.create_environment_batch_file()

        # Final success message
        self.print_header("🎉 Setup Complete!")
        print("""
Bloomberg API has been installed successfully!

Next steps:
1. Ensure Bloomberg Terminal is running and logged in
2. Test connection: python -c "import blpapi; print('Success!')"
3. Run quick test: python scripts/historical_fetch.py --quick-test
4. Use setup_environment.bat to set environment variables for new sessions

For troubleshooting, run: python bloomberg_diagnostics.py
""")
        return True

if __name__ == "__main__":
    setup = BloombergOfficialSetup()
    success = setup.run_setup()

    if not success:
        print("\n❌ Setup failed. Please check errors above and try again.")
        sys.exit(1)

    print("\n✅ Setup completed successfully!")
    input("\nPress Enter to exit...")