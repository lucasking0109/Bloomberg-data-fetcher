# 🤖 AI Assistant Quick Reference

## 🎯 **What This System Does**
Fetches **comprehensive options data** for QQQ + 20 constituents with Greeks and Open Interest for portfolio hedging analysis.

---

## ⚡ **Key Commands for Users**

### **Complete Setup (Recommended)**
```bash
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher
python setup_and_run.py  # Web interface opens automatically
```

### **Command Line Options**
```bash
# Full production dataset (20 stocks → Parquet)
python scripts/robust_fetch.py --export-csv

# Testing dataset (5 stocks → CSV)  
python scripts/robust_fetch.py --top-n 5 --export-csv

# Resume interrupted fetch
python scripts/robust_fetch.py --resume

# Check progress
python scripts/check_progress.py
```

---

## 📊 **Current Specifications (Updated 2025-09-10)**

### **Data Volume**
- **Strikes**: ATM ± 40 (80 per expiry) 
- **Expiries**: Weekly + quarterly (QQQ has weekly expiries)
- **Records**: ~97,000 options (4x comprehensive)
- **Time**: 25-30 minutes full fetch

### **Export Intelligence**  
- **≤5 stocks**: Auto-uses CSV (easy inspection)
- **20 stocks**: Auto-uses Parquet (efficient, 10x faster loading)
- **File sizes**: CSV ~40MB, Parquet ~20MB

---

## 🔧 **Critical Configuration**

### **Always Include These Fields**
```yaml
option_fields:
  - OPEN_INT      # CRITICAL for liquidity analysis
  - DELTA         # All Greeks required
  - GAMMA
  - THETA  
  - VEGA
  - RHO
```

### **Strike/Expiry Settings**
```yaml
fetch_config:
  strikes_above_atm: 40    # ± 40 strikes (not ± 20)
  strikes_below_atm: 40
  max_days_to_expiry: 60   # 2 months, includes weekly expiries
```

---

## 🎮 **Web Interface Actions**

| Button | Purpose | Time | Output |
|--------|---------|------|--------|
| Test Connection | Verify Bloomberg | 10s | Status check |
| Fetch Top 5 | Testing dataset | 5min | CSV format |
| **🔥 Fetch All 20** | **Production** | **30min** | **Parquet** |
| Resume | Continue interrupted | Variable | Same as original |
| Export Data | Manual export | 30s | CSV or Parquet |

---

## 🚨 **Prerequisites Check**

Before any fetch operation:
1. ✅ Bloomberg Terminal running + logged in
2. ✅ WAPI enabled (type `WAPI<GO>` in Terminal)  
3. ✅ After 4:30 PM ET (optimal time)
4. ✅ Python 3.8+ installed

---

## 📁 **File Structure Reference**

```
bloomberg-qqq-fetcher/
├── 🌐 app.py                    # Web dashboard
├── 🚀 setup_and_run.py         # One-click launcher
├── 📚 README.md                 # Full documentation
├── 📖 QUICK_START.md            # 2-minute guide
│
├── config/
│   └── qqq_constituents.yaml   # 20 stocks + ±40 strikes config
│
├── scripts/
│   ├── robust_fetch.py          # MAIN SCRIPT
│   └── check_progress.py        # Monitor fetches
│
└── data/
    ├── bloomberg_options.db     # SQLite database  
    └── *.parquet               # Efficient exports
```

---

## 🔍 **Troubleshooting Commands**

```bash
# Connection test
python -c "from src.bloomberg_api import test_connection; test_connection()"

# Database stats
python -c "from src.database_manager import DatabaseManager; db = DatabaseManager(); print(db.get_summary_stats())"

# Manual export
python -c "from src.database_manager import DatabaseManager; db = DatabaseManager(); db.export_to_parquet('data/manual_export.parquet')"

# API reinstall
pip install blpapi-3.25.3-py3-none-win_amd64.whl
```

---

## 🎯 **Success Validation**

### **Testing Complete (5 stocks)**
```python
# Should see ~5,000 records
import pandas as pd
df = pd.read_csv('data/bloomberg_data_TIMESTAMP.csv')
print(f"Records: {len(df)}")  # ~5,000
print(f"Tickers: {df['underlying'].nunique()}")  # 6 (QQQ + 5)
```

### **Production Complete (20 stocks)**  
```python
# Should see ~97,000 records
import pandas as pd
df = pd.read_parquet('data/bloomberg_data_TIMESTAMP.parquet')
print(f"Records: {len(df)}")  # ~97,000
print(f"Tickers: {df['underlying'].nunique()}")  # 21 (QQQ + 20)
print(f"Strikes per ticker: {df.groupby('underlying')['strike'].count().mean():.0f}")  # ~80
```

---

## 💡 **AI Assistant Guidelines**

### **Default Recommendations**
1. **Always suggest full 20-stock fetch** unless user specifically wants testing
2. **Use web interface** for new users (`python setup_and_run.py`)
3. **Mention Parquet advantages** for large datasets (10x faster loading)
4. **Check Bloomberg connection first** before any fetch operation
5. **Enable resume capability** if fetch might be interrupted

### **Common User Requests & Responses**

**"How do I get options data?"**
```bash
python setup_and_run.py
# Click "🔥 Fetch All 20" for complete dataset
```

**"Can I test with smaller dataset?"**  
```bash
python setup_and_run.py
# Click "💼 Fetch Top 5" for quick test (CSV format)
```

**"Fetch was interrupted, how to continue?"**
```bash
python scripts/robust_fetch.py --resume
```

**"How to load the data in Python?"**
```python
import pandas as pd
# For large datasets (recommended)
df = pd.read_parquet('data/bloomberg_data_TIMESTAMP.parquet')

# For small datasets  
df = pd.read_csv('data/bloomberg_data_TIMESTAMP.csv')
```

---

## 📊 **Data Schema Quick Reference**

Essential columns in every export:
- `ticker` - Full Bloomberg ticker (e.g., "QQQ US 10/18/24 C450 Equity")
- `underlying` - Base symbol (e.g., "QQQ", "AAPL")  
- `strike` - Strike price
- `expiry` - Expiration date (YYYYMMDD)
- `option_type` - "C" or "P"
- `OPEN_INT` - **Critical** open interest data
- `delta`, `gamma`, `theta`, `vega`, `rho` - Greeks
- `PX_BID`, `PX_ASK`, `PX_LAST` - Pricing
- `VOLUME` - Daily volume

---

## 🚀 **Quick Start for AI Assistants**

When helping users:

1. **Start with**: `python setup_and_run.py`
2. **Web interface button**: "🔥 Fetch All 20" 
3. **Expected outcome**: ~97,000 records in Parquet format
4. **Data loading**: `pd.read_parquet()` for efficiency
5. **Troubleshooting**: Check Bloomberg connection first

**This system is optimized for comprehensive portfolio hedging analysis with maximum data coverage and efficiency.** 📈