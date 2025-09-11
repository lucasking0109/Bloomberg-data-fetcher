#!/usr/bin/env python3
"""
One-Click Setup and Run Script
Automatically sets up and launches the Bloomberg QQQ Fetcher
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     📊 Bloomberg QQQ Options Fetcher - Easy Setup 📊        ║
║                                                              ║
║     Fetches QQQ + Top 20 Constituents Options Data          ║
║     With Open Interest, Greeks, and More!                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Check Python version"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor} detected")
        return True
    else:
        print(f"❌ Python 3.7+ required (found {version.major}.{version.minor})")
        return False

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    
    packages = [
        "pandas",
        "numpy", 
        "pyyaml",
        "streamlit",
        "plotly"
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package, "--quiet"], 
                      capture_output=True)
    
    print("✅ Dependencies installed")

def check_bloomberg_api():
    """Check if Bloomberg API is installed"""
    print("\n🔍 Checking Bloomberg API...")
    try:
        import blpapi
        print("✅ Bloomberg API found")
        return True
    except ImportError:
        print("⚠️ Bloomberg API not found")
        print("""
To install Bloomberg API:
1. Open Bloomberg Terminal
2. Type: WAPI<GO>
3. Download Python API
4. Install the downloaded package
        """)
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    dirs = ["data", "logs", "config"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/ ready")

def test_bloomberg_connection():
    """Quick test of Bloomberg connection"""
    print("\n🔌 Testing Bloomberg connection...")
    try:
        from src.bloomberg_api import BloombergAPI
        api = BloombergAPI()
        if api.connect(max_retries=1):
            api.disconnect()
            print("✅ Bloomberg Terminal connected!")
            return True
        else:
            print("❌ Cannot connect to Bloomberg Terminal")
            print("Please ensure:")
            print("  1. Bloomberg Terminal is running")
            print("  2. You are logged in")
            print("  3. API is enabled (WAPI<GO>)")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def launch_app():
    """Launch the Streamlit app"""
    print("\n🚀 Launching Bloomberg Fetcher Dashboard...")
    print("-" * 50)
    print("The dashboard will open in your browser automatically")
    print("If not, open: http://localhost:8501")
    print("-" * 50)
    print("\nPress Ctrl+C to stop the app\n")
    
    # Launch Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def launch_cli_menu():
    """Show CLI menu if Streamlit not available"""
    while True:
        print("\n" + "="*50)
        print("BLOOMBERG QQQ FETCHER - MENU")
        print("="*50)
        print("1. Test Bloomberg Connection")
        print("2. Fetch QQQ Options Only")
        print("3. Fetch Top 5 Constituents")
        print("4. Fetch All (QQQ + 20 Constituents)")
        print("5. Resume Previous Fetch")
        print("6. Check Progress")
        print("7. Export Data to CSV")
        print("8. Exit")
        print("="*50)
        
        choice = input("\nSelect option (1-8): ")
        
        if choice == "1":
            test_bloomberg_connection()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            print("\n🚀 Starting QQQ fetch...")
            subprocess.run([sys.executable, "scripts/robust_fetch.py", "--qqq-only", "--export-csv"])
            
        elif choice == "3":
            print("\n🚀 Starting Top 5 fetch...")
            subprocess.run([sys.executable, "scripts/robust_fetch.py", "--top-n", "5", "--export-csv"])
            
        elif choice == "4":
            confirm = input("\n⚠️ This will fetch QQQ + ALL 20 constituents. Continue? (y/n): ")
            if confirm.lower() == 'y':
                print("\n🚀 Starting full fetch of all 20 stocks...")
                subprocess.run([sys.executable, "scripts/robust_fetch.py", "--top-n", "20", "--export-csv"])
            
        elif choice == "5":
            print("\n▶️ Resuming previous fetch...")
            subprocess.run([sys.executable, "scripts/robust_fetch.py", "--resume"])
            
        elif choice == "6":
            print("\n📊 Checking progress...")
            subprocess.run([sys.executable, "scripts/check_progress.py"])
            input("\nPress Enter to continue...")
            
        elif choice == "7":
            print("\n📥 Exporting data...")
            from src.database_manager import DatabaseManager
            db = DatabaseManager()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/export_{timestamp}.csv"
            db.export_to_csv(filepath)
            print(f"✅ Data exported to {filepath}")
            input("\nPress Enter to continue...")
            
        elif choice == "8":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

def main():
    """Main setup and run function"""
    print_banner()
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    try:
        install_dependencies()
    except Exception as e:
        print(f"⚠️ Some packages may not have installed: {e}")
    
    # Check Bloomberg API
    has_bloomberg = check_bloomberg_api()
    
    if not has_bloomberg:
        print("\n⚠️ Bloomberg API not installed")
        print("You need to install it from Bloomberg Terminal first")
        choice = input("\nContinue anyway? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(0)
    
    # Test connection if Bloomberg available
    if has_bloomberg:
        connected = test_bloomberg_connection()
        if not connected:
            print("\n⚠️ Bloomberg Terminal not connected")
            choice = input("Continue anyway? (y/n): ")
            if choice.lower() != 'y':
                sys.exit(0)
    
    # Check if Streamlit is available
    try:
        import streamlit
        print("\n✅ All systems ready!")
        print("\nLaunching options:")
        print("1. Web Dashboard (Recommended)")
        print("2. Command Line Interface")
        
        choice = input("\nSelect option (1 or 2): ")
        
        if choice == "2":
            launch_cli_menu()
        else:
            launch_app()
            
    except ImportError:
        print("\n⚠️ Streamlit not available, using CLI mode")
        launch_cli_menu()

if __name__ == "__main__":
    from datetime import datetime
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)