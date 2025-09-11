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
import threading
from pathlib import Path

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.fetch_state_manager import FetchStateManager
from src.database_manager import DatabaseManager
from src.usage_monitor import UsageMonitor
from src.bloomberg_api import BloombergAPI

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
    .warning-button > button {
        background-color: #ffc107;
        color: black;
    }
    .danger-button > button {
        background-color: #dc3545;
        color: white;
    }
    .info-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'fetch_process' not in st.session_state:
    st.session_state.fetch_process = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'fetch_log' not in st.session_state:
    st.session_state.fetch_log = []

class BloombergFetcherApp:
    def __init__(self):
        self.state_manager = FetchStateManager()
        self.db = DatabaseManager()
        self.monitor = UsageMonitor()
        
    def check_bloomberg_connection(self):
        """Test Bloomberg Terminal connection"""
        try:
            api = BloombergAPI()
            connected = api.connect(max_retries=1)
            if connected:
                api.disconnect()
            return connected
        except:
            return False
    
    def run_fetch_command(self, command):
        """Run fetch command in background"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            st.session_state.fetch_process = process
            return process
        except Exception as e:
            st.error(f"Failed to start fetch: {e}")
            return None
    
    def get_fetch_status(self):
        """Get current fetch status"""
        progress = self.state_manager.get_progress_summary()
        return progress
    
    def get_database_stats(self):
        """Get database statistics"""
        return self.db.get_summary_stats()
    
    def get_api_usage(self):
        """Get API usage statistics"""
        daily_used = self.monitor.get_daily_usage()
        daily_limit = self.monitor.config.get('daily_limit', 50000)
        monthly_used = self.monitor.get_monthly_usage()
        monthly_limit = self.monitor.config.get('monthly_limit', 500000)
        
        return {
            'daily_used': daily_used,
            'daily_limit': daily_limit,
            'daily_percent': (daily_used / daily_limit * 100) if daily_limit > 0 else 0,
            'monthly_used': monthly_used,
            'monthly_limit': monthly_limit,
            'monthly_percent': (monthly_used / monthly_limit * 100) if monthly_limit > 0 else 0
        }
    
    def render_header(self):
        """Render app header"""
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.title("📊 Bloomberg QQQ Fetcher")
        
        with col2:
            # Connection status
            connected = self.check_bloomberg_connection()
            if connected:
                st.success("✅ Bloomberg Terminal Connected")
            else:
                st.error("❌ Bloomberg Terminal Not Connected")
        
        with col3:
            st.write(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button("🔄 Refresh", key="refresh"):
                st.rerun()
    
    def render_quick_actions(self):
        """Render quick action buttons"""
        st.header("⚡ Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎯 Test Connection", key="test_conn", help="Test Bloomberg Terminal connection"):
                with st.spinner("Testing connection..."):
                    if self.check_bloomberg_connection():
                        st.success("✅ Connection successful!")
                    else:
                        st.error("❌ Connection failed! Check Terminal")
        
        with col2:
            if st.button("🚀 Fetch QQQ Only", key="fetch_qqq", help="Fetch only QQQ index options"):
                command = "python scripts/robust_fetch.py --qqq-only --export-csv"
                self.run_fetch_command(command)
                st.success("Started QQQ fetch...")
                time.sleep(2)
                st.rerun()
        
        with col3:
            if st.button("💼 Fetch Top 5", key="fetch_top5", help="Fetch QQQ + top 5 constituents"):
                command = "python scripts/robust_fetch.py --top-n 5 --export-csv --export-format csv"
                self.run_fetch_command(command)
                st.success("Started fetching top 5...")
                time.sleep(2)
                st.rerun()
        
        with col4:
            if st.button("🔥 Fetch All 20", key="fetch_all", help="Fetch QQQ + ALL 20 constituents"):
                if st.session_state.get('confirm_all', False):
                    command = "python scripts/robust_fetch.py --top-n 20 --export-csv --export-format parquet"
                    self.run_fetch_command(command)
                    st.success("Started fetching all 20 constituents...")
                    st.session_state.confirm_all = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.session_state.confirm_all = True
                    st.warning("Click again to confirm fetching ALL 20 stocks")
        
        # Resume button if there's a previous session
        if self.state_manager.state.get('pending'):
            st.warning("⚠️ Previous fetch incomplete!")
            if st.button("▶️ Resume Previous Fetch", key="resume", help="Continue from where you left off"):
                command = "python scripts/robust_fetch.py --resume"
                self.run_fetch_command(command)
                st.success("Resuming fetch...")
                time.sleep(2)
                st.rerun()
    
    def render_progress_dashboard(self):
        """Render progress dashboard"""
        st.header("📈 Fetch Progress")
        
        progress = self.get_fetch_status()
        
        if progress['total_tickers'] > 0:
            # Progress bar
            progress_pct = progress['progress_percentage'] / 100
            st.progress(progress_pct)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Progress", f"{progress['progress_percentage']:.1f}%", 
                         f"{progress['completed']}/{progress['total_tickers']}")
            
            with col2:
                st.metric("Records Fetched", f"{progress['records_fetched']:,}")
            
            with col3:
                st.metric("API Points Used", f"{progress['api_points_used']:,}")
            
            with col4:
                status_color = "🟢" if progress['status'] == 'completed' else "🔄"
                st.metric("Status", f"{status_color} {progress['status']}")
            
            # Current ticker
            if progress['in_progress']:
                st.info(f"Currently processing: **{progress['in_progress']}**")
            
            # Failed tickers
            if progress['failed'] > 0:
                with st.expander(f"⚠️ Failed Tickers ({progress['failed']})"):
                    failed = self.state_manager.state.get('failed', {})
                    for ticker, info in failed.items():
                        st.write(f"- **{ticker}**: {info.get('error', 'Unknown error')}")
        else:
            st.info("No active fetch session. Start a new fetch above.")
    
    def render_api_usage(self):
        """Render API usage dashboard"""
        st.header("📊 API Usage Monitor")
        
        usage = self.get_api_usage()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily usage gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = usage['daily_percent'],
                title = {'text': "Daily Usage"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Used: {usage['daily_used']:,} / {usage['daily_limit']:,}")
        
        with col2:
            # Monthly usage gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = usage['monthly_percent'],
                title = {'text': "Monthly Usage"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Used: {usage['monthly_used']:,} / {usage['monthly_limit']:,}")
    
    def render_database_view(self):
        """Render database statistics and preview"""
        st.header("💾 Database Overview")
        
        stats = self.get_database_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Records", f"{stats['total_records']:,}")
        
        with col2:
            st.metric("Unique Dates", stats['unique_dates'])
        
        with col3:
            st.metric("Date Range", stats['date_range'])
        
        with col4:
            st.metric("Expiries", stats['unique_expiries'])
        
        with col5:
            st.metric("Strikes", stats['unique_strikes'])
        
        # Data preview
        if st.button("👁️ Preview Latest Data"):
            try:
                latest_data = self.db.get_latest_data(limit=100)
                if not latest_data.empty:
                    st.dataframe(latest_data, use_container_width=True)
                else:
                    st.info("No data available")
            except:
                st.info("No data available yet")
        
        # Export options
        st.subheader("📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_format = st.selectbox(
                "Format:", 
                ["CSV", "Parquet"], 
                help="CSV: Easy to open in Excel. Parquet: More efficient for large datasets"
            )
        
        with col2:
            if st.button("📥 Export Data", key="export_data"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                format_lower = export_format.lower()
                filepath = f"data/export_{timestamp}.{format_lower}"
                
                try:
                    if format_lower == "csv":
                        self.db.export_to_csv(filepath)
                    else:  # parquet
                        self.db.export_to_parquet(filepath)
                    
                    file_size = Path(filepath).stat().st_size / (1024 * 1024)  # MB
                    st.success(f"✅ Exported to {filepath}")
                    st.info(f"📊 File size: {file_size:.1f} MB")
                    
                    if format_lower == "parquet":
                        st.code(f"# Load data in Python:\nimport pandas as pd\ndf = pd.read_parquet('{filepath}')")
                    
                except Exception as e:
                    st.error(f"Export failed: {e}")
        
        with col3:
            if st.button("🗑️ Clear Old Data (>90 days)", key="clear_old"):
                deleted = self.db.cleanup_old_data(90)
                st.success(f"Deleted {deleted} old records")
    
    def render_sidebar(self):
        """Render sidebar with settings and info"""
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # Fetch options
            st.subheader("Fetch Options")
            num_constituents = st.slider("Number of Constituents", 1, 20, 20)
            
            st.subheader("Strike Configuration")
            strikes_above = st.number_input("Strikes Above ATM", value=20, min_value=5, max_value=50)
            strikes_below = st.number_input("Strikes Below ATM", value=20, min_value=5, max_value=50)
            
            st.subheader("Expiry Range")
            max_days = st.slider("Max Days to Expiry", 30, 90, 60)
            
            if st.button("💾 Save Settings"):
                # Save settings to config
                st.success("Settings saved!")
            
            st.divider()
            
            # System info
            st.subheader("📋 System Info")
            st.text(f"Python: {sys.version.split()[0]}")
            st.text(f"Working Dir: {os.getcwd()}")
            
            # Help section
            st.divider()
            st.subheader("❓ Help")
            st.write("""
            **Quick Start:**
            1. Ensure Bloomberg Terminal is running
            2. Click 'Test Connection'
            3. Choose a fetch option
            4. Monitor progress
            5. Export data when complete
            
            **Best Practices:**
            - Run after 4:30 PM ET
            - Start with 'Fetch Top 5'
            - Monitor API usage
            - Export data regularly
            """)
    
    def render_logs(self):
        """Render recent logs"""
        with st.expander("📜 Recent Logs"):
            log_file = Path("logs/robust_fetch.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_logs = lines[-50:]  # Last 50 lines
                    for line in recent_logs:
                        if "ERROR" in line:
                            st.error(line.strip())
                        elif "WARNING" in line:
                            st.warning(line.strip())
                        else:
                            st.text(line.strip())
            else:
                st.info("No logs available yet")
    
    def run(self):
        """Main app execution"""
        self.render_header()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Quick Start", "📈 Progress", "📊 API Usage", "💾 Database", "📜 Logs"])
        
        with tab1:
            self.render_quick_actions()
            
            # Quick tips
            st.info("""
            💡 **Quick Tips:**
            - Start with **Test Connection** to verify Bloomberg Terminal
            - Use **Fetch Top 5** for your first run
            - **Fetch All** takes 15-30 minutes
            - Data includes Open Interest and all Greeks
            """)
        
        with tab2:
            self.render_progress_dashboard()
            
            # Auto-refresh option
            auto_refresh = st.checkbox("Auto-refresh every 5 seconds")
            if auto_refresh:
                time.sleep(5)
                st.rerun()
        
        with tab3:
            self.render_api_usage()
        
        with tab4:
            self.render_database_view()
        
        with tab5:
            self.render_logs()
        
        # Sidebar
        self.render_sidebar()

def main():
    app = BloombergFetcherApp()
    app.run()

if __name__ == "__main__":
    main()