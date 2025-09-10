# Bloomberg Terminal Setup Instructions 🖥️

## 在 Bloomberg Terminal 電腦上執行步驟

### 1. Clone Repository
```bash
git clone https://github.com/[your-username]/[your-repo].git
cd [your-repo]/bloomberg_fetcher
```

### 2. 安裝 Python 套件
```bash
pip install -r requirements.txt
```

**重要**: 如果 `blpapi` 安裝失敗，請從 Bloomberg Terminal 下載:
1. 在 Terminal 輸入: `WAPI<GO>`
2. 選擇 "API Library"
3. 下載 Python 版本
4. 手動安裝

### 3. 測試連接
```bash
python scripts/quick_test.py
```

應該看到:
- ✅ Successfully connected to Bloomberg API
- ✅ All tests passed!

### 4. 設定配置
編輯 `config/config.yaml`:
- 調整 `strikes_above` 和 `strikes_below` (建議 20)
- 設定 `expiries_to_fetch` (建議 [1,2,3] 獲取3個月)
- 確認 API limits 符合您的訂閱

### 5. 每日執行 (美股收盤後)

**手動執行:**
```bash
python scripts/daily_fetch.py --save-db --export-csv
```

**自動化 (Windows Task Scheduler):**
1. 開啟 Task Scheduler
2. Create Basic Task
3. 設定時間: 每天 4:30 PM ET
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\bloomberg_fetcher\scripts\daily_fetch.py --save-db`

### 6. 獲取歷史資料 (60天)
```bash
python scripts/historical_fetch.py --days 60 --save-db
```

## 📊 預期 API 使用量

### 每日抓取
- QQQ 現價 ± 20 strikes = 40 strikes
- 3 個到期日
- 40 × 2 (Call+Put) × 3 = 240 options
- 每個 option 14 個欄位
- **總計**: 240 × 14 = 3,360 data points (約 7% 每日限額)

### 60天歷史資料
- 僅抓取 ATM ± 5 strikes (流動性較高)
- 10 × 2 × 3 × 60 = 3,600 options
- 每個 option 6 個欄位 (減少欄位)
- **總計**: 3,600 × 6 = 21,600 data points (約 43% 每日限額)

### 每月總使用量
- 每日: 3,360 × 20 (工作日) = 67,200
- 每週歷史更新: 21,600 × 4 = 86,400
- **總計**: 153,600 (約 31% 月限額)

## 🔍 資料驗證

檢查資料庫:
```python
from src.database_manager import DatabaseManager

db = DatabaseManager()
stats = db.get_summary_stats()
print(stats)
```

匯出到 Excel:
```python
db.export_to_csv("qqq_options_export.csv")
```

## ⚠️ 注意事項

1. **Bloomberg Terminal 必須開啟並登入**
2. **執行時不要最小化 Terminal**
3. **避免在市場時間執行大量歷史查詢**
4. **定期檢查 API 使用量**:
   ```bash
   cat logs/api_usage.json
   ```

## 📞 故障排除

### 連接失敗
- 確認 Terminal 已登入
- 輸入 `WAPI<GO>` 啟用 API
- 檢查防火牆是否封鎖 port 8194

### API 限制
- 減少 strikes 數量
- 分批執行歷史資料
- 增加 batch delay

### 資料缺失
- 某些 strikes 可能沒有交易
- Greeks 只在流動性足夠時計算
- 使用 `filter_liquid_options()` 過濾

## 🎯 最佳實踐

1. **每日 4:30 PM ET 後執行**
2. **週末執行歷史資料更新**
3. **每週檢查資料完整性**
4. **保留 20% API 配額應急**

---

準備好後，執行:
```bash
python scripts/daily_fetch.py --save-db
```

成功! 🎉