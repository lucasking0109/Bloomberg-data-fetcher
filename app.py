#!/usr/bin/env python3
"""
Bloomberg QQQ Fetcher - Easy Web Interface
A simple, user-friendly dashboard for fetching Bloomberg data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import sys
import os
import json
import subprocess
import sqlite3
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database_manager import DatabaseManager
from src.usage_monitor import UsageMonitor

# Page configuration
st.set_page_config(
    page_title="Bloomberg QQQ Fetcher",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        margin: 5px 0;
    }
    .success-button > button {
        background-color: #28a745;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

class BloombergFetcherApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.monitor = UsageMonitor({})

    def get_database_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect('./data/bloomberg_options.db')

            # Count total records
            cursor = conn.execute("SELECT COUNT(*) FROM options_data")
            total_records = cursor.fetchone()[0]

            # Get unique dates
            cursor = conn.execute("SELECT COUNT(DISTINCT date(fetch_time)) FROM options_data")
            unique_days = cursor.fetchone()[0] if cursor.fetchone() else 0

            # Get latest fetch time
            cursor = conn.execute("SELECT MAX(fetch_time) FROM options_data")
            latest_fetch = cursor.fetchone()[0]

            # Get unique tickers
            cursor = conn.execute("SELECT COUNT(DISTINCT underlying) FROM options_data")
            unique_tickers = cursor.fetchone()[0] if cursor.fetchone() else 0

            conn.close()

            return {
                'total_records': total_records,
                'unique_days': unique_days,
                'latest_fetch': latest_fetch,
                'unique_tickers': unique_tickers
            }
        except Exception as e:
            return {'total_records': 0, 'unique_days': 0, 'latest_fetch': None, 'unique_tickers': 0}

    def render_dashboard(self):
        """Main dashboard"""
        st.title("📊 Bloomberg QQQ Options Fetcher")
        st.markdown("---")

        # Database status
        st.subheader("💾 Database Status")
        stats = self.get_database_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Records", f"{stats['total_records']:,}")

        with col2:
            st.metric("Unique Days", stats['unique_days'])

        with col3:
            st.metric("Unique Tickers", stats['unique_tickers'])

        with col4:
            if stats['latest_fetch']:
                st.metric("Latest Fetch", stats['latest_fetch'][:10])  # Date only
            else:
                st.metric("Latest Fetch", "None")

        st.markdown("---")

        # Fetch controls
        st.subheader("🚀 Data Fetching")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### QQQ Historical Options")
            days = st.slider("Days of history", 1, 90, 30)

            if st.button("📈 Fetch QQQ Historical Data", key="qqq"):
                with st.spinner("Starting QQQ fetch..."):
                    command = f"python scripts/historical_fetch.py --days {days}"
                    self.run_command(command)

        with col2:
            st.markdown("### Individual Stock Options")
            option = st.selectbox("Choose option:", [
                "Single Stock", "Top 5 Stocks", "Top 10 Stocks", "All 20 Stocks"
            ])

            if option == "Single Stock":
                ticker = st.text_input("Enter ticker (e.g., AAPL):", "AAPL")
                if st.button("📊 Fetch Single Stock", key="single"):
                    command = f"python scripts/constituents_fetch.py --ticker {ticker}"
                    self.run_command(command)
            else:
                top_n = {"Top 5 Stocks": 5, "Top 10 Stocks": 10, "All 20 Stocks": None}[option]
                if st.button(f"📊 Fetch {option}", key="multi"):
                    if top_n:
                        command = f"python scripts/constituents_fetch.py --top {top_n}"
                    else:
                        command = "python scripts/constituents_fetch.py --all"
                    self.run_command(command)

        # Data viewer
        if stats['total_records'] > 0:
            st.markdown("---")
            st.subheader("📋 Recent Data Preview")

            try:
                conn = sqlite3.connect('./data/bloomberg_options.db')
                df = pd.read_sql_query("""
                    SELECT underlying, strike, expiry, option_type,
                           px_last, px_bid, px_ask, volume, open_int,
                           date(fetch_time) as fetch_date
                    FROM options_data
                    ORDER BY fetch_time DESC
                    LIMIT 100
                """, conn)
                conn.close()

                st.dataframe(df, use_container_width=True)

                # Simple chart
                if not df.empty and 'px_last' in df.columns:
                    fig = px.histogram(df, x='underlying', y='px_last',
                                     title="Average Option Prices by Ticker")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error loading data: {e}")

    def run_command(self, command):
        """Run a command and show results"""
        try:
            st.info(f"Running: {command}")
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                st.success("✅ Command completed successfully!")
                if result.stdout:
                    with st.expander("📄 Output"):
                        st.text(result.stdout)
            else:
                st.error("❌ Command failed!")
                if result.stderr:
                    with st.expander("📄 Error Details"):
                        st.text(result.stderr)

        except subprocess.TimeoutExpired:
            st.warning("⏱️ Command timed out (5 minutes limit)")
        except Exception as e:
            st.error(f"❌ Error running command: {e}")

def main():
    """Main app entry point"""
    app = BloombergFetcherApp()
    app.render_dashboard()

if __name__ == "__main__":
    main()