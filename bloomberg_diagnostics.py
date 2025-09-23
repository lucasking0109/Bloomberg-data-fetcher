#!/usr/bin/env python3
"""
Bloomberg API Diagnostic Script
Comprehensive tool to diagnose Bloomberg API installation and connection issues
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import ctypes

class BloombergDiagnostics:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.python_dir = Path(sys.executable).parent
        self.is_windows = platform.system() == 'Windows'
        self.issues = []
        self.warnings = []
        self.success = []

    def print_section(self, title):
        """Print formatted section header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def add_issue(self, message):
        """Add an issue to the list"""
        self.issues.append(message)
        print(f"❌ {message}")

    def add_warning(self, message):
        """Add a warning to the list"""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def add_success(self, message):
        """Add a success to the list"""
        self.success.append(message)
        print(f"✅ {message}")

    def check_python_environment(self):
        """Check Python installation and environment"""
        self.print_section("Python Environment Check")

        # Python version
        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.add_issue("Python 3.8+ required for Bloomberg API")
        else:
            self.add_success(f"Python version {version.major}.{version.minor}.{version.micro} is supported")

        # Architecture check
        is_64bit = sys.maxsize > 2**32
        arch = "64-bit" if is_64bit else "32-bit"
        print(f"Python architecture: {arch}")

        if not is_64bit:
            self.add_issue("64-bit Python required for Bloomberg API")
        else:
            self.add_success("64-bit Python detected")

        # Python path
        print(f"Python executable: {sys.executable}")
        print(f"Python directory: {self.python_dir}")

    def check_bloomberg_terminal_process(self):
        """Check if Bloomberg Terminal is running"""
        self.print_section("Bloomberg Terminal Process Check")

        if not self.is_windows:
            self.add_warning("Bloomberg Terminal process check only available on Windows")
            return

        try:
            import subprocess
            # Check for Bloomberg Terminal processes
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq bbcomm.exe'],
                                  capture_output=True, text=True)

            if 'bbcomm.exe' in result.stdout:
                self.add_success("Bloomberg Terminal communication process (bbcomm.exe) is running")
            else:
                self.add_issue("Bloomberg Terminal communication process (bbcomm.exe) NOT running")
                self.add_issue("Please start Bloomberg Terminal and log in")

            # Check for Terminal UI process
            result2 = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Trminal.exe'],
                                   capture_output=True, text=True)

            if 'Trminal.exe' in result2.stdout:
                self.add_success("Bloomberg Terminal UI (Trminal.exe) is running")
            else:
                self.add_warning("Bloomberg Terminal UI (Trminal.exe) may not be running")

        except Exception as e:
            self.add_warning(f"Could not check Bloomberg processes: {e}")

    def check_bloomberg_files(self):
        """Check for Bloomberg API files"""
        self.print_section("Bloomberg API Files Check")

        # Check for wheel file
        wheel_files = list(self.current_dir.glob("blpapi*.whl"))
        if wheel_files:
            for wheel in wheel_files:
                size_mb = wheel.stat().st_size / (1024 * 1024)
                self.add_success(f"Found wheel file: {wheel.name} ({size_mb:.1f} MB)")

                # Check if wheel is installed
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, '-m', 'pip', 'list'],
                                          capture_output=True, text=True)
                    if 'blpapi' in result.stdout:
                        self.add_success("blpapi package is installed")
                    else:
                        self.add_warning("blpapi package not installed (wheel file exists but not installed)")
                except:
                    self.add_warning("Could not check if blpapi package is installed")
        else:
            self.add_issue("No blpapi wheel file found (blpapi*.whl)")
            self.add_issue("Download from: Bloomberg Terminal API<GO> or Developer Portal")

        # Check for DLL file
        dll_file = self.current_dir / "blpapi3_64.dll"
        if dll_file.exists():
            size_mb = dll_file.stat().st_size / (1024 * 1024)
            self.add_success(f"Found DLL file: blpapi3_64.dll ({size_mb:.1f} MB)")

            # Verify DLL version and properties
            if size_mb < 1.0:
                self.add_warning(f"DLL file seems too small ({size_mb:.1f} MB), may be corrupted")
            elif size_mb > 50.0:
                self.add_warning(f"DLL file seems unusually large ({size_mb:.1f} MB)")
        else:
            self.add_issue("blpapi3_64.dll not found in project directory")
            self.add_issue("This file should come with the Bloomberg API download")

    def check_dll_locations(self):
        """Check DLL file locations in system"""
        self.print_section("System DLL Locations Check")

        dll_locations = []

        # Check Python directory
        python_dll = self.python_dir / "blpapi3_64.dll"
        if python_dll.exists():
            dll_locations.append(str(python_dll))
            self.add_success(f"DLL found in Python directory: {python_dll}")

        # Check Scripts directory
        scripts_dir = self.python_dir / "Scripts"
        if scripts_dir.exists():
            scripts_dll = scripts_dir / "blpapi3_64.dll"
            if scripts_dll.exists():
                dll_locations.append(str(scripts_dll))
                self.add_success(f"DLL found in Scripts directory: {scripts_dll}")

        # Check site-packages
        try:
            import site
            if hasattr(site, 'getusersitepackages'):
                site_packages = Path(site.getusersitepackages())
                if site_packages.exists():
                    site_dll = site_packages / "blpapi3_64.dll"
                    if site_dll.exists():
                        dll_locations.append(str(site_dll))
                        self.add_success(f"DLL found in site-packages: {site_dll}")
        except:
            pass

        # Check System32
        if self.is_windows:
            system32 = Path(os.environ.get('WINDIR', 'C:\\Windows')) / "System32" / "blpapi3_64.dll"
            if system32.exists():
                dll_locations.append(str(system32))
                self.add_success(f"DLL found in System32: {system32}")

        # Check Bloomberg paths
        bloomberg_paths = [
            "C:\\blp\\DAPI\\blpapi3_64.dll",
            "C:\\Program Files (x86)\\blp\\DAPI\\blpapi3_64.dll",
            "C:\\Program Files\\Bloomberg\\blp\\DAPI\\blpapi3_64.dll"
        ]

        for path in bloomberg_paths:
            if Path(path).exists():
                dll_locations.append(path)
                self.add_success(f"DLL found in Bloomberg directory: {path}")

        if not dll_locations:
            self.add_issue("No blpapi3_64.dll found in any system location")

        return dll_locations

    def check_path_environment(self):
        """Check PATH environment variable"""
        self.print_section("PATH Environment Check")

        current_path = os.environ.get('PATH', '')
        path_dirs = current_path.split(os.pathsep)

        print(f"Total PATH directories: {len(path_dirs)}")

        # Check if project directory is in PATH
        if str(self.current_dir) in path_dirs:
            self.add_success("Project directory is in PATH")
        else:
            self.add_warning("Project directory not in PATH")

        # Check for Bloomberg directories in PATH
        bloomberg_in_path = any('blp' in path.lower() or 'bloomberg' in path.lower()
                              for path in path_dirs)

        if bloomberg_in_path:
            bloomberg_paths = [path for path in path_dirs
                             if 'blp' in path.lower() or 'bloomberg' in path.lower()]
            for path in bloomberg_paths:
                self.add_success(f"Bloomberg directory in PATH: {path}")
        else:
            self.add_warning("No Bloomberg directories found in PATH")

    def test_blpapi_import(self):
        """Test Bloomberg API import"""
        self.print_section("Bloomberg API Import Test")

        try:
            import blpapi
            self.add_success("blpapi module imported successfully")

            # Try to get version
            try:
                version = blpapi.versionInfo()
                self.add_success(f"Bloomberg API version: {version}")
            except:
                self.add_warning("Could not get Bloomberg API version")

            return True
        except ImportError as e:
            self.add_issue(f"Failed to import blpapi: {e}")
            return False

    def test_bloomberg_connection(self):
        """Test Bloomberg Terminal connection"""
        self.print_section("Bloomberg Terminal Connection Test")

        try:
            import blpapi

            # Create session options
            session_options = blpapi.SessionOptions()
            session_options.setServerHost("localhost")
            session_options.setServerPort(8194)

            # Try to create session
            session = blpapi.Session(session_options)

            if session.start():
                self.add_success("Bloomberg Terminal connection successful")
                session.stop()
                return True
            else:
                self.add_warning("Could not connect to Bloomberg Terminal")
                self.add_warning("Ensure Bloomberg Terminal is running and logged in")
                return False

        except Exception as e:
            self.add_issue(f"Bloomberg connection test failed: {e}")
            return False

    def check_admin_rights(self):
        """Check if running with admin rights"""
        self.print_section("Admin Rights Check")

        if self.is_windows:
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if is_admin:
                    self.add_success("Running with administrator privileges")
                else:
                    self.add_warning("Not running as administrator")
                    self.add_warning("Some DLL installations may fail without admin rights")
            except:
                self.add_warning("Could not check administrator status")
        else:
            self.add_warning("Admin check only available on Windows")

    def provide_recommendations(self):
        """Provide recommendations based on findings"""
        self.print_section("Recommendations")

        if self.issues:
            print("\n🔴 Critical Issues Found:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")

        if self.warnings:
            print("\n🟡 Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        print("\n💡 Recommended Actions:")

        if any("wheel file" in issue for issue in self.issues):
            print("   📥 Download Bloomberg API from: https://www.bloomberg.com/professional/support/api-library/")

        if any("blpapi3_64.dll" in issue for issue in self.issues):
            print("   📁 Ensure blpapi3_64.dll is in your project directory")
            print("   🔧 Run setup_bloomberg_terminal.py to install DLL properly")

        if any("64-bit Python" in issue for issue in self.issues):
            print("   🐍 Install 64-bit Python from: https://www.python.org/downloads/")

        if any("import blpapi" in issue for issue in self.issues):
            print("   🔧 Run: python setup_bloomberg_terminal.py")
            print("   🔧 Or manually: pip install blpapi-3.25.3-py3-none-win_amd64.whl")

        if any("Bloomberg Terminal" in issue or "connection" in issue for issue in self.issues):
            print("   🖥️  Ensure Bloomberg Terminal is running and logged in")
            print("   🔍 In Bloomberg Terminal, type: API<GO> (not WAPI<GO>)")

    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print("🔍 Bloomberg API Diagnostic Tool")
        print("=" * 60)

        self.check_admin_rights()
        self.check_python_environment()
        self.check_bloomberg_terminal_process()  # New check
        self.check_bloomberg_files()
        self.check_dll_locations()
        self.check_path_environment()

        # Try to import blpapi
        if self.test_blpapi_import():
            self.test_bloomberg_connection()

        # Provide recommendations
        self.provide_recommendations()

        # Summary
        self.print_section("Diagnostic Summary")
        print(f"✅ Successes: {len(self.success)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")

        if self.issues:
            print("\n🎯 Focus on resolving the critical issues first.")
        elif self.warnings:
            print("\n🎯 Address warnings to improve reliability.")
        else:
            print("\n🎉 All checks passed! Bloomberg API should work correctly.")

if __name__ == "__main__":
    diagnostics = BloombergDiagnostics()
    diagnostics.run_full_diagnostic()

    print("\n" + "=" * 60)
    print("Press Enter to exit...")
    input()