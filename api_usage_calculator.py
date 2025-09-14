#!/usr/bin/env python3
"""
Bloomberg API Usage Calculator
Calculate data points usage for historical options fetching
"""

def calculate_usage(strikes_range=60, expiry_count=6, fields=10, days=1, time_points=1):
    """
    Calculate Bloomberg API usage

    Args:
        strikes_range: ATM ± strikes (default: 60 for ±30)
        expiry_count: Number of expiry dates within 1 month
        fields: Number of data fields to fetch
        days: Days of historical data per time point
        time_points: Number of historical time points

    Returns:
        Dictionary with usage breakdown
    """

    # Calculate option contracts
    option_contracts = strikes_range * 2 * expiry_count  # strikes × (Call+Put) × expiries

    # Calculate usage per time point
    usage_per_timepoint = option_contracts * fields * days

    # Total usage
    total_usage = usage_per_timepoint * time_points

    return {
        'strikes_range': strikes_range,
        'option_contracts': option_contracts,
        'fields': fields,
        'days_per_timepoint': days,
        'time_points': time_points,
        'usage_per_timepoint': usage_per_timepoint,
        'total_usage': total_usage,
        'daily_limit': 50000,
        'monthly_limit': 500000,
        'daily_usage_pct': (total_usage / 50000) * 100,
        'monthly_usage_pct': (total_usage / 500000) * 100
    }

def print_usage_report(usage):
    """Print formatted usage report"""
    print("\n" + "="*60)
    print("📊 BLOOMBERG API USAGE CALCULATOR")
    print("="*60)
    print(f"🎯 ATM ± {usage['strikes_range']//2} strikes")
    print(f"📅 {usage['time_points']} historical time points")
    print(f"📋 {usage['fields']} data fields per option")
    print(f"📈 {usage['option_contracts']} option contracts per time point")
    print("-"*60)
    print(f"📊 Usage per time point: {usage['usage_per_timepoint']:,} data points")
    print(f"🔥 Total usage: {usage['total_usage']:,} data points")
    print("-"*60)
    print(f"📅 Daily limit: {usage['daily_limit']:,} data points")
    print(f"📈 Daily usage: {usage['daily_usage_pct']:.1f}%")
    print(f"📊 Monthly limit: {usage['monthly_limit']:,} data points")
    print(f"🔥 Monthly usage: {usage['monthly_usage_pct']:.1f}%")
    print("="*60)

    # Recommendations
    if usage['total_usage'] <= 50000:
        print("✅ Can fetch in single day")
    elif usage['total_usage'] <= 500000:
        days_needed = (usage['total_usage'] // 50000) + 1
        print(f"⚠️  Need to split across {days_needed} days")
    else:
        print("❌ Exceeds monthly limit - reduce scope")

    print()

if __name__ == "__main__":
    print("Bloomberg API Usage Calculator")

    # Different scenarios
    scenarios = [
        {"name": "1個月歷史時點 (ATM±30)", "time_points": 1},
        {"name": "3個月歷史時點 (每月1次)", "time_points": 3},
        {"name": "6個月歷史時點 (每月1次)", "time_points": 6},
        {"name": "1年歷史時點 (每月1次)", "time_points": 12},
        {"name": "3個月 (每週1次)", "time_points": 12},
        {"name": "6個月 (每週1次)", "time_points": 24},
        {"name": "精簡版: ATM±10, 3個月", "strikes_range": 20, "time_points": 3}
    ]

    for scenario in scenarios:
        print(f"\n🎯 情境: {scenario['name']}")
        strikes = scenario.get('strikes_range', 60)
        time_points = scenario['time_points']

        usage = calculate_usage(
            strikes_range=strikes,
            expiry_count=6,
            fields=10,
            days=1,
            time_points=time_points
        )

        print_usage_report(usage)