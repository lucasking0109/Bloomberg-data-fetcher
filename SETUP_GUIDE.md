# 🚀 Bloomberg QQQ Fetcher - 完整安裝指南

## 📋 系統需求

- **Bloomberg Terminal** 已安裝並登入
- **Python 3.6+** (64-bit)
- **Windows 作業系統**

## ⚡ 一鍵安裝（推薦）

### 方法1: 自動安裝腳本

1. **Clone 或下載專案**
   ```bash
   git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
   cd bloomberg-qqq-fetcher
   ```

2. **執行自動安裝**
   ```bash
   python setup_bloomberg_terminal.py
   ```

3. **測試執行**
   ```bash
   python scripts\historical_fetch.py --quick-test
   ```

### 方法2: 使用批次檔案

雙擊執行：
- `run_bloomberg_fetcher.bat` (Windows CMD)
- `run_bloomberg_fetcher.ps1` (PowerShell)

## 🔧 手動安裝步驟

如果自動安裝失敗，請按順序執行：

### 1. 檢查環境
```bash
python --version  # 需要 3.6+ 且為 64-bit
pip --version
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt --user
```

### 3. 安裝 Bloomberg API
```bash
pip install blpapi-3.25.3-py3-none-win_amd64.whl --user
```

### 4. 設置 DLL 路徑

**PowerShell:**
```powershell
$env:PATH += ";$(Get-Location)"
```

**CMD:**
```cmd
set PATH=%PATH%;%CD%
```

### 5. 測試連線
```bash
python -c "import blpapi; print('Success!')"
python scripts\historical_fetch.py --quick-test
```

## 🎯 快速使用

### 基本功能測試
```bash
# 1. API 使用量計算
python api_usage_calculator.py

# 2. 快速連線測試
python scripts\historical_fetch.py --quick-test

# 3. Web 介面
python app.py
```

### 歷史資料抓取
```bash
# 測試模式 (1週, ATM附近)
python scripts\historical_fetch.py --days 7 --atm-only

# 標準模式 (30天)
python scripts\historical_fetch.py --days 30

# 大量資料 (60天)
python scripts\historical_fetch.py --days 60
```

## ❓ 常見問題

### Q: "No module named 'blpapi'"
**A:** 重新執行安裝腳本
```bash
python setup_bloomberg_terminal.py
```

### Q: "cannot find blpapi3_64.dll"
**A:** 設置環境變數
```bash
# PowerShell
$env:PATH += ";$(Get-Location)"

# CMD
set PATH=%PATH%;%CD%
```

### Q: "Connection failed"
**A:** 檢查 Bloomberg Terminal
1. 確保 Bloomberg Terminal 已開啟並登入
2. 在 Bloomberg 輸入 `WAPI<GO>` 檢查 API 狀態
3. 確認 API 服務狀態為 "Running"

### Q: Bloomberg Terminal 沒有 Git
**A:** 下載 ZIP 檔案
1. 前往 GitHub: https://github.com/lucasking0109/bloomberg-qqq-fetcher
2. 點擊 "Code" → "Download ZIP"
3. 解壓縮後執行 `python setup_bloomberg_terminal.py`

## 🔄 更新專案

```bash
git pull origin main
python setup_bloomberg_terminal.py  # 重新安裝
```

## 📊 檔案輸出說明

執行後將產生以下檔案：

```
data/
├── QQQ_options_2025-09-13.csv              # QQQ 當日選擇權
├── QQQ_options_historical_2025-08-01_to_2025-09-13.parquet  # 歷史資料
└── bloomberg_options.db                     # SQLite 資料庫
```

## 📞 支援

如果遇到問題：
1. 檢查 Bloomberg Terminal 是否正常運行
2. 確認使用 64-bit Python
3. 重新執行 `python setup_bloomberg_terminal.py`