#!/usr/bin/env python3
"""
Convenience script to run all Bloomberg data fetchers
Easy-to-use interface for all QQQ options fetching operations
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_quick_test():
    """Run quick connection test"""
    print("\n🔍 Running Bloomberg API connection test...")
    print("-" * 50)
    result = os.system("python scripts/quick_test.py")
    return result == 0

def run_daily_fetch():
    """Run daily options fetch"""
    print("\n📊 Running daily QQQ options fetch...")
    print("-" * 50)
    result = os.system("python scripts/daily_fetch.py --save-db --export-csv")
    return result == 0

def run_historical_fetch(days=60):
    """Run historical QQQ options fetch"""
    print(f"\n📈 Running historical QQQ options fetch ({days} days)...")
    print("-" * 50)
    
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.bloomberg_api import BloombergAPI
    from datetime import datetime, timedelta
    import pandas as pd
    
    api = BloombergAPI()
    
    if not api.connect():
        print("❌ Failed to connect to Bloomberg API")
        return False
    
    print("✅ Connected to Bloomberg API")
    
    # Get liquid options from existing data
    csv_files = [f for f in os.listdir('data') if 'qqq_options_' in f and f.endswith('.csv')]
    if not csv_files:
        print("❌ No QQQ options CSV files found")
        api.disconnect()
        return False
    
    # Use the original daily fetch file, not the simple historical file
    latest_csv = None
    for csv in sorted(csv_files):
        if 'qqq_options_historical_simple' not in csv:  # Skip the simple historical file
            latest_csv = csv
            break
    
    if latest_csv is None:
        print("❌ No suitable QQQ options CSV files found")
        api.disconnect()
        return False
    df = pd.read_csv(f'data/{latest_csv}')
    liquid_options = df[df['PX_LAST'].notna() & (df['PX_LAST'] > 0)]
    
    if liquid_options.empty:
        print("❌ No liquid options found")
        api.disconnect()
        return False
    
    # Select top 5 options by volume
    if 'VOLUME' in liquid_options.columns:
        selected_options = liquid_options.nlargest(5, 'VOLUME')
    else:
        selected_options = liquid_options.head(5)
    
    print(f"🎯 Fetching historical data for {len(selected_options)} options")
    
    # Calculate date range
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=min(days, 7))).strftime('%Y%m%d')  # Limit to 7 days for reliability
    
    all_data = []
    successful_fetches = 0
    
    for i, (_, option) in enumerate(selected_options.iterrows()):
        ticker = option['ticker']
        print(f"\n📊 [{i+1}/{len(selected_options)}] Processing: {ticker}")
        
        try:
            # Fetch historical data
            hist_data = api.fetch_historical_data([ticker], ["PX_LAST"], start_date, end_date, "DAILY")
            
            if not hist_data.empty:
                # Clean up column names
                hist_data.columns = [col.replace(f'{ticker}_', '') for col in hist_data.columns]
                hist_data['ticker'] = ticker
                hist_data['strike'] = option['strike']
                hist_data['option_type'] = option['option_type']
                hist_data['expiry'] = option['expiry']
                
                all_data.append(hist_data)
                successful_fetches += 1
                
                print(f"   ✅ {len(hist_data)} days of data")
                
                # Show sample data
                if 'PX_LAST' in hist_data.columns:
                    valid_data = hist_data[hist_data['PX_LAST'].notna()]
                    if not valid_data.empty:
                        latest_price = valid_data['PX_LAST'].iloc[-1]
                        print(f"   💰 Latest price: ${latest_price:.2f}")
            else:
                print(f"   ❌ No historical data available")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    api.disconnect()
    print(f"\nDisconnected from Bloomberg API")
    
    # Save results
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        filename = f"data/qqq_options_historical_{start_date}_{end_date}.csv"
        combined_data.to_csv(filename)
        
        print(f"\n📊 SUMMARY")
        print(f"✅ Successfully fetched data for {successful_fetches}/{len(selected_options)} options")
        print(f"📈 Total records: {len(combined_data)}")
        print(f"💾 Data saved to: {filename}")
        
        return True
    else:
        print(f"\n❌ No historical options data was successfully fetched")
        return False

def run_qqq_historical_fetch(days=30):
    """Run QQQ stock historical fetch (alternative to options historical)"""
    print(f"\n📈 Running QQQ stock historical fetch ({days} days)...")
    print("-" * 50)
    
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.bloomberg_api import BloombergAPI
    from datetime import datetime, timedelta
    import pandas as pd
    
    api = BloombergAPI()
    
    if not api.connect():
        print("❌ Failed to connect to Bloomberg API")
        return False
    
    print("✅ Connected to Bloomberg API")
    
    # Fetch QQQ historical data
    ticker = ["QQQ US Equity"]
    fields = ["PX_LAST", "VOLUME", "PX_HIGH", "PX_LOW", "PX_OPEN"]
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    try:
        data = api.fetch_historical_data(ticker, fields, start_date, end_date, "DAILY")
        
        if not data.empty:
            # Clean up column names
            data.columns = [col.replace('QQQ US Equity_', '') for col in data.columns]
            
            # Add calculated fields
            data['daily_return'] = data['PX_LAST'].pct_change()
            data['volatility'] = data['daily_return'].rolling(window=5).std()
            data['price_range'] = data['PX_HIGH'] - data['PX_LOW']
            
            # Save to CSV
            filename = f"data/qqq_historical_{start_date}_{end_date}.csv"
            data.to_csv(filename)
            
            print(f"✅ Successfully fetched {len(data)} days of QQQ data")
            print(f"💾 Data saved to: {filename}")
            print(f"📊 Price range: ${data['PX_LAST'].min():.2f} - ${data['PX_LAST'].max():.2f}")
            print(f"📊 Average volume: {data['VOLUME'].mean():,.0f}")
            
            return True
        else:
            print("❌ No historical data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return False
        
    finally:
        api.disconnect()

def show_status():
    """Show current data status"""
    print("\n📋 Current Data Status:")
    print("-" * 30)
    
    # Check CSV files
    data_dir = "data"
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        print(f"CSV files: {len(csv_files)}")
        for csv in csv_files[:3]:  # Show first 3
            print(f"  - {csv}")
        if len(csv_files) > 3:
            print(f"  ... and {len(csv_files) - 3} more")
    
    # Check database
    db_path = "data/bloomberg_options.db"
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM options_data")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"Database records: {count}")
        except:
            print("Database: Error reading")
    else:
        print("Database: Not found")

def main():
    parser = argparse.ArgumentParser(
        description='Bloomberg QQQ Options Fetcher - Easy Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/run_all.py --test          # Test Bloomberg connection
  python scripts/run_all.py --daily         # Fetch today's options data
  python scripts/run_all.py --historical    # Fetch 60 days historical data
  python scripts/run_all.py --historical --days 30  # Fetch 30 days
  python scripts/run_all.py --all           # Run everything
  python scripts/run_all.py --status        # Show current data status
        '''
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Run Bloomberg API connection test only')
    parser.add_argument('--daily', action='store_true', 
                       help='Run daily QQQ options fetch')
    parser.add_argument('--historical', action='store_true', 
                       help='Run historical QQQ options fetch')
    parser.add_argument('--qqq-historical', action='store_true',
                       help='Run QQQ stock historical fetch (alternative to options)')
    parser.add_argument('--days', type=int, default=60, 
                       help='Number of days for historical fetch (default: 60)')
    parser.add_argument('--all', action='store_true', 
                       help='Run all fetches (test + daily + historical)')
    parser.add_argument('--status', action='store_true', 
                       help='Show current data status')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 BLOOMBERG QQQ OPTIONS FETCHER")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success_count = 0
    total_operations = 0
    
    if args.status:
        show_status()
        return 0
    
    if args.test:
        total_operations += 1
        if run_quick_test():
            success_count += 1
    
    if args.daily:
        total_operations += 1
        if run_daily_fetch():
            success_count += 1
    
    if args.historical:
        total_operations += 1
        if run_historical_fetch(args.days):
            success_count += 1
    
    if args.qqq_historical:
        total_operations += 1
        if run_qqq_historical_fetch(args.days):
            success_count += 1
    
    if args.all:
        total_operations += 3
        print("\n🔄 Running complete workflow...")
        
        # Test connection first
        if run_quick_test():
            success_count += 1
            print("✅ Connection test passed, proceeding...")
            
            # Daily fetch
            if run_daily_fetch():
                success_count += 1
            
            # Historical fetch
            if run_historical_fetch(args.days):
                success_count += 1
        else:
            print("❌ Connection test failed, stopping workflow")
    
    if not any([args.test, args.daily, args.historical, args.all, args.status]):
        print("\n📖 Usage Examples:")
        print("  python scripts/run_all.py --test              # Test connection")
        print("  python scripts/run_all.py --daily             # Daily fetch")
        print("  python scripts/run_all.py --historical        # Historical options fetch")
        print("  python scripts/run_all.py --qqq-historical    # QQQ stock historical fetch")
        print("  python scripts/run_all.py --all               # Run everything")
        print("  python scripts/run_all.py --status            # Show data status")
        print("\n💡 For more help: python scripts/run_all.py --help")
        return 0
    
    # Summary
    print("\n" + "="*60)
    print("📊 OPERATION SUMMARY")
    print("="*60)
    print(f"Operations completed: {success_count}/{total_operations}")
    
    if success_count == total_operations:
        print("🎉 All operations completed successfully!")
        show_status()
    elif success_count > 0:
        print("⚠️ Some operations completed successfully")
    else:
        print("❌ All operations failed")
        print("💡 Check Bloomberg Terminal is running and logged in")
    
    print("="*60)
    
    return 0 if success_count == total_operations else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
