#!/usr/bin/env python3
"""
Bloomberg API Core Functions
Handles connection and data requests to Bloomberg Terminal
"""

import blpapi
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BloombergAPI:
    """Bloomberg API wrapper for fetching options data"""
    
    def __init__(self, host: str = "localhost", port: int = 8194):
        """
        Initialize Bloomberg API connection
        
        Args:
            host: Bloomberg API host (default: localhost)
            port: Bloomberg API port (default: 8194)
        """
        self.host = host
        self.port = port
        self.session = None
        self.service = None
        self.connected = False
        
    def connect(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Establish connection to Bloomberg API with retry logic
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if connected successfully
        """
        for attempt in range(max_retries):
            try:
                # Session options
                sessionOptions = blpapi.SessionOptions()
                sessionOptions.setServerHost(self.host)
                sessionOptions.setServerPort(self.port)
                
                # Create and start session
                self.session = blpapi.Session(sessionOptions)
                
                if not self.session.start():
                    logger.error(f"Failed to start Bloomberg session (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                    
                if not self.session.openService("//blp/refdata"):
                    logger.error(f"Failed to open Bloomberg service (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                    
                self.service = self.session.getService("//blp/refdata")
                self.connected = True
                logger.info("Successfully connected to Bloomberg API")
                return True
                
            except Exception as e:
                logger.error(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def disconnect(self):
        """Close Bloomberg API connection"""
        if self.session:
            self.session.stop()
            self.connected = False
            logger.info("Disconnected from Bloomberg API")
    
    def fetch_historical_data(self, 
                            tickers: List[str], 
                            fields: List[str],
                            start_date: str,
                            end_date: str,
                            frequency: str = "DAILY") -> pd.DataFrame:
        """
        Fetch historical data using BDH (Bloomberg Data History)
        
        Args:
            tickers: List of Bloomberg tickers
            fields: List of fields to fetch (e.g., ['PX_LAST', 'VOLUME'])
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            frequency: Data frequency (DAILY, WEEKLY, MONTHLY)
            
        Returns:
            DataFrame with historical data
        """
        if not self.connected:
            logger.error("Not connected to Bloomberg")
            return pd.DataFrame()
        
        try:
            request = self.service.createRequest("HistoricalDataRequest")
            
            # Add securities
            for ticker in tickers:
                request.getElement("securities").appendValue(ticker)
            
            # Add fields
            for field in fields:
                request.getElement("fields").appendValue(field)
            
            # Set date range
            request.set("startDate", start_date)
            request.set("endDate", end_date)
            request.set("periodicitySelection", frequency)
            
            # Additional options
            request.set("adjustmentNormal", True)
            request.set("adjustmentAbnormal", True)
            request.set("adjustmentSplit", True)
            
            # Send request
            logger.info(f"Fetching historical data for {len(tickers)} tickers")
            self.session.sendRequest(request)
            
            # Process response
            data = self._process_historical_response()
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def fetch_reference_data(self, 
                           tickers: List[str], 
                           fields: List[str],
                           max_retries: int = 2) -> pd.DataFrame:
        """
        Fetch reference data using BDP (Bloomberg Data Point) with retry logic
        
        Args:
            tickers: List of Bloomberg tickers
            fields: List of fields to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            DataFrame with reference data
        """
        if not self.connected:
            logger.error("Not connected to Bloomberg")
            # Try to reconnect
            if not self.connect():
                return pd.DataFrame()
        
        for attempt in range(max_retries):
            try:
                request = self.service.createRequest("ReferenceDataRequest")
                
                # Add securities
                for ticker in tickers:
                    request.getElement("securities").appendValue(ticker)
                
                # Add fields
                for field in fields:
                    request.getElement("fields").appendValue(field)
                
                # Send request
                logger.info(f"Fetching reference data for {len(tickers)} tickers (attempt {attempt + 1}/{max_retries})")
                self.session.sendRequest(request)
                
                # Process response
                data = self._process_reference_response()
                
                if not data.empty:
                    return data
                elif attempt < max_retries - 1:
                    logger.warning(f"Empty response, retrying...")
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error fetching reference data (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return pd.DataFrame()
        
        return pd.DataFrame()
    
    def _process_historical_response(self) -> pd.DataFrame:
        """Process historical data response"""
        data_dict = {}
        
        try:
            while True:
                event = self.session.nextEvent(500)
                
                for msg in event:
                    if msg.hasElement("securityData"):
                        security_data = msg.getElement("securityData")
                        ticker = security_data.getElementAsString("security")
                        field_data = security_data.getElement("fieldData")
                        
                        dates = []
                        values = {}
                        
                        for i in range(field_data.numValues()):
                            element = field_data.getValue(i)
                            date = element.getElementAsString("date")
                            dates.append(date)
                            
                            for field_name in element.elementNames():
                                if field_name != "date":
                                    if field_name not in values:
                                        values[field_name] = []
                                    values[field_name].append(
                                        element.getElementAsFloat(field_name)
                                    )
                        
                        # Store data
                        for field, vals in values.items():
                            key = f"{ticker}_{field}"
                            data_dict[key] = pd.Series(vals, index=pd.to_datetime(dates))
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            # Convert to DataFrame
            if data_dict:
                df = pd.DataFrame(data_dict)
                return df
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
        
        return pd.DataFrame()
    
    def _process_reference_response(self) -> pd.DataFrame:
        """Process reference data response"""
        data_list = []
        
        try:
            while True:
                event = self.session.nextEvent(500)
                
                for msg in event:
                    if msg.hasElement("securityData"):
                        security_data_array = msg.getElement("securityData")
                        
                        for i in range(security_data_array.numValues()):
                            security_data = security_data_array.getValue(i)
                            ticker = security_data.getElementAsString("security")
                            field_data = security_data.getElement("fieldData")
                            
                            row_data = {"ticker": ticker}
                            
                            for field_name in field_data.elementNames():
                                row_data[field_name] = field_data.getElementAsString(field_name)
                            
                            data_list.append(row_data)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            
            # Convert to DataFrame
            if data_list:
                df = pd.DataFrame(data_list)
                return df
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
        
        return pd.DataFrame()
    
    def build_option_ticker(self, 
                          underlying: str, 
                          expiry: str, 
                          strike: float, 
                          option_type: str) -> str:
        """
        Build Bloomberg option ticker
        
        Args:
            underlying: Underlying symbol (e.g., 'QQQ')
            expiry: Expiry date in YYYYMMDD format
            strike: Strike price
            option_type: 'C' for Call, 'P' for Put
            
        Returns:
            Bloomberg option ticker string
        """
        # Format: "QQQ US 12/20/24 C500 Equity"
        expiry_date = datetime.strptime(expiry, "%Y%m%d")
        expiry_str = expiry_date.strftime("%m/%d/%y")
        
        ticker = f"{underlying} US {expiry_str} {option_type}{strike:.0f} Equity"
        return ticker
    
    def get_option_chain(self, 
                        underlying: str, 
                        expiry: str,
                        min_strike: float,
                        max_strike: float,
                        strike_interval: float = 5.0) -> List[str]:
        """
        Generate option chain tickers
        
        Args:
            underlying: Underlying symbol
            expiry: Expiry date (YYYYMMDD)
            min_strike: Minimum strike price
            max_strike: Maximum strike price
            strike_interval: Strike price interval
            
        Returns:
            List of option tickers
        """
        tickers = []
        
        strike = min_strike
        while strike <= max_strike:
            # Add call
            call_ticker = self.build_option_ticker(underlying, expiry, strike, "C")
            tickers.append(call_ticker)
            
            # Add put
            put_ticker = self.build_option_ticker(underlying, expiry, strike, "P")
            tickers.append(put_ticker)
            
            strike += strike_interval
        
        return tickers
    
    def batch_request(self, 
                     tickers: List[str], 
                     fields: List[str],
                     batch_size: int = 20,
                     delay: float = 1.0,
                     continue_on_error: bool = True) -> pd.DataFrame:
        """
        Batch request to avoid hitting API limits with error recovery
        
        Args:
            tickers: List of tickers
            fields: List of fields
            batch_size: Number of tickers per batch
            delay: Delay between batches (seconds)
            continue_on_error: Continue processing if a batch fails
            
        Returns:
            Combined DataFrame
        """
        all_data = []
        failed_batches = []
        
        total_batches = (len(tickers) - 1) // batch_size + 1
        
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} tickers)")
            
            try:
                # Fetch data for batch
                data = self.fetch_reference_data(batch, fields)
                
                if not data.empty:
                    all_data.append(data)
                    logger.info(f"Batch {batch_num} successful: {len(data)} records")
                else:
                    logger.warning(f"Batch {batch_num} returned no data")
                    if not continue_on_error:
                        failed_batches.append(batch_num)
                    
            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}")
                failed_batches.append(batch_num)
                
                if not continue_on_error:
                    logger.error("Stopping due to batch failure")
                    break
            
            # Delay to avoid rate limits
            if i + batch_size < len(tickers):
                time.sleep(delay)
        
        if failed_batches:
            logger.warning(f"Failed batches: {failed_batches}")
        
        # Combine all data
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"Total records fetched: {len(combined)}")
            return combined
        
        return pd.DataFrame()


def test_connection():
    """Test Bloomberg API connection"""
    api = BloombergAPI()
    
    if api.connect():
        print("✅ Successfully connected to Bloomberg API")
        
        # Test with a simple request
        test_ticker = ["SPY US Equity"]
        test_fields = ["PX_LAST", "VOLUME"]
        
        data = api.fetch_reference_data(test_ticker, test_fields)
        
        if not data.empty:
            print("✅ Successfully fetched test data:")
            print(data)
        else:
            print("❌ Failed to fetch test data")
        
        api.disconnect()
    else:
        print("❌ Failed to connect to Bloomberg API")
        print("Please ensure Bloomberg Terminal is running and logged in")


if __name__ == "__main__":
    test_connection()