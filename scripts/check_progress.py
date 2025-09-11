#!/usr/bin/env python3
"""
Check Progress Script
Monitor fetching progress and database status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetch_state_manager import FetchStateManager
from src.database_manager import DatabaseManager
from src.usage_monitor import UsageMonitor
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import argparse


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def check_fetch_progress():
    """Check current fetch progress from state manager"""
    print_section("FETCH PROGRESS")
    
    state_manager = FetchStateManager()
    progress = state_manager.get_progress_summary()
    
    if progress['session_id']:
        print(f"Session ID: {progress['session_id']}")
        print(f"Status: {progress['status']}")
        print(f"Last Update: {progress['last_update']}")
        print("")
        
        # Progress bar
        total = progress['total_tickers']
        completed = progress['completed']
        pct = progress['progress_percentage']
        
        if total > 0:
            bar_length = 40
            filled = int(bar_length * pct / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"Progress: [{bar}] {pct:.1f}%")
            print(f"Tickers: {completed}/{total} completed")
            
            if progress['failed'] > 0:
                print(f"⚠️ Failed: {progress['failed']} tickers")
            
            if progress['pending'] > 0:
                print(f"📋 Pending: {progress['pending']} tickers")
            
            if progress['in_progress']:
                print(f"🔄 Currently processing: {progress['in_progress']}")
        else:
            print("No active fetch session")
        
        print(f"\nRecords fetched: {progress['records_fetched']:,}")
        print(f"API points used: {progress['api_points_used']:,}")
        print(f"Errors encountered: {progress['errors']}")
        
        # Show failed tickers if any
        if state_manager.state.get('failed'):
            print("\n❌ Failed Tickers:")
            for ticker, info in state_manager.state['failed'].items():
                print(f"  - {ticker}: {info.get('error', 'Unknown error')}")
                print(f"    Retries: {info.get('retry_count', 0)}")
    else:
        print("No active fetch session found")


def check_database_status():
    """Check database status and statistics"""
    print_section("DATABASE STATUS")
    
    db = DatabaseManager()
    stats = db.get_summary_stats()
    
    print(f"Total records: {stats['total_records']:,}")
    print(f"Unique dates: {stats['unique_dates']}")
    print(f"Date range: {stats['date_range']}")
    print(f"Unique expiries: {stats['unique_expiries']}")
    print(f"Unique strikes: {stats['unique_strikes']}")
    
    # Check constituent tables
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Check equity data
    cursor.execute("SELECT COUNT(*) FROM equity_data")
    equity_count = cursor.fetchone()[0]
    print(f"\nEquity records: {equity_count:,}")
    
    # Check constituent options
    cursor.execute("SELECT COUNT(*) FROM constituent_options")
    const_options_count = cursor.fetchone()[0]
    print(f"Constituent options: {const_options_count:,}")
    
    # Get recent fetches
    cursor.execute("""
        SELECT fetch_date, COUNT(*) as records
        FROM options_data
        GROUP BY fetch_date
        ORDER BY fetch_date DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()
    
    if recent:
        print("\nRecent Fetches:")
        for date, count in recent:
            print(f"  {date}: {count:,} records")
    
    # Check for missing OPEN_INT
    cursor.execute("""
        SELECT COUNT(*) 
        FROM options_data 
        WHERE open_interest IS NULL
    """)
    missing_oi = cursor.fetchone()[0]
    
    if missing_oi > 0:
        print(f"\n⚠️ Records missing Open Interest: {missing_oi}")
    else:
        print("\n✅ All records have Open Interest data")
    
    conn.close()


def check_api_usage():
    """Check API usage statistics"""
    print_section("API USAGE")
    
    monitor = UsageMonitor()
    
    daily_used = monitor.get_daily_usage()
    daily_limit = monitor.config.get('daily_limit', 50000)
    daily_remaining = daily_limit - daily_used
    daily_pct = (daily_used / daily_limit * 100) if daily_limit > 0 else 0
    
    monthly_used = monitor.get_monthly_usage()
    monthly_limit = monitor.config.get('monthly_limit', 500000)
    monthly_remaining = monthly_limit - monthly_used
    monthly_pct = (monthly_used / monthly_limit * 100) if monthly_limit > 0 else 0
    
    print(f"Daily Usage:")
    print(f"  Used: {daily_used:,} / {daily_limit:,} ({daily_pct:.1f}%)")
    print(f"  Remaining: {daily_remaining:,}")
    
    if daily_pct > 80:
        print("  ⚠️ Warning: Approaching daily limit!")
    
    print(f"\nMonthly Usage:")
    print(f"  Used: {monthly_used:,} / {monthly_limit:,} ({monthly_pct:.1f}%)")
    print(f"  Remaining: {monthly_remaining:,}")
    
    if monthly_pct > 80:
        print("  ⚠️ Warning: Approaching monthly limit!")
    
    # Estimate what can be fetched with remaining budget
    print("\nEstimated Coverage with Remaining Budget:")
    
    # Assume average of 1500 points per ticker (options + equity)
    avg_points_per_ticker = 1500
    tickers_possible_daily = daily_remaining // avg_points_per_ticker
    
    print(f"  Daily: ~{tickers_possible_daily} tickers")
    print(f"  Monthly: ~{monthly_remaining // avg_points_per_ticker} tickers")


