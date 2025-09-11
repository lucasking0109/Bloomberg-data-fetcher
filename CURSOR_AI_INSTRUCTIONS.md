# 🤖 CURSOR AI - COMPLETE PROJECT UNDERSTANDING

## PROJECT OVERVIEW
This is a Bloomberg Terminal data fetcher that collects options data for QQQ index and its **TOP 20 CONSTITUENT STOCKS** (not just 5). The system fetches comprehensive options data including Open Interest (OI) and all Greeks for portfolio hedging analysis.

## ⚠️ CRITICAL CONFIGURATION - FETCH ALL 20 STOCKS!

### DEFAULT BEHAVIOR MUST BE:
```python
# Always fetch ALL 20 constituents, not just 5
python scripts/robust_fetch.py --top-n 20 --export-csv

# Or simply (defaults to all 20):
python scripts/robust_fetch.py --export-csv
```

### The 20 stocks configured in `config/qqq_constituents.yaml`:
1. AAPL (8.9% weight)
2. MSFT (8.5% weight)
3. NVDA (6.2% weight)
4. AMZN (5.1% weight)
5. META (4.8% weight)
6. AVGO (4.5% weight)
7. GOOGL (2.5% weight)
8. GOOG (2.4% weight)
9. TSLA (2.3% weight)
10. COST (2.1% weight)
11. NFLX (2.0% weight)
12. AMD (1.9% weight)
13. PEP (1.5% weight)
14. ADBE (1.4% weight)
15. CSCO (1.4% weight)
16. TMUS (1.3% weight)
17. INTC (1.2% weight)
18. CMCSA (1.1% weight)
19. QCOM (1.1% weight)
20. TXN (1.0% weight)

## 📊 DATA REQUIREMENTS

### For EACH Stock (QQQ + 20 constituents):
- **Options**: ATM ± 20 strikes (40 strikes total)
- **Expiries**: All within 2 months (60 days)
- **Critical Fields**: 
  - OPEN_INT (Open Interest) - MUST HAVE
  - All Greeks (Delta, Gamma, Theta, Vega, Rho)
  - Bid/Ask spreads
  - Volume
  - Implied Volatility

### Equity Data Fields:
- Price (Last, Open, High, Low)
- Volume (Current and 30-day average)
- Market Cap
- PE Ratio
- Dividend Yield

## 🚀 HOW TO RUN THE COMPLETE FETCH

### Method 1: Web Interface (RECOMMENDED)
```bash
# Run this single command
python setup_and_run.py

# In the web browser:
# Click "Fetch All" button (not "Fetch Top 5")
```

### Method 2: Direct Command
```bash
# Fetch QQQ + ALL 20 constituents
python scripts/robust_fetch.py --export-csv

# This is equivalent to:
python scripts/robust_fetch.py --top-n 20 --export-csv
```

### Method 3: If you need to test first
```bash
# Test with dry run
python scripts/robust_fetch.py --dry-run

# Then run the full fetch
python scripts/robust_fetch.py --export-csv
```

## 📁 PROJECT STRUCTURE

```
bloomberg-qqq-fetcher/
├── app.py                      # Web dashboard interface
├── setup_and_run.py           # One-click setup and launcher
├── START_HERE.md              # User guide
│
├── config/
│   ├── config.yaml            # Main configuration
│   └── qqq_constituents.yaml  # LIST OF 20 STOCKS (not 5!)
│
├── src/
│   ├── bloomberg_api.py       # Bloomberg connection with retry logic
│   ├── constituents_fetcher.py # Fetches ALL 20 constituents
│   ├── qqq_options_fetcher.py # QQQ index options
│   ├── fetch_state_manager.py # Resume capability
│   ├── database_manager.py    # SQLite storage
│   ├── data_processor.py      # Data validation
│   └── usage_monitor.py       # API limit tracking
│
├── scripts/
│   ├── robust_fetch.py        # MAIN SCRIPT - fetches everything
│   ├── check_progress.py      # Monitor progress
│   ├── daily_fetch.py         # Legacy QQQ-only script
│   └── historical_fetch.py    # Historical data
│
├── data/                      # Output directory
└── logs/                      # Logging directory
```

## 🔧 KEY CODE COMPONENTS

### 1. Main Fetcher (`scripts/robust_fetch.py`)
- Default behavior: Fetches QQQ + ALL 20 constituents
- Has resume capability if interrupted
- Saves to database and exports to CSV
- **Line 385**: Default top_n should be None (all) or 20

