# Bloomberg API Installation - Quick Reference 🚀

## ⚠️ Important: WAPI Command Retired
The old `WAPI<GO>` command has been retired. Use the new methods below.

## 🎯 Current Installation Methods

### Method 1: Bloomberg Developer Portal (Recommended)
```
1. Go to: https://www.bloomberg.com/professional/support/api-library/
2. Login with Bloomberg credentials
3. Download Python API library (blpapi)
4. Run installer as Administrator
5. Choose Python path: C:\Users\cchunan\AppData\Local\Programs\Python\Python313\
```

### Method 2: Bloomberg Terminal (New Command)
```
1. Open Bloomberg Terminal
2. Type: API<GO> (not WAPI<GO>)
3. Select "API Library"
4. Choose "Python" version
5. Download and install
```

### Method 3: Direct Download
```
1. Visit: https://www.bloomberg.com/professional/support/api-library/
2. Select "Bloomberg API" → "Python"
3. Download latest Windows version
4. Install as Administrator
```

## 🔧 Installation Steps

1. **Download** the Bloomberg API installer
2. **Run as Administrator**
3. **Choose Python path**: `C:\Users\cchunan\AppData\Local\Programs\Python\Python313\`
4. **Verify installation**: Run `python -c "import blpapi; print('Success!')"`
5. **Test connection**: Run `python scripts/quick_test.py`

## 🚨 Common Issues

- **"WAPI was retired"**: Use `API<GO>` instead
- **Installation fails**: Run as Administrator
- **Python not found**: Use full path to Python executable
- **Connection fails**: Ensure Bloomberg Terminal is running and logged in

## ✅ Verification

After installation, test with:
```bash
python scripts/setup_bloomberg.py
```

This will check:
- ✅ Python installation
- ✅ Bloomberg Terminal status
- ✅ Bloomberg API library
- ✅ Connection test

## 🎉 Ready to Use

Once installed, you can use:
- `python scripts/run_all.py --test` - Test connection
- `python scripts/run_all.py --daily` - Daily fetch
- `python scripts/run_all.py --historical` - Historical data
- `run_bloomberg.bat` - Windows menu interface

---
**Need help?** Check `BLOOMBERG_SETUP.md` for detailed instructions.
