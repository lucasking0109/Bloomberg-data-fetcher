#!/usr/bin/env python3
"""
Quick Test Script
Test Bloomberg API connection and fetch sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bloomberg_api import BloombergAPI
from datetime import datetime
import pandas as pd


def test_connection():
    """Test basic Bloomberg connection"""
    print("\n" + "="*60)
    print("BLOOMBERG API CONNECTION TEST")
    print("="*60 + "\n")
    
    api = BloombergAPI()
    
    print("1. Testing connection to Bloomberg Terminal...")
    if not api.connect():
        print("❌ Failed to connect to Bloomberg API")
        print("\nTroubleshooting:")
        print("1. Ensure Bloomberg Terminal is running")
        print("2. Ensure you are logged in")
        print("3. Check API settings (WAPI<GO>)")
        print("4. Verify port 8194 is not blocked")
        return False
    
    print("✅ Successfully connected to Bloomberg API\n")
    return api


def test_reference_data(api):
    """Test fetching reference data"""
    print("2. Testing reference data fetch...")
    
    # Test with SPY
    test_ticker = ["SPY US Equity"]
    test_fields = ["PX_LAST", "VOLUME", "NAME"]
    
    try:
        data = api.fetch_reference_data(test_ticker, test_fields)
        
        if not data.empty:
            print("✅ Successfully fetched reference data:")
            print(data.to_string())
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return False


def test_qqq_option(api):
    """Test fetching QQQ option data"""
    print("\n3. Testing QQQ option data fetch...")
    
    # Build a sample QQQ option ticker
    # Get next monthly expiry
    from datetime import datetime, timedelta
    
    # Calculate next monthly expiry (3rd Friday)
    today = datetime.now()
    next_month = today + timedelta(days=30)
    
    # Find third Friday
    first_day = next_month.replace(day=1)
    days_until_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=days_until_friday)
    third_friday = first_friday + timedelta(weeks=2)
    
    expiry_str = third_friday.strftime("%m/%d/%y")
    
    # Build option ticker
    strike = 480  # Approximate QQQ price
    option_ticker = f"QQQ US {expiry_str} C{strike} Equity"
    
    print(f"Testing with option: {option_ticker}")
    
    fields = ["PX_BID", "PX_ASK", "PX_LAST", "IVOL_MID", "DELTA"]
    
    try:
        data = api.fetch_reference_data([option_ticker], fields)
        
        if not data.empty:
            print("✅ Successfully fetched option data:")
            print(data.to_string())
            return True
        else:
            print("❌ No option data returned")
            print("Note: Option might not exist or be expired")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching option data: {e}")
        return False


def test_historical_data(api):
    """Test fetching historical data"""
    print("\n4. Testing historical data fetch...")
    
    # Test with QQQ
    ticker = ["QQQ US Equity"]
    fields = ["PX_LAST", "VOLUME"]
    
    # Last 5 days
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
    
    try:
        data = api.fetch_historical_data(
            ticker, fields, start_date, end_date, "DAILY"
        )
        
        if not data.empty:
            print("✅ Successfully fetched historical data:")
            print(f"   Records: {len(data)}")
            print(f"   Date range: {data.index.min()} to {data.index.max()}")
            print("\nSample data:")
            print(data.head())
            return True
        else:
            print("❌ No historical data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return False


def main():
    """Main test function"""
    
    # Test connection
    api = test_connection()
    if not api:
        return 1
    
    try:
        # Run tests
        tests_passed = 0
        tests_total = 3
        
        if test_reference_data(api):
            tests_passed += 1
        
        if test_qqq_option(api):
            tests_passed += 1
        
        if test_historical_data(api):
            tests_passed += 1
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Passed: {tests_passed}/{tests_total}")
        
        if tests_passed == tests_total:
            print("✅ All tests passed! Bloomberg API is working correctly.")
        elif tests_passed > 0:
            print("⚠️ Some tests passed. Check the failed tests above.")
        else:
            print("❌ All tests failed. Please check your Bloomberg setup.")
        
        print("="*60)
        
        return 0 if tests_passed == tests_total else 1
        
    finally:
        # Disconnect
        api.disconnect()
        print("\nDisconnected from Bloomberg API")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)