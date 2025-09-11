# 🚀 SUPER EASY START GUIDE

## One Command to Rule Them All!

When you clone this repo on the Bloomberg Terminal, just run:

```bash
python setup_and_run.py
```

That's it! This will:
1. ✅ Check your Python version
2. ✅ Install all dependencies
3. ✅ Test Bloomberg connection
4. ✅ Launch the easy web interface

---

## 🖥️ Web Dashboard Features

Once launched, you'll see a beautiful dashboard with:

### ⚡ One-Click Actions
- **Test Connection** - Verify Bloomberg Terminal is connected
- **Fetch QQQ Only** - Quick test (2 minutes)
- **Fetch Top 5** - Medium fetch (5 minutes)
- **Fetch All 20** - Complete data for ALL 20 stocks (20-30 minutes)
- **Resume** - Continue if interrupted

### 📊 Real-Time Monitoring
- Live progress bar
- Records fetched counter
- API usage gauges
- Current ticker being processed

### 💾 Data Management
- Preview data instantly
- Export to CSV with one click
- Database statistics
- Automatic cleanup options

---

## 🎯 Quick Start Steps

### Step 1: Launch
```bash
cd bloomberg-qqq-fetcher
python setup_and_run.py
```

### Step 2: In the Web Browser
1. Click **"Test Connection"** button
2. Click **"Fetch Top 5"** to start
3. Watch the progress bar
4. Click **"Export to CSV"** when done

### Step 3: Get Your Data
Your data will be in:
- Database: `data/bloomberg_options.db`
- CSV: `data/export_TIMESTAMP.csv`

---

## 📱 Alternative: Command Line Menu

If you prefer not to use the web interface:

```bash
python setup_and_run.py
# Then choose option 2 for CLI menu
```

Menu Options:
1. Test Bloomberg Connection
2. Fetch QQQ Options Only
3. Fetch Top 5 Constituents
4. Fetch All (QQQ + 20 Constituents)
5. Resume Previous Fetch
6. Check Progress
7. Export Data to CSV
8. Exit

---

## ⚠️ Before You Start

Make sure:
1. **Bloomberg Terminal is running and logged in**
2. **You're on the Terminal computer**
3. **Bloomberg API is installed** (see below)
4. **It's after 4:30 PM ET** (best time)

### 🔧 Bloomberg API Installation

If you see "blpapi not found" error:

#### Method 1: From Bloomberg Terminal
1. In Terminal, type: `WAPI<GO>`
2. Download Python API
3. Install the downloaded file

#### Method 2: Use included files (Windows)
```bash
# Use the included wheel file
pip install blpapi-3.25.3-py3-none-win_amd64.whl

# Or run the setup script
./setup_bloom_env_v2.ps1
```

---

## 🆘 Troubleshooting

### "Bloomberg not connected"
1. Open Bloomberg Terminal
2. Type: `WAPI<GO>`
3. Make sure API is enabled

### "blpapi not found"
1. In Bloomberg Terminal, type: `WAPI<GO>`
2. Download Python API
3. Install the downloaded file
4. Run setup again

### "Fetch interrupted"
Just run:
```bash
python scripts/robust_fetch.py --resume
```

---

## 📊 What You Get

Each fetch gives you:
- **QQQ Options**: ATM ± 20 strikes, 2 months expiry
- **Top 20 Stocks**: AAPL, MSFT, NVDA, etc.
- **All Greeks**: Delta, Gamma, Theta, Vega, Rho
- **Open Interest**: Critical for liquidity analysis
- **Equity Data**: Prices, volumes, PE ratios

---

## 🎉 That's It!

You now have a professional Bloomberg data fetcher with:
- Beautiful web interface
- One-click operations
- Automatic error recovery
- Complete options data with OI and Greeks

Enjoy your data! 📈