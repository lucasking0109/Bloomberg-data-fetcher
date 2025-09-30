#!/usr/bin/env python3
"""
QQQ Constituents Data Fetcher
Fetches options and equity data for top QQQ holdings with robust error handling
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import yaml
import os
import time
from pathlib import Path

from .bloomberg_api import BloombergAPI
from .usage_monitor import UsageMonitor
from .data_processor import DataProcessor
from .database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConstituentsFetcher:
    """Fetch data for QQQ constituent stocks with error recovery"""
    
    def __init__(self, 
                 config_path: str = "config/config.yaml",
                 constituents_path: str = "config/qqq_constituents.yaml"):
        """
        Initialize constituents fetcher
        
        Args:
            config_path: Path to main configuration
            constituents_path: Path to constituents configuration
        """
        self.config = self._load_config(config_path)
        self.constituents_config = self._load_constituents_config(constituents_path)
        
        self.api = BloombergAPI(
            host=self.config.get('bloomberg', {}).get('host', 'localhost'),
            port=self.config.get('bloomberg', {}).get('port', 8194)
        )
        
        self.monitor = UsageMonitor(self.config.get('limits', {}))
        self.processor = DataProcessor()
        self.db = DatabaseManager(self.config.get('output', {}).get('database_path', 'data/bloomberg_options.db'))
        
        # Extract configuration
        self.fetch_config = self.constituents_config.get('fetch_config', {})
        self.constituents = self.constituents_config.get('constituents', [])
        
        # Options configuration
        self.strikes_above = self.fetch_config.get('strikes_above_atm', 20)
        self.strikes_below = self.fetch_config.get('strikes_below_atm', 20)
        self.max_days_expiry = self.fetch_config.get('max_days_to_expiry', 60)
        
        # Fields to fetch
        self.equity_fields = self.fetch_config.get('equity_fields', [])
        self.option_fields = self.fetch_config.get('option_fields', [])
        
        # Error handling
        self.error_config = self.constituents_config.get('error_handling', {})
        self.max_retries = self.error_config.get('max_retries', 3)
        self.retry_delay = self.error_config.get('retry_delay', 5)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load main configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_constituents_config(self, constituents_path: str) -> Dict:
        """Load constituents configuration"""
        if os.path.exists(constituents_path):
            with open(constituents_path, 'r') as f:
                return yaml.safe_load(f)
        logger.warning(f"Constituents config not found at {constituents_path}")
        return {}
    
    def get_constituent_tickers(self, top_n: Optional[int] = None) -> List[str]:
        """
        Get list of constituent tickers to fetch
        
        Args:
            top_n: Number of top constituents to fetch (None for all)
            
        Returns:
            List of ticker symbols
        """
        tickers = [c['ticker'] for c in self.constituents]
        
        if top_n:
            return tickers[:top_n]
        return tickers
    
    def fetch_constituent_equity_data(self, ticker: str) -> pd.DataFrame:
        """
        Fetch equity data for a constituent
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with equity data
        """
        try:
            bloomberg_ticker = f"{ticker} US Equity"
            
            logger.info(f"Fetching equity data for {ticker}")
            
            # Check API usage
            estimated_usage = len(self.equity_fields)
            if not self.monitor.can_make_request(estimated_usage):
                logger.warning(f"API limit would be exceeded for {ticker} equity data")
                return pd.DataFrame()
            
            # Fetch reference data
            data = self.api.fetch_reference_data(
                [bloomberg_ticker],
                self.equity_fields
            )
            
            if not data.empty:
                data['underlying'] = ticker
                data['data_type'] = 'equity'
                data['fetch_time'] = datetime.now()
                
                # Update usage monitor
                self.monitor.record_usage(estimated_usage)
                
                logger.info(f"Successfully fetched equity data for {ticker}")
                return data
            
        except Exception as e:
            logger.error(f"Error fetching equity data for {ticker}: {e}")
            
        return pd.DataFrame()
    
    def fetch_constituent_options(self, 
                                 ticker: str,
                                 spot_price: Optional[float] = None) -> pd.DataFrame:
        """
        Fetch options data for a constituent with ATM ± 20 strikes
        
        Args:
            ticker: Stock ticker symbol
            spot_price: Current stock price (will fetch if not provided)
            
        Returns:
            DataFrame with options data
        """
        try:
            # Get spot price if not provided
            if spot_price is None:
                equity_data = self.fetch_constituent_equity_data(ticker)
                if not equity_data.empty and 'PX_LAST' in equity_data.columns:
                    spot_price = float(equity_data['PX_LAST'].iloc[0])
                else:
                    logger.warning(f"Could not get spot price for {ticker}")
                    return pd.DataFrame()
            
            logger.info(f"Fetching options for {ticker} (spot: ${spot_price:.2f})")
            
            # Calculate strike range (ATM ± 20 strikes)
            strike_interval = self._get_strike_interval(spot_price)
            min_strike = np.floor(spot_price - self.strikes_below * strike_interval)
            max_strike = np.ceil(spot_price + self.strikes_above * strike_interval)
            
            # Round to interval
            min_strike = np.floor(min_strike / strike_interval) * strike_interval
            max_strike = np.ceil(max_strike / strike_interval) * strike_interval
            
            logger.info(f"{ticker} strike range: ${min_strike:.0f} - ${max_strike:.0f}, interval: ${strike_interval}")
            
            # Get expiry dates (within 2 months)
            expiries = self._get_expiry_dates_within_months(2)
            
            all_options_data = []
            
            for expiry in expiries:
                # Generate option tickers
                option_tickers = self.api.get_option_chain(
                    ticker,
                    expiry,
                    min_strike,
                    max_strike,
                    strike_interval
                )
                
                logger.info(f"Fetching {len(option_tickers)} options for {ticker} expiry {expiry}")
                
                # Check API usage
                estimated_usage = len(option_tickers) * len(self.option_fields)
                if not self.monitor.can_make_request(estimated_usage):
                    logger.warning(f"API limit would be exceeded for {ticker} options")
                    break
                
                # Fetch in batches
                batch_size = self.config.get('limits', {}).get('batch_size', 20)
                delay = self.config.get('limits', {}).get('request_delay', 1.0)
                
                data = self.api.batch_request(
                    option_tickers,
                    self.option_fields,
                    batch_size,
                    delay
                )
                
                if not data.empty:
                    # Add metadata
                    data['underlying'] = ticker
                    data['expiry'] = expiry
                    data['fetch_time'] = datetime.now()
                    data['spot_price'] = spot_price
                    
                    # Parse ticker to extract strike and type
                    data = self._parse_option_tickers(data)
                    
                    all_options_data.append(data)
                    
                    # Update usage monitor
                    self.monitor.record_usage(len(data) * len(self.option_fields))
            
            # Combine all expiries
            if all_options_data:
                combined_data = pd.concat(all_options_data, ignore_index=True)
                logger.info(f"Successfully fetched {len(combined_data)} options for {ticker}")
                return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching options for {ticker}: {e}")
        
        return pd.DataFrame()
    
    def _get_strike_interval(self, spot_price: float) -> float:
        """Determine appropriate strike interval based on stock price"""
        if spot_price < 50:
            return 0.5
        elif spot_price < 100:
            return 1.0
        elif spot_price < 200:
            return 2.5
        elif spot_price < 500:
            return 5.0
        else:
            return 10.0
    
    def _get_expiry_dates_within_months(self, months: int) -> List[str]:
        """
        Get option expiry dates within specified months
        
        Args:
            months: Number of months ahead
            
        Returns:
            List of expiry dates in YYYYMMDD format
        """
        expiries = []
        today = datetime.now()
        end_date = today + timedelta(days=30 * months)
        
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
        
        logger.info(f"Expiry dates within {months} months: {expiries}")
        return expiries
    
    def _parse_option_tickers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse Bloomberg option tickers to extract strike and type"""
        if 'ticker' in df.columns:
            # Extract strike and type from ticker
            # Format: "AAPL US 12/20/24 C150 Equity"
            
            df['strike'] = df['ticker'].str.extract(r'[CP](\d+(?:\.\d+)?)')[0].astype(float)
            df['option_type'] = df['ticker'].str.extract(r'([CP])\d+')[0]
        
        return df
    
    def fetch_all_constituents(self, 
                              resume: bool = False,
                              save_to_db: bool = True) -> Dict:
        """
        Fetch data for all configured constituents with error recovery
        
        Args:
            resume: Resume from previous state if available
            save_to_db: Save data to database
            
        Returns:
            Dictionary with fetch results
        """
        # Connect to Bloomberg
        if not self.api.connected:
            if not self.api.connect():
                logger.error("Failed to connect to Bloomberg API")
                return {'error': 'Connection failed'}
        
        # Get tickers to fetch
        tickers = self.get_constituent_tickers()

        # Note: Resume functionality removed with state manager
        if resume:
            logger.warning("Resume functionality not available - fetching all tickers")
        
        results = {
            'successful': [],
            'failed': [],
            'total_records': 0,
            'total_api_points': 0
        }
        
        for ticker in tickers:
            retry_count = 0
            success = False
            
            while retry_count < self.max_retries and not success:
                try:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Processing {ticker} (attempt {retry_count + 1}/{self.max_retries})")
                    logger.info(f"{'='*60}")
                    
                    # Fetch equity data
                    equity_data = self.fetch_constituent_equity_data(ticker)
                    
                    spot_price = None
                    if not equity_data.empty and 'PX_LAST' in equity_data.columns:
                        spot_price = float(equity_data['PX_LAST'].iloc[0])
                        
                        # Save equity data
                        if save_to_db and not equity_data.empty:
                            self._save_equity_data(equity_data)
                    
                    # Fetch options data
                    options_data = self.fetch_constituent_options(ticker, spot_price)
                    
                    if not options_data.empty:
                        # Process and validate data
                        processed_data = self.processor.validate_data(options_data)
                        
                        # Save to database
                        if save_to_db and not processed_data.empty:
                            records_saved = self.db.save_options_data(processed_data)
                            logger.info(f"Saved {records_saved} options records for {ticker}")
                        
                        # Update results
                        total_records = len(equity_data) + len(processed_data)
                        api_points = len(self.equity_fields) + len(processed_data) * len(self.option_fields)

                        results['successful'].append(ticker)
                        results['total_records'] += total_records
                        results['total_api_points'] += api_points

                        success = True
                        
                    else:
                        raise Exception("No options data fetched")
                    
                except Exception as e:
                    retry_count += 1
                    logger.error(f"Error processing {ticker}: {e}")
                    
                    if retry_count < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(f"Failed to process {ticker} after {retry_count} attempts: {e}")
                        results['failed'].append(ticker)
            
            # Show progress
            completed = len(results['successful']) + len(results['failed'])
            total = len(tickers)
            progress_pct = (completed / total) * 100 if total > 0 else 0
            logger.info(f"\nProgress: {completed}/{total} ({progress_pct:.1f}%)")

            # Check API usage
            self.monitor.print_usage_report()

            # Small delay between tickers
            time.sleep(2)
        
        # Final summary
        logger.info("\n" + "="*60)
        logger.info("CONSTITUENT FETCH COMPLETE")
        logger.info("="*60)
        logger.info(f"Successful: {len(results['successful'])} tickers")
        logger.info(f"Failed: {len(results['failed'])} tickers")
        logger.info(f"Total records: {results['total_records']}")
        logger.info(f"API points used: {results['total_api_points']}")
        
        if results['failed']:
            logger.warning(f"Failed tickers: {results['failed']}")
        
        return results
    
    def _save_equity_data(self, df: pd.DataFrame):
        """Save equity data to database"""
        try:
            # Add to a new equity_data table (extend database schema)
            conn = self.db._get_connection()
            df.to_sql('equity_data', conn, if_exists='append', index=False)
            conn.close()
        except Exception as e:
            logger.error(f"Error saving equity data: {e}")
    
    def _get_connection(self):
        """Get database connection"""
        import sqlite3
        return sqlite3.connect(self.db.db_path)


if __name__ == "__main__":
    # Test the constituents fetcher
    fetcher = ConstituentsFetcher()
    
    # Test getting tickers
    tickers = fetcher.get_constituent_tickers(top_n=3)
    print(f"Top 3 constituents: {tickers}")
    
    # Test with a single ticker
    if fetcher.api.connect():
        # Test equity data
        equity_data = fetcher.fetch_constituent_equity_data("AAPL")
        if not equity_data.empty:
            print("\nEquity data for AAPL:")
            print(equity_data)
        
        # Test options data
        options_data = fetcher.fetch_constituent_options("AAPL")
        if not options_data.empty:
            print(f"\nFetched {len(options_data)} options for AAPL")
            print(options_data.head())
        
        fetcher.api.disconnect()