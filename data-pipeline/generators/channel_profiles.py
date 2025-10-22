"""
Marketing channel profiles with realistic characteristics
Based on real-world performance data
"""

CHANNEL_PROFILES = {
    'Meta': {
        'display_name': 'Meta (Facebook/Instagram)',
        'base_cpi': 2.50,
        'cpi_variance': 0.40,
        'daily_volume': 5000,
        'weekend_multiplier': 0.85,  # 15% drop on weekends
        'quality_score': 0.72,  # D7 retention
        'ltv_multiplier': 1.0,
        'creative_fatigue_days': 14,
        'properties': {
            'auction_competition': 'high',
            'targeting_precision': 'high',
            'creative_formats': ['video', 'image', 'carousel'],
            'best_geos': ['US', 'UK', 'CA', 'AU'],
            'peak_hours': [18, 19, 20, 21],  # 6pm-9pm
        }
    },
    'Google': {
        'display_name': 'Google UAC',
        'base_cpi': 3.20,
        'cpi_variance': 0.30,  # More stable
        'daily_volume': 3500,
        'weekend_multiplier': 0.90,
        'quality_score': 0.68,
        'ltv_multiplier': 0.95,
        'creative_fatigue_days': 21,  # Slower fatigue
        'properties': {
            'auction_competition': 'medium',
            'targeting_precision': 'medium',
            'creative_formats': ['video', 'image'],
            'best_geos': ['US', 'UK', 'DE', 'JP'],
            'peak_hours': [10, 11, 14, 15, 20],  # Business hours + evening
        }
    },
    'TikTok': {
        'display_name': 'TikTok Ads',
        'base_cpi': 1.80,  # Cheaper but lower quality
        'cpi_variance': 0.60,  # Very volatile
        'daily_volume': 8000,  # High volume
        'weekend_multiplier': 1.15,  # 15% boost on weekends (younger demo)
        'quality_score': 0.55,  # Lower retention
        'ltv_multiplier': 0.75,
        'creative_fatigue_days': 7,  # Burns out fast
        'properties': {
            'auction_competition': 'low',  # Less mature
            'targeting_precision': 'medium',
            'creative_formats': ['video'],
            'best_geos': ['US', 'BR', 'MX', 'IN'],
            'peak_hours': [19, 20, 21, 22, 23],  # Late evening
        }
    },
    'Programmatic': {
        'display_name': 'Programmatic DSP',
        'base_cpi': 4.50,  # Expensive
        'cpi_variance': 0.50,
        'daily_volume': 1500,
        'weekend_multiplier': 0.95,
        'quality_score': 0.80,  # High quality
        'ltv_multiplier': 1.25,  # Best LTV
        'creative_fatigue_days': 30,
        'properties': {
            'auction_competition': 'low',
            'targeting_precision': 'very_high',
            'creative_formats': ['video', 'image', 'native'],
            'best_geos': ['US', 'UK', 'CA', 'AU', 'DE'],
            'peak_hours': [9, 10, 11, 14, 15, 16],  # Business hours
        }
    }
}


# User segment distributions by channel
USER_SEGMENTS = {
    'Meta': {
        'power_user': 0.12,
        'regular': 0.45,
        'casual': 0.43
    },
    'Google': {
        'power_user': 0.10,
        'regular': 0.42,
        'casual': 0.48
    },
    'TikTok': {
        'power_user': 0.06,
        'regular': 0.32,
        'casual': 0.62
    },
    'Programmatic': {
        'power_user': 0.18,
        'regular': 0.52,
        'casual': 0.30
    }
}


# Device distributions by channel
DEVICE_DISTRIBUTIONS = {
    'Meta': {
        'iOS': 0.55,
        'Android': 0.45
    },
    'Google': {
        'iOS': 0.48,
        'Android': 0.52
    },
    'TikTok': {
        'iOS': 0.42,
        'Android': 0.58
    },
    'Programmatic': {
        'iOS': 0.62,
        'Android': 0.38
    }
}


# Geographic distributions
GEO_DISTRIBUTIONS = {
    'countries': {
        'US': 0.40,
        'UK': 0.12,
        'CA': 0.08,
        'AU': 0.06,
        'DE': 0.07,
        'FR': 0.05,
        'BR': 0.08,
        'MX': 0.06,
        'IN': 0.05,
        'JP': 0.03
    },
    'tiers': {
        'tier1': ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP'],
        'tier2': ['BR', 'MX', 'IN']
    }
}


# Monetization profiles
MONETIZATION_PROFILES = {
    'power_user': {
        'paying_rate': 0.35,
        'avg_revenue': 45.0,
        'first_purchase_day_range': (1, 3),
        'session_frequency': (5, 10),  # sessions per day
        'avg_session_duration': (30, 60),  # minutes
    },
    'regular': {
        'paying_rate': 0.08,
        'avg_revenue': 15.0,
        'first_purchase_day_range': (3, 14),
        'session_frequency': (1, 3),
        'avg_session_duration': (10, 20),
    },
    'casual': {
        'paying_rate': 0.01,
        'avg_revenue': 5.0,
        'first_purchase_day_range': (7, 30),
        'session_frequency': (0.2, 1),
        'avg_session_duration': (5, 10),
    }
}


# Churn profiles
CHURN_PROFILES = {
    'power_user': {
        'churn_rate': 0.10,  # 10% churn
        'avg_days_to_churn': 60,
    },
    'regular': {
        'churn_rate': 0.30,  # 30% churn
        'avg_days_to_churn': 30,
    },
    'casual': {
        'churn_rate': 0.60,  # 60% churn
        'avg_days_to_churn': 14,
    }
}


def get_channel_profile(channel_name):
    """Get channel profile by name"""
    return CHANNEL_PROFILES.get(channel_name)


def get_all_channel_names():
    """Get list of all channel names"""
    return list(CHANNEL_PROFILES.keys())
