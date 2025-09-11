#!/usr/bin/env python3
"""
Database Manager for Bloomberg Options Data
Handles SQLite database operations
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os
import logging
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage SQLite database for options data"""
    
    def __init__(self, db_path: str = "data/bloomberg_options.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
        self._init_database()
    
    def _ensure_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create options data table with OPEN_INT explicitly included
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticker TEXT,
                underlying TEXT,
                expiry TEXT,
                strike REAL,
                option_type TEXT,
                bid REAL,
                ask REAL,
                last REAL,
                volume INTEGER,
                open_interest INTEGER,  -- Critical field for analysis
                implied_vol REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                rho REAL,
                underlying_price REAL,
                bid_size INTEGER,
                ask_size INTEGER,
                spread REAL,
                spread_pct REAL,
                moneyness REAL,
                days_to_expiry INTEGER,
                fetch_date DATE,
                UNIQUE(ticker, fetch_date)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_underlying_expiry 
            ON options_data(underlying, expiry)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fetch_date 
            ON options_data(fetch_date)
        """)
        
        # Create usage tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                hour INTEGER,
                request_count INTEGER,
                data_points INTEGER,
                UNIQUE(date, hour)
            )
        """)
        
        # Create equity data table for constituent stocks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticker TEXT,
                underlying TEXT,
                px_last REAL,
                px_open REAL,
                px_high REAL,
                px_low REAL,
                px_volume INTEGER,
                volume_avg_30d INTEGER,
                px_bid REAL,
                px_ask REAL,
                chg_pct_1d REAL,
                volatility_30d REAL,
                cur_mkt_cap REAL,
                pe_ratio REAL,
                div_yield REAL,
                fetch_date DATE,
                UNIQUE(ticker, fetch_date)
            )
        """)
        
        # Create constituents metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE,
                name TEXT,
                weight REAL,
                sector TEXT,
                last_updated DATE
            )
        """)
        
        # Create constituent options table (similar to options_data but for constituents)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituent_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticker TEXT,
                underlying TEXT,
                expiry TEXT,
                strike REAL,
                option_type TEXT,
                bid REAL,
                ask REAL,
                last REAL,
                volume INTEGER,
                open_interest INTEGER,  -- Critical for liquidity analysis
                implied_vol REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                rho REAL,
                underlying_price REAL,
                bid_size INTEGER,
                ask_size INTEGER,
                spread REAL,
                spread_pct REAL,
                moneyness REAL,
                days_to_expiry INTEGER,
                fetch_date DATE,
                UNIQUE(ticker, fetch_date)
            )
        """)
        
        # Create indices for constituent tables
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_equity_ticker 
            ON equity_data(underlying, fetch_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_constituent_options 
            ON constituent_options(underlying, expiry, strike)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_options_data(self, df: pd.DataFrame) -> int:
        """
        Save options data to database
        
        Args:
            df: DataFrame with options data
            
        Returns:
            Number of records saved
        """
        if df.empty:
            logger.warning("Empty DataFrame, nothing to save")
            return 0
        
        # Add fetch date
        df['fetch_date'] = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Save to database
            records_before = self._get_record_count(conn)
            
            df.to_sql(
                'options_data',
                conn,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            records_after = self._get_record_count(conn)
            records_saved = records_after - records_before
            
            logger.info(f"Saved {records_saved} records to database")
            return records_saved
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"Some records already exist: {e}")
            # Try to update existing records
            return self._update_existing_records(df, conn)
            
        finally:
            conn.close()
    
    def _get_record_count(self, conn: sqlite3.Connection) -> int:
        """Get total record count"""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM options_data")
        return cursor.fetchone()[0]
    
    def _update_existing_records(self, df: pd.DataFrame, conn: sqlite3.Connection) -> int:
        """Update existing records"""
        updated = 0
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    UPDATE options_data 
                    SET bid=?, ask=?, last=?, volume=?, open_interest=?,
                        implied_vol=?, delta=?, gamma=?, theta=?, vega=?,
                        timestamp=CURRENT_TIMESTAMP
                    WHERE ticker=? AND fetch_date=?
                """, (
                    row.get('bid'), row.get('ask'), row.get('last'),
                    row.get('volume'), row.get('open_interest'),
                    row.get('implied_vol'), row.get('delta'),
                    row.get('gamma'), row.get('theta'), row.get('vega'),
                    row.get('ticker'), row.get('fetch_date')
                ))
                
                if cursor.rowcount > 0:
                    updated += 1
                    
            except Exception as e:
                logger.debug(f"Failed to update record: {e}")
        
        conn.commit()
        logger.info(f"Updated {updated} existing records")
        return updated
    
    def get_latest_data(self, 
                       underlying: str = 'QQQ',
                       expiry: Optional[str] = None) -> pd.DataFrame:
        """
        Get latest options data
        
        Args:
            underlying: Underlying symbol
            expiry: Optional expiry filter
            
        Returns:
            DataFrame with latest data
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM options_data
            WHERE underlying = ?
        """
        params = [underlying]
        
        if expiry:
            query += " AND expiry = ?"
            params.append(expiry)
        
        query += " ORDER BY timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_historical_data(self,
                          start_date: str,
                          end_date: str,
                          underlying: str = 'QQQ') -> pd.DataFrame:
        """
        Get historical options data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            underlying: Underlying symbol
            
        Returns:
            DataFrame with historical data
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM options_data
            WHERE underlying = ?
            AND fetch_date BETWEEN ? AND ?
            ORDER BY fetch_date, expiry, strike, option_type
        """
        
        df = pd.read_sql_query(
            query,
            conn,
            params=(underlying, start_date, end_date)
        )
        
        conn.close()
        return df
    
    def get_summary_stats(self) -> Dict:
        """
        Get database summary statistics
        
        Returns:
            Dictionary with summary stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM options_data")
        stats['total_records'] = cursor.fetchone()[0]
        
        # Unique dates
        cursor.execute("SELECT COUNT(DISTINCT fetch_date) FROM options_data")
        stats['unique_dates'] = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("SELECT MIN(fetch_date), MAX(fetch_date) FROM options_data")
        min_date, max_date = cursor.fetchone()
        stats['date_range'] = f"{min_date} to {max_date}"
        
        # Unique expiries
        cursor.execute("SELECT COUNT(DISTINCT expiry) FROM options_data")
        stats['unique_expiries'] = cursor.fetchone()[0]
        
        # Unique strikes
        cursor.execute("SELECT COUNT(DISTINCT strike) FROM options_data")
        stats['unique_strikes'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Remove data older than specified days
        
        Args:
            days_to_keep: Number of days to keep
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM options_data
            WHERE fetch_date < date('now', '-' || ? || ' days')
        """, (days_to_keep,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {deleted} old records")
        return deleted
    
    def export_to_csv(self, 
                     output_path: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None):
        """
        Export data to CSV file
        
        Args:
            output_path: Output CSV file path
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM options_data"
        params = []
        
        if start_date and end_date:
            query += " WHERE fetch_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        query += " ORDER BY fetch_date, underlying, expiry, strike"
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} records to {output_path}")
    
    def export_to_parquet(self, 
                         output_path: str,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None):
        """
        Export data to Parquet file for efficient storage and fast access
        
        Args:
            output_path: Output Parquet file path
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM options_data"
        params = []
        
        if start_date and end_date:
            query += " WHERE fetch_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        query += " ORDER BY fetch_date, underlying, expiry, strike"
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        
        # Convert date columns to proper datetime types for better Parquet compression
        if 'fetch_date' in df.columns:
            df['fetch_date'] = pd.to_datetime(df['fetch_date'])
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'expiry' in df.columns:
            df['expiry'] = pd.to_datetime(df['expiry'], format='%Y%m%d')
        
        df.to_parquet(output_path, index=False, compression='snappy')
        logger.info(f"Exported {len(df)} records to {output_path} (Parquet format)")
    
    def export_constituent_options(self,
                                  output_path: str,
                                  format_type: str = 'parquet',
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None):
        """
        Export constituent options data with format selection
        
        Args:
            output_path: Output file path (extension will be added based on format)
            format_type: 'csv' or 'parquet'
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM constituent_options"
        params = []
        
        if start_date and end_date:
            query += " WHERE fetch_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        query += " ORDER BY fetch_date, underlying, expiry, strike"
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        
        if df.empty:
            logger.warning("No constituent options data found")
            return
        
        # Add appropriate file extension
        if not output_path.endswith(f'.{format_type}'):
            output_path = f"{output_path}.{format_type}"
        
        if format_type.lower() == 'csv':
            df.to_csv(output_path, index=False)
        elif format_type.lower() == 'parquet':
            # Convert date columns for better Parquet performance
            if 'fetch_date' in df.columns:
                df['fetch_date'] = pd.to_datetime(df['fetch_date'])
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'expiry' in df.columns:
                df['expiry'] = pd.to_datetime(df['expiry'], format='%Y%m%d')
            
            df.to_parquet(output_path, index=False, compression='snappy')
        
        logger.info(f"Exported {len(df)} constituent options records to {output_path} ({format_type.upper()} format)")


if __name__ == "__main__":
    # Test database manager
    db = DatabaseManager()
    
    # Get summary stats
    stats = db.get_summary_stats()
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")