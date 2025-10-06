#!/usr/bin/env python3
"""
Greeks Database Manager
Manages historical EOD Greeks database with SQLite
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GreeksDatabase:
    """Manage historical Greeks data in SQLite database"""

    def __init__(self, db_path: str = "./data/eod_greeks/historical_greeks.db"):
        """Initialize Greeks database"""
        self.db_path = db_path

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create main Greeks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eod_greeks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                settle_date DATE NOT NULL,
                ticker TEXT NOT NULL,
                underlying TEXT NOT NULL,
                strike REAL NOT NULL,
                expiry DATE NOT NULL,
                option_type TEXT NOT NULL,

                -- Price data
                px_settle REAL,
                px_last REAL,
                px_bid REAL,
                px_ask REAL,
                volume INTEGER,
                open_int INTEGER,

                -- Greeks
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                rho REAL,

                -- Additional fields
                ivol_mid REAL,
                opt_undl_px REAL,
                moneyness REAL,
                time_to_expiry REAL,

                -- Metadata
                fetch_time TIMESTAMP,
                data_source TEXT,  -- 'bloomberg' or 'calculated'

                -- Unique constraint to prevent duplicates
                UNIQUE(settle_date, ticker)
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_settle_date
            ON eod_greeks(settle_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_underlying_expiry
            ON eod_greeks(underlying, expiry)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker
            ON eod_greeks(ticker)
        """)

        # Create summary statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_records INTEGER,
                unique_tickers INTEGER,
                unique_underlyings INTEGER,
                greeks_available INTEGER,
                greeks_calculated INTEGER,
                fetch_time TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        logger.info(f"Database initialized at {self.db_path}")

    def insert_eod_data(self, df: pd.DataFrame,
                       settle_date: Optional[str] = None,
                       replace: bool = False) -> int:
        """
        Insert EOD Greeks data into database

        Args:
            df: DataFrame with EOD Greeks data
            settle_date: Settlement date (YYYY-MM-DD or YYYYMMDD)
            replace: Whether to replace existing data for the date

        Returns:
            Number of records inserted
        """
        if df.empty:
            logger.warning("No data to insert")
            return 0

        # Parse settle_date
        if settle_date:
            if len(settle_date) == 8:  # YYYYMMDD
                settle_date = f"{settle_date[:4]}-{settle_date[4:6]}-{settle_date[6:8]}"
        else:
            settle_date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # If replace, delete existing data for this date
            if replace:
                cursor.execute(
                    "DELETE FROM eod_greeks WHERE settle_date = ?",
                    (settle_date,)
                )
                logger.info(f"Deleted existing data for {settle_date}")

            # Prepare data for insertion
            records = []
            for _, row in df.iterrows():
                # Determine data source
                data_source = 'bloomberg'
                if 'data_source' in row:
                    data_source = row['data_source']
                elif pd.isna(row.get('DELTA')) and not pd.isna(row.get('IVOL_MID')):
                    data_source = 'calculated'

                record = (
                    settle_date,
                    row.get('ticker', ''),
                    row.get('underlying', 'QQQ'),
                    float(row.get('strike', 0)),
                    row.get('expiry', ''),
                    row.get('option_type', 'C'),

                    # Price data
                    float(row.get('PX_SETTLE', row.get('px_settle', 0)) or 0),
                    float(row.get('PX_LAST', row.get('px_last', 0)) or 0),
                    float(row.get('PX_BID', row.get('px_bid', 0)) or 0),
                    float(row.get('PX_ASK', row.get('px_ask', 0)) or 0),
                    int(row.get('VOLUME', row.get('volume', 0)) or 0),
                    int(row.get('OPEN_INT', row.get('open_int', 0)) or 0),

                    # Greeks
                    float(row.get('DELTA', row.get('delta')) or 0) if not pd.isna(row.get('DELTA', row.get('delta'))) else None,
                    float(row.get('GAMMA', row.get('gamma')) or 0) if not pd.isna(row.get('GAMMA', row.get('gamma'))) else None,
                    float(row.get('THETA', row.get('theta')) or 0) if not pd.isna(row.get('THETA', row.get('theta'))) else None,
                    float(row.get('VEGA', row.get('vega')) or 0) if not pd.isna(row.get('VEGA', row.get('vega'))) else None,
                    float(row.get('RHO', row.get('rho')) or 0) if not pd.isna(row.get('RHO', row.get('rho'))) else None,

                    # Additional fields
                    float(row.get('IVOL_MID', row.get('ivol_mid', 0)) or 0),
                    float(row.get('OPT_UNDL_PX', row.get('opt_undl_px', row.get('spot_price', 0))) or 0),
                    float(row.get('MONEYNESS', row.get('moneyness', 0)) or 0),
                    float(row.get('TIME_TO_EXPIRY', row.get('time_to_expiry', 0)) or 0),

                    # Metadata
                    datetime.now().isoformat(),
                    data_source
                )

                records.append(record)

            # Insert records
            cursor.executemany("""
                INSERT OR IGNORE INTO eod_greeks (
                    settle_date, ticker, underlying, strike, expiry, option_type,
                    px_settle, px_last, px_bid, px_ask, volume, open_int,
                    delta, gamma, theta, vega, rho,
                    ivol_mid, opt_undl_px, moneyness, time_to_expiry,
                    fetch_time, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)

            inserted = cursor.rowcount

            # Update daily summary
            self._update_daily_summary(cursor, settle_date, len(records))

            conn.commit()
            logger.info(f"Inserted {inserted} records for {settle_date}")
            return inserted

        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            conn.rollback()
            return 0

        finally:
            conn.close()

    def _update_daily_summary(self, cursor, date: str, total_records: int):
        """Update daily summary statistics"""
        # Get statistics
        cursor.execute("""
            SELECT
                COUNT(DISTINCT ticker) as unique_tickers,
                COUNT(DISTINCT underlying) as unique_underlyings,
                SUM(CASE WHEN delta IS NOT NULL THEN 1 ELSE 0 END) as greeks_available,
                SUM(CASE WHEN data_source = 'calculated' THEN 1 ELSE 0 END) as greeks_calculated
            FROM eod_greeks
            WHERE settle_date = ?
        """, (date,))

        stats = cursor.fetchone()

        # Insert or update summary
        cursor.execute("""
            INSERT OR REPLACE INTO daily_summary
            (date, total_records, unique_tickers, unique_underlyings,
             greeks_available, greeks_calculated, fetch_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (date, total_records, stats[0], stats[1], stats[2], stats[3],
              datetime.now().isoformat()))

    def query_greeks(self,
                    start_date: str,
                    end_date: Optional[str] = None,
                    underlying: str = "QQQ",
                    strike: Optional[float] = None,
                    expiry: Optional[str] = None) -> pd.DataFrame:
        """
        Query historical Greeks data

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (default: start_date)
            underlying: Underlying ticker
            strike: Option strike (optional)
            expiry: Option expiry (optional)

        Returns:
            DataFrame with query results
        """
        if end_date is None:
            end_date = start_date

        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT * FROM eod_greeks
            WHERE settle_date BETWEEN ? AND ?
            AND underlying = ?
        """
        params = [start_date, end_date, underlying]

        if strike:
            query += " AND strike = ?"
            params.append(strike)

        if expiry:
            query += " AND expiry = ?"
            params.append(expiry)

        query += " ORDER BY settle_date, expiry, strike, option_type"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def get_latest_greeks(self,
                         underlying: str = "QQQ",
                         num_days: int = 1) -> pd.DataFrame:
        """Get most recent EOD Greeks"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT * FROM eod_greeks
            WHERE underlying = ?
            AND settle_date >= date('now', ? || ' days')
            ORDER BY settle_date DESC, expiry, strike, option_type
        """

        df = pd.read_sql_query(query, conn, params=[underlying, -num_days])
        conn.close()

        return df

    def get_missing_dates(self,
                         start_date: str,
                         end_date: str) -> List[str]:
        """Get list of missing trading days in date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get existing dates
        cursor.execute("""
            SELECT DISTINCT settle_date
            FROM eod_greeks
            WHERE settle_date BETWEEN ? AND ?
            ORDER BY settle_date
        """, (start_date, end_date))

        existing_dates = set(row[0] for row in cursor.fetchall())
        conn.close()

        # Generate all trading days in range
        trading_days = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        while current <= end:
            # Skip weekends
            if current.weekday() < 5:
                date_str = current.strftime("%Y-%m-%d")
                if date_str not in existing_dates:
                    trading_days.append(date_str)
            current += timedelta(days=1)

        return trading_days

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total records
        cursor.execute("SELECT COUNT(*) FROM eod_greeks")
        stats['total_records'] = cursor.fetchone()[0]

        # Date range
        cursor.execute("SELECT MIN(settle_date), MAX(settle_date) FROM eod_greeks")
        min_date, max_date = cursor.fetchone()
        stats['date_range'] = f"{min_date} to {max_date}" if min_date else "No data"

        # Unique dates
        cursor.execute("SELECT COUNT(DISTINCT settle_date) FROM eod_greeks")
        stats['unique_dates'] = cursor.fetchone()[0]

        # Greeks availability
        cursor.execute("""
            SELECT
                SUM(CASE WHEN delta IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pct_with_greeks
            FROM eod_greeks
        """)
        stats['greeks_coverage'] = f"{cursor.fetchone()[0]:.1f}%" if stats['total_records'] > 0 else "0%"

        # Data sources
        cursor.execute("""
            SELECT data_source, COUNT(*) as cnt
            FROM eod_greeks
            GROUP BY data_source
        """)
        stats['data_sources'] = dict(cursor.fetchall())

        conn.close()

        return stats

    def export_to_csv(self,
                     output_path: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None):
        """Export database to CSV file"""
        conn = sqlite3.connect(self.db_path)

        if start_date and end_date:
            query = """
                SELECT * FROM eod_greeks
                WHERE settle_date BETWEEN ? AND ?
                ORDER BY settle_date, underlying, expiry, strike, option_type
            """
            df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        else:
            query = """
                SELECT * FROM eod_greeks
                ORDER BY settle_date, underlying, expiry, strike, option_type
            """
            df = pd.read_sql_query(query, conn)

        conn.close()

        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} records to {output_path}")


def demo_database():
    """Demonstrate database functionality"""
    print("=" * 60)
    print("📊 Greeks Database Demo")
    print("=" * 60)

    db = GreeksDatabase()

    # Get database stats
    stats = db.get_database_stats()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Get latest Greeks
    latest = db.get_latest_greeks(num_days=7)
    if not latest.empty:
        print(f"\nLatest Greeks ({len(latest)} records)")
        print(latest[['settle_date', 'ticker', 'strike', 'delta', 'gamma', 'theta']].head())


if __name__ == "__main__":
    demo_database()