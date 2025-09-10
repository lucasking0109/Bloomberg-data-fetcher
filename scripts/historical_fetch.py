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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function for historical fetch"""
    
    parser = argparse.ArgumentParser(description='Fetch historical QQQ options data')
    parser.add_argument('--days', type=int, default=60, 
                       help='Number of days of history to fetch')
    parser.add_argument('--start-date', type=str, 
                       help='Start date (YYYYMMDD)')
    parser.add_argument('--end-date', type=str,
                       help='End date (YYYYMMDD)')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--save-db', action='store_true',
                       help='Save to database')
    args = parser.parse_args()
    
    # Calculate date range
    if args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
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
        
        # Fetch historical data
        logger.info("Fetching historical options data...")
        data = fetcher.fetch_historical_options(start_date, end_date)
        
        if data.empty:
            logger.warning("No data fetched")
            return 1
        
        logger.info(f"Fetched {len(data)} historical records")
        
        # Process data
        processed_data = fetcher.processor.validate_data(data)
        logger.info(f"Validated {len(processed_data)} records")
        
        # Save to database if requested
        if args.save_db:
            logger.info("Saving to database...")
            db = DatabaseManager()
            records_saved = db.save_options_data(processed_data)
            logger.info(f"Saved {records_saved} records to database")
        
        # Save to file
        filepath = fetcher.save_data(processed_data, suffix="_historical")
        logger.info(f"Exported to {filepath}")
        
        # Show summary
        print("\n" + "="*60)
        print("HISTORICAL FETCH SUMMARY")
        print("="*60)
        print(f"Date Range: {start_date} to {end_date}")
        print(f"Records Fetched: {len(data)}")
        print(f"Records Validated: {len(processed_data)}")
        
        if not processed_data.empty:
            print(f"Unique Dates: {processed_data['fetch_time'].dt.date.nunique()}")
            print(f"Unique Strikes: {processed_data['strike'].nunique()}")
            print(f"Unique Expiries: {processed_data['expiry'].nunique()}")
        
        print("="*60)
        
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