#!/usr/bin/env python3
"""
Daily QQQ Options Fetch Script
Run this after market close to get end-of-day options data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qqq_options_fetcher import QQQOptionsFetcher
from src.database_manager import DatabaseManager
from datetime import datetime
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function for daily fetch"""
    
    parser = argparse.ArgumentParser(description='Fetch daily QQQ options data')
    parser.add_argument('--config', default='config/config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--save-db', action='store_true', 
                       help='Save to database')
    parser.add_argument('--export-csv', action='store_true', 
                       help='Export to CSV file')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("QQQ OPTIONS DAILY FETCH")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    try:
        # Initialize fetcher
        fetcher = QQQOptionsFetcher(args.config)
        
        # Connect to Bloomberg
        logger.info("Connecting to Bloomberg Terminal...")
        if not fetcher.api.connect():
            logger.error("Failed to connect to Bloomberg API")
            logger.error("Please ensure:")
            logger.error("1. Bloomberg Terminal is running")
            logger.error("2. You are logged in")
            logger.error("3. API is enabled (WAPI<GO>)")
            return 1
        
        logger.info("Successfully connected to Bloomberg")
        
        # Fetch end-of-day data
        logger.info("Fetching QQQ options data...")
        data = fetcher.fetch_eod_data()
        
        if data.empty:
            logger.warning("No data fetched")
            return 1
        
        logger.info(f"Fetched {len(data)} option records")
        
        # Process data
        processed_data = fetcher.processor.validate_data(data)
        logger.info(f"Validated {len(processed_data)} records")
        
        # Save to database if requested
        if args.save_db:
            logger.info("Saving to database...")
            db = DatabaseManager()
            records_saved = db.save_options_data(processed_data)
            logger.info(f"Saved {records_saved} records to database")
            
            # Show database stats
            stats = db.get_summary_stats()
            print("\nDatabase Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Export to CSV if requested
        if args.export_csv:
            filepath = fetcher.save_data(processed_data, suffix="_daily")
            logger.info(f"Exported to {filepath}")
        
        # Show summary
        summary = fetcher.processor.create_summary_report(processed_data)
        
        print("\n" + "="*60)
        print("FETCH SUMMARY")
        print("="*60)
        for key, value in summary.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"{key:20}: {value:.4f}")
                else:
                    print(f"{key:20}: {value}")
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