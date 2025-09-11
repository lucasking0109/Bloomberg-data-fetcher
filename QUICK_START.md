# 🚀 QUICK START - Bloomberg QQQ Fetcher

## 🎯 For New Users (2 Minutes)

```bash
# Clone repository
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher

# One-click setup and launch
python setup_and_run.py
```

**That's it!** Web interface opens automatically in your browser.

---

## 🔥 Web Interface Actions

### **Testing (5 minutes)**
1. Click **"Test Connection"** → Verify Bloomberg is connected
2. Click **"💼 Fetch Top 5"** → Get QQQ + 5 stocks (CSV format)
3. Click **"📥 Export Data"** → Download results

### **Production (30 minutes)**  
1. Click **"🔥 Fetch All 20"** → Get complete dataset (Parquet format)
2. Wait for completion → Monitor progress bar
3. Click **"📥 Export Data"** → Download results

---

## 💻 Command Line (Alternative)

```bash
# Testing dataset
python scripts/robust_fetch.py --top-n 5 --export-csv

# Production dataset  
python scripts/robust_fetch.py --export-csv

# Resume if interrupted
python scripts/robust_fetch.py --resume
```

---

## 📊 What You Get

### **Testing (5 stocks)**
- **Records**: ~5,000 options 
- **File**: CSV format (~2MB)
- **Time**: 5 minutes
- **Use**: Data validation, testing

### **Production (20 stocks)**  
- **Records**: ~97,000 options
- **File**: Parquet format (~20MB)
- **Time**: 30 minutes
- **Use**: Portfolio analysis, hedging

---

## 📂 Output Files

```
data/
├── bloomberg_options.db              # SQLite database
├── bloomberg_data_20250910_143022.csv      # CSV export (testing)
└── bloomberg_data_20250910_143022.parquet  # Parquet export (production)
```

### **Loading Data**
```python
import pandas as pd

# CSV files
df = pd.read_csv('data/bloomberg_data_20250910_143022.csv')

# Parquet files (10x faster)
df = pd.read_parquet('data/bloomberg_data_20250910_143022.parquet')
```

---

## ⚠️ Prerequisites

Before running, ensure:

1. **Bloomberg Terminal** is running and logged in
2. **Python 3.8+** is installed
3. **WAPI enabled** in Bloomberg (type `WAPI<GO>`)
4. **Best time**: After 4:30 PM ET (market close)

---

## 🆘 Common Issues

### **"Bloomberg not connected"**
```bash
# Check Terminal is running and logged in
# Type WAPI<GO> in Terminal to enable API
```

### **"blpapi not found"**
```bash
# API will auto-install, or manually:
pip install blpapi-3.25.3-py3-none-win_amd64.whl
```

### **"Fetch interrupted"**
```bash
# Resume from where it stopped
python scripts/robust_fetch.py --resume
```

---

## 🎯 Success Indicators

### **Testing Complete When:**
- Progress bar reaches 100%
- Message: "✅ Data exported to CSV"
- File size: ~2MB
- Records: ~5,000

### **Production Complete When:**
- Progress bar reaches 100%  
- Message: "✅ Data exported to Parquet"
- File size: ~20MB
- Records: ~97,000

---

## 📈 Data Contents

Each options record includes:
- **Basics**: ticker, strike, expiry, type (call/put)
- **Prices**: bid, ask, last, underlying price
- **Greeks**: Delta, Gamma, Theta, Vega, Rho
- **Liquidity**: Volume, **Open Interest**, bid/ask sizes
- **Analytics**: Implied volatility, moneyness, days to expiry

---

## 🔗 Next Steps

- **Analysis**: Use Jupyter notebooks with pandas
- **Automation**: Schedule daily runs via cron/Task Scheduler  
- **Integration**: Import data into your trading systems
- **Documentation**: See [README.md](README.md) for full details

---

## 🚀 Ready to Start?

```bash
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher
python setup_and_run.py
```

**Click "💼 Fetch Top 5" to begin!** 🎯