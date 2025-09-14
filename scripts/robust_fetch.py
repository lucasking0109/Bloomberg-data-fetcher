#!/usr/bin/env python3
"""
Robust Fetch Script
Master script for fetching all data with error recovery and progress tracking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qqq_options_fetcher import QQQOptionsFetcher
from src.constituents_fetcher import ConstituentsFetcher
from src.database_manager import DatabaseManager
from src.fetch_state_manager import FetchStateManager
from src.usage_monitor import UsageMonitor
from datetime import datetime
import logging
import argparse
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/robust_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RobustFetcher:
    """Master fetcher with complete error recovery"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize robust fetcher"""
        self.config_path = config_path
        self.state_manager = FetchStateManager()
        self.db = DatabaseManager()
        self.monitor = UsageMonitor()
        
        # Initialize fetchers
        self.qqq_fetcher = QQQOptionsFetcher(config_path)
        self.constituents_fetcher = ConstituentsFetcher(config_path)
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f" {title}")
        print("="*70)
        
    def fetch_all(self, 
                 include_qqq: bool = True,
                 include_constituents: bool = True,
                 top_n_constituents: Optional[int] = None,
                 resume: bool = False,
                 save_to_db: bool = True,
                 export_csv: bool = False,
                 export_format: str = 'auto'):
        """
        Fetch all configured data with error recovery
        
        Args:
            include_qqq: Fetch QQQ index options
            include_constituents: Fetch constituent data
            top_n_constituents: Number of top constituents to fetch
            resume: Resume from previous state
            save_to_db: Save to database
            export_csv: Export to CSV after completion
            export_format: 'csv', 'parquet', or 'auto' (auto: CSV for testing ≤5, Parquet for full)
        """
        start_time = datetime.now()
        
        self.print_header("BLOOMBERG DATA FETCH - ROBUST MODE")
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Resume mode: {resume}")
        print(f"Include QQQ: {include_qqq}")
        print(f"Include constituents: {include_constituents}")
        
        # Check if resuming
        if resume and self.state_manager.state['status'] != 'initialized':
            print(f"Resuming session: {self.state_manager.state['session_id']}")
            progress = self.state_manager.get_progress_summary()
            print(f"Previous progress: {progress['completed']}/{progress['total_tickers']} completed")
        
        results = {
            'qqq': None,
            'constituents': None,
            'total_records': 0,
            'total_api_points': 0,
            'errors': []
        }
        
        try:
            # Connect to Bloomberg
            self.print_header("CONNECTING TO BLOOMBERG")
            
            if not self._connect_bloomberg():
                logger.error("Failed to connect to Bloomberg API")
                return results
            
            print("✅ Connected to Bloomberg API")
            
            # Fetch QQQ index options
            if include_qqq:
                self.print_header("FETCHING QQQ INDEX OPTIONS")
                results['qqq'] = self._fetch_qqq_with_recovery(save_to_db)
            
            # Fetch constituent data
            if include_constituents:
                self.print_header("FETCHING CONSTITUENT DATA")
                
                # Get list of constituents
                tickers = self.constituents_fetcher.get_constituent_tickers(top_n_constituents)
                print(f"Will fetch {len(tickers)} constituents: {', '.join(tickers[:5])}...")
                
                # Check API usage before starting
                if not self._check_api_budget(len(tickers)):
                    logger.warning("Insufficient API budget for all constituents")
                    user_input = input("Continue with partial fetch? (y/n): ")
                    if user_input.lower() != 'y':
                        return results
                
                # Fetch constituents
                results['constituents'] = self.constituents_fetcher.fetch_all_constituents(
                    resume=resume,
                    save_to_db=save_to_db
                )
            
            # Calculate totals
            if results['qqq']:
                results['total_records'] += results['qqq'].get('records', 0)
                results['total_api_points'] += results['qqq'].get('api_points', 0)
            
            if results['constituents']:
                results['total_records'] += results['constituents'].get('total_records', 0)
                results['total_api_points'] += results['constituents'].get('total_api_points', 0)
            
        except KeyboardInterrupt:
            logger.warning("Fetch interrupted by user")
            self.state_manager.save_checkpoint()
            print("\n⚠️ Fetch interrupted. State saved for resume.")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            results['errors'].append(str(e))
            
        finally:
            # Disconnect from Bloomberg
            self._disconnect_bloomberg()
            
            # Print summary
            self._print_summary(results, start_time)
            
            # Export if requested
            if export_csv and results['total_records'] > 0:
                self._export_results(export_format, top_n_constituents)
        
        return results
    
    def _connect_bloomberg(self) -> bool:
        """Connect to Bloomberg with retries"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Try QQQ fetcher connection
                if self.qqq_fetcher.api.connect():
                    # Share connection with constituents fetcher
                    self.constituents_fetcher.api = self.qqq_fetcher.api
                    return True
                    
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                
            if attempt < max_attempts - 1:
                print(f"Retrying connection in 5 seconds...")
                time.sleep(5)
        
        return False
    
    def _disconnect_bloomberg(self):
        """Disconnect from Bloomberg"""
        try:
            if self.qqq_fetcher.api.connected:
                self.qqq_fetcher.api.disconnect()
                logger.info("Disconnected from Bloomberg")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    def _fetch_qqq_with_recovery(self, save_to_db: bool) -> Dict:
        """Fetch QQQ data with error recovery"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Fetching QQQ options (attempt {retry_count + 1}/{max_retries})")
                
                # Get spot price
                spot_price = self.qqq_fetcher.get_qqq_spot_price()
                print(f"QQQ spot price: ${spot_price:.2f}")
                
                # Get expiries within 2 months
                expiries = self._get_two_month_expiries()
                print(f"Fetching expiries: {expiries}")
                
                all_data = []
                total_api_points = 0
                
                for expiry in expiries:
                    print(f"\nFetching QQQ options for expiry {expiry}...")
                    
                    # Fetch options chain with ATM ± 20 strikes
                    data = self.qqq_fetcher.fetch_options_chain(expiry, spot_price)
                    
                    if not data.empty:
                        # Validate data includes OPEN_INT
                        if 'OPEN_INT' not in data.columns:
                            logger.warning("OPEN_INT field missing from data")
                        
                        all_data.append(data)
                        
                        # Estimate API usage
                        api_points = len(data) * len(self.qqq_fetcher.OPTION_FIELDS)
                        total_api_points += api_points
                        
                        print(f"✅ Fetched {len(data)} records for expiry {expiry}")
                        
                        # Save to database immediately
                        if save_to_db:
                            processed = self.qqq_fetcher.processor.validate_data(data)
                            records_saved = self.db.save_options_data(processed)
                            print(f"Saved {records_saved} records to database")
                    else:
                        logger.warning(f"No data for expiry {expiry}")
                
                # Combine all data
                if all_data:
                    combined = pd.concat(all_data, ignore_index=True)
                    
                    # Save checkpoint
                    self.state_manager.complete_ticker("QQQ", len(combined), total_api_points)
                    
                    return {
                        'status': 'success',
                        'records': len(combined),
                        'api_points': total_api_points,
                        'expiries': len(expiries)
                    }
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error fetching QQQ: {e}")
                
                if retry_count < max_retries:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    self.state_manager.fail_ticker("QQQ", str(e), retry_count)
                    return {'status': 'failed', 'error': str(e)}
        
        return {'status': 'failed', 'error': 'Max retries exceeded'}
    
    def _get_two_month_expiries(self) -> List[str]:
        """Get option expiries within 2 months"""
        from datetime import datetime, timedelta
        
        expiries = []
        today = datetime.now()
        end_date = today + timedelta(days=60)  # 2 months
        
        # Get monthly expiries (3rd Friday)
        current_month = today.replace(day=1)
        
        while current_month <= end_date:
            # Get third Friday of the month
            first_day = current_month.replace(day=1)
            days_until_friday = (4 - first_day.weekday()) % 7
            first_friday = first_day + timedelta(days=days_until_friday)
            third_friday = first_friday + timedelta(weeks=2)
            
            # Only include if within our time window and not expired
            if today <= third_friday <= end_date:
                expiries.append(third_friday.strftime("%Y%m%d"))
            
            # Move to next month
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
        
        return expiries
    
    def _check_api_budget(self, num_tickers: int) -> bool:
        """Check if we have enough API budget"""
        # Estimate usage per ticker
        estimated_per_ticker = 2000  # Conservative estimate
        total_estimated = num_tickers * estimated_per_ticker
        
        remaining = self.monitor.get_remaining_daily()
        
        print(f"\nAPI Usage Check:")
        print(f"  Estimated usage: {total_estimated:,} points")
        print(f"  Daily remaining: {remaining:,} points")
        print(f"  Coverage: {min(100, remaining/total_estimated*100):.1f}%")
        
        return remaining >= total_estimated * 0.5  # Need at least 50% coverage
    
    def _print_summary(self, results: Dict, start_time: datetime):
        """Print fetch summary"""
        self.print_header("FETCH SUMMARY")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"Duration: {duration}")
        print(f"Total records: {results['total_records']:,}")
        print(f"Total API points: {results['total_api_points']:,}")
        
        if results['qqq']:
            print(f"\nQQQ Index:")
            print(f"  Status: {results['qqq'].get('status', 'N/A')}")
            print(f"  Records: {results['qqq'].get('records', 0):,}")
            print(f"  Expiries: {results['qqq'].get('expiries', 0)}")
        
        if results['constituents']:
            print(f"\nConstituents:")
            print(f"  Successful: {len(results['constituents'].get('successful', []))}")
            print(f"  Failed: {len(results['constituents'].get('failed', []))}")
            
            if results['constituents'].get('failed'):
                print(f"  Failed tickers: {', '.join(results['constituents']['failed'])}")
        
        if results['errors']:
            print(f"\n⚠️ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        # Show usage statistics
        print("\n" + "-"*70)
        self.monitor.print_usage_report()
        
        # Show database statistics
        print("\n" + "-"*70)
        db_stats = self.db.get_summary_stats()
        print("Database Statistics:")
        for key, value in db_stats.items():
            print(f"  {key}: {value}")
    
    def _export_results(self, export_format: str = 'auto', top_n_constituents: Optional[int] = None):
        """
        Export results with smart format selection
        
        Args:
            export_format: 'csv', 'parquet', or 'auto'
            top_n_constituents: Number of constituents being fetched (for auto format selection)
        """
        try:
            # Auto format selection logic
            if export_format == 'auto':
                # Use CSV for testing (≤5 stocks) for easy inspection
                # Use Parquet for full datasets for efficiency
                if top_n_constituents and top_n_constituents <= 5:
                    actual_format = 'csv'
                    print(f"\n📋 Testing mode detected ({top_n_constituents} stocks) - using CSV format for easy inspection")
                else:
                    actual_format = 'parquet'
                    print(f"\n🚀 Full dataset mode - using Parquet format for efficiency")
            else:
                actual_format = export_format.lower()

            # Determine scope for intelligent filename generation
            if top_n_constituents is None or top_n_constituents == 0:
                scope = 'qqq_only'
            elif top_n_constituents <= 5:
                scope = 'top5'
            elif top_n_constituents >= 15:
                scope = 'all20'
            else:
                scope = 'all'

            # Export with intelligent filename generation
            if actual_format == 'csv':
                filename = self.db.export_to_csv(scope=scope)
            elif actual_format == 'parquet':
                filename = self.db.export_to_parquet(scope=scope)
            else:
                raise ValueError(f"Unsupported export format: {actual_format}")
            
            # Get file size for reporting
            import os
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            
            print(f"✅ Data exported to {filename}")
            print(f"   📊 File size: {file_size:.1f} MB")
            print(f"   📁 Format: {actual_format.upper()}")
            
            if actual_format == 'parquet':
                print(f"   💡 Use pandas.read_parquet('{filename}') to load data efficiently")
            else:
                print(f"   💡 Use pandas.read_csv('{filename}') to load data")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            print(f"❌ Export failed: {e}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Robust Bloomberg data fetcher')
    
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from previous state')
    parser.add_argument('--qqq-only', action='store_true',
                       help='Fetch only QQQ index options')
    parser.add_argument('--constituents-only', action='store_true',
                       help='Fetch only constituent data')
    parser.add_argument('--top-n', type=int, default=20,
                       help='Number of top constituents to fetch (default: 20 - all configured)')
    parser.add_argument('--no-db', action='store_true',
                       help='Do not save to database')
    parser.add_argument('--export-csv', action='store_true',
                       help='Export data after completion')
    parser.add_argument('--export-format', choices=['csv', 'parquet', 'auto'], default='auto',
                       help='Export format: csv, parquet, or auto (auto: CSV for ≤5 stocks, Parquet for full)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test run without fetching data')
    
    args = parser.parse_args()
    
    # Determine what to fetch
    include_qqq = not args.constituents_only
    include_constituents = not args.qqq_only
    save_to_db = not args.no_db
    
    if args.dry_run:
        print("DRY RUN MODE - No data will be fetched")
        fetcher = RobustFetcher(args.config)
        
        # Just show what would be fetched
        print("\nConfiguration:")
        print(f"  QQQ options: {include_qqq}")
        print(f"  Constituents: {include_constituents}")
        
        if include_constituents:
            tickers = fetcher.constituents_fetcher.get_constituent_tickers(args.top_n)
            print(f"  Would fetch {len(tickers)} constituents:")
            for i, ticker in enumerate(tickers, 1):
                print(f"    {i}. {ticker}")
        
        return 0
    
    # Run the fetcher
    try:
        fetcher = RobustFetcher(args.config)
        
        results = fetcher.fetch_all(
            include_qqq=include_qqq,
            include_constituents=include_constituents,
            top_n_constituents=args.top_n,
            resume=args.resume,
            save_to_db=save_to_db,
            export_csv=args.export_csv,
            export_format=args.export_format
        )
        
        # Return appropriate exit code
        if results.get('errors'):
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Fetch interrupted by user")
        print("Run with --resume flag to continue from where you left off")
        return 130
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    import pandas as pd
    from typing import Optional, Dict, List
    
    exit_code = main()
    sys.exit(exit_code)