# 🚀 Bloomberg QQQ Options Fetcher

**Professional-grade options data fetcher for QQQ index and top 20 constituent stocks with comprehensive Greeks and Open Interest data.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Bloomberg API](https://img.shields.io/badge/Bloomberg-API-orange.svg)](https://www.bloomberg.com/professional/support/api-library/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Does

Fetches comprehensive options data for **portfolio hedging analysis**:
- **QQQ Index Options**: ATM ± 40 strikes, all weekly expiries within 60 days  
- **Top 20 QQQ Constituents**: AAPL, MSFT, NVDA, AMZN, META, etc.
- **Critical Data**: Open Interest, all Greeks (Delta, Gamma, Theta, Vega, Rho)
- **Smart Export**: CSV for testing, Parquet for production datasets

**Data Volume**: ~97,000 options records per fetch (4x more comprehensive than typical)

---

## ⚡ Quick Start (2 Commands)

```bash
# 1. Clone and setup
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher
python setup_and_run.py

# 2. Click "🔥 Fetch All 20" in the web interface
# That's it! Data saved to bloomberg_options.db + exported as Parquet
```

**Time Required**: 25-30 minutes for complete dataset

---

## 🖥️ Web Interface Features

![Dashboard Preview](https://via.placeholder.com/800x400/1f1f1f/ffffff?text=Bloomberg+QQQ+Fetcher+Dashboard)

### 🔥 One-Click Operations
- **Test Connection** - Verify Bloomberg Terminal access
- **Fetch Top 5** - Quick test (5 min, CSV export)  
- **Fetch All 20** - Complete dataset (30 min, Parquet export)
- **Resume** - Continue interrupted fetches
- **Smart Export** - Auto-selects optimal format

### 📊 Real-Time Monitoring  
- Live progress bars and counters
- API usage tracking (50K daily limit)
- Current ticker being processed
- Error recovery status

### 💾 Data Management
- Database statistics and health
- Export format selection (CSV/Parquet)
- Historical data cleanup
- Data preview and validation

---

## 📦 What You Get

### **Options Data** (per ticker):
- **Strikes**: ATM ± 40 (80 total per expiry)
- **Expiries**: All weekly + quarterly within 60 days
- **Greeks**: Delta, Gamma, Theta, Vega, Rho
- **Liquidity**: Volume, **Open Interest**, Bid/Ask spreads

### **Equity Data**:
- Real-time prices and volumes
- Market cap, PE ratios, dividend yields
- 30-day volatility and averages

### **Export Formats**:
```python
# CSV (testing, ≤5 stocks)
df = pd.read_csv('data/bloomberg_data_20250910_143022.csv')

# Parquet (production, full dataset - 10x faster loading)
df = pd.read_parquet('data/bloomberg_data_20250910_143022.parquet')
```

---

## 🏗️ Architecture

```
bloomberg-qqq-fetcher/
├── 🌐 app.py                  # Web dashboard (Streamlit)
├── 🚀 setup_and_run.py       # One-click launcher
├── 📖 START_HERE.md           # Simple user guide
│
├── config/
│   ├── config.yaml            # Main configuration  
│   └── qqq_constituents.yaml  # 20 stocks + settings
│
├── src/
│   ├── bloomberg_api.py       # Bloomberg Terminal connection
│   ├── qqq_options_fetcher.py # QQQ index options (weekly expiries)
│   ├── constituents_fetcher.py # 20 stocks options (±40 strikes)
│   ├── database_manager.py    # SQLite + Parquet export
│   └── fetch_state_manager.py # Resume capability
│
├── scripts/
│   ├── robust_fetch.py        # Main CLI script
│   ├── check_progress.py      # Monitor running fetches
│   └── setup_bloomberg.py     # Bloomberg API installer
│
└── data/                      # Output directory
    ├── bloomberg_options.db   # SQLite database
    └── *.parquet             # Efficient data files
```

---

## 🎮 Usage Modes

### 1. **Web Interface** (Recommended)
```bash
python setup_and_run.py
# Opens browser automatically
# Click buttons to fetch data
```

### 2. **Command Line**
```bash
# Full dataset (QQQ + 20 stocks, Parquet)
python scripts/robust_fetch.py --export-csv

# Testing (5 stocks, CSV)  
python scripts/robust_fetch.py --top-n 5 --export-csv --export-format csv

# Resume if interrupted
python scripts/robust_fetch.py --resume
```

### 3. **Python Integration**
```python
from src.database_manager import DatabaseManager
from src.constituents_fetcher import ConstituentsFetcher

# Load existing data
db = DatabaseManager()
df = db.get_latest_data()

# Fetch specific data
fetcher = ConstituentsFetcher('config/config.yaml')
aapl_options = fetcher.fetch_constituent_options('AAPL')
```

---

## ⚙️ Configuration

Key settings in `config/qqq_constituents.yaml`:

```yaml
fetch_config:
  strikes_above_atm: 40      # ±40 strikes (was ±20)
  strikes_below_atm: 40
  max_days_to_expiry: 60     # 2 months
  
option_fields:
  - OPEN_INT                 # Critical for liquidity
  - DELTA                    # All Greeks included
  - GAMMA
  - THETA
  - VEGA
  - RHO
```

---

## 🔧 System Requirements

### **Bloomberg Terminal**
- ✅ Terminal running and logged in
- ✅ API enabled (type `WAPI<GO>` to check)
- ✅ Python API installed (included in repo)

### **Python Environment**
- Python 3.8+ 
- Dependencies auto-installed by `setup_and_run.py`
- ~200MB for virtual environment

### **Hardware**
- 4GB+ RAM (for large datasets)
- 1GB disk space (for data storage)
- Stable internet connection

---

## 📈 Performance & Limits

### **Bloomberg API Usage**
- **Daily Limit**: 50,000 data points
- **Monthly Limit**: 500,000 data points  
- **Full Fetch Usage**: ~43,000 points (85% of daily)
- **Optimal Time**: After 4:30 PM ET

### **Data Processing**
- **Fetch Time**: 25-30 minutes (full dataset)
- **Database Size**: ~100MB (97,000 records)
- **Export Speeds**: 
  - CSV: ~40MB, moderate loading
  - Parquet: ~20MB, 10x faster loading

---

## 🆘 Troubleshooting

### **Bloomberg Connection Issues**
```bash
# Check API status
python -c "from src.bloomberg_api import test_connection; test_connection()"

# Reinstall API
pip install blpapi-3.25.3-py3-none-win_amd64.whl
```

### **Interrupted Fetches**
```bash
# Resume from where it stopped
python scripts/robust_fetch.py --resume

# Check progress
python scripts/check_progress.py
```

### **Data Validation**
```python
from src.database_manager import DatabaseManager
db = DatabaseManager()
stats = db.get_summary_stats()
print(f"Total records: {stats['total_records']}")  # Should be ~97,000
```

---

## 🎯 For AI Assistants

**Default Behavior**: This system fetches QQQ + **all 20 constituents** by default. Key commands:

```bash
# Full production fetch (preferred)
python scripts/robust_fetch.py --export-csv

# Testing subset  
python scripts/robust_fetch.py --top-n 5 --export-csv

# Web interface
python setup_and_run.py
```

**Critical Fields**: Always ensure `OPEN_INT` (Open Interest) is included in options data for liquidity analysis.

**Export Logic**: Auto-selects CSV for ≤5 stocks (testing), Parquet for full datasets (production).

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 2-minute setup guide
- **[START_HERE.md](START_HERE.md)** - Simple user guide  
- **[AI_ASSISTANT_GUIDE.md](AI_ASSISTANT_GUIDE.md)** - AI assistant reference
- **[CURSOR_AI_INSTRUCTIONS.md](CURSOR_AI_INSTRUCTIONS.md)** - Complete technical specs  
- **[BLOOMBERG_SETUP.md](BLOOMBERG_SETUP.md)** - Bloomberg API installation
- **[BLOOMBERG_API_QUICK_REFERENCE.md](BLOOMBERG_API_QUICK_REFERENCE.md)** - API usage guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[DISCLAIMER.md](DISCLAIMER.md)** - Legal notices

---

## 📄 License

MIT License - feel free to use for commercial or personal projects.

---

## 🚀 Get Started Now

```bash
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher  
python setup_and_run.py
```

**Ready to fetch comprehensive options data for portfolio hedging analysis!** 📊⚡

---

*Built for professional traders and quants who need comprehensive options data with Open Interest and Greeks for QQQ and its major constituents.*