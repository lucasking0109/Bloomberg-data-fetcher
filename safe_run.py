#!/usr/bin/env python3
"""
🛡️ Safe Bloomberg QQQ Fetcher - 防錯版執行器
自動處理所有常見錯誤，確保順利執行
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    print(f"📌 Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ 需要 Python 3.6 或更高版本")
        return False
    return True

def check_blpapi():
    """檢查Bloomberg API是否安裝"""
    try:
        import blpapi
        print("✅ Bloomberg API (blpapi) 已安裝")
        return True
    except ImportError:
        print("❌ Bloomberg API (blpapi) 未安裝")
        return False

def install_blpapi():
    """安裝Bloomberg API"""
    print("\n🔧 正在安裝 Bloomberg API...")
    try:
        # 嘗試官方來源
        cmd = [sys.executable, "-m", "pip", "install", "--index-url",
               "https://blpapi.bloomberg.com/repository/releases/python/simple/", "blpapi"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Bloomberg API 安裝成功")
            return True
        else:
            print(f"❌ 安裝失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安裝錯誤: {e}")
        return False

def install_requirements():
    """安裝所有必要套件"""
    print("\n📦 安裝必要套件...")
    packages = [
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
        "plotly>=5.0.0"
    ]

    for package in packages:
        try:
            pkg_name = package.split('>=')[0]
            __import__(pkg_name)
            print(f"  ✅ {pkg_name} 已安裝")
        except ImportError:
            print(f"  📥 安裝 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package],
                         capture_output=True)

def test_bloomberg_connection():
    """測試Bloomberg連線"""
    print("\n🔗 測試 Bloomberg 連線...")

    test_code = """
import blpapi
try:
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost("localhost")
    sessionOptions.setServerPort(8194)
    session = blpapi.Session(sessionOptions)

    if session.start():
        print("✅ Bloomberg 連線成功")
        session.stop()
        exit(0)
    else:
        print("❌ Bloomberg 連線失敗")
        exit(1)
except Exception as e:
    print(f"❌ 連線錯誤: {e}")
    exit(1)
"""

    result = subprocess.run([sys.executable, "-c", test_code], capture_output=True, text=True)
    print(result.stdout)

    if result.returncode != 0:
        print("\n⚠️ Bloomberg Terminal 檢查清單:")
        print("  1. Bloomberg Terminal 是否已開啟？")
        print("  2. 您是否已登入 Bloomberg？")
        print("  3. 在 Terminal 輸入 API<GO> 檢查權限")
        return False
    return True

def check_code_fix():
    """檢查Greeks修復是否已套用"""
    print("\n🔍 檢查程式碼修復...")

    fetcher_path = "src/qqq_options_fetcher.py"
    if os.path.exists(fetcher_path):
        with open(fetcher_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "self.OPTION_FIELDS[:11]" in content:
            print("✅ Greeks 修復已套用 ([:11])")
            return True
        elif "self.OPTION_FIELDS[:6]" in content:
            print("❌ 發現舊版程式碼 ([:6])，需要更新")
            print("   請執行: git pull origin main")
            return False
    else:
        print("❌ 找不到 src/qqq_options_fetcher.py")
        return False

    return True

def run_quick_test():
    """執行快速測試"""
    print("\n🚀 執行快速測試...")
    print("-" * 60)

    cmd = [sys.executable, "scripts/historical_fetch.py", "--quick-test"]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, universal_newlines=True)

        # 即時顯示輸出
        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            print("\n✅ 測試成功！")
            return True
        else:
            stderr = process.stderr.read()
            print(f"\n❌ 測試失敗")
            if stderr:
                print(f"錯誤訊息: {stderr}")
            return False

    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return False

def main_menu():
    """主選單"""
    print("\n" + "="*60)
    print("📊 選擇執行選項:")
    print("="*60)
    print("1. 快速測試 (少量資料)")
    print("2. 完整 QQQ 資料 (30天)")
    print("3. 個別股票 (AAPL)")
    print("4. 網頁介面")
    print("5. 診斷工具")
    print("6. 退出")

    choice = input("\n請選擇 (1-6): ").strip()

    commands = {
        "1": ([sys.executable, "scripts/historical_fetch.py", "--quick-test"], "快速測試"),
        "2": ([sys.executable, "scripts/historical_fetch.py", "--days", "30"], "完整QQQ資料"),
        "3": ([sys.executable, "scripts/constituents_fetch.py", "--ticker", "AAPL"], "AAPL選擇權"),
        "4": (["streamlit", "run", "app.py"], "網頁介面"),
        "5": ([sys.executable, "diagnose_greeks.py"], "診斷工具"),
        "6": (None, "退出")
    }

    if choice in commands:
        if choice == "6":
            print("👋 再見！")
            return False

        cmd, desc = commands[choice]
        print(f"\n🔄 執行: {desc}")
        print("-" * 60)

        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"❌ 執行錯誤: {e}")

        return True
    else:
        print("❌ 無效選項")
        return True

def main():
    """主程式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║       🛡️ Safe Bloomberg QQQ Fetcher - 防錯版            ║
║            自動處理所有常見問題                           ║
╚══════════════════════════════════════════════════════════╝
    """)

    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. 檢查Python版本
    if not check_python_version():
        print("❌ Python 版本不符合要求")
        input("\n按 Enter 結束...")
        return

    # 2. 檢查/安裝 blpapi
    if not check_blpapi():
        if not install_blpapi():
            print("\n❌ 無法安裝 Bloomberg API")
            print("請手動執行: python setup_bloomberg_terminal.py")
            input("\n按 Enter 結束...")
            return

    # 3. 安裝其他套件
    install_requirements()

    # 4. 檢查程式碼修復
    if not check_code_fix():
        print("\n⚠️ 程式碼需要更新")
        update = input("是否要自動更新? (y/n): ").strip().lower()
        if update == 'y':
            subprocess.run(["git", "pull", "origin", "main"])
            print("✅ 已更新程式碼")

    # 5. 測試Bloomberg連線
    if not test_bloomberg_connection():
        print("\n⚠️ Bloomberg 連線有問題")
        cont = input("是否仍要繼續? (y/n): ").strip().lower()
        if cont != 'y':
            return

    # 6. 主選單
    while main_menu():
        pass

if __name__ == "__main__":
    main()