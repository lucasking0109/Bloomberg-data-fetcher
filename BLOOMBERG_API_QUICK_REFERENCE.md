# Bloomberg API Installation - Quick Reference 🚀

## 🎯 Current Installation Methods (2025)

### Method 1: Official Pip Installation (Recommended)
```bash
# Bloomberg's official pip repository
python -m pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple/ blpapi

# Verify installation
python -c "import blpapi; print('✅ Success!')"
```

### Method 2: Our Automated Setup (Easiest)
```bash
# Run our setup script (handles everything automatically)
python setup_bloomberg_terminal.py
```

### Method 3: Bloomberg Terminal (If pip fails)
```
1. Open Bloomberg Terminal and log in
2. Type: API<GO> (NOT the old WAPI<GO>)
3. Navigate to "API Library" section
4. Select "Python API" for your platform
5. Download and install, then run: python setup_bloomberg_terminal.py
```

## 🔧 Quick Setup Steps

1. **Ensure Prerequisites**:
   - Bloomberg Terminal installed and logged in
   - Python 3.6+ (64-bit)
   - Administrator privileges

2. **Install**:
   ```bash
   python setup_bloomberg_terminal.py
   ```

3. **Verify**:
   ```bash
   python -c "import blpapi; print('✅ Installation successful!')"
   ```

## 🚨 Common Issues & Solutions

### "Import blpapi failed"
- **Check**: Python is 64-bit (`python -c "import sys; print(sys.maxsize > 2**32)"`)
- **Solution**: Run `python setup_bloomberg_terminal.py` with administrator privileges

### "Connection to Bloomberg failed"
- **Check**: Bloomberg Terminal is running and logged in
- **Check**: Account has API access enabled
- **Test**: Type `API<GO>` in Bloomberg Terminal

### "FileNotFoundError: blpapi3_64.dll"
- **Solution**: Run `python setup_bloomberg_terminal.py` (auto-fixes DLL issues)

## ✅ Verification Commands

```bash
# Full setup and verification
python setup_bloomberg_terminal.py

# Manual connection test
python -c "import blpapi; s=blpapi.Session(); print('✅ Connected' if s.start() else '❌ Failed'); s.stop()"
```

## 🎉 Ready to Use

Once installed and verified:
```bash
# Quick test (recommended first step)
python scripts/historical_fetch.py --quick-test

# Web interface
streamlit run app.py

# Fetch QQQ options data
python scripts/historical_fetch.py --days 30

# Fetch individual stock options
python scripts/constituents_fetch.py --ticker AAPL
```

## 📞 Support

If issues persist:
1. **Run setup again**: `python setup_bloomberg_terminal.py`
2. **Check Bloomberg support**: https://www.bloomberg.com/professional/support/
3. **Contact your Bloomberg representative** for API access issues

---
**⚠️ Important**: The old `WAPI<GO>` command was retired in 2024. Always use `API<GO>` instead.