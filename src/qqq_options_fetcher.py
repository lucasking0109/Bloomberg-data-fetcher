#!/usr/bin/env python3
"""
QQQ Options Data Fetcher
Specialized fetcher for QQQ options with smart strike selection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import yaml
import os
import time
from .bloomberg_api import BloombergAPI
from .usage_monitor import UsageMonitor
from .data_processor import DataProcessor

# Try to import Greeks calculator
try:
    from .greeks_calculator import GreeksCalculator
    GREEKS_CALCULATOR_AVAILABLE = True
except ImportError:
    GREEKS_CALCULATOR_AVAILABLE = False
    logging.warning("Greeks calculator not available. Install scipy: pip install scipy")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QQQOptionsFetcher:
    """Fetch QQQ options data with optimized API usage"""
    
    # Bloomberg fields for options
    OPTION_FIELDS = [
        'PX_LAST',       # Last price
        'PX_BID',        # Bid price
        'PX_ASK',        # Ask price
        'VOLUME',        # Volume
        'OPEN_INT',      # Open interest
        'IVOL_MID',      # Implied volatility
        'DELTA',         # Delta
        'GAMMA',         # Gamma
        'THETA',         # Theta
        'VEGA',          # Vega
        'RHO',           # Rho
        'OPT_UNDL_PX',   # Underlying price
        'BID_SIZE',      # Bid size
        'ASK_SIZE',      # Ask size
        'PX_SETTLE',     # Settlement price
        'CHG_NET_1D',    # Net change 1 day
        'CHG_PCT_1D',    # Percent change 1 day
        'VOLATILITY_30D', # 30-day historical volatility
        'PX_HIGH',       # High price
        'PX_LOW',        # Low price
        'TIME_LAST_UPD', # Last update time
        'IVOL_BID',      # Implied volatility bid
        'IVOL_ASK',      # Implied volatility ask
        'MONEYNESS',     # Moneyness
        'TIME_TO_EXPIRY' # Time to expiry in years
    ]
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize QQQ Options Fetcher
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.api = BloombergAPI(
            host=self.config.get('bloomberg', {}).get('host', 'localhost'),
            port=self.config.get('bloomberg', {}).get('port', 8194)
        )
        self.monitor = UsageMonitor(self.config.get('limits', {}))
        self.processor = DataProcessor()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default config if file doesn't exist
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'bloomberg': {
                'host': 'localhost',
                'port': 8194
            },
            'qqq_options': {
                'strikes_above': 20,
                'strikes_below': 20,
                'strike_interval': 2.5,
                'expiries_to_fetch': [1, 2, 3]  # Next 3 monthly expiries
            },
            'limits': {
                'daily_limit': 50000,
                'monthly_limit': 500000,
                'batch_size': 20,
                'request_delay': 1.0
            },
            'output': {
                'format': 'csv',
                'path': './data/'
            }
        }
    
    def get_qqq_spot_price(self) -> float:
        """Get current QQQ spot price"""
        try:
            if not self.api.connected:
                self.api.connect()
            
            data = self.api.fetch_reference_data(
                ["QQQ US Equity"], 
                ["PX_LAST"]
            )
            
            if not data.empty:
                return float(data['PX_LAST'].iloc[0])
            
        except Exception as e:
            logger.error(f"Error fetching QQQ spot price: {e}")
        
        # Return approximate price if fetch fails
        return 480.0  # Update this default value
    
    def calculate_strike_range(self, spot_price: float) -> Tuple[float, float, float]:
        """
        Calculate strike range based on spot price
        
        Args:
            spot_price: Current QQQ price
            
        Returns:
            Tuple of (min_strike, max_strike, interval)
        """
        config = self.config.get('qqq_options', {})
        strikes_above = config.get('strikes_above', 20)
        strikes_below = config.get('strikes_below', 20)
        
        # Determine strike interval based on price level
        if spot_price < 100:
            interval = 1.0
        elif spot_price < 200:
            interval = 2.5
        else:
            interval = 5.0
        
        # Override with config if specified
        interval = config.get('strike_interval', interval)
        
        # Calculate range
        min_strike = np.floor(spot_price - strikes_below * interval)
        max_strike = np.ceil(spot_price + strikes_above * interval)
        
        # Round to interval
        min_strike = np.floor(min_strike / interval) * interval
        max_strike = np.ceil(max_strike / interval) * interval
        
        logger.info(f"Strike range: ${min_strike:.0f} - ${max_strike:.0f}, interval: ${interval}")
        
        return min_strike, max_strike, interval
    
    def get_expiry_dates(self) -> List[str]:
        """
        Get ALL available expiry dates for QQQ options (weekly + monthly)
        QQQ has weekly expiries, not just monthly ones
        
        Returns:
            List of expiry dates in YYYYMMDD format
        """
        config = self.config.get('qqq_options', {})
        max_days = config.get('max_days_to_expiry', 60)  # 2 months
        
        expiries = []
        today = datetime.now()
        end_date = today + timedelta(days=max_days)
        
        # Generate all Fridays within the date range (QQQ has weekly expiries)
        current_date = today
        while current_date <= end_date:
            # Find next Friday
            days_ahead = 4 - current_date.weekday()  # Friday is weekday 4
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            friday = current_date + timedelta(days=days_ahead)
            
            # Only include if it's in the future
            if friday > today:
                expiries.append(friday.strftime("%Y%m%d"))
            
            # Move to next week
            current_date = friday + timedelta(days=1)
        
        # Also add quarterly expiries (3rd Friday of March, June, September, December)
        # These often have more liquidity
        quarterly_months = [3, 6, 9, 12]
        current_year = today.year
        next_year = current_year + 1
        
        for year in [current_year, next_year]:
            for month in quarterly_months:
                quarterly_expiry = self._get_third_friday(datetime(year, month, 1))
                if today < quarterly_expiry <= end_date:
                    quarterly_date = quarterly_expiry.strftime("%Y%m%d")
                    if quarterly_date not in expiries:
                        expiries.append(quarterly_date)
        
        # Sort expiries by date
        expiries.sort()
        
        logger.info(f"Found {len(expiries)} expiry dates (including weekly expiries): {expiries[:5]}...")
        return expiries
    
    def _get_third_friday(self, date: datetime) -> datetime:
        """Get third Friday of the month"""
        # Get first day of month
        first_day = date.replace(day=1)
        
        # Find first Friday
        days_until_friday = (4 - first_day.weekday()) % 7
        first_friday = first_day + timedelta(days=days_until_friday)
        
        # Get third Friday
        third_friday = first_friday + timedelta(weeks=2)
        
        return third_friday
    
    def fetch_options_chain(self,
                           expiry: str,
                           spot_price: Optional[float] = None) -> pd.DataFrame:
        """
        Fetch complete options chain for an expiry using hybrid approach:
        - Reference Data API for all current data including Greeks

        Args:
            expiry: Expiry date (YYYYMMDD)
            spot_price: Current spot price (will fetch if not provided)

        Returns:
            DataFrame with options data including Greeks
        """
        # Get spot price if not provided
        if spot_price is None:
            spot_price = self.get_qqq_spot_price()

        # Calculate strike range
        min_strike, max_strike, interval = self.calculate_strike_range(spot_price)

        # Generate option tickers
        tickers = self.api.get_option_chain(
            "QQQ",
            expiry,
            min_strike,
            max_strike,
            interval
        )

        logger.info(f"Fetching {len(tickers)} options for expiry {expiry}")

        # Check API usage before fetching
        estimated_usage = len(tickers) * len(self.OPTION_FIELDS)
        if not self.monitor.can_make_request(estimated_usage):
            logger.warning("API limit would be exceeded, skipping request")
            return pd.DataFrame()

        # Fetch ALL fields using Reference Data API for current snapshot
        # This should include Greeks
        config = self.config.get('limits', {})
        batch_size = config.get('batch_size', 20)
        delay = config.get('request_delay', 1.0)

        # Use Reference Data API which should provide Greeks
        all_data = []

        # Process in batches
        for i in range(0, len(tickers), batch_size):
            batch_tickers = tickers[i:i + batch_size]

            try:
                # Fetch all fields including Greeks via Reference Data
                batch_data = self.api.fetch_reference_data(
                    batch_tickers,
                    self.OPTION_FIELDS  # All 26 fields including Greeks
                )

                if not batch_data.empty:
                    all_data.append(batch_data)
                    logger.info(f"Fetched batch {i//batch_size + 1}: {len(batch_data)} options with Greeks")

                # Delay between batches
                if i + batch_size < len(tickers):
                    time.sleep(delay)

            except Exception as e:
                logger.warning(f"Error fetching batch: {e}")
                continue

        # Combine all batches
        if all_data:
            data = pd.concat(all_data, ignore_index=True)
        else:
            data = pd.DataFrame()

        # Update usage monitor
        self.monitor.record_usage(len(data) * len(self.OPTION_FIELDS))

        # Process and add metadata
        if not data.empty:
            data['expiry'] = expiry
            data['fetch_time'] = datetime.now()
            data['spot_price'] = spot_price

            # Parse ticker to extract strike and type
            data = self._parse_tickers(data)

        return data
    
    def _parse_tickers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse Bloomberg tickers to extract strike and option type"""
        if 'ticker' in df.columns:
            # Extract strike and type from ticker
            # Format: "QQQ US 12/20/24 C500 Equity"
            
            df['strike'] = df['ticker'].str.extract(r'[CP](\d+)')[0].astype(float)
            df['option_type'] = df['ticker'].str.extract(r'([CP])\d+')[0]
            df['underlying'] = 'QQQ'
        
        return df
    
    def fetch_historical_options(self,
                                start_date: str,
                                end_date: str,
                                expiries: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetch historical options data with hybrid approach:
        - Historical Data API for price/volume data
        - Reference Data API for Greeks

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            expiries: List of expiry dates (will generate if not provided)

        Returns:
            DataFrame with historical options data including Greeks
        """
        if not self.api.connected:
            self.api.connect()

        # Get expiries if not provided
        if expiries is None:
            expiries = self.get_expiry_dates()

        all_data = []

        for expiry in expiries:
            logger.info(f"Fetching historical data for expiry {expiry}")

            # Get spot price (use current as approximation)
            spot_price = self.get_qqq_spot_price()

            # Calculate strike range
            min_strike, max_strike, interval = self.calculate_strike_range(spot_price)

            # Generate option tickers
            tickers = self.api.get_option_chain(
                "QQQ",
                expiry,
                min_strike,
                max_strike,
                interval
            )

            # Limit tickers to most liquid ones (near ATM)
            atm_strikes = self._get_atm_strikes(spot_price, min_strike, max_strike, interval, n=10)
            filtered_tickers = [t for t in tickers if any(f"{s:.0f}" in t for s in atm_strikes)]

            logger.info(f"Fetching {len(filtered_tickers)} near-ATM options")

            # Check API usage
            estimated_usage = len(filtered_tickers) * len(self.OPTION_FIELDS) * 60  # 60 days
            if not self.monitor.can_make_request(estimated_usage):
                logger.warning("API limit would be exceeded, reducing scope")
                filtered_tickers = filtered_tickers[:10]  # Reduce to 10 options

            # HYBRID APPROACH:
            # 1. Fetch historical price/volume data
            price_fields = ['PX_LAST', 'PX_BID', 'PX_ASK', 'VOLUME', 'OPEN_INT', 'IVOL_MID']
            historical_data = self.api.fetch_historical_data(
                filtered_tickers,
                price_fields,
                start_date,
                end_date,
                "DAILY"
            )

            # 2. Try to fetch Greeks using Reference Data API
            greeks_fields = ['DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO']
            greeks_fetched = False

            try:
                greeks_data = self.api.fetch_reference_data(
                    filtered_tickers,
                    greeks_fields
                )

                # Check if Greeks actually have values
                if not greeks_data.empty:
                    has_greeks = any(greeks_data[field].notna().any()
                                    for field in greeks_fields
                                    if field in greeks_data.columns)

                    if has_greeks:
                        # Merge Greeks with historical data
                        for greek in greeks_fields:
                            if greek in greeks_data.columns:
                                # Map Greeks by ticker
                                greeks_dict = greeks_data.set_index('ticker')[greek].to_dict()
                                historical_data[greek] = historical_data['ticker'].map(greeks_dict)

                        logger.info(f"Successfully merged Bloomberg Greeks for {len(filtered_tickers)} options")
                        greeks_fetched = True
                    else:
                        logger.warning("Bloomberg Greeks fields exist but have no values")

            except Exception as e:
                logger.warning(f"Could not fetch Greeks from Bloomberg: {e}")

            # 3. If Bloomberg Greeks not available, calculate them using Black-Scholes
            if not greeks_fetched and GREEKS_CALCULATOR_AVAILABLE and not historical_data.empty:
                logger.info("Calculating Greeks using Black-Scholes model...")

                try:
                    calculator = GreeksCalculator(risk_free_rate=0.045)  # Current US risk-free rate

                    # Ensure we have required fields
                    if 'IVOL_MID' in historical_data.columns:
                        # Parse strike from ticker if not already present
                        if 'strike' not in historical_data.columns:
                            historical_data = self._parse_tickers(historical_data)

                        # Add underlying price if not present
                        if 'OPT_UNDL_PX' not in historical_data.columns:
                            historical_data['OPT_UNDL_PX'] = spot_price

                        # Calculate Greeks
                        historical_data = calculator.add_greeks_to_dataframe(
                            historical_data,
                            spot_col='OPT_UNDL_PX',
                            strike_col='strike',
                            expiry_col='expiry',
                            ivol_col='IVOL_MID',
                            type_col='option_type'
                        )

                        logger.info("✅ Greeks calculated successfully using Black-Scholes")
                    else:
                        logger.warning("Cannot calculate Greeks: IVOL_MID not available")

                except Exception as e:
                    logger.warning(f"Error calculating Greeks: {e}")

            if not historical_data.empty:
                historical_data['expiry'] = expiry
                all_data.append(historical_data)

            # Update usage monitor
            self.monitor.record_usage(len(historical_data) * 11)

        # Combine all data
        if all_data:
            return pd.concat(all_data, ignore_index=True)

        return pd.DataFrame()
    
    def _get_atm_strikes(self, 
                        spot: float, 
                        min_strike: float, 
                        max_strike: float, 
                        interval: float,
                        n: int = 10) -> List[float]:
        """Get n strikes closest to ATM"""
        strikes = np.arange(min_strike, max_strike + interval, interval)
        distances = np.abs(strikes - spot)
        sorted_indices = np.argsort(distances)
        
        return strikes[sorted_indices[:n]].tolist()
    
    def fetch_eod_data(self) -> pd.DataFrame:
        """
        Fetch end-of-day options data
        Perfect for daily execution after market close
        
        Returns:
            DataFrame with EOD options data
        """
        logger.info("Fetching end-of-day QQQ options data")
        
        if not self.api.connected:
            self.api.connect()
        
        # Get current spot price
        spot_price = self.get_qqq_spot_price()
        
        # Get next 3 monthly expiries
        expiries = self.get_expiry_dates()
        
        all_data = []
        
        for expiry in expiries:
            data = self.fetch_options_chain(expiry, spot_price)
            
            if not data.empty:
                all_data.append(data)
        
        # Combine and save
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Save to file
            self.save_data(combined_data)
            
            return combined_data
        
        return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, suffix: str = ""):
        """Save data to file with intelligent naming for historical data"""
        config = self.config.get('output', {})
        output_path = config.get('path', './data/')
        output_format = config.get('format', 'csv')

        # Create directory if not exists
        os.makedirs(output_path, exist_ok=True)

        # Generate intelligent filename for historical data
        if "_historical" in suffix and not df.empty:
            # Extract date range from historical data
            today = datetime.now().strftime("%Y-%m-%d")

            # Try to extract date range from data
            if 'fetch_time' in df.columns:
                dates = pd.to_datetime(df['fetch_time']).dt.date
                start_date = dates.min().strftime("%Y-%m-%d")
                end_date = dates.max().strftime("%Y-%m-%d")

                if start_date == end_date:
                    filename = f"QQQ_options_historical_{start_date}"
                else:
                    filename = f"QQQ_options_historical_{start_date}_to_{end_date}"
            else:
                filename = f"QQQ_options_historical_{today}"
        else:
            # Use existing logic for current data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qqq_options_{timestamp}{suffix}"

        if output_format == 'csv':
            filepath = os.path.join(output_path, f"{filename}.csv")
            df.to_csv(filepath, index=False)
            logger.info(f"Data saved to {filepath}")

        elif output_format == 'parquet':
            filepath = os.path.join(output_path, f"{filename}.parquet")
            # Convert datetime columns for better Parquet compression
            df_copy = df.copy()
            if 'fetch_time' in df_copy.columns:
                df_copy['fetch_time'] = pd.to_datetime(df_copy['fetch_time'])
            df_copy.to_parquet(filepath, index=False, compression='snappy')
            logger.info(f"Data saved to {filepath}")

        elif output_format == 'excel':
            filepath = os.path.join(output_path, f"{filename}.xlsx")
            df.to_excel(filepath, index=False)
            logger.info(f"Data saved to {filepath}")

        return filepath
    
    def run(self):
        """Main execution function"""
        try:
            # Connect to Bloomberg
            if not self.api.connect():
                logger.error("Failed to connect to Bloomberg API")
                return
            
            # Fetch EOD data
            data = self.fetch_eod_data()
            
            if not data.empty:
                logger.info(f"Successfully fetched {len(data)} options records")
                
                # Display summary
                print("\n" + "="*60)
                print("QQQ OPTIONS DATA FETCH SUMMARY")
                print("="*60)
                print(f"Records fetched: {len(data)}")
                print(f"Expiries: {data['expiry'].unique()}")
                print(f"Strike range: ${data['strike'].min():.0f} - ${data['strike'].max():.0f}")
                print(f"Spot price: ${data['spot_price'].iloc[0]:.2f}")
                print("="*60)
                
                # Show usage statistics
                self.monitor.print_usage_report()
            else:
                logger.warning("No data fetched")
            
        finally:
            # Disconnect
            self.api.disconnect()


if __name__ == "__main__":
    fetcher = QQQOptionsFetcher()
    fetcher.run()