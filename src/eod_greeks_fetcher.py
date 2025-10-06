#!/usr/bin/env python3
"""
EOD Greeks Fetcher
Daily End-of-Day Greeks collection system for QQQ options
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import os
import yaml
from pathlib import Path

from .bloomberg_api import BloombergAPI
from .usage_monitor import UsageMonitor
from .greeks_calculator import GreeksCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EODGreeksFetcher:
    """Fetch and store EOD Greeks data for options"""

    # EOD-specific fields including Greeks
    EOD_FIELDS = [
        'PX_SETTLE',      # Settlement price
        'PX_LAST',        # Last price at close
        'PX_BID',         # Closing bid
        'PX_ASK',         # Closing ask
        'VOLUME',         # Daily volume
        'OPEN_INT',       # Open interest at EOD
        'IVOL_MID',       # Implied volatility at close
        'DELTA',          # Delta at close
        'GAMMA',          # Gamma at close
        'THETA',          # Theta at close
        'VEGA',           # Vega at close
        'RHO',            # Rho at close
        'OPT_UNDL_PX',    # Underlying price at close
        'MONEYNESS',      # Moneyness at close
        'TIME_TO_EXPIRY'  # Time to expiry
    ]

    # Alternative Greek field names to try
    GREEK_FIELD_VARIANTS = [
        ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO'],
        ['OPT_DELTA', 'OPT_GAMMA', 'OPT_THETA', 'OPT_VEGA', 'OPT_RHO'],
        ['DELTA_MID', 'GAMMA_MID', 'THETA_MID', 'VEGA_MID', 'RHO_MID'],
        ['SETTLE_DELTA', 'SETTLE_GAMMA', 'SETTLE_THETA', 'SETTLE_VEGA', 'SETTLE_RHO']
    ]

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize EOD Greeks Fetcher"""
        self.config = self._load_config(config_path)
        self.api = BloombergAPI(
            host=self.config.get('bloomberg', {}).get('host', 'localhost'),
            port=self.config.get('bloomberg', {}).get('port', 8194)
        )
        self.monitor = UsageMonitor(self.config.get('limits', {}))
        self.calculator = GreeksCalculator(risk_free_rate=0.045)

        # Create EOD data directory
        self.eod_path = Path('./data/eod_greeks')
        self.eod_path.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'bloomberg': {
                'host': 'localhost',
                'port': 8194
            },
            'eod': {
                'fetch_time': '16:30',  # 4:30 PM EST
                'max_strikes': 40,       # Number of strikes around ATM
                'expiries_ahead': 5      # Number of expiries to fetch
            },
            'limits': {
                'daily_limit': 50000,
                'batch_size': 20
            }
        }

    def fetch_eod_greeks(self,
                        ticker: str = "QQQ",
                        settle_date: Optional[str] = None,
                        expiries: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetch EOD Greeks for options

        Args:
            ticker: Underlying ticker (default: QQQ)
            settle_date: Settlement date YYYYMMDD (None for previous business day)
            expiries: List of expiry dates to fetch (None for auto-select)

        Returns:
            DataFrame with EOD Greeks data
        """
        if not self.api.connected:
            self.api.connect()

        # Get spot price for the ticker
        spot_price = self._get_spot_price(ticker)

        # Get option expiries if not provided
        if expiries is None:
            expiries = self._get_upcoming_expiries(ticker)

        all_data = []

        for expiry in expiries[:self.config.get('eod', {}).get('expiries_ahead', 5)]:
            logger.info(f"Fetching EOD Greeks for {ticker} expiry {expiry}")

            # Get option tickers for this expiry
            option_tickers = self._generate_option_tickers(
                ticker, expiry, spot_price
            )

            if not option_tickers:
                logger.warning(f"No option tickers generated for expiry {expiry}")
                continue

            # Try to fetch EOD Greeks using different field variants
            greeks_data = self._fetch_with_field_variants(
                option_tickers, settle_date
            )

            if not greeks_data.empty:
                # Add metadata
                greeks_data['underlying'] = ticker
                greeks_data['expiry'] = expiry
                greeks_data['fetch_time'] = datetime.now()
                greeks_data['spot_price'] = spot_price

                # Parse strike and option type from ticker
                greeks_data = self._parse_option_info(greeks_data)

                # If Greeks not available from Bloomberg, calculate them
                if not self._has_greeks(greeks_data):
                    logger.info("Greeks not available from Bloomberg, calculating...")
                    greeks_data = self._calculate_missing_greeks(greeks_data)

                all_data.append(greeks_data)

            # Update usage monitor
            self.monitor.record_usage(len(option_tickers) * len(self.EOD_FIELDS))

        # Combine all data
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data

        return pd.DataFrame()

    def _fetch_with_field_variants(self,
                                  tickers: List[str],
                                  settle_date: Optional[str]) -> pd.DataFrame:
        """Try fetching with different field name variants"""
        # First try with standard EOD fields
        data = self.api.fetch_eod_reference_data(
            tickers,
            self.EOD_FIELDS,
            settle_date
        )

        if not data.empty:
            return data

        # If no data, try different Greek field variants
        for variant in self.GREEK_FIELD_VARIANTS:
            logger.info(f"Trying Greek field variant: {variant}")

            # Combine price fields with Greek variant
            fields = ['PX_SETTLE', 'PX_LAST', 'PX_BID', 'PX_ASK',
                     'VOLUME', 'OPEN_INT', 'IVOL_MID', 'OPT_UNDL_PX']
            fields.extend(variant)

            data = self.api.fetch_eod_reference_data(
                tickers,
                fields,
                settle_date
            )

            if not data.empty and self._has_valid_greeks(data, variant):
                # Standardize Greek column names
                for i, greek in enumerate(['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']):
                    if variant[i] in data.columns:
                        data[greek] = data[variant[i]]
                        if variant[i] != greek:
                            data.drop(variant[i], axis=1, inplace=True)

                logger.info(f"Successfully fetched Greeks using variant: {variant}")
                return data

        logger.warning("Could not fetch Greeks with any field variant")
        return data if not data.empty else pd.DataFrame()

    def _has_greeks(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame has Greek values"""
        greek_cols = ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']
        for col in greek_cols:
            if col in df.columns and df[col].notna().any():
                return True
        return False

    def _has_valid_greeks(self, df: pd.DataFrame, fields: List[str]) -> bool:
        """Check if DataFrame has valid Greek values"""
        for field in fields:
            if field in df.columns and df[field].notna().any():
                return True
        return False

    def _calculate_missing_greeks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Greeks using Black-Scholes if missing"""
        if 'IVOL_MID' in df.columns and 'strike' in df.columns:
            df = self.calculator.add_greeks_to_dataframe(
                df,
                spot_col='spot_price' if 'spot_price' in df.columns else 'OPT_UNDL_PX',
                strike_col='strike',
                expiry_col='expiry',
                ivol_col='IVOL_MID',
                type_col='option_type'
            )
            logger.info("✅ Greeks calculated successfully using Black-Scholes")
        else:
            logger.warning("Cannot calculate Greeks: missing required fields")

        return df

    def _get_spot_price(self, ticker: str) -> float:
        """Get spot price for ticker"""
        try:
            data = self.api.fetch_reference_data(
                [f"{ticker} US Equity"],
                ["PX_LAST"]
            )
            if not data.empty:
                return float(data['PX_LAST'].iloc[0])
        except Exception as e:
            logger.error(f"Error fetching spot price: {e}")

        # Return approximate default
        return 480.0 if ticker == "QQQ" else 100.0

    def _get_upcoming_expiries(self, ticker: str) -> List[str]:
        """Get upcoming option expiry dates"""
        expiries = []
        today = datetime.now()

        # Generate weekly expiries for next 2 months
        for weeks_ahead in range(8):
            # Calculate next Friday
            days_to_friday = (4 - today.weekday() + 7) % 7
            if days_to_friday == 0 and weeks_ahead == 0:
                days_to_friday = 7  # Next week if today is Friday

            friday = today + timedelta(days=days_to_friday + weeks_ahead * 7)
            expiries.append(friday.strftime("%Y%m%d"))

        return expiries

    def _generate_option_tickers(self,
                                ticker: str,
                                expiry: str,
                                spot_price: float) -> List[str]:
        """Generate option tickers for an expiry"""
        tickers = []

        # Parse expiry date
        exp_date = datetime.strptime(expiry, "%Y%m%d")
        exp_str = exp_date.strftime("%m/%d/%y")

        # Calculate strike range
        num_strikes = self.config.get('eod', {}).get('max_strikes', 40) // 2
        strike_interval = 5 if spot_price > 200 else 2.5 if spot_price > 100 else 1

        min_strike = int(spot_price - num_strikes * strike_interval)
        max_strike = int(spot_price + num_strikes * strike_interval)

        # Generate tickers for calls and puts
        for strike in range(min_strike, max_strike + 1, int(strike_interval)):
            # Call option
            call_ticker = f"{ticker} US {exp_str} C{strike} Equity"
            tickers.append(call_ticker)

            # Put option
            put_ticker = f"{ticker} US {exp_str} P{strike} Equity"
            tickers.append(put_ticker)

        logger.info(f"Generated {len(tickers)} option tickers for expiry {expiry}")
        return tickers

    def _parse_option_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse strike and option type from ticker"""
        if 'ticker' in df.columns:
            # Extract strike: "QQQ US 12/20/24 C500 Equity" -> 500
            df['strike'] = df['ticker'].str.extract(r'[CP](\d+)')[0].astype(float)

            # Extract option type: C or P
            df['option_type'] = df['ticker'].str.extract(r'([CP])\d+')[0]

        return df

    def save_eod_data(self, df: pd.DataFrame, date: Optional[str] = None):
        """Save EOD Greeks data to file"""
        if df.empty:
            logger.warning("No data to save")
            return

        # Use provided date or today's date
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Save to CSV
        csv_file = self.eod_path / f"{date}_eod_greeks.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"EOD Greeks saved to {csv_file}")

        # Also save to parquet for better compression
        parquet_file = self.eod_path / f"{date}_eod_greeks.parquet"
        df.to_parquet(parquet_file, index=False, compression='snappy')
        logger.info(f"EOD Greeks saved to {parquet_file}")

        return str(csv_file)

    def fetch_and_save_daily_eod(self) -> str:
        """Fetch and save today's EOD Greeks - main daily execution"""
        logger.info("=" * 60)
        logger.info("Starting daily EOD Greeks collection")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 60)

        try:
            # Connect to Bloomberg
            if not self.api.connect():
                logger.error("Failed to connect to Bloomberg API")
                return ""

            # Fetch EOD Greeks for QQQ
            data = self.fetch_eod_greeks("QQQ")

            if not data.empty:
                # Save to file
                file_path = self.save_eod_data(data)

                # Print summary
                logger.info("\n" + "=" * 60)
                logger.info("EOD GREEKS COLLECTION SUMMARY")
                logger.info("=" * 60)
                logger.info(f"Records collected: {len(data)}")
                logger.info(f"Expiries: {data['expiry'].nunique()} unique")
                logger.info(f"Greeks available: {self._has_greeks(data)}")
                logger.info(f"Data saved to: {file_path}")
                logger.info("=" * 60)

                return file_path
            else:
                logger.warning("No EOD data collected")
                return ""

        except Exception as e:
            logger.error(f"Error in daily EOD collection: {e}")
            return ""

        finally:
            # Disconnect
            self.api.disconnect()


if __name__ == "__main__":
    # Run daily EOD collection
    fetcher = EODGreeksFetcher()
    fetcher.fetch_and_save_daily_eod()