### 2. Constituents Fetcher (`src/constituents_fetcher.py`)
- **Line 88**: Gets all 20 tickers from config
- **Line 195**: Fetches options with ATM ± 20 strikes
- **Line 234**: Ensures OPEN_INT is included

### 3. Configuration (`config/qqq_constituents.yaml`)
- **Lines 7-47**: Lists ALL 20 constituents
- **Line 51**: strikes_above_atm: 20
- **Line 52**: strikes_below_atm: 20
- **Line 53**: max_days_to_expiry: 60

### 4. Database Schema (`src/database_manager.py`)
- **Line 57**: open_interest field is REQUIRED
- **Line 150**: constituent_options table for individual stocks
- Has tables for: options_data, equity_data, constituent_options

## ⚠️ COMMON MISTAKES TO AVOID

### DON'T DO THIS:
```bash
# Wrong - only fetches 5 stocks
python scripts/robust_fetch.py --top-n 5

# Wrong - only fetches QQQ
python scripts/robust_fetch.py --qqq-only
```

### DO THIS INSTEAD:
```bash
# Correct - fetches all 20 constituents
python scripts/robust_fetch.py --export-csv

# Or explicitly:
python scripts/robust_fetch.py --top-n 20 --export-csv
```

## 📊 EXPECTED OUTPUT

After successful complete fetch:
- **QQQ Options**: ~240 contracts
- **Constituent Options**: ~24,000 contracts (20 stocks × ~1,200 each)
- **Total Records**: ~24,240 options records
- **API Usage**: ~43,000 points (85% of daily limit)
- **Time Required**: 20-30 minutes

## 🔄 ERROR RECOVERY

If fetch is interrupted:
```bash
# Resume from where it stopped
python scripts/robust_fetch.py --resume

# Check progress
python scripts/check_progress.py
```

## 📈 DATA VALIDATION CHECKLIST

After fetch completes, verify:
1. ✅ All 20 constituents fetched (not just 5)
2. ✅ OPEN_INT field has data (not null)
3. ✅ Greeks are present (Delta, Gamma, etc.)
4. ✅ Expiries within 60 days
5. ✅ Strikes cover ATM ± 20

Check using:
```python
from src.database_manager import DatabaseManager
db = DatabaseManager()
stats = db.get_summary_stats()
print(f"Total records: {stats['total_records']}")  # Should be ~24,000+
```

## 🚨 BLOOMBERG TERMINAL REQUIREMENTS

Before running ANY fetch:
1. Bloomberg Terminal MUST be running
2. User MUST be logged in
3. Terminal window CANNOT be minimized
4. Bloomberg API must be installed (see installation files)
5. API must be enabled (type WAPI<GO> to check)
6. Best time: After 4:30 PM ET

## 📦 BLOOMBERG API INSTALLATION

The repository includes Bloomberg API files:
- `blpapi-3.25.3-py3-none-win_amd64.whl` - Python wheel package
- `blpapi3_64.dll` - Windows DLL
- `setup_bloom_env_v2.ps1` - PowerShell setup script
- `run_bloomberg.bat` - Windows batch file

Install using:
```bash
pip install blpapi-3.25.3-py3-none-win_amd64.whl
```

## 💡 FOR CURSOR AI ASSISTANCE

When helping with this codebase:
1. **Default to fetching ALL 20 constituents**, not 5
2. **Ensure OPEN_INT is always included** in option fields
3. **Use robust_fetch.py** as the main script
4. **Enable resume capability** for interrupted fetches
5. **Export to CSV** after database storage
6. **Monitor API usage** to avoid limits

## 📝 QUICK COMMAND REFERENCE

```bash
# Complete setup and run
python setup_and_run.py

# Full data fetch (QQQ + 20 stocks)
python scripts/robust_fetch.py --export-csv

# Resume if interrupted
python scripts/robust_fetch.py --resume

# Check progress
python scripts/check_progress.py

# Export existing data
python -c "from src.database_manager import DatabaseManager; db = DatabaseManager(); db.export_to_csv('data/all_options.csv')"
```

## 🎯 SUCCESS CRITERIA

The fetch is successful when:
1. Database has 24,000+ options records
2. All 20 constituents are present
3. OPEN_INT data is populated
4. Greeks are calculated
5. CSV export contains all data

## ⭐ REMEMBER

**This system is designed to fetch ALL TOP 20 QQQ CONSTITUENTS by default, not just 5. The user needs comprehensive data for portfolio hedging analysis, so always fetch the complete dataset unless explicitly told otherwise.**

---

*This document is specifically for Cursor AI or any AI assistant reading this codebase. The primary goal is fetching options data for QQQ and ALL 20 major constituents with Open Interest and Greeks for hedging analysis.*