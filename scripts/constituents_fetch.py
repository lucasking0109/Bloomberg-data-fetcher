#!/usr/bin/env python3
"""
Individual Stock Options Fetch Script
Fetch options data for individual stocks (QQQ constituents)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constituents_fetcher import ConstituentsFetcher
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
    """Main execution function for constituents fetch"""

    parser = argparse.ArgumentParser(description='Fetch individual stock options data')
    parser.add_argument('--ticker', type=str,
                       help='Single ticker to fetch (e.g., AAPL, MSFT)')
    parser.add_argument('--top', type=int,
                       help='Fetch top N constituents by weight (e.g., --top 10)')
    parser.add_argument('--all', action='store_true',
                       help='Fetch all 20 configured constituents')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days of history to fetch (default: 7)')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--constituents-config', default='config/qqq_constituents.yaml',
                       help='Path to constituents configuration file')
    parser.add_argument('--save-db', action='store_true', default=True,
                       help='Save to database (default: True)')
    parser.add_argument('--export-format', choices=['csv', 'parquet', 'excel'], default='parquet',
                       help='Export format (default: parquet)')
    parser.add_argument('--no-export', action='store_true',
                       help='Skip file export, only save to database')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.ticker, args.top, args.all]):
        parser.error("Must specify one of: --ticker, --top, or --all")

    print("\n" + "="*60)
    print("INDIVIDUAL STOCK OPTIONS FETCH")
    if args.ticker:
        print(f"Target: {args.ticker}")
    elif args.top:
        print(f"Target: Top {args.top} constituents by weight")
    else:
        print("Target: All configured constituents")
    print(f"History: {args.days} days")
    print("="*60 + "\n")

    try:
        # Initialize fetcher
        fetcher = ConstituentsFetcher(args.config, args.constituents_config)

        # Connect to Bloomberg
        logger.info("Connecting to Bloomberg Terminal...")
        if not fetcher.api.connect():
            logger.error("Failed to connect to Bloomberg API")
            return 1

        logger.info("Successfully connected to Bloomberg")

        # Check API usage
        quota = fetcher.monitor.get_remaining_quota()
        logger.info(f"API Quota - Daily: {quota['daily_remaining']:,}, "
                   f"Monthly: {quota['monthly_remaining']:,}")

        results = {}

        if args.ticker:
            # Single ticker fetch
            logger.info(f"Fetching data for {args.ticker}...")

            # Get spot price first
            spot_data = fetcher.fetch_constituent_equity_data(args.ticker)
            spot_price = None
            if not spot_data.empty and 'PX_LAST' in spot_data.columns:
                spot_price = spot_data['PX_LAST'].iloc[0]
                logger.info(f"{args.ticker} current price: ${spot_price:.2f}")

            # Fetch options data
            options_data = fetcher.fetch_constituent_options(args.ticker, spot_price)

            if not options_data.empty:
                # Transform data format
                transformed_data = fetcher.processor.transform_bloomberg_data(options_data)
                validated_data = fetcher.processor.validate_data(transformed_data)

                results[args.ticker] = {
                    'equity_data': spot_data,
                    'options_data': validated_data,
                    'records_count': len(validated_data)
                }

                logger.info(f"Successfully fetched {len(validated_data)} options records for {args.ticker}")
            else:
                logger.warning(f"No options data found for {args.ticker}")

        elif args.top or args.all:
            # Multiple tickers fetch
            constituents = fetcher.constituents_config.get('constituents', [])

            if args.top:
                constituents = constituents[:args.top]
                logger.info(f"Fetching top {args.top} constituents by weight")
            else:
                logger.info(f"Fetching all {len(constituents)} constituents")

            for i, constituent in enumerate(constituents, 1):
                ticker = constituent['ticker']
                weight = constituent['weight']

                logger.info(f"Processing {i}/{len(constituents)}: {ticker} (weight: {weight}%)")

                try:
                    # Get spot price
                    spot_data = fetcher.fetch_constituent_equity_data(ticker)
                    spot_price = None
                    if not spot_data.empty and 'PX_LAST' in spot_data.columns:
                        spot_price = spot_data['PX_LAST'].iloc[0]
                        logger.info(f"  {ticker} current price: ${spot_price:.2f}")

                    # Fetch options
                    options_data = fetcher.fetch_constituent_options(ticker, spot_price)

                    if not options_data.empty:
                        transformed_data = fetcher.processor.transform_bloomberg_data(options_data)
                        validated_data = fetcher.processor.validate_data(transformed_data)

                        results[ticker] = {
                            'equity_data': spot_data,
                            'options_data': validated_data,
                            'records_count': len(validated_data)
                        }

                        logger.info(f"  ✅ {ticker}: {len(validated_data)} options records")
                    else:
                        logger.warning(f"  ⚠️ {ticker}: No options data found")

                except Exception as e:
                    logger.error(f"  ❌ {ticker}: Error - {e}")
                    continue

                # Brief pause between requests
                if i < len(constituents):
                    import time
                    time.sleep(1)

        # Save results to database
        if args.save_db and results:
            logger.info("Saving to database...")
            db = DatabaseManager()

            total_saved = 0
            for ticker, data in results.items():
                if not data['options_data'].empty:
                    saved = db.save_options_data(data['options_data'])
                    total_saved += saved

                if not data['equity_data'].empty:
                    db.save_equity_data(data['equity_data'])

            logger.info(f"Saved {total_saved} options records to database")

        # Export to files
        if not args.no_export and results:
            logger.info("Exporting data files...")

            # Combine all options data
            all_options = []
            for ticker, data in results.items():
                if not data['options_data'].empty:
                    all_options.append(data['options_data'])

            if all_options:
                combined_data = pd.concat(all_options, ignore_index=True)

                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                if args.ticker:
                    filename = f"{args.ticker}_options_{timestamp}"
                elif args.top:
                    filename = f"top{args.top}_constituents_{timestamp}"
                else:
                    filename = f"all_constituents_{timestamp}"

                output_dir = "./data/"
                os.makedirs(output_dir, exist_ok=True)

                if args.export_format == 'parquet':
                    filepath = f"{output_dir}{filename}.parquet"
                    combined_data.to_parquet(filepath, index=False)
                elif args.export_format == 'csv':
                    filepath = f"{output_dir}{filename}.csv"
                    combined_data.to_csv(filepath, index=False)
                elif args.export_format == 'excel':
                    filepath = f"{output_dir}{filename}.xlsx"
                    combined_data.to_excel(filepath, index=False)

                logger.info(f"Exported to {filepath}")

        # Show summary
        print("\n" + "="*70)
        print("🎯 CONSTITUENTS FETCH SUMMARY")
        print("="*70)

        total_records = sum(data['records_count'] for data in results.values())
        successful_tickers = len(results)

        print(f"📊 Tickers Processed: {successful_tickers}")
        print(f"✅ Total Options Records: {total_records:,}")

        if results:
            print("\n📈 By Ticker:")
            for ticker, data in results.items():
                print(f"  {ticker}: {data['records_count']:,} records")

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