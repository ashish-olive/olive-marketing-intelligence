"""
Utility helper functions
"""
import numpy as np
from datetime import datetime, timedelta


def get_date_range(days=30):
    """Get date range for queries"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def calculate_percentage_change(current, previous):
    """Calculate percentage change"""
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_number(number):
    """Format large numbers with K, M suffixes"""
    if number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return str(int(number))


def calculate_z_score(value, mean, std):
    """Calculate z-score for anomaly detection"""
    if std == 0:
        return 0.0
    return (value - mean) / std


def detect_trend(values, window=7):
    """
    Detect trend direction in time series
    Returns: 'increasing', 'decreasing', 'stable'
    """
    if len(values) < window:
        return 'stable'
    
    recent = values[-window:]
    trend = np.polyfit(range(len(recent)), recent, 1)[0]
    
    # Threshold for significance
    threshold = np.std(values) * 0.1
    
    if trend > threshold:
        return 'increasing'
    elif trend < -threshold:
        return 'decreasing'
    else:
        return 'stable'


def calculate_moving_average(values, window=7):
    """Calculate moving average"""
    if len(values) < window:
        return values
    
    return np.convolve(values, np.ones(window)/window, mode='valid')


def is_weekend(date):
    """Check if date is weekend"""
    return date.weekday() >= 5


def get_day_of_week_name(date):
    """Get day of week name"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date.weekday()]


def calculate_retention_rate(active_users, total_users):
    """Calculate retention rate"""
    if total_users == 0:
        return 0.0
    return (active_users / total_users) * 100


def calculate_roas(revenue, spend):
    """Calculate Return on Ad Spend"""
    if spend == 0:
        return 0.0
    return revenue / spend


def calculate_ltv_cac_ratio(ltv, cac):
    """Calculate LTV/CAC ratio"""
    if cac == 0:
        return 0.0
    return ltv / cac
