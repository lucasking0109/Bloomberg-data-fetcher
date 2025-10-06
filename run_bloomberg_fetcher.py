#!/usr/bin/env python3
"""
🚀 Bloomberg QQQ Fetcher - 一鍵執行腳本
只要執行這個檔案就會自動抓取所有資料
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """執行命令並顯示狀態"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功！")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ 失敗")
            if result.stderr:
                print(f"錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     🚀 Bloomberg QQQ Options Fetcher - 一鍵執行         ║
╚══════════════════════════════════════════════════════════╝
    """)

    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 選擇執行模式
    print("\n請選擇執行模式:")
    print("1. 快速測試 (建議先執行)")
    print("2. 完整 QQQ 資料 (30天)")
    print("3. 個別股票 (AAPL)")
    print("4. Top 10 成分股")
    print("5. 啟動網頁介面")
    print("6. 執行診斷工具")

    choice = input("\n請輸入選項 (1-6): ").strip()

    commands = {
        "1": ("python scripts/historical_fetch.py --quick-test",
              "執行快速測試 (少量資料)"),
        "2": ("python scripts/historical_fetch.py --days 30",
              "抓取 QQQ 30天完整資料"),
        "3": ("python scripts/constituents_fetch.py --ticker AAPL",
              "抓取 AAPL 選擇權資料"),
        "4": ("python scripts/constituents_fetch.py --top 10",
              "抓取 Top 10 成分股資料"),
        "5": ("streamlit run app.py",
              "啟動網頁介面"),
        "6": ("python diagnose_greeks.py",
              "執行 Greeks 診斷工具")
    }

    if choice in commands:
        cmd, desc = commands[choice]

        # 先檢查 Bloomberg API
        print("\n🔍 檢查 Bloomberg API...")
        check_cmd = "python -c \"import blpapi; print('✅ Bloomberg API 已安裝')\""
        if not run_command(check_cmd, "檢查 Bloomberg API"):
            print("\n⚠️  Bloomberg API 未安裝，正在安裝...")
            run_command("python setup_bloomberg_terminal.py", "安裝 Bloomberg API")

        # 執行選擇的命令
        success = run_command(cmd, desc)

        if success:
            print(f"\n{'='*60}")
            print("🎉 執行完成！")
            print(f"{'='*60}")

            if choice in ["1", "2", "3", "4"]:
                print("\n📊 資料已儲存到:")
                print("   • data/ 資料夾中的 .parquet 檔案")
                print("   • data/bloomberg_options.db 資料庫")
                print("\n💡 提示: 可以用 pandas 讀取 parquet 檔案查看資料")
            elif choice == "5":
                print("\n🌐 網頁介面已啟動!")
                print("   請在瀏覽器開啟: http://localhost:8501")
        else:
            print("\n❌ 執行失敗，請檢查:")
            print("   1. Bloomberg Terminal 是否正在執行並已登入")
            print("   2. Python 環境是否正確")
            print("   3. 執行 'python diagnose_greeks.py' 診斷問題")
    else:
        print("\n❌ 無效的選項，請重新執行並選擇 1-6")

    input("\n按 Enter 結束...")

if __name__ == "__main__":
    main()