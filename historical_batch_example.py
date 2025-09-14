#!/usr/bin/env python3
"""
Bloomberg Historical Batch Fetching Example
Demonstrates how to fetch multiple historical time points efficiently
"""

from datetime import datetime, timedelta

def generate_historical_dates(start_months_ago=6, frequency='monthly'):
    """
    Generate list of historical dates for "time machine" analysis

    Args:
        start_months_ago: How many months back to start
        frequency: 'weekly' or 'monthly'

    Returns:
        List of dates (YYYYMMDD format)
    """

    dates = []
    today = datetime.now()

    if frequency == 'monthly':
        # Generate monthly dates
        for i in range(start_months_ago):
            date = today - timedelta(days=30 * (i + 1))
            # Use 15th of each month for consistency
            date = date.replace(day=15)
            dates.append(date.strftime('%Y%m%d'))

    elif frequency == 'weekly':
        # Generate weekly dates
        for i in range(start_months_ago * 4):
            date = today - timedelta(weeks=i + 1)
            # Use Wednesday of each week
            days_since_monday = date.weekday()
            wednesday = date - timedelta(days=days_since_monday) + timedelta(days=2)
            dates.append(wednesday.strftime('%Y%m%d'))

    return sorted(dates)

def print_batch_plan():
    """Print recommended batch fetching plan"""

    print("\n" + "="*70)
    print("🎯 BLOOMBERG 歷史資料批次抓取計劃")
    print("="*70)

    scenarios = [
        {
            "name": "保守策略：6個月，每月1次",
            "months": 6,
            "frequency": "monthly",
            "usage": 43200,
            "days_needed": 1,
            "description": "適合初次使用，風險最低"
        },
        {
            "name": "標準策略：1年，每月1次",
            "months": 12,
            "frequency": "monthly",
            "usage": 86400,
            "days_needed": 2,
            "description": "最常見的時間跨度"
        },
        {
            "name": "精細策略：3個月，每週1次",
            "months": 3,
            "frequency": "weekly",
            "usage": 86400,
            "days_needed": 2,
            "description": "高解析度分析"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 方案 {i}: {scenario['name']}")
        print(f"   📅 時間跨度: {scenario['months']} 個月")
        print(f"   🔄 頻率: {scenario['frequency']}")
        print(f"   📊 API使用量: {scenario['usage']:,} data points")
        print(f"   ⏰ 需要時間: {scenario['days_needed']} 天")
        print(f"   💡 說明: {scenario['description']}")

        # Generate sample dates
        dates = generate_historical_dates(scenario['months'], scenario['frequency'])
        print(f"   📆 範例時間點: {dates[0]} ... {dates[-1]} ({len(dates)}個時點)")

    print("\n" + "="*70)
    print("💰 成本效益分析:")
    print("• 每個時點 = 7,200 data points (ATM±30)")
    print("• 每日限制 = 50,000 data points")
    print("• 每月限制 = 500,000 data points")
    print("• 建議單日最多抓取 6 個時點 (42,000 points)")
    print("="*70)

    # Command examples
    print("\n🚀 實際執行指令範例:")
    print("\n# 方案1: 6個月，每月15日")
    dates = generate_historical_dates(6, 'monthly')
    for date in dates[:3]:  # Show first 3
        cmd = f"python scripts/historical_fetch.py --start-date {date} --days 1 --export-format parquet"
        print(f"  {cmd}")
    print("  ...")

    print(f"\n# 總共 {len(dates)} 個指令，建議分成 {(len(dates) + 5) // 6} 天執行")

if __name__ == "__main__":
    print_batch_plan()