# 🏢 Bloomberg Terminal 完整設置指南

**專為沒有 Python 環境的 Bloomberg Terminal 工作站設計**

## 📋 **開始前確認**

您的 Bloomberg Terminal 工作站需要：
- ✅ Bloomberg Terminal 已安裝並可正常登入
- ✅ 可訪問網路（下載 Python）
- ✅ 基本的檔案操作權限

## 🚀 **方法1: 一鍵安裝（推薦）**

### **步驟1: 下載專案**

**如果有 Git：**
```cmd
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher
```

**如果沒有 Git：**
1. 瀏覽器前往：https://github.com/lucasking0109/bloomberg-qqq-fetcher
2. 點擊綠色 `Code` 按鈕 → `Download ZIP`
3. 解壓縮到 `Documents` 資料夾

### **步驟2: 執行安裝**

雙擊 `run_bloomberg_fetcher.bat` 檔案，腳本會自動：
- 檢查 Python 是否已安裝
- 如果沒有，提供下載連結和安裝指引
- 自動安裝所有依賴套件
- 設置 Bloomberg API
- 測試連線

## 🔧 **方法2: 手動安裝 Python**

如果自動安裝失敗，請手動安裝：

### **步驟1: 下載 Python**

1. **前往官網**：https://www.python.org/downloads/
2. **下載 Python 3.8+ (64-bit)**
3. **重要設定**：
   - ✅ 勾選 "Add Python to PATH"
   - ✅ 選擇 "Install for all users"（如果有權限）
   - ✅ 確認下載 64-bit 版本

### **步驟2: 安裝 Python**

1. 執行下載的安裝檔
2. **自訂安裝**，確保勾選：
   - ✅ pip
   - ✅ Add to PATH
   - ✅ py launcher

### **步驟3: 驗證安裝**

打開新的命令提示字元：
```cmd
python --version
pip --version
```

應該顯示 Python 3.8+ 和 pip 版本

### **步驟4: 執行專案安裝**

```cmd
cd bloomberg-qqq-fetcher
python setup_bloomberg_terminal.py
```

## 🎯 **快速使用**

安裝完成後：

### **基本測試**
```cmd
# 快速連線測試
python scripts\historical_fetch.py --quick-test

# API 使用量計算
python api_usage_calculator.py
```

### **Web 介面**
```cmd
python app.py
# 然後瀏覽器開啟 http://localhost:8501
```

### **歷史資料抓取**
```cmd
# 測試模式（1週）
python scripts\historical_fetch.py --days 7 --atm-only

# 標準模式（30天）
python scripts\historical_fetch.py --days 30
```

## ❓ **常見問題**

### **Q: 我沒有安裝權限怎麼辦？**

**A: 使用便攜版 Python**
1. 下載 Python Embedded 版本
2. 解壓縮到用戶目錄（如 `C:\Users\您的名字\Python`）
3. 設置環境變數：
   ```cmd
   set PATH=%PATH%;C:\Users\您的名字\Python
   set PATH=%PATH%;C:\Users\您的名字\Python\Scripts
   ```

### **Q: Bloomberg Terminal 沒有網路權限**

**A: 離線安裝**
1. 在有網路的電腦下載：
   - Python 安裝檔
   - 專案 ZIP 檔案
   - 所有依賴套件（使用 `pip download -r requirements.txt`）
2. 複製到 Bloomberg Terminal 工作站
3. 離線安裝

### **Q: "Access Denied" 錯誤**

**A: 權限處理**
```cmd
# 使用用戶安裝
pip install --user -r requirements.txt

# 或請 IT 部門協助
```

### **Q: Bloomberg API 連線失敗**

**A: 檢查清單**
1. Bloomberg Terminal 是否已登入？
2. 在 Bloomberg 輸入 `WAPI<GO>` 檢查 API 狀態
3. API 服務是否為 "Running"？
4. 防火牆是否阻擋？

## 🔄 **維護和更新**

### **更新專案**
```cmd
git pull origin main
python setup_bloomberg_terminal.py
```

### **重新安裝**
```cmd
# 如果遇到問題，重新安裝
python setup_bloomberg_terminal.py
```

## 📊 **預期輸出**

成功執行後會在 `data/` 目錄產生：

```
data/
├── QQQ_options_2025-09-16.csv              # 當日資料
├── QQQ_options_historical_2025-08-01_to_2025-09-16.parquet  # 歷史資料
├── bloomberg_options.db                     # SQLite 資料庫
└── export_logs/                             # 執行記錄
```

## 🆘 **緊急支援**

如果所有方法都失敗：

1. **確認環境**：
   ```cmd
   systeminfo | findstr "System Type"  # 確認 64-bit
   python -c "import platform; print(platform.architecture())"  # 確認 Python 64-bit
   ```

2. **檢查 Bloomberg**：
   - Bloomberg Terminal 完全重啟
   - 重新登入
   - 確認 WAPI 狀態

3. **聯繫 IT 部門**：
   - 請求 Python 3.8+ (64-bit) 安裝權限
   - 請求網路訪問權限（pip 安裝）

## 💡 **最佳實踐**

1. **定期執行**：建議美股收盤後執行（台灣時間早上）
2. **API 使用量**：使用計算器規劃抓取範圍
3. **資料備份**：定期備份 `data/` 目錄
4. **更新專案**：每月檢查更新

---

**準備好開始了嗎？雙擊 `run_bloomberg_fetcher.bat` 開始！** 🚀