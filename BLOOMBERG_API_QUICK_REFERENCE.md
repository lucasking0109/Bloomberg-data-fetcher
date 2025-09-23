# Bloomberg API Installation - Quick Reference 🚀

## ⚠️ Important: WAPI Command Retired (2024)
The old `WAPI<GO>` command has been **RETIRED** by Bloomberg. Use the new methods below.

## 🎯 Current Installation Methods (2025)

### Method 1: Bloomberg Developer Portal (Recommended)
```
1. Go to: https://www.bloomberg.com/professional/support/api-library/
2. Login with your Bloomberg Terminal credentials
3. Download "Python API Library" (blpapi v3.25.3+)
4. Run installer as Administrator
5. Select Python installation path: C:\Users\{username}\AppData\Local\Programs\Python\Python313\
6. Verify installation: python -c "import blpapi; print('Success!')"
```

### Method 2: Bloomberg Terminal (New Command)
```
1. Open Bloomberg Terminal and log in
2. Type: API<GO> (NOT the old WAPI<GO>)
3. Navigate to "API Library" section
4. Select "Python API" for your platform
5. Download and run installer as Administrator
```

### Method 3: Manual Installation (If automatic fails)
```
1. Ensure you have the following files:
   - blpapi-3.25.3-py3-none-win_amd64.whl
   - blpapi3_64.dll
2. Run: pip install blpapi-3.25.3-py3-none-win_amd64.whl --user
3. Copy blpapi3_64.dll to Python directory
4. Run: python bloomberg_diagnostics.py (to verify)
```

### Method 4: Account Verification
```
Bloomberg API requires:
✅ Valid Bloomberg Terminal subscription
✅ Bloomberg Terminal running and logged in
✅ WAPI/API access enabled on your account
✅ Contact Bloomberg support if API access is denied
```

## 🔧 Installation Steps

1. **Download** Bloomberg API from Developer Portal or Terminal
2. **Run installer as Administrator** (CRITICAL!)
3. **Select Python path**: `C:\Users\{username}\AppData\Local\Programs\Python\Python313\`
4. **Verify installation**: `python -c "import blpapi; print('Success!')"`
5. **Run diagnostics**: `python bloomberg_diagnostics.py`
6. **Test connection**: `python setup_bloomberg_terminal.py`

## 🚨 Common Issues & Solutions

### "WAPI was retired"
- **Solution**: Use `API<GO>` instead of `WAPI<GO>`
- **New URL**: https://www.bloomberg.com/professional/support/api-library/

### "FileNotFoundError: blpapi3_64.dll"
- **Solution 1**: Run `python setup_bloomberg_terminal.py` (auto-fix)
- **Solution 2**: Run `python bloomberg_diagnostics.py` (diagnosis)
- **Solution 3**: Copy DLL to Python directory manually

### "Import blpapi failed"
- **Check**: Python is 64-bit (`python -c "import sys; print(sys.maxsize > 2**32)"`)
- **Check**: DLL version matches wheel version
- **Solution**: Reinstall with admin rights

### "Connection to Bloomberg failed"
- **Check**: Bloomberg Terminal is running and logged in
- **Check**: Account has API access enabled
- **Test**: Type `API<GO>` in Bloomberg Terminal

### Permission Errors
- **Solution**: Run Command Prompt as Administrator
- **Alternative**: Use `--user` flag for pip installs

## ✅ Verification Commands

```bash
# Full diagnostic (RECOMMENDED)
python bloomberg_diagnostics.py

# Quick setup and test
python setup_bloomberg_terminal.py

# Manual import test
python -c "import blpapi; print('✅ Success!')"

# Connection test
python -c "import blpapi; s=blpapi.Session(); print('✅ Connected' if s.start() else '❌ Failed'); s.stop()"
```

## 🎉 Ready to Use

Once installed and verified:
```bash
# Quick test (recommended first step)
python scripts/historical_fetch.py --quick-test

# Web interface
python app.py

# Full data fetch
python scripts/historical_fetch.py --days 30 --export-format parquet

# Windows GUI
run_bloomberg_fetcher.bat
```

## 📞 Support

If issues persist:
1. **Run diagnostics**: `python bloomberg_diagnostics.py`
2. **Check Bloomberg support**: https://www.bloomberg.com/professional/support/
3. **Contact your Bloomberg representative** for API access issues
4. **Check account permissions** - API access may need to be enabled

---
**Need help?** Check `BLOOMBERG_SETUP.md` for detailed instructions.