def check_logs():
    """Check recent log entries for errors"""
    print_section("RECENT ERRORS")
    
    log_dir = Path("logs")
    
    # Check main log file
    log_file = log_dir / "fetcher.log"
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Find recent errors
        errors = [line for line in lines[-100:] if 'ERROR' in line]
        
        if errors:
            print(f"Found {len(errors)} recent errors:")
            for error in errors[-5:]:  # Show last 5 errors
                print(f"  {error.strip()}")
        else:
            print("✅ No recent errors found")
    else:
        print("Log file not found")
    
    # Check error log if exists
    error_file = log_dir / "errors.log"
    if error_file.exists():
        with open(error_file, 'r') as f:
            error_lines = f.readlines()
        
        if error_lines:
            print(f"\n⚠️ Error log contains {len(error_lines)} entries")
            print("Latest error:")
            print(f"  {error_lines[-1].strip()}")


def show_recommendations():
    """Show recommendations based on current status"""
    print_section("RECOMMENDATIONS")
    
    state_manager = FetchStateManager()
    monitor = UsageMonitor()
    
    recommendations = []
    
    # Check if there's a resumable session
    if state_manager.state.get('pending'):
        recommendations.append("📌 Resume incomplete fetch: python scripts/robust_fetch.py --resume")
    
    # Check if failed tickers need retry
    if state_manager.state.get('failed'):
        failed_count = len(state_manager.state['failed'])
        recommendations.append(f"🔄 Retry {failed_count} failed tickers")
    
    # Check API usage
    daily_remaining = monitor.get_remaining_daily()
    if daily_remaining < 10000:
        recommendations.append("⚠️ Low daily API budget - consider waiting until tomorrow")
    
    # Check database
    db = DatabaseManager()
    stats = db.get_summary_stats()
    
    if stats['total_records'] == 0:
        recommendations.append("💡 Database is empty - run initial fetch")
    
    # Check time of day
    now = datetime.now()
    if now.hour < 16:  # Before 4 PM
        recommendations.append("⏰ Consider running after market close (4:30 PM ET)")
    
    if recommendations:
        for rec in recommendations:
            print(f"• {rec}")
    else:
        print("✅ System ready for fetching")


def export_status_report(output_file: str = None):
    """Export complete status report to file"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"logs/status_report_{timestamp}.json"
    
    state_manager = FetchStateManager()
    db = DatabaseManager()
    monitor = UsageMonitor()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'fetch_progress': state_manager.get_progress_summary(),
        'database_stats': db.get_summary_stats(),
        'api_usage': {
            'daily_used': monitor.get_daily_usage(),
            'daily_limit': monitor.config.get('daily_limit', 50000),
            'monthly_used': monitor.get_monthly_usage(),
            'monthly_limit': monitor.config.get('monthly_limit', 500000)
        },
        'session_report': state_manager.get_session_report()
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Status report exported to: {output_file}")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Check Bloomberg fetcher progress')
    
    parser.add_argument('--progress', action='store_true',
                       help='Show only fetch progress')
    parser.add_argument('--database', action='store_true',
                       help='Show only database status')
    parser.add_argument('--usage', action='store_true',
                       help='Show only API usage')
    parser.add_argument('--logs', action='store_true',
                       help='Show recent log entries')
    parser.add_argument('--export', action='store_true',
                       help='Export status report to file')
    parser.add_argument('--all', action='store_true',
                       help='Show all information (default)')
    
    args = parser.parse_args()
    
    # Default to showing all if no specific flags
    if not any([args.progress, args.database, args.usage, args.logs]):
        args.all = True
    
    print("\n" + "="*60)
    print(" BLOOMBERG FETCHER STATUS CHECK")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.all or args.progress:
            check_fetch_progress()
        
        if args.all or args.database:
            check_database_status()
        
        if args.all or args.usage:
            check_api_usage()
        
        if args.all or args.logs:
            check_logs()
        
        if args.all:
            show_recommendations()
        
        if args.export:
            export_status_report()
        
        print("\n" + "="*60)
        print(" END OF STATUS CHECK")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error checking status: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)