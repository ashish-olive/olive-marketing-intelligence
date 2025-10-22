"""
Golden events - Pre-defined dramatic moments for compelling demo
These events are injected into the generated data to ensure interesting signals
"""

GOLDEN_EVENTS = [
    {
        'name': 'tiktok_breakthrough',
        'date_offset': 31,  # Day 31
        'type': 'creative_breakthrough',
        'channel': 'TikTok',
        'description': 'New video creative format drives 34% CPI drop',
        'effect': {
            'cpi_multiplier': 0.66,  # 34% drop
            'volume_multiplier': 1.73,  # 73% increase
            'retention_boost': 0.09,  # +9 percentage points
            'ctr_boost': 0.015,  # +1.5 percentage points
        },
        'duration_days': 30,
        'signal': {
            'title': 'TikTok CPI dropped 34% WoW following creative refresh',
            'severity': 'info',
            'recommended_action': 'Shift +15% budget from Meta → TikTok',
            'predicted_impact': {
                'monthly_savings': 45000,
                'install_increase_pct': 18,
                'roi_improvement': 0.28
            }
        }
    },
    {
        'name': 'meta_fatigue',
        'date_offset': 46,  # Day 46
        'type': 'creative_fatigue',
        'channel': 'Meta',
        'description': 'Creative fatigue causes 52% CPI increase',
        'effect': {
            'cpi_multiplier': 1.52,  # 52% increase
            'volume_multiplier': 0.64,  # 36% decrease
            'ctr_decline': 0.014,  # CTR drops 1.4 points
        },
        'duration_days': 15,
        'recovery_day': 61,  # Creative refresh on day 61
        'signal': {
            'title': 'Meta CPI rising 7 consecutive days (+38% vs baseline)',
            'severity': 'warning',
            'recommended_action': 'Pause fatigued creatives, launch new batch',
            'predicted_impact': {
                'cpi_reduction': 0.38,
                'volume_recovery': 1500,
                'daily_savings': 4200
            }
        }
    },
    {
        'name': 'influencer_surge',
        'date_offset': 42,  # Day 42
        'type': 'viral_moment',
        'channel': 'Organic',
        'description': 'Influencer campaign drives 240% organic surge',
        'effect': {
            'organic_multiplier': 3.4,  # 240% increase
            'app_store_rank_boost': -33,  # Rank improves (lower number)
            'social_mentions_multiplier': 4.5,
            'sentiment_boost': 0.15,
        },
        'duration_days': 8,  # Exponential decay over 8 days
        'signal': {
            'title': 'Influencer campaign drove 6K incremental organic installs',
            'severity': 'info',
            'recommended_action': 'Retarget organic cohort with paid ads within 48h',
            'predicted_impact': {
                'ltv_boost_pct': 25,
                'cohort_size': 6000,
                'estimated_value': 90000
            }
        }
    },
    {
        'name': 'google_efficiency_drop',
        'date_offset': 68,  # Day 68
        'type': 'competitor_launch',
        'channel': 'Google',
        'description': 'Competitor launch causes 52% CPI spike in Tier-1',
        'effect': {
            'cpi_multiplier': 1.52,  # 52% increase
            'volume_multiplier': 0.80,  # 20% decrease
            'tier1_only': True,  # Only affects tier-1 geos
        },
        'duration_days': 14,
        'signal': {
            'title': 'Google UAC ROAS dipped 28% in Tier-1 markets',
            'severity': 'warning',
            'recommended_action': 'Pause bottom 15% of ad groups, shift budget to Tier-2',
            'predicted_impact': {
                'roas_recovery': 0.21,
                'weekly_savings': 18000,
                'tier2_opportunity': 12000
            }
        }
    },
    {
        'name': 'budget_pacing_alert',
        'date_offset': 20,  # Day 20
        'type': 'budget_overrun',
        'channel': 'All',
        'description': 'Spend pacing 38% over budget',
        'effect': {
            'spend_multiplier': 1.40,  # 40% overspend
        },
        'duration_days': 5,
        'signal': {
            'title': 'Spend pacing 38% over budget - projected $202K overage',
            'severity': 'critical',
            'recommended_action': 'Reduce daily budgets by 25% across all channels',
            'predicted_impact': {
                'budget_saved': 202000,
                'month_end_projection': 495000,
                'target_budget': 500000
            }
        }
    },
    {
        'name': 'cross_channel_synergy',
        'date_offset': 55,  # Day 55
        'type': 'synergy_detected',
        'channel': 'Multiple',
        'description': 'Meta + Influencer synergy detected',
        'effect': {
            'meta_ltv_boost': 0.18,  # 18% LTV boost when combined
            'organic_halo_boost': 0.12,  # 12% more organic
        },
        'duration_days': 10,
        'signal': {
            'title': 'Meta campaigns + influencer activity show 18% LTV synergy',
            'severity': 'info',
            'recommended_action': 'Coordinate Meta campaigns with influencer drops',
            'predicted_impact': {
                'ltv_improvement': 0.18,
                'monthly_value': 32000,
                'optimal_timing': '24-48h after influencer post'
            }
        }
    }
]


def get_golden_event(event_name):
    """Get golden event by name"""
    for event in GOLDEN_EVENTS:
        if event['name'] == event_name:
            return event
    return None


def get_events_for_day(day_number):
    """Get all golden events that should trigger on a specific day"""
    events = []
    for event in GOLDEN_EVENTS:
        if event['date_offset'] == day_number:
            events.append(event)
    return events


def is_event_active(event, day_number):
    """Check if an event is active on a specific day"""
    start_day = event['date_offset']
    end_day = start_day + event.get('duration_days', 1)
    return start_day <= day_number < end_day


def get_event_multiplier(event, day_number, metric):
    """
    Get the multiplier for a specific metric on a specific day
    Handles decay for events that fade over time
    """
    if not is_event_active(event, day_number):
        return 1.0
    
    days_since_start = day_number - event['date_offset']
    duration = event.get('duration_days', 1)
    
    # Get base multiplier
    effect = event.get('effect', {})
    multiplier = effect.get(metric, 1.0)
    
    # Apply decay for certain event types
    if event['type'] in ['viral_moment', 'influencer_surge']:
        # Exponential decay: starts strong, fades quickly
        decay_factor = np.exp(-days_since_start / (duration / 3))
        return 1.0 + (multiplier - 1.0) * decay_factor
    
    elif event['type'] == 'creative_fatigue':
        # Linear increase: gets worse over time
        progress = days_since_start / duration
        return 1.0 + (multiplier - 1.0) * progress
    
    else:
        # Constant effect
        return multiplier


import numpy as np
