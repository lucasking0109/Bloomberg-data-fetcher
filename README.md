# 🚀 Bloomberg QQQ Options Fetcher

**Professional-grade options data fetcher for QQQ index and individual constituent stocks with comprehensive Greeks and market data.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Bloomberg API](https://img.shields.io/badge/Bloomberg-API-orange.svg)](https://www.bloomberg.com/professional/support/api-library/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🎯 What This Does

Fetches comprehensive options data for **professional trading analysis**:
- **QQQ Index Options**: Historical and real-time options data with full Greeks
- **Top 20 QQQ Constituents**: AAPL, MSFT, NVDA, AMZN, META, GOOGL, etc.
- **26 Bloomberg Fields**: Open Interest, Delta, Gamma, Theta, Vega, Implied Vol, Time Value
- **Multiple Formats**: CSV, Parquet, Excel export with SQLite database storage
- **Visual Interface**: Streamlit dashboard for easy operation

---

## ⚡ Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/lucasking0109/bloomberg-qqq-fetcher.git
cd bloomberg-qqq-fetcher
python setup_bloomberg_terminal.py
```

### 2. Fetch Data
```bash
# QQQ historical options (30 days)
python scripts/historical_fetch.py --days 30

# Individual stock options (AAPL)
python scripts/constituents_fetch.py --ticker AAPL

# Top 10 constituents by weight
python scripts/constituents_fetch.py --top 10
```

### 3. Visual Interface (Optional)
```bash
# Launch web dashboard
streamlit run app.py
```

**Time Required**: 2 minutes setup, 5-30 minutes for data fetching

---

## 📊 Features

### QQQ Options Data
- **ATM ± 40 strikes** for comprehensive coverage
- **All expiries within 60 days**
- **Historical snapshots** for backtesting
- **Full Greeks** (Delta, Gamma, Theta, Vega, Rho)

### Individual Stock Options
- **Top 20 QQQ constituents** by market weight
- **Single ticker** or **bulk fetching**
- **Same comprehensive fields** as QQQ
- **Real-time spot prices** for accurate moneyness

### Data Quality
- **Built-in validation** removes invalid records
- **Quality scoring** (A+ to F grades)
- **Error handling** with automatic retries
- **Progress tracking** and resumable fetches

---

## 🛠️ Requirements

### Prerequisites
- **Bloomberg Terminal** subscription and login
- **Python 3.8+** (64-bit)
- **Windows/Mac/Linux** support

### Dependencies
```bash
# Automatically installed by setup script
pandas>=1.3.0
numpy>=1.21.0
blpapi>=3.18.0
streamlit>=1.28.0
plotly>=5.0.0
pyyaml>=6.0
```

---

## 📁 Project Structure

```
bloomberg-qqq-fetcher/
├── setup_bloomberg_terminal.py  # Main setup script
├── app.py                      # Streamlit web interface
├── scripts/
│   ├── historical_fetch.py     # QQQ options fetcher
│   └── constituents_fetch.py   # Individual stocks fetcher
├── src/                        # Core modules
│   ├── bloomberg_api.py        # Bloomberg Terminal connection
│   ├── qqq_options_fetcher.py  # QQQ data logic
│   ├── constituents_fetcher.py # Individual stocks logic
│   ├── data_processor.py       # Data validation & transformation
│   ├── database_manager.py     # SQLite database operations
│   └── usage_monitor.py        # API quota management
├── config/
│   ├── config.yaml             # Main configuration
│   └── qqq_constituents.yaml   # Top 20 stocks configuration
└── data/                       # Output directory
    └── bloomberg_options.db    # SQLite database
```

---

## 🚀 Usage Examples

### Quick Test
```bash
# Test with limited data (recommended first run)
python scripts/historical_fetch.py --quick-test
```

### Historical QQQ Data
```bash
# Last 60 days
python scripts/historical_fetch.py --days 60 --export-format parquet

# Specific date range
python scripts/historical_fetch.py --start-date 2024-01-01 --end-date 2024-01-31
```

### Individual Stocks
```bash
# Single stock
python scripts/constituents_fetch.py --ticker AAPL --export-format csv

# Top 5 by weight
python scripts/constituents_fetch.py --top 5

# All 20 constituents
python scripts/constituents_fetch.py --all
```

### Web Interface
```bash
# Launch dashboard
streamlit run app.py

# Features:
# - Visual database statistics
# - One-click data fetching
# - Real-time progress monitoring
# - Data preview with charts
```

---

## 📈 Data Output

### Exported Files
```
data/
├── qqq_options_20241201_143022.parquet    # QQQ historical data
├── AAPL_options_20241201_143045.csv       # Individual stock data
└── bloomberg_options.db                   # SQLite database
```

### Database Tables
- **options_data**: All options records with full Bloomberg fields
- **equity_data**: Underlying stock prices and metrics

### Key Fields
```python
# Options data includes:
'ticker', 'underlying', 'strike', 'expiry', 'option_type',
'px_last', 'px_bid', 'px_ask', 'px_settle', 'volume', 'open_int',
'delta', 'gamma', 'theta', 'vega', 'rho', 'ivol_mid',
'time_value', 'intrinsic_val', 'moneyness', 'fetch_time'
```

---

## 🔧 Configuration

### Main Settings (`config/config.yaml`)
```yaml
bloomberg:
  host: localhost
  port: 8194

limits:
  daily_limit: 100000
  monthly_limit: 1000000
  batch_size: 20
  request_delay: 1.0

output:
  format: parquet
  database_path: data/bloomberg_options.db
```

### Constituents (`config/qqq_constituents.yaml`)
```yaml
constituents:
  - ticker: AAPL
    name: Apple Inc
    weight: 8.9
  - ticker: MSFT
    name: Microsoft Corporation
    weight: 8.5
  # ... (20 total stocks)
```

---

## 🚨 Troubleshooting

### Common Issues
1. **"Import blpapi failed"**
   ```bash
   # Re-run setup with admin privileges
   python setup_bloomberg_terminal.py
   ```

2. **"Connection failed"**
   - Ensure Bloomberg Terminal is running and logged in
   - Check account has API access enabled

3. **"No data returned"**
   - Verify market hours (options data available 6:30 AM - 5:00 PM ET)
   - Check ticker symbols are valid

### Quick Fixes
```bash
# Full diagnostic and setup
python setup_bloomberg_terminal.py

# Test connection
python -c "import blpapi; print('✅ Success')"

# Check API access in Bloomberg Terminal
API<GO>
```

---

## 📞 Support

- **Setup Issues**: Run `python setup_bloomberg_terminal.py`
- **API Problems**: Check `BLOOMBERG_API_QUICK_REFERENCE.md`
- **Data Issues**: See `BLOOMBERG_API_FIXES.md`
- **Bloomberg Support**: https://www.bloomberg.com/professional/support/

---

## 📄 License

MIT License - feel free to use for commercial and personal projects.

---

## 🎯 Quick Commands Summary

```bash
# Setup
python setup_bloomberg_terminal.py

# Quick test
python scripts/historical_fetch.py --quick-test

# QQQ data (30 days)
python scripts/historical_fetch.py --days 30

# Individual stock
python scripts/constituents_fetch.py --ticker AAPL

# Web interface
streamlit run app.py
```

**Ready to fetch professional-grade options data!** 🚀

---

## 👨‍💻 Author

**Lucas King** - Professional Bloomberg Terminal Integration Developer
- GitHub: [@lucasking0109](https://github.com/lucasking0109)
- Email: lucas196700@gmail.com

*Specializing in institutional-grade financial data solutions and Bloomberg Terminal integrations.*