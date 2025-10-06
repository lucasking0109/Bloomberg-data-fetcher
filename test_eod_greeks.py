#!/usr/bin/env python3
"""
EOD Greeks Testing Script
Test the complete EOD Greeks fetching implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import pandas as pd
import time

def test_eod_greeks_system():
    """Comprehensive test of EOD Greeks system"""

    print("="*60)
    print("🧪 EOD Greeks System Test")
    print("="*60)

    # Test 1: Bloomberg API Connection with EOD override
    print("\n📌 Test 1: EOD Reference Data with SETTLE_DT Override")
    print("-"*40)

    try:
        from src.bloomberg_api import BloombergAPI

        api = BloombergAPI()
        if api.connect():
            print("✅ Connected to Bloomberg API")

            # Test EOD reference data with SETTLE_DT
            test_ticker = ["QQQ US 12/20/24 C500 Equity"]
            fields = ["PX_SETTLE", "DELTA", "GAMMA", "THETA", "VEGA", "RHO"]
            settle_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

            print(f"Testing EOD fetch for {test_ticker[0]}")
            print(f"Settlement date: {settle_date}")
            print(f"Fields: {fields}")

            data = api.fetch_eod_reference_data(test_ticker, fields, settle_date)

            if not data.empty:
                print("✅ EOD data fetched successfully")
                print("\nData preview:")
                print(data)
            else:
                print("⚠️ No data returned (might need different ticker or permissions)")

            api.disconnect()
        else:
            print("❌ Could not connect to Bloomberg API")

    except Exception as e:
        print(f"❌ Error testing Bloomberg API: {e}")

    # Test 2: EOD Greeks Fetcher
    print("\n📌 Test 2: EOD Greeks Fetcher")
    print("-"*40)

    try:
        from src.eod_greeks_fetcher import EODGreeksFetcher

        fetcher = EODGreeksFetcher()
        print("✅ EOD Greeks Fetcher initialized")

        # Test fetching EOD Greeks
        print("\nFetching QQQ EOD Greeks...")
        data = fetcher.fetch_eod_greeks("QQQ")

        if not data.empty:
            print(f"✅ Fetched {len(data)} EOD records")

            # Check for Greeks
            greek_cols = ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']
            has_greeks = False
            for col in greek_cols:
                if col in data.columns:
                    non_null = data[col].notna().sum()
                    if non_null > 0:
                        print(f"  ✅ {col}: {non_null}/{len(data)} values")
                        has_greeks = True
                    else:
                        print(f"  ⚠️ {col}: No values")
                else:
                    print(f"  ❌ {col}: Column missing")

            if not has_greeks:
                print("\n⚠️ No Greeks from Bloomberg, checking Black-Scholes calculation...")
                if 'IVOL_MID' in data.columns and data['IVOL_MID'].notna().any():
                    print("✅ Can calculate Greeks using Black-Scholes")
                else:
                    print("❌ Cannot calculate Greeks: IVOL_MID not available")

            # Save test data
            file_path = fetcher.save_eod_data(data, "test")
            print(f"\n📁 Test data saved to: {file_path}")

        else:
            print("❌ No EOD data fetched")

    except Exception as e:
        print(f"❌ Error testing EOD Greeks Fetcher: {e}")

    # Test 3: Greeks Database
    print("\n📌 Test 3: Greeks Database")
    print("-"*40)

    try:
        from src.greeks_database import GreeksDatabase

        db = GreeksDatabase()
        print("✅ Greeks Database initialized")

        # Get database stats
        stats = db.get_database_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Test data insertion
        if 'data' in locals() and not data.empty:
            print("\nInserting test data into database...")
            records = db.insert_eod_data(data, "2025-10-06")
            print(f"✅ Inserted {records} records")

            # Query back the data
            print("\nQuerying database...")
            query_data = db.get_latest_greeks("QQQ", num_days=7)
            if not query_data.empty:
                print(f"✅ Retrieved {len(query_data)} records from database")
            else:
                print("⚠️ No data retrieved from database")

    except Exception as e:
        print(f"❌ Error testing Greeks Database: {e}")

    # Test 4: Integrated System
    print("\n📌 Test 4: Integrated QQQ Options Fetcher with EOD")
    print("-"*40)

    try:
        from src.qqq_options_fetcher import QQQOptionsFetcher

        fetcher = QQQOptionsFetcher(use_eod_greeks=True)
        print("✅ QQQ Options Fetcher initialized with EOD Greeks")

        # Test EOD data fetch
        print("\nFetching EOD data with new method...")
        eod_data = fetcher.fetch_eod_data(use_eod_method=True)

        if not eod_data.empty:
            print(f"✅ Fetched {len(eod_data)} EOD records")

            # Check data quality
            print("\nData Quality Check:")
            print(f"  Unique expiries: {eod_data['expiry'].nunique()}")
            print(f"  Strike range: ${eod_data['strike'].min():.0f} - ${eod_data['strike'].max():.0f}")

            greek_cols = ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']
            for col in greek_cols:
                if col in eod_data.columns:
                    coverage = (eod_data[col].notna().sum() / len(eod_data)) * 100
                    print(f"  {col} coverage: {coverage:.1f}%")

        else:
            print("❌ No EOD data fetched")

        # Test with history
        print("\nFetching EOD Greeks with 7 days history...")
        historical_data = fetcher.fetch_eod_greeks_with_history(days_back=7)

        if not historical_data.empty:
            print(f"✅ Retrieved {len(historical_data)} records with history")
            if 'settle_date' in historical_data.columns:
                print(f"  Date range: {historical_data['settle_date'].min()} to {historical_data['settle_date'].max()}")
        else:
            print("⚠️ No historical data available")

    except Exception as e:
        print(f"❌ Error testing integrated system: {e}")

    # Test 5: Scheduler
    print("\n📌 Test 5: EOD Scheduler (Dry Run)")
    print("-"*40)

    try:
        from scripts.eod_greeks_scheduler import EODScheduler

        scheduler = EODScheduler()
        print("✅ EOD Scheduler initialized")

        # Check for missing dates
        print("\nChecking for missing dates...")
        scheduler._check_missing_dates(days_back=7)

    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")

    # Summary
    print("\n"+"="*60)
    print("📊 Test Summary")
    print("="*60)

    print("""
✅ Components Created:
1. fetch_eod_reference_data() - EOD data with SETTLE_DT override
2. EODGreeksFetcher - Daily EOD Greeks collection
3. GreeksDatabase - SQLite storage for historical Greeks
4. Updated QQQ fetcher with EOD integration
5. Daily scheduler for automated collection

📝 Usage Instructions:

1. Manual EOD Collection:
   python scripts/eod_greeks_scheduler.py --mode once

2. Scheduled Daily Collection (4:30 PM):
   python scripts/eod_greeks_scheduler.py --mode schedule

3. Backfill Missing Dates:
   python scripts/eod_greeks_scheduler.py --mode backfill --days 30

4. In Python Code:
   from src.qqq_options_fetcher import QQQOptionsFetcher
   fetcher = QQQOptionsFetcher(use_eod_greeks=True)
   data = fetcher.fetch_eod_data()

⚠️ Notes:
- If Bloomberg doesn't provide Greeks, they'll be calculated using Black-Scholes
- EOD data is stored in: data/eod_greeks/
- Database is at: data/eod_greeks/historical_greeks.db
""")

if __name__ == "__main__":
    test_eod_greeks_system()