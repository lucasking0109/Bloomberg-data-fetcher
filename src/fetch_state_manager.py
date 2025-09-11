#!/usr/bin/env python3
"""
Fetch State Manager
Handles state persistence and recovery for resilient data fetching
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetchStateManager:
    """Manages fetch state for recovery and progress tracking"""
    
    def __init__(self, state_dir: str = "logs"):
        """
        Initialize state manager
        
        Args:
            state_dir: Directory for state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        
        self.state_file = self.state_dir / "fetch_state.json"
        self.progress_db = self.state_dir / "fetch_progress.db"
        
        self.session_id = None
        self.state = self._load_or_create_state()
        self._init_progress_db()
    
    def _load_or_create_state(self) -> Dict:
        """Load existing state or create new one"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info(f"Loaded existing state from session {state.get('session_id')}")
                    return state
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")
        
        return self._create_new_state()
    
    def _create_new_state(self) -> Dict:
        """Create a new state structure"""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return {
            'session_id': self.session_id,
            'status': 'initialized',
            'start_time': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'total_tickers': 0,
            'completed': [],
            'failed': {},
            'pending': [],
            'in_progress': None,
            'statistics': {
                'records_fetched': 0,
                'api_points_used': 0,
                'errors_encountered': 0,
                'retries_attempted': 0,
                'time_elapsed': 0
            },
            'checkpoints': []
        }
    
    def _init_progress_db(self):
        """Initialize SQLite database for detailed progress tracking"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        # Create fetch history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fetch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                ticker TEXT,
                ticker_type TEXT,  -- 'index' or 'constituent'
                status TEXT,       -- 'completed', 'failed', 'partial'
                start_time DATETIME,
                end_time DATETIME,
                records_fetched INTEGER,
                api_points_used INTEGER,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                UNIQUE(session_id, ticker)
            )
        """)
        
        # Create error log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                ticker TEXT,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT
            )
        """)
        
        # Create checkpoint table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                checkpoint_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_count INTEGER,
                failed_count INTEGER,
                pending_count INTEGER,
                total_records INTEGER,
                api_usage INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def initialize_tickers(self, tickers: List[str]):
        """
        Initialize the list of tickers to fetch
        
        Args:
            tickers: List of ticker symbols
        """
        self.state['total_tickers'] = len(tickers)
        self.state['pending'] = tickers.copy()
        self.state['completed'] = []
        self.state['failed'] = {}
        self.state['status'] = 'ready'
        self.save_state()
        
        logger.info(f"Initialized {len(tickers)} tickers for fetching")
    
    def start_ticker(self, ticker: str) -> bool:
        """
        Mark a ticker as in progress
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            True if ticker was started, False if already completed
        """
        if ticker in self.state['completed']:
            logger.info(f"Ticker {ticker} already completed, skipping")
            return False
        
        if ticker in self.state['pending']:
            self.state['pending'].remove(ticker)
        
        self.state['in_progress'] = ticker
        self.state['status'] = 'fetching'
        self.state['last_update'] = datetime.now().isoformat()
        self.save_state()
        
        # Log to database
        self._log_ticker_start(ticker)
        
        return True
    
    def complete_ticker(self, ticker: str, records: int = 0, api_points: int = 0):
        """
        Mark a ticker as successfully completed
        
        Args:
            ticker: Ticker symbol
            records: Number of records fetched
            api_points: API points used
        """
        if ticker not in self.state['completed']:
            self.state['completed'].append(ticker)
        
        if ticker in self.state['failed']:
            del self.state['failed'][ticker]
        
        if self.state['in_progress'] == ticker:
            self.state['in_progress'] = None
        
        # Update statistics
        self.state['statistics']['records_fetched'] += records
        self.state['statistics']['api_points_used'] += api_points
        self.state['last_update'] = datetime.now().isoformat()
        
        self.save_state()
        self._log_ticker_complete(ticker, records, api_points)
        
        logger.info(f"Completed {ticker}: {records} records, {api_points} API points")
    
    def fail_ticker(self, ticker: str, error: str, retry_count: int = 0):
        """
        Mark a ticker as failed
        
        Args:
            ticker: Ticker symbol
            error: Error message
            retry_count: Number of retries attempted
        """
        self.state['failed'][ticker] = {
            'error': error,
            'retry_count': retry_count,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.state['in_progress'] == ticker:
            self.state['in_progress'] = None
        
        self.state['statistics']['errors_encountered'] += 1
        self.state['statistics']['retries_attempted'] += retry_count
        self.state['last_update'] = datetime.now().isoformat()
        
        self.save_state()
        self._log_ticker_failure(ticker, error)
        
        logger.error(f"Failed {ticker}: {error}")
    
    def get_next_ticker(self) -> Optional[str]:
        """
        Get the next ticker to process
        
        Returns:
            Next ticker symbol or None if all done
        """
        if self.state['pending']:
            return self.state['pending'][0]
        return None
    
    def get_resume_point(self) -> Optional[str]:
        """
        Get the ticker to resume from after interruption
        
        Returns:
            Ticker to resume from or None
        """
        # First check if there was a ticker in progress
        if self.state['in_progress']:
            return self.state['in_progress']
        
        # Otherwise get the next pending ticker
        return self.get_next_ticker()
    
    def should_retry_failed(self, max_retries: int = 3) -> List[str]:
        """
        Get list of failed tickers that should be retried
        
        Args:
            max_retries: Maximum retry attempts
            
        Returns:
            List of tickers to retry
        """
        retry_list = []
        for ticker, info in self.state['failed'].items():
            if info.get('retry_count', 0) < max_retries:
                retry_list.append(ticker)
        return retry_list
    
    def save_checkpoint(self):
        """Save a checkpoint of current progress"""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'completed': len(self.state['completed']),
            'failed': len(self.state['failed']),
            'pending': len(self.state['pending']),
            'records': self.state['statistics']['records_fetched'],
            'api_usage': self.state['statistics']['api_points_used']
        }
        
        self.state['checkpoints'].append(checkpoint)
        self.save_state()
        
        # Also save to database
        self._save_checkpoint_to_db(checkpoint)
        
        logger.info(f"Checkpoint saved: {checkpoint}")
    
    def save_state(self):
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_progress_summary(self) -> Dict:
        """
        Get a summary of current progress
        
        Returns:
            Dictionary with progress information
        """
        total = self.state['total_tickers']
        completed = len(self.state['completed'])
        failed = len(self.state['failed'])
        pending = len(self.state['pending'])
        
        progress_pct = (completed / total * 100) if total > 0 else 0
        
        return {
            'session_id': self.state['session_id'],
            'status': self.state['status'],
            'progress_percentage': progress_pct,
            'total_tickers': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'in_progress': self.state['in_progress'],
            'records_fetched': self.state['statistics']['records_fetched'],
            'api_points_used': self.state['statistics']['api_points_used'],
            'errors': self.state['statistics']['errors_encountered'],
            'last_update': self.state['last_update']
        }
    
    def reset_state(self):
        """Reset state for a fresh start"""
        self.state = self._create_new_state()
        self.save_state()
        logger.info("State reset for new session")
    
    def export_failed_tickers(self, filepath: str = None) -> str:
        """
        Export list of failed tickers to file
        
        Args:
            filepath: Output file path
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.state_dir / f"failed_tickers_{self.state['session_id']}.json"
        
        failed_data = {
            'session_id': self.state['session_id'],
            'timestamp': datetime.now().isoformat(),
            'failed_tickers': self.state['failed']
        }
        
        with open(filepath, 'w') as f:
            json.dump(failed_data, f, indent=2)
        
        logger.info(f"Exported failed tickers to {filepath}")
        return str(filepath)
    
    # Database helper methods
    def _log_ticker_start(self, ticker: str):
        """Log ticker start to database"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO fetch_history 
            (session_id, ticker, status, start_time)
            VALUES (?, ?, 'in_progress', ?)
        """, (self.state['session_id'], ticker, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _log_ticker_complete(self, ticker: str, records: int, api_points: int):
        """Log ticker completion to database"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fetch_history 
            SET status = 'completed',
                end_time = ?,
                records_fetched = ?,
                api_points_used = ?
            WHERE session_id = ? AND ticker = ?
        """, (datetime.now(), records, api_points, self.state['session_id'], ticker))
        
        conn.commit()
        conn.close()
    
    def _log_ticker_failure(self, ticker: str, error: str):
        """Log ticker failure to database"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        # Update fetch history
        cursor.execute("""
            UPDATE fetch_history 
            SET status = 'failed',
                end_time = ?,
                error_message = ?
            WHERE session_id = ? AND ticker = ?
        """, (datetime.now(), error, self.state['session_id'], ticker))
        
        # Add to error log
        cursor.execute("""
            INSERT INTO error_log 
            (session_id, ticker, error_type, error_message)
            VALUES (?, ?, 'fetch_error', ?)
        """, (self.state['session_id'], ticker, error))
        
        conn.commit()
        conn.close()
    
    def _save_checkpoint_to_db(self, checkpoint: Dict):
        """Save checkpoint to database"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO checkpoints 
            (session_id, completed_count, failed_count, pending_count, 
             total_records, api_usage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.state['session_id'],
            checkpoint['completed'],
            checkpoint['failed'],
            checkpoint['pending'],
            checkpoint['records'],
            checkpoint['api_usage']
        ))
        
        conn.commit()
        conn.close()
    
    def get_session_report(self) -> Dict:
        """Generate a detailed session report"""
        conn = sqlite3.connect(self.progress_db)
        cursor = conn.cursor()
        
        # Get fetch statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(records_fetched) as total_records,
                SUM(api_points_used) as total_api_points
            FROM fetch_history
            WHERE session_id = ?
        """, (self.state['session_id'],))
        
        stats = cursor.fetchone()
        
        # Get error summary
        cursor.execute("""
            SELECT ticker, error_message, COUNT(*) as error_count
            FROM error_log
            WHERE session_id = ?
            GROUP BY ticker, error_message
        """, (self.state['session_id'],))
        
        errors = cursor.fetchall()
        
        conn.close()
        
        return {
            'session_id': self.state['session_id'],
            'start_time': self.state['start_time'],
            'last_update': self.state['last_update'],
            'statistics': {
                'total_attempts': stats[0] if stats else 0,
                'completed': stats[1] if stats else 0,
                'failed': stats[2] if stats else 0,
                'total_records': stats[3] if stats else 0,
                'total_api_points': stats[4] if stats else 0
            },
            'errors': [{'ticker': e[0], 'message': e[1], 'count': e[2]} for e in errors]
        }


if __name__ == "__main__":
    # Test the state manager
    manager = FetchStateManager()
    
    # Test initialization
    test_tickers = ['QQQ', 'AAPL', 'MSFT', 'NVDA']
    manager.initialize_tickers(test_tickers)
    
    # Test progress tracking
    print("\nInitial state:")
    print(json.dumps(manager.get_progress_summary(), indent=2))
    
    # Simulate processing
    ticker = manager.get_next_ticker()
    if ticker:
        manager.start_ticker(ticker)
        manager.complete_ticker(ticker, records=100, api_points=1400)
    
    print("\nAfter processing one ticker:")
    print(json.dumps(manager.get_progress_summary(), indent=2))
    
    # Save checkpoint
    manager.save_checkpoint()
    
    print("\nSession report:")
    print(json.dumps(manager.get_session_report(), indent=2))