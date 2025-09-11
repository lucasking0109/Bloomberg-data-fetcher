# 🤖 CURSOR AI - COMPLETE PROJECT UNDERSTANDING

## PROJECT OVERVIEW
This is a Bloomberg Terminal data fetcher that collects options data for QQQ index and its **TOP 20 CONSTITUENT STOCKS** (not just 5). The system fetches comprehensive options data including Open Interest (OI) and all Greeks for portfolio hedging analysis.

## ⚠️ CRITICAL CONFIGURATION - UPDATED SPECIFICATIONS!

### DEFAULT BEHAVIOR (Updated 2025-09-10):
```python
# Full production dataset - 97,000 options records
python scripts/robust_fetch.py --export-csv  # Defaults to 20 stocks, Parquet format

# Testing subset - 5,000 options records  
python scripts/robust_fetch.py --top-n 5 --export-csv  # Auto-uses CSV format

# Or with explicit format control:
python scripts/robust_fetch.py --export-csv --export-format parquet
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

## 📊 DATA REQUIREMENTS (UPDATED SPECIFICATIONS)

### For EACH Stock (QQQ + 20 constituents):
- **Options**: ATM ± 40 strikes (80 strikes total) - EXPANDED from ±20
- **Expiries**: All weekly + quarterly within 2 months (60 days) - QQQ has weekly expiries
- **Critical Fields**: 
  - OPEN_INT (Open Interest) - MUST HAVE for liquidity analysis
  - All Greeks (Delta, Gamma, Theta, Vega, Rho)
  - Bid/Ask spreads and sizes
  - Volume (daily and average)
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

## 📊 EXPECTED OUTPUT (UPDATED VOLUMES)

After successful complete fetch:
- **QQQ Options**: ~1,000 contracts (80 strikes × ~12 weekly expiries)
- **Constituent Options**: ~96,000 contracts (20 stocks × 80 strikes × ~60 options each)  
- **Total Records**: ~97,000 options records (4x increase from previous spec)
- **API Usage**: ~43,000 points (85% of daily limit)
- **Time Required**: 25-30 minutes
- **Export Formats**: 
  - **Testing (≤5 stocks)**: CSV format (~5MB)
  - **Production (20 stocks)**: Parquet format (~20MB, 10x faster loading)

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
4. ✅ Expiries include weekly dates (QQQ has weekly expiries)
5. ✅ Strikes cover ATM ± 40 (80 total per expiry)
6. ✅ Export format matches expectation (CSV for testing, Parquet for production)

Check using:
```python
from src.database_manager import DatabaseManager
db = DatabaseManager()
stats = db.get_summary_stats()
print(f"Total records: {stats['total_records']}")  # Should be ~97,000+

# Verify strike range
import pandas as pd
df = pd.read_parquet('data/bloomberg_data_latest.parquet')
print(f"Strike range per ticker: {df.groupby('underlying')['strike'].agg(['min', 'max', 'count'])}")
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

## 🎯 SUCCESS CRITERIA (UPDATED TARGETS)

The fetch is successful when:
1. Database has 97,000+ options records (4x previous target)
2. All 20 constituents are present (not just 5)
3. OPEN_INT data is populated (critical for liquidity analysis)
4. Greeks are calculated (Delta, Gamma, Theta, Vega, Rho)
5. Strike range is ATM ± 40 (80 per expiry, not 40)
6. QQQ has weekly expiries (not just monthly)
7. Export format is appropriate:
   - CSV for testing datasets (≤5 stocks)
   - Parquet for production datasets (20 stocks)

## ⭐ REMEMBER (UPDATED 2025-09-10)

**This system is designed to fetch comprehensive options data with the following specifications:**

1. **Coverage**: QQQ + ALL 20 constituents by default (not just 5)
2. **Strikes**: ATM ± 40 (80 total per expiry) for comprehensive hedging analysis
3. **Expiries**: All weekly + quarterly (QQQ has weekly expiries unlike typical stocks)
4. **Format Intelligence**: 
   - Auto-selects CSV for testing (≤5 stocks, easy inspection)
   - Auto-selects Parquet for production (20 stocks, efficient storage/loading)
5. **Critical Data**: Always include OPEN_INT for liquidity analysis
6. **Volume**: Expect ~97,000 records (4x previous specification)

## 💡 FOR AI ASSISTANTS

When helping with this codebase:
1. **Default to fetching ALL 20 constituents** with ATM ± 40 strikes
2. **Use QQQ weekly expiries** (not just monthly like other stocks)
3. **Smart format selection** based on dataset size
4. **Always include OPEN_INT** in option fields for liquidity analysis
5. **Use robust_fetch.py** as the main script with resume capability
6. **Monitor API usage** to avoid Bloomberg limits (43K/50K daily)

---

*This document is specifically for AI assistants reading this codebase. The system provides comprehensive options data for QQQ and ALL 20 major constituents with Open Interest and Greeks for professional portfolio hedging analysis.*