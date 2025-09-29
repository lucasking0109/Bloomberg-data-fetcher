#!/usr/bin/env python3
"""
Historical QQQ Options Fetch Script
Fetch historical options data for specified date range
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qqq_options_fetcher import QQQOptionsFetcher
from src.database_manager import DatabaseManager
from datetime import datetime, timedelta
import logging
import argparse
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function for historical fetch"""
    
    parser = argparse.ArgumentParser(description='Fetch historical QQQ options data')
    parser.add_argument('--days', type=int, default=60,
                       help='Number of days of history to fetch (default: 60)')
    parser.add_argument('--start-date', type=str,
                       help='Start date (YYYYMMDD or YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='End date (YYYYMMDD or YYYY-MM-DD)')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--save-db', action='store_true', default=True,
                       help='Save to database (default: True)')
    parser.add_argument('--export-format', choices=['csv', 'parquet', 'excel'], default='parquet',
                       help='Export format (default: parquet for historical data)')
    parser.add_argument('--quick-test', action='store_true',
                       help='Quick test mode - fetch only 1 week, 5 near-ATM strikes')
    parser.add_argument('--atm-only', action='store_true',
                       help='Fetch only at-the-money strikes (faster)')
    parser.add_argument('--no-export', action='store_true',
                       help='Skip file export, only save to database')
    args = parser.parse_args()
    
    # Handle quick test mode
    if args.quick_test:
        print("🧪 Quick test mode enabled - fetching 1 week of data with limited strikes")
        args.days = 7
        args.atm_only = True
        if not args.export_format:
            args.export_format = 'csv'

    # Calculate date range with flexible date format support
    def parse_date(date_str):
        """Parse date from YYYYMMDD or YYYY-MM-DD format"""
        if '-' in date_str:
            return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
        return date_str

    if args.start_date and args.end_date:
        start_date = parse_date(args.start_date)
        end_date = parse_date(args.end_date)
    else:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y%m%d')
    
    print("\n" + "="*60)
    print("QQQ OPTIONS HISTORICAL FETCH")
    print(f"Date Range: {start_date} to {end_date}")
    print("="*60 + "\n")
    
    try:
        # Initialize fetcher
        fetcher = QQQOptionsFetcher(args.config)
        
        # Connect to Bloomberg
        logger.info("Connecting to Bloomberg Terminal...")
        if not fetcher.api.connect():
            logger.error("Failed to connect to Bloomberg API")
            return 1
        
        logger.info("Successfully connected to Bloomberg")
        
        # Check API usage before starting
        quota = fetcher.monitor.get_remaining_quota()
        logger.info(f"API Quota - Daily: {quota['daily_remaining']:,}, "
                   f"Monthly: {quota['monthly_remaining']:,}")
        
        # Estimate usage
        estimated_usage = args.days * 40 * 10  # days * options * fields
        logger.info(f"Estimated API usage: {estimated_usage:,} data points")
        
        if not fetcher.monitor.can_make_request(estimated_usage):
            logger.warning("Request would exceed API limits!")
            response = input("Continue with reduced scope? (y/n): ")
            if response.lower() != 'y':
                return 1
        
        # Fetch historical data with options
        logger.info("Fetching historical options data...")

        # Modify fetcher for ATM-only mode
        if args.atm_only:
            logger.info("ATM-only mode: limiting to 5 strikes around current price")
            # This will be handled in the fetch_historical_options method

        data = fetcher.fetch_historical_options(start_date, end_date)

        if data.empty:
            logger.warning("No data fetched")
            return 1

        logger.info(f"Fetched {len(data)} historical records")

        # Transform Bloomberg data format to standardized format
        if not data.empty:
            logger.info("Transforming Bloomberg data format...")
            transformed_data = fetcher.processor.transform_bloomberg_data(data)
            logger.info(f"Transformed data to {len(transformed_data)} records")
        else:
            transformed_data = data

        # Validate processed data
        processed_data = fetcher.processor.validate_data(transformed_data)
        logger.info(f"Validated {len(processed_data)} records")

        # Save to database if requested
        if args.save_db:
            logger.info("Saving to database...")
            db = DatabaseManager()
            records_saved = db.save_options_data(processed_data)
            logger.info(f"Saved {records_saved} records to database")

        # Export to file unless --no-export is specified
        if not args.no_export:
            # Temporarily set the output format in config
            original_format = fetcher.config.get('output', {}).get('format', 'csv')
            if 'output' not in fetcher.config:
                fetcher.config['output'] = {}
            fetcher.config['output']['format'] = args.export_format

            # Export with intelligent naming
            filepath = fetcher.save_data(processed_data, suffix="_historical")
            logger.info(f"Exported to {filepath}")

            # Restore original format
            fetcher.config['output']['format'] = original_format
        else:
            logger.info("Skipping file export as requested")
            filepath = None
        
        # Show enhanced summary
        print("\n" + "="*70)
        print("🎯 HISTORICAL FETCH SUMMARY")
        print("="*70)

        # Format dates for display
        start_display = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        end_display = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')

        print(f"📅 Date Range: {start_display} to {end_display}")
        print(f"📊 Records Fetched: {len(data):,}")
        print(f"✅ Records Validated: {len(processed_data):,}")

        if not processed_data.empty:
            if 'fetch_date' in processed_data.columns:
                print(f"📈 Unique Trading Days: {pd.to_datetime(processed_data['fetch_date']).dt.date.nunique()}")
            else:
                print(f"📈 Unique Trading Days: N/A (fetch_date not available)")
            print(f"🎯 Unique Strikes: {processed_data['strike'].nunique()}")
            print(f"📅 Unique Expiries: {processed_data['expiry'].nunique()}")

            # Show data range
            min_strike = processed_data['strike'].min()
            max_strike = processed_data['strike'].max()
            print(f"💰 Strike Range: ${min_strike:.0f} - ${max_strike:.0f}")

            # Show expiry range
            expiries = processed_data['expiry'].unique()
            if len(expiries) > 0:
                print(f"⏰ Expiry Range: {min(expiries)} to {max(expiries)}")

        if filepath:
            import os
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"💾 Export File: {filepath}")
            print(f"📁 File Size: {file_size:.1f} MB")
            print(f"📝 Format: {args.export_format.upper()}")

            # Loading instructions
            if args.export_format == 'parquet':
                print(f"💡 Load with: df = pd.read_parquet('{filepath}')")
            elif args.export_format == 'csv':
                print(f"💡 Load with: df = pd.read_csv('{filepath}')")

        print("="*70)
        
        # Show usage report
        fetcher.monitor.print_usage_report()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during fetch: {e}")
        return 1
        
    finally:
        # Disconnect
        if 'fetcher' in locals():
            fetcher.api.disconnect()
            logger.info("Disconnected from Bloomberg")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)