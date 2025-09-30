# 🚀 QUICK START - Bloomberg QQQ Fetcher

## ⚡ 3-Step Setup (2 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher

# 2. Setup Bloomberg API
python setup_bloomberg_terminal.py

# 3. Test connection
python scripts/historical_fetch.py --quick-test
```

**Done!** You now have professional-grade options data fetching.

---

## 🎯 Choose Your Interface

### 🖥️ Command Line (Fast)
```bash
# QQQ options (30 days)
python scripts/historical_fetch.py --days 30

# Individual stock (AAPL)
python scripts/constituents_fetch.py --ticker AAPL

# Top 10 constituents
python scripts/constituents_fetch.py --top 10
```

### 📊 Web Interface (Visual)
```bash
# Launch dashboard
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Features:**
- ✅ Visual database statistics
- ✅ One-click data fetching
- ✅ Real-time progress bars
- ✅ Data preview with charts

---

## 🔥 Quick Commands

### Testing (5 minutes)
```bash
# Quick test with limited data
python scripts/historical_fetch.py --quick-test

# Single stock test
python scripts/constituents_fetch.py --ticker AAPL --export-format csv
```

### Production (15-30 minutes)
```bash
# Full QQQ dataset (60 days)
python scripts/historical_fetch.py --days 60 --export-format parquet

# All 20 constituents
python scripts/constituents_fetch.py --all --export-format parquet
```

---

## 📁 Your Data

All fetched data is saved to:
```
data/
├── qqq_options_[timestamp].parquet     # QQQ options data
├── AAPL_options_[timestamp].csv        # Individual stock data
├── top10_constituents_[timestamp].csv  # Bulk constituent data
└── bloomberg_options.db                # SQLite database
```

---

## 🚨 Troubleshooting

### "Import blpapi failed"
```bash
# Re-run setup with admin privileges
python setup_bloomberg_terminal.py
```

### "Connection failed"
1. **Check Bloomberg Terminal is running and logged in**
2. **Test API access**: Type `API<GO>` in Bloomberg Terminal
3. **Verify account permissions** with Bloomberg support

### "No data returned"
- **Market hours**: Options data available 6:30 AM - 5:00 PM ET
- **Valid tickers**: Ensure stock symbols exist and have options

---

## 🎯 What You Get

### QQQ Options
- **ATM ± 40 strikes** for comprehensive coverage
- **All weekly expiries** within 60 days
- **Full Greeks**: Delta, Gamma, Theta, Vega, Rho
- **Open Interest** for liquidity analysis

### Individual Stocks
- **Top 20 QQQ constituents** by weight
- **Same comprehensive fields** as QQQ
- **Real-time spot prices**
- **Bulk or single-ticker** fetching

### Data Quality
- **26 Bloomberg fields** per option
- **Built-in validation** removes bad records
- **Quality scoring** (A+ to F grades)
- **Professional export formats**

---

## 🎉 Next Steps

1. **Start with quick test**: `python scripts/historical_fetch.py --quick-test`
2. **Try web interface**: `streamlit run app.py`
3. **Fetch production data**: `python scripts/historical_fetch.py --days 30`
4. **Analyze in Python**: `pandas.read_parquet('data/qqq_options_*.parquet')`

**Ready to analyze professional options data!** 🚀