# 手動修復Bloomberg API問題指南 🔧

如果自動安裝失敗，請按照以下步驟手動修復。

## 🎯 **核心問題**

你看到的錯誤 `FileNotFoundError: blpapi3_64.dll` 表示：
1. **DLL檔案位置錯誤** - Python找不到DLL檔案路徑
2. **Bloomberg Terminal未運行** - API需要連接到localhost:8194
3. **帳號未登入** - Bloomberg API需要有效的Terminal session

## 🔍 **第一步：診斷問題**

```cmd
python bloomberg_diagnostics.py
```

這會檢查：
- ✅ Bloomberg Terminal是否運行 (bbcomm.exe)
- ✅ Python環境是否正確
- ✅ DLL檔案位置
- ✅ API連接狀態

## 🛠️ **手動修復步驟**

### **步驟1：確保Bloomberg Terminal運行**

1. **啟動Bloomberg Terminal**
2. **完成登入** - 確保看到Terminal主畫面
3. **檢查API狀態** - 在Terminal輸入: `API<GO>`

### **步驟2：手動複製DLL檔案**

**以管理員身份開啟命令提示字元**，然後執行：

```cmd
# 方法1：複製到Python目錄
copy "blpapi3_64.dll" "C:\Users\cchunan\AppData\Local\Programs\Python\Python313\"

# 方法2：複製到Scripts目錄
copy "blpapi3_64.dll" "C:\Users\cchunan\AppData\Local\Programs\Python\Python313\Scripts\"

# 方法3：複製到System32 (需要管理員權限)
copy "blpapi3_64.dll" "C:\Windows\System32\"
```

**替換路徑說明：**
- 將 `cchunan` 替換為你的用戶名
- 將 `Python313` 替換為你的Python版本

### **步驟3：安裝Python套件**

```cmd
# 先解除安裝舊版本
pip uninstall blpapi -y

# 安裝新版本
pip install blpapi-3.25.3-py3-none-win_amd64.whl --user

# 驗證安裝
python -c "import blpapi; print('Success!')"
```

### **步驟4：測試連接**

```cmd
# 測試導入
python -c "import blpapi; print('✅ Import successful')"

# 測試連接
python -c "
import blpapi
session = blpapi.Session()
if session.start():
    print('✅ Connected to Bloomberg Terminal')
    session.stop()
else:
    print('❌ Cannot connect - check Terminal is running')
"
```

## 🚨 **常見問題排解**

### **問題1：找不到blpapi3_64.dll**
```
FileNotFoundError: Could not find module 'blpapi3_64.dll'
```

**解決方案：**
1. 確認DLL檔案在專案資料夾
2. 以管理員權限複製DLL到System32
3. 更新環境變數PATH

### **問題2：無法連接到Bloomberg**
```
Connection failed to localhost:8194
```

**解決方案：**
1. 確認Bloomberg Terminal正在運行
2. 確認已登入Bloomberg Terminal
3. 檢查Windows防火牆設定
4. 重新啟動Bloomberg Terminal

### **問題3：沒有API權限**
```
Not authorized to access API
```

**解決方案：**
1. 確認你的Bloomberg帳號有API存取權限
2. 聯絡Bloomberg支援申請API存取
3. 確認公司的Bloomberg訂閱包含API功能

### **問題4：Python版本不相容**
```
ImportError: DLL load failed
```

**解決方案：**
1. 確認使用64位元Python
2. 確認Python版本3.8+
3. 重新安裝對應的wheel檔案

## 📋 **完整檢查清單**

在聯絡支援前，請確認：

- [ ] Bloomberg Terminal正在運行且已登入
- [ ] 在Terminal輸入`API<GO>`可以看到API資訊
- [ ] Python是64位元版本 (`python -c "import sys; print(sys.maxsize > 2**32)"`)
- [ ] blpapi3_64.dll在專案資料夾中
- [ ] 已將DLL複製到Python目錄
- [ ] 已安裝blpapi wheel檔案
- [ ] 以管理員權限執行安裝命令

## 🔄 **重置和重新安裝**

如果所有方法都失敗：

```cmd
# 1. 完全清理
pip uninstall blpapi -y
del "C:\Users\cchunan\AppData\Local\Programs\Python\Python313\blpapi3_64.dll"
del "C:\Windows\System32\blpapi3_64.dll"

# 2. 重新從Bloomberg下載
# 在Bloomberg Terminal: API<GO> → Download Python API

# 3. 重新執行自動安裝
python setup_bloomberg_terminal.py
```

## 📞 **獲得幫助**

如果問題持續：

1. **執行診斷：** `python bloomberg_diagnostics.py`
2. **聯絡Bloomberg支援：** https://www.bloomberg.com/professional/support/
3. **檢查帳號權限** - 可能需要升級訂閱以包含API存取

## ✅ **驗證修復成功**

修復完成後，執行：

```cmd
# 完整測試
python setup_bloomberg_terminal.py

# 快速數據測試
python scripts/historical_fetch.py --quick-test
```

成功後你應該看到：
- ✅ Bloomberg API導入成功
- ✅ 連接到Bloomberg Terminal
- ✅ 可以獲取測試數據

---

**注意：** Bloomberg API **必須**有有效的Bloomberg Terminal訂閱才能使用。這不是免費的公開API。