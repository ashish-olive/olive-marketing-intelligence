"""
Marketing Data Generator
Generates realistic marketing data with correlations, patterns, and golden events
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from faker import Faker
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.data_layer.models import (
    db, MarketingChannel, Campaign, Creative, DailyCampaignPerformance,
    UserInstall, UserSession, DailyOrganicMetric, Signal
)
from shared.data_layer.config import AppConfig
from data_pipeline.generators.channel_profiles import (
    CHANNEL_PROFILES, USER_SEGMENTS, DEVICE_DISTRIBUTIONS,
    GEO_DISTRIBUTIONS, MONETIZATION_PROFILES, CHURN_PROFILES
)
from data_pipeline.generators.golden_events import (
    GOLDEN_EVENTS, get_events_for_day, is_event_active, get_event_multiplier
)

fake = Faker()
Faker.seed(42)
np.random.seed(42)


class MarketingDataGenerator:
    """Generate realistic marketing data"""
    
    def __init__(self, days=90, users_target=500000, campaigns_per_channel=15):
        self.days = days
        self.users_target = users_target
        self.campaigns_per_channel = campaigns_per_channel
        self.start_date = datetime.now().date() - timedelta(days=days)
        
        # Storage for generated data
        self.channels = {}
        self.campaigns = []
        self.creatives = []
        self.users = []
        self.sessions = []
        
        print(f"Initializing data generator:")
        print(f"  - Days: {days}")
        print(f"  - Target users: {users_target:,}")
        print(f"  - Campaigns per channel: {campaigns_per_channel}")
        print(f"  - Start date: {self.start_date}")
    
    def generate_all(self, app):
        """Generate all data"""
        with app.app_context():
            print("\n" + "="*60)
            print("STARTING DATA GENERATION")
            print("="*60)
            
            # Create tables
            db.create_all()
            print("✓ Database tables created")
            
            # Generate data
            self.generate_channels()
            self.generate_campaigns_and_creatives()
            self.generate_daily_campaign_performance()
            self.generate_users()
            self.generate_sessions()
            self.generate_organic_metrics()
            self.generate_signals()
            
            print("\n" + "="*60)
            print("DATA GENERATION COMPLETE")
            print("="*60)
            self.print_summary()
    
    def generate_channels(self):
        """Generate marketing channels"""
        print("\n[1/7] Generating channels...")
        
        for channel_name, profile in CHANNEL_PROFILES.items():
            channel = MarketingChannel(
                name=channel_name,
                display_name=profile['display_name'],
                base_cpi=profile['base_cpi'],
                cpi_variance=profile['cpi_variance'],
                daily_volume=profile['daily_volume'],
                weekend_multiplier=profile['weekend_multiplier'],
                quality_score=profile['quality_score'],
                ltv_multiplier=profile['ltv_multiplier'],
                creative_fatigue_days=profile['creative_fatigue_days']
            )
            channel.set_properties(profile['properties'])
            db.session.add(channel)
            self.channels[channel_name] = channel
        
        db.session.commit()
        print(f"  ✓ Created {len(self.channels)} channels")
    
    def generate_campaigns_and_creatives(self):
        """Generate campaigns and creatives"""
        print("\n[2/7] Generating campaigns and creatives...")
        
        creative_id_counter = 1
        campaign_id_counter = 1
        
        for channel_name, channel in self.channels.items():
            for i in range(self.campaigns_per_channel):
                # Create 3 creatives per campaign
                campaign_creatives = []
                for j in range(3):
                    creative = Creative(
                        name=f"{channel_name}_Creative_{creative_id_counter}",
                        creative_type=np.random.choice(['video', 'image', 'carousel']),
                        created_date=self.start_date - timedelta(days=np.random.randint(0, 30)),
                        performance_score=np.random.uniform(60, 95)
                    )
                    db.session.add(creative)
                    campaign_creatives.append(creative)
                    creative_id_counter += 1
                
                # Create campaign
                campaign_start = self.start_date + timedelta(days=np.random.randint(0, 15))
                campaign = Campaign(
                    channel_id=channel.id,
                    name=f"{channel_name}_Campaign_{campaign_id_counter}",
                    start_date=campaign_start,
                    status='active',
                    daily_budget=np.random.uniform(1000, 5000),
                    creative=campaign_creatives[0]  # Primary creative
                )
                db.session.add(campaign)
                self.campaigns.append(campaign)
                campaign_id_counter += 1
        
        db.session.commit()
        print(f"  ✓ Created {len(self.campaigns)} campaigns")
        print(f"  ✓ Created {creative_id_counter-1} creatives")
    
    def generate_daily_campaign_performance(self):
        """Generate daily performance for each campaign"""
        print("\n[3/7] Generating daily campaign performance...")
        
        records = []
        total_records = len(self.campaigns) * self.days
        
        for campaign in self.campaigns:
            channel = campaign.channel
            profile = CHANNEL_PROFILES[channel.name]
            
            for day_num in range(self.days):
                current_date = self.start_date + timedelta(days=day_num)
                
                # Calculate CPI with all factors
                cpi = self._calculate_realistic_cpi(
                    channel, profile, current_date, day_num, campaign
                )
                
                # Calculate volume
                volume = self._calculate_realistic_volume(
                    channel, profile, current_date, day_num
                )
                
                # Calculate other metrics
                spend = cpi * volume
                impressions = int(volume / np.random.uniform(0.008, 0.015))  # CVR 0.8-1.5%
                clicks = int(impressions * np.random.uniform(0.02, 0.05))  # CTR 2-5%
                
                ctr = clicks / impressions if impressions > 0 else 0
                cvr = volume / clicks if clicks > 0 else 0
                
                # Quality metrics (will be updated after user generation)
                retention_d1 = profile['quality_score'] * np.random.uniform(0.9, 1.1)
                retention_d7 = retention_d1 * np.random.uniform(0.55, 0.65)
                retention_d30 = retention_d7 * np.random.uniform(0.40, 0.50)
                
                # Revenue metrics (estimated)
                ltv_predicted = self._estimate_ltv(channel, retention_d7)
                revenue_7d = volume * ltv_predicted * 0.15  # 15% of LTV in first 7 days
                revenue_30d = volume * ltv_predicted * 0.40  # 40% in first 30 days
                
                roas_7d = revenue_7d / spend if spend > 0 else 0
                roas_30d = revenue_30d / spend if spend > 0 else 0
                
                record = DailyCampaignPerformance(
                    campaign_id=campaign.id,
                    date=current_date,
                    spend=spend,
                    impressions=impressions,
                    clicks=clicks,
                    installs=volume,
                    cpi=cpi,
                    ctr=ctr,
                    cvr=cvr,
                    retention_d1=retention_d1,
                    retention_d7=retention_d7,
                    retention_d30=retention_d30,
                    revenue_7d=revenue_7d,
                    revenue_30d=revenue_30d,
                    ltv_predicted=ltv_predicted,
                    roas_7d=roas_7d,
                    roas_30d=roas_30d
                )
                records.append(record)
        
        # Bulk insert
        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f"  ✓ Created {len(records):,} daily performance records")
    
    def _calculate_realistic_cpi(self, channel, profile, current_date, day_num, campaign):
        """Calculate realistic CPI with all factors"""
        base_cpi = profile['base_cpi']
        
        # 1. Day of week effect
        day_multiplier = profile['weekend_multiplier'] if current_date.weekday() >= 5 else 1.0
        
        # 2. Creative age (fatigue)
        creative_age = (current_date - campaign.creative.created_date).days
        fatigue_days = profile['creative_fatigue_days']
        fatigue_multiplier = 1.0 + (creative_age / fatigue_days) * 0.5
        
        # 3. Budget exhaustion (diminishing returns)
        budget_multiplier = 1.0 + (campaign.daily_budget / 50000) * 0.3
        
        # 4. Random competition spikes
        competition_spike = np.random.choice([1.0, 1.3], p=[0.95, 0.05])
        
        # 5. Seasonal trends (monthly cycles)
        seasonal_multiplier = 1.0 + 0.1 * np.sin(2 * np.pi * day_num / 30)
        
        # 6. Golden events
        golden_multiplier = self._get_golden_event_multiplier(channel.name, day_num, 'cpi_multiplier')
        
        # 7. Random noise
        noise = np.random.normal(1.0, profile['cpi_variance'])
        
        cpi = base_cpi * day_multiplier * fatigue_multiplier * budget_multiplier * competition_spike * seasonal_multiplier * golden_multiplier * noise
        
        return max(0.5, min(20.0, cpi))  # Bound between $0.50 and $20
    
    def _calculate_realistic_volume(self, channel, profile, current_date, day_num):
        """Calculate realistic install volume"""
        base_volume = profile['daily_volume']
        
        # Day of week effect
        day_multiplier = profile['weekend_multiplier'] if current_date.weekday() >= 5 else 1.0
        
        # Golden events
        golden_multiplier = self._get_golden_event_multiplier(channel.name, day_num, 'volume_multiplier')
        
        # Random variance
        noise = np.random.normal(1.0, 0.2)
        
        volume = int(base_volume * day_multiplier * golden_multiplier * noise)
        
        return max(10, volume)  # At least 10 installs
    
    def _get_golden_event_multiplier(self, channel_name, day_num, metric):
        """Get multiplier from golden events"""
        multiplier = 1.0
        
        for event in GOLDEN_EVENTS:
            if event.get('channel') == channel_name or event.get('channel') == 'All':
                if is_event_active(event, day_num):
                    event_mult = get_event_multiplier(event, day_num, metric)
                    multiplier *= event_mult
        
        return multiplier
    
    def _estimate_ltv(self, channel, retention_d7):
        """Estimate LTV based on channel and retention"""
        base_ltv = 15.0
        ltv_mult = CHANNEL_PROFILES[channel.name]['ltv_multiplier']
        retention_mult = retention_d7 / 0.50  # Normalize to 50% baseline
        
        return base_ltv * ltv_mult * retention_mult
    
    def generate_users(self):
        """Generate user install records"""
        print("\n[4/7] Generating user installs...")
        print(f"  Target: {self.users_target:,} users")
        
        # This will be continued in the next part...
        # Due to size, splitting into multiple methods
        pass
    
    def generate_sessions(self):
        """Generate user session records"""
        print("\n[5/7] Generating user sessions...")
        # Will implement
        pass
    
    def generate_organic_metrics(self):
        """Generate daily organic metrics"""
        print("\n[6/7] Generating organic metrics...")
        # Will implement
        pass
    
    def generate_signals(self):
        """Generate performance signals"""
        print("\n[7/7] Generating signals...")
        # Will implement
        pass
    
    def print_summary(self):
        """Print generation summary"""
        print("\nGeneration Summary:")
        print(f"  - Channels: {len(self.channels)}")
        print(f"  - Campaigns: {len(self.campaigns)}")
        print(f"  - Users: {len(self.users):,}")
        print(f"  - Sessions: {len(self.sessions):,}")
