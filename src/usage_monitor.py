#!/usr/bin/env python3
"""
Bloomberg API Usage Monitor
Tracks and manages API usage to stay within limits
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UsageMonitor:
    """Monitor and track Bloomberg API usage"""
    
    def __init__(self, limits: Dict):
        """
        Initialize usage monitor
        
        Args:
            limits: Dictionary with daily_limit and monthly_limit
        """
        self.daily_limit = limits.get('daily_limit', 50000)
        self.monthly_limit = limits.get('monthly_limit', 500000)
        self.usage_file = 'logs/api_usage.json'
        self.usage_data = self._load_usage_data()
        
    def _load_usage_data(self) -> Dict:
        """Load usage data from file"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'daily': {},
            'monthly': {},
            'total': 0
        }
    
    def _save_usage_data(self):
        """Save usage data to file"""
        os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def record_usage(self, count: int):
        """Record API usage"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Update daily usage
        if today not in self.usage_data['daily']:
            self.usage_data['daily'][today] = 0
        self.usage_data['daily'][today] += count
        
        # Update monthly usage
        if month not in self.usage_data['monthly']:
            self.usage_data['monthly'][month] = 0
        self.usage_data['monthly'][month] += count
        
        # Update total
        self.usage_data['total'] += count
        
        # Save
        self._save_usage_data()
        
        # Check limits
        self._check_limits()
    
    def _check_limits(self):
        """Check if approaching limits"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        daily_usage = self.usage_data['daily'].get(today, 0)
        monthly_usage = self.usage_data['monthly'].get(month, 0)
        
        # Check daily limit
        if daily_usage > self.daily_limit * 0.8:
            logger.warning(f"Approaching daily limit: {daily_usage}/{self.daily_limit}")
        if daily_usage > self.daily_limit:
            logger.error(f"Daily limit exceeded: {daily_usage}/{self.daily_limit}")
        
        # Check monthly limit
        if monthly_usage > self.monthly_limit * 0.8:
            logger.warning(f"Approaching monthly limit: {monthly_usage}/{self.monthly_limit}")
        if monthly_usage > self.monthly_limit:
            logger.error(f"Monthly limit exceeded: {monthly_usage}/{self.monthly_limit}")
    
    def can_make_request(self, estimated_count: int) -> bool:
        """Check if request can be made within limits"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        daily_usage = self.usage_data['daily'].get(today, 0)
        monthly_usage = self.usage_data['monthly'].get(month, 0)
        
        # Check if request would exceed limits
        if daily_usage + estimated_count > self.daily_limit:
            logger.warning(f"Request would exceed daily limit")
            return False
        
        if monthly_usage + estimated_count > self.monthly_limit:
            logger.warning(f"Request would exceed monthly limit")
            return False
        
        return True
    
    def get_remaining_quota(self) -> Dict:
        """Get remaining API quota"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        daily_usage = self.usage_data['daily'].get(today, 0)
        monthly_usage = self.usage_data['monthly'].get(month, 0)
        
        return {
            'daily_remaining': self.daily_limit - daily_usage,
            'monthly_remaining': self.monthly_limit - monthly_usage,
            'daily_used': daily_usage,
            'monthly_used': monthly_usage,
            'daily_limit': self.daily_limit,
            'monthly_limit': self.monthly_limit
        }
    
    def print_usage_report(self):
        """Print usage report"""
        quota = self.get_remaining_quota()
        
        print("\n" + "="*60)
        print("BLOOMBERG API USAGE REPORT")
        print("="*60)
        print(f"Daily:   {quota['daily_used']:,} / {quota['daily_limit']:,} "
              f"({quota['daily_used']/quota['daily_limit']*100:.1f}%)")
        print(f"Monthly: {quota['monthly_used']:,} / {quota['monthly_limit']:,} "
              f"({quota['monthly_used']/quota['monthly_limit']*100:.1f}%)")
        print("-"*60)
        print(f"Daily Remaining:   {quota['daily_remaining']:,}")
        print(f"Monthly Remaining: {quota['monthly_remaining']:,}")
        print("="*60)
    
    def reset_daily_usage(self):
        """Reset daily usage (for testing)"""
        today = datetime.now().strftime('%Y-%m-%d')
        if today in self.usage_data['daily']:
            self.usage_data['daily'][today] = 0
            self._save_usage_data()
            logger.info("Daily usage reset")


if __name__ == "__main__":
    # Test usage monitor
    monitor = UsageMonitor({
        'daily_limit': 50000,
        'monthly_limit': 500000
    })
    
    # Record some usage
    monitor.record_usage(1000)
    monitor.record_usage(2000)
    
    # Print report
    monitor.print_usage_report()