# Bloomberg QQQ Options Fetcher

Standalone package for fetching QQQ options data from Bloomberg Terminal.

## Features
- Fetch QQQ options data (±20 strikes, 60 days historical)
- API usage monitoring (50K daily / 500K monthly limits)
- SQLite database storage
- Batch processing for efficiency

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Bloomberg connection
# Edit config/config.yaml with your settings

# Run daily fetch
python scripts/daily_fetch.py

# Or fetch historical data
python scripts/historical_fetch.py
```

## Requirements
- Bloomberg Terminal with API access
- Python 3.8+
- blpapi package

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup guide.
