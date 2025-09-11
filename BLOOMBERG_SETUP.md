# Bloomberg Terminal Setup Guide 🏦

## Prerequisites
- Bloomberg Terminal installed and running
- Valid Bloomberg subscription with API access
- Python 3.8+ installed (✅ Already done!)

## Step 1: Enable Bloomberg API

### Method 1: Through Bloomberg Developer Portal (Recommended)
1. **Go to**: https://www.bloomberg.com/professional/support/api-library/
2. **Login** with your Bloomberg credentials
3. **Download**: Bloomberg API Python library (blpapi)
4. **Run**: The installer as Administrator

### Method 2: Through Bloomberg Terminal (New Method)
1. **Open Bloomberg Terminal**
2. **Type**: `API<GO>` and press Enter
3. **Select**: "API Library" from the menu
4. **Choose**: "Python" version
5. **Download**: The Bloomberg API installer

### Method 3: Direct Download
1. **Go to**: https://www.bloomberg.com/professional/support/api-library/
2. **Select**: "Bloomberg API" → "Python"
3. **Download**: Latest version for Windows
4. **Run**: Installer as Administrator

## Step 2: Install Bloomberg API

### Automatic Installation (Recommended)
Run the provided script:
```bash
python scripts/setup_bloomberg.py
```

### Manual Installation
1. **Run installer** as Administrator
2. **Choose**: Python installation path: `C:\Users\cchunan\AppData\Local\Programs\Python\Python313\`
3. **Verify**: Installation by running test script

## Step 3: Test Connection

### Quick Test
```bash
python scripts/quick_test.py
```

### Expected Output
```
✅ Successfully connected to Bloomberg API
✅ Successfully fetched reference data
✅ Successfully fetched option data
✅ All tests passed!
```

## Step 4: Configure Settings

Edit `config/config.yaml` if needed:
- Adjust `strikes_above` and `strikes_below` (default: 20)
- Set `expiries_to_fetch` (default: [1,2,3] for 3 months)
- Confirm API limits match your subscription

## Step 5: Run Data Fetching

### Daily Fetch (After Market Close)
```bash
python scripts/run_all.py --daily
```

### Historical Data (60 days)
```bash
python scripts/run_all.py --historical --days 60
```

### Both Daily + Historical
```bash
python scripts/run_all.py --all
```

## Troubleshooting

### Connection Issues
- **Terminal not running**: Ensure Bloomberg Terminal is open and logged in
- **API not enabled**: Run `API<GO>` in Terminal (WAPI was retired)
- **Port blocked**: Check if port 8194 is accessible
- **Firewall**: Allow Bloomberg Terminal through Windows Firewall

### API Limits
- **Daily limit**: 50,000 requests (default)
- **Monthly limit**: 500,000 requests (default)
- **Monitor usage**: Check `logs/api_usage.json`

### Data Issues
- **No data returned**: Some strikes may not have active options
- **Missing Greeks**: Options need sufficient liquidity
- **Expired options**: Filter out options expiring soon

## Best Practices

1. **Run after market close** (4:30 PM ET)
2. **Don't minimize Terminal** while fetching
3. **Monitor API usage** regularly
4. **Keep 20% API quota** for emergencies
5. **Run historical updates** on weekends

## Support

If you encounter issues:
1. Check `logs/fetcher.log` for error details
2. Verify Bloomberg Terminal is running
3. Test with `scripts/quick_test.py`
4. Contact Bloomberg support if API issues persist

---
**Ready to start?** Run: `python scripts/setup_bloomberg.py`
