#!/usr/bin/env python3
"""
EOD Greeks Scheduler
Daily automated collection of EOD Greeks data
Run this after market close (4:30 PM EST) to collect EOD Greeks
"""

import sys
import os
import time
import schedule
import logging
from datetime import datetime, timedelta
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.eod_greeks_fetcher import EODGreeksFetcher
from src.greeks_database import GreeksDatabase
from src.usage_monitor import UsageMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/eod_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EODScheduler:
    """Scheduler for daily EOD Greeks collection"""

    def __init__(self):
        """Initialize scheduler"""
        self.fetcher = EODGreeksFetcher()
        self.database = GreeksDatabase()
        self.monitor = UsageMonitor({})

        # Create logs directory
        os.makedirs('logs', exist_ok=True)

    def daily_eod_collection(self):
        """Execute daily EOD Greeks collection"""
        try:
            logger.info("=" * 60)
            logger.info("STARTING DAILY EOD GREEKS COLLECTION")
            logger.info(f"Time: {datetime.now()}")
            logger.info("=" * 60)

            # Check if market was open today (skip weekends/holidays)
            if not self._is_trading_day():
                logger.info("Not a trading day, skipping collection")
                return

            # Fetch EOD Greeks
            data = self.fetcher.fetch_eod_greeks("QQQ")

            if not data.empty:
                # Save to database
                settle_date = self._get_settle_date()
                records_inserted = self.database.insert_eod_data(data, settle_date)

                # Save to file
                file_path = self.fetcher.save_eod_data(data, settle_date)

                # Log success
                logger.info(f"✅ Successfully collected {len(data)} EOD records")
                logger.info(f"   Database records inserted: {records_inserted}")
                logger.info(f"   Data saved to: {file_path}")

                # Print database stats
                stats = self.database.get_database_stats()
                logger.info("\nDatabase Statistics:")
                for key, value in stats.items():
                    logger.info(f"  {key}: {value}")

                # Check for missing dates and backfill if needed
                self._check_missing_dates()

            else:
                logger.warning("❌ No EOD data collected")

            # Print usage statistics
            self.monitor.print_usage_report()

        except Exception as e:
            logger.error(f"Error in daily collection: {e}", exc_info=True)

        finally:
            logger.info("=" * 60)
            logger.info("DAILY EOD COLLECTION COMPLETE")
            logger.info("=" * 60)

    def _is_trading_day(self) -> bool:
        """Check if today is a trading day"""
        today = datetime.now()

        # Skip weekends
        if today.weekday() >= 5:
            return False

        # TODO: Add holiday calendar check
        # For now, assume weekdays are trading days
        return True

    def _get_settle_date(self) -> str:
        """Get settlement date (previous business day)"""
        today = datetime.now()

        # If running after market close, use today
        if today.hour >= 16:
            if today.weekday() < 5:
                return today.strftime("%Y-%m-%d")

        # Otherwise use previous business day
        if today.weekday() == 0:  # Monday
            settle = today - timedelta(days=3)
        elif today.weekday() == 6:  # Sunday
            settle = today - timedelta(days=2)
        else:
            settle = today - timedelta(days=1)

        return settle.strftime("%Y-%m-%d")

    def _check_missing_dates(self, days_back: int = 30):
        """Check for missing dates and log them"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        missing_dates = self.database.get_missing_dates(start_date, end_date)

        if missing_dates:
            logger.warning(f"Missing data for {len(missing_dates)} dates:")
            for date in missing_dates[:5]:  # Show first 5
                logger.warning(f"  - {date}")
            if len(missing_dates) > 5:
                logger.warning(f"  ... and {len(missing_dates) - 5} more")

    def backfill_missing_dates(self, days_back: int = 30):
        """Backfill missing EOD Greeks for past dates"""
        logger.info("Starting backfill process...")

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        missing_dates = self.database.get_missing_dates(start_date, end_date)

        if not missing_dates:
            logger.info("No missing dates to backfill")
            return

        logger.info(f"Found {len(missing_dates)} missing dates to backfill")

        for date in missing_dates:
            logger.info(f"Backfilling {date}...")

            # Format date for Bloomberg (YYYYMMDD)
            settle_date = date.replace("-", "")

            try:
                # Fetch EOD Greeks for specific date
                data = self.fetcher.fetch_eod_greeks("QQQ", settle_date)

                if not data.empty:
                    # Save to database
                    records = self.database.insert_eod_data(data, date)
                    logger.info(f"  ✅ Inserted {records} records for {date}")
                else:
                    logger.warning(f"  ❌ No data available for {date}")

                # Add delay to avoid hitting rate limits
                time.sleep(2)

            except Exception as e:
                logger.error(f"  ❌ Error backfilling {date}: {e}")

        logger.info("Backfill process complete")

    def run_scheduler(self, run_time: str = "16:30"):
        """
        Run the scheduler

        Args:
            run_time: Time to run daily collection (HH:MM format)
        """
        logger.info(f"Scheduler started. Will run daily at {run_time} EST")

        # Schedule daily job
        schedule.every().day.at(run_time).do(self.daily_eod_collection)

        # Run immediately on start if after market close
        current_hour = datetime.now().hour
        if current_hour >= 16:
            logger.info("Market is closed, running collection now...")
            self.daily_eod_collection()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_once(self):
        """Run collection once and exit"""
        self.daily_eod_collection()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EOD Greeks Scheduler")
    parser.add_argument(
        "--mode",
        choices=["once", "schedule", "backfill"],
        default="once",
        help="Execution mode: once (run once), schedule (run daily), backfill (fill missing dates)"
    )
    parser.add_argument(
        "--time",
        default="16:30",
        help="Time to run daily collection (HH:MM format, default: 16:30)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to backfill (default: 30)"
    )

    args = parser.parse_args()

    scheduler = EODScheduler()

    if args.mode == "once":
        logger.info("Running EOD collection once...")
        scheduler.run_once()
    elif args.mode == "schedule":
        logger.info(f"Starting scheduler to run daily at {args.time}...")
        scheduler.run_scheduler(args.time)
    elif args.mode == "backfill":
        logger.info(f"Backfilling missing dates for past {args.days} days...")
        scheduler.backfill_missing_dates(args.days)


if __name__ == "__main__":
    main()