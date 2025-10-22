"""
Complete Marketing Data Generator
Streamlined version for testing and production use
"""
import sys
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Add project root and data-pipeline to path
project_root = Path(__file__).parent.parent.parent
data_pipeline_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(data_pipeline_root))

from shared.data_layer.models import (
    db, MarketingChannel, Campaign, Creative, DailyCampaignPerformance,
    UserInstall, UserSession, DailyOrganicMetric, Signal
)
from generators.channel_profiles import (
    CHANNEL_PROFILES, USER_SEGMENTS, DEVICE_DISTRIBUTIONS,
    GEO_DISTRIBUTIONS, MONETIZATION_PROFILES, CHURN_PROFILES
)
from generators.golden_events import GOLDEN_EVENTS

fake = Faker()


class CompleteDataGenerator:
    """Complete data generator with all components"""
    
    def __init__(self, days=90, users_target=500000, campaigns_per_channel=15):
        self.days = days
        self.users_target = users_target
        self.campaigns_per_channel = campaigns_per_channel
        self.start_date = datetime.now().date() - timedelta(days=days)
        
        # Set random seeds for reproducibility
        Faker.seed(42)
        np.random.seed(42)
        
        print(f"\n{'='*70}")
        print(f"OLIVE MARKETING INTELLIGENCE - DATA GENERATOR")
        print(f"{'='*70}")
        print(f"Configuration:")
        print(f"  Days: {days}")
        print(f"  Target users: {users_target:,}")
        print(f"  Campaigns per channel: {campaigns_per_channel}")
        print(f"  Start date: {self.start_date}")
        print(f"{'='*70}\n")
    
    def generate_all(self, app):
        """Generate all data"""
        with app.app_context():
            # Create tables
            db.create_all()
            print("✓ Database tables created\n")
            
            # Generate in order
            channels = self.generate_channels()
            campaigns, creatives = self.generate_campaigns_and_creatives(channels)
            self.generate_daily_performance(campaigns)
            users = self.generate_users(campaigns)
            self.generate_sessions(users)
            self.generate_organic_metrics()
            self.generate_signals()
            
            print(f"\n{'='*70}")
            print("DATA GENERATION COMPLETE!")
            print(f"{'='*70}")
            self.print_summary()
    
    def generate_channels(self):
        """Generate marketing channels"""
        print("[1/7] Generating channels...")
        channels = {}
        
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
            channels[channel_name] = channel
        
        db.session.commit()
        print(f"  ✓ Created {len(channels)} channels\n")
        return channels
    
    def generate_campaigns_and_creatives(self, channels):
        """Generate campaigns and creatives"""
        print("[2/7] Generating campaigns and creatives...")
        campaigns = []
        creatives = []
        
        for channel_name, channel in channels.items():
            for i in range(self.campaigns_per_channel):
                # Create creatives
                for j in range(3):
                    creative = Creative(
                        name=f"{channel_name}_Creative_{len(creatives)+1}",
                        creative_type=np.random.choice(['video', 'image', 'carousel']),
                        created_date=self.start_date - timedelta(days=np.random.randint(0, 30)),
                        performance_score=np.random.uniform(60, 95)
                    )
                    db.session.add(creative)
                    creatives.append(creative)
                
                db.session.flush()  # Get creative IDs
                
                # Create campaign
                campaign = Campaign(
                    channel_id=channel.id,
                    name=f"{channel_name}_Campaign_{len(campaigns)+1}",
                    start_date=self.start_date,
                    status='active',
                    daily_budget=np.random.uniform(1000, 5000),
                    creative_id=creatives[-3].id
                )
                db.session.add(campaign)
                campaigns.append(campaign)
        
        db.session.commit()
        print(f"  ✓ Created {len(campaigns)} campaigns")
        print(f"  ✓ Created {len(creatives)} creatives\n")
        return campaigns, creatives
    
    def generate_daily_performance(self, campaigns):
        """Generate daily campaign performance"""
        print("[3/7] Generating daily campaign performance...")
        
        records = []
        for campaign in campaigns:
            channel_name = campaign.channel.name
            profile = CHANNEL_PROFILES[channel_name]
            
            for day_num in range(self.days):
                current_date = self.start_date + timedelta(days=day_num)
                
                # Calculate metrics
                cpi = self._calc_cpi(profile, current_date, day_num, campaign)
                volume = int(profile['daily_volume'] / self.campaigns_per_channel * np.random.uniform(0.8, 1.2))
                spend = cpi * volume
                impressions = int(volume / 0.01)
                clicks = int(impressions * 0.03)
                
                record = DailyCampaignPerformance(
                    campaign_id=campaign.id,
                    date=current_date,
                    spend=spend,
                    impressions=impressions,
                    clicks=clicks,
                    installs=volume,
                    cpi=cpi,
                    ctr=clicks/impressions if impressions > 0 else 0,
                    cvr=volume/clicks if clicks > 0 else 0,
                    retention_d1=profile['quality_score'] * 1.1,
                    retention_d7=profile['quality_score'],
                    retention_d30=profile['quality_score'] * 0.5,
                    revenue_7d=volume * 2.0,
                    revenue_30d=volume * 6.0,
                    ltv_predicted=15.0 * profile['ltv_multiplier'],
                    roas_7d=(volume * 2.0) / spend if spend > 0 else 0,
                    roas_30d=(volume * 6.0) / spend if spend > 0 else 0
                )
                records.append(record)
        
        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f"  ✓ Created {len(records):,} daily performance records\n")
    
    def _calc_cpi(self, profile, date, day_num, campaign):
        """Calculate CPI with golden events"""
        base_cpi = profile['base_cpi']
        weekend_mult = profile['weekend_multiplier'] if date.weekday() >= 5 else 1.0
        
        # Apply golden events
        golden_mult = 1.0
        for event in GOLDEN_EVENTS:
            if event.get('channel') == campaign.channel.name:
                if event['date_offset'] <= day_num < event['date_offset'] + event.get('duration_days', 1):
                    golden_mult *= event['effect'].get('cpi_multiplier', 1.0)
        
        noise = np.random.normal(1.0, profile['cpi_variance'])
        return max(0.5, base_cpi * weekend_mult * golden_mult * noise)
    
    def generate_users(self, campaigns):
        """Generate user installs"""
        print("[4/7] Generating user installs...")
        print(f"  Target: {self.users_target:,} users")
        
        users = []
        users_per_day = self.users_target // self.days
        
        for day_num in range(self.days):
            install_date = self.start_date + timedelta(days=day_num)
            daily_users = int(users_per_day * np.random.uniform(0.8, 1.2))
            
            for _ in range(daily_users):
                # Pick random campaign
                campaign = np.random.choice(campaigns)
                channel_name = campaign.channel.name
                
                # User segment
                segment_probs = USER_SEGMENTS[channel_name]
                segment = np.random.choice(
                    ['power_user', 'regular', 'casual'],
                    p=[segment_probs['power_user'], segment_probs['regular'], segment_probs['casual']]
                )
                
                # Device
                device_probs = DEVICE_DISTRIBUTIONS[channel_name]
                device = np.random.choice(['iOS', 'Android'], p=[device_probs['iOS'], device_probs['Android']])
                
                # Country
                countries = list(GEO_DISTRIBUTIONS['countries'].keys())
                country_probs = list(GEO_DISTRIBUTIONS['countries'].values())
                country = np.random.choice(countries, p=country_probs)
                
                # Monetization
                mon_profile = MONETIZATION_PROFILES[segment]
                is_payer = np.random.random() < mon_profile['paying_rate']
                
                user = UserInstall(
                    user_id=str(uuid.uuid4()),
                    campaign_id=campaign.id,
                    creative_id=campaign.creative_id,
                    channel_id=campaign.channel_id,
                    install_date=install_date,
                    install_source='paid',
                    device_type=device,
                    country=country,
                    d1_active=True,
                    d7_active=np.random.random() < 0.6,
                    d30_active=np.random.random() < 0.3,
                    retention_d1=0.8,
                    retention_d7=0.5,
                    retention_d30=0.25,
                    session_count_7d=int(np.random.uniform(1, 10)),
                    session_count_30d=int(np.random.uniform(5, 30)),
                    avg_session_duration=np.random.uniform(5, 30),
                    is_payer=is_payer,
                    total_revenue=mon_profile['avg_revenue'] if is_payer else 0,
                    ltv_7d=2.0 if is_payer else 0,
                    ltv_30d=6.0 if is_payer else 0,
                    ltv_90d=12.0 if is_payer else 0,
                    ltv_180d=mon_profile['avg_revenue'] if is_payer else 0,
                    is_churned=np.random.random() < CHURN_PROFILES[segment]['churn_rate'],
                    user_segment=segment
                )
                users.append(user)
                
                if len(users) >= 10000:  # Batch insert
                    db.session.bulk_save_objects(users)
                    db.session.commit()
                    print(f"  → {len(users):,} users created...", end='\r')
                    users = []
        
        if users:
            db.session.bulk_save_objects(users)
            db.session.commit()
        
        print(f"  ✓ Created {self.users_target:,} user installs\n")
        return users
    
    def generate_sessions(self, users):
        """Generate user sessions"""
        print("[5/7] Generating user sessions...")
        
        # Generate full session dataset
        target_sessions = self.users_target * 10  # 10 sessions per user
        sessions_per_user = 10
        
        print(f"  Target: {target_sessions:,} sessions ({sessions_per_user} per user avg)")
        print(f"  This will take 3-5 minutes...")
        
        # Process all users in batches
        batch_size = 10000
        total_users = UserInstall.query.count()
        print(f"  Processing {total_users:,} users in batches of {batch_size:,}")
        
        sessions = []
        processed = 0
        
        for offset in range(0, total_users, batch_size):
            user_records = UserInstall.query.offset(offset).limit(batch_size).all()
            
            for user in user_records:
                num_sessions = int(np.random.uniform(1, sessions_per_user * 2))
                
                for i in range(num_sessions):
                    session_date = user.install_date + timedelta(days=np.random.randint(0, 30))
                    
                    session = UserSession(
                        user_id=user.user_id,
                        session_id=str(uuid.uuid4()),
                        session_date=session_date,
                        session_start_time=datetime.combine(session_date, datetime.min.time()) + timedelta(hours=np.random.randint(0, 24)),
                        duration_seconds=int(np.random.uniform(60, 1800)),
                        revenue_this_session=np.random.uniform(0, 5) if user.is_payer and np.random.random() < 0.1 else 0,
                        session_quality_score=np.random.uniform(60, 95)
                    )
                    sessions.append(session)
                    
                    if len(sessions) >= 10000:
                        db.session.bulk_save_objects(sessions)
                        db.session.commit()
                        sessions = []
            
            processed += len(user_records)
            print(f"  → Processed {processed:,}/{total_users:,} users...", end='\r')
        
        if sessions:
            db.session.bulk_save_objects(sessions)
            db.session.commit()
        
        total_sessions = UserSession.query.count()
        print(f"\n  ✓ Created {total_sessions:,} user sessions\n")
    
    def generate_organic_metrics(self):
        """Generate daily organic metrics"""
        print("[6/7] Generating organic metrics...")
        
        records = []
        for day_num in range(self.days):
            current_date = self.start_date + timedelta(days=day_num)
            
            # Base organic installs
            organic_base = 2500
            
            # Apply golden events
            organic_mult = 1.0
            for event in GOLDEN_EVENTS:
                if event.get('type') == 'viral_moment' and event.get('channel') == 'Organic':
                    if event['date_offset'] <= day_num < event['date_offset'] + event.get('duration_days', 1):
                        organic_mult = event['effect'].get('organic_multiplier', 1.0)
            
            organic_installs = int(organic_base * organic_mult * np.random.uniform(0.8, 1.2))
            
            record = DailyOrganicMetric(
                date=current_date,
                organic_installs=organic_installs,
                app_store_rank=np.random.randint(20, 100),
                app_store_rating=np.random.uniform(4.0, 4.8),
                app_store_reviews=np.random.randint(100, 500),
                social_mentions=np.random.randint(1000, 5000),
                sentiment_score=np.random.uniform(0.6, 0.9),
                paid_halo_contribution=np.random.uniform(0.15, 0.35)
            )
            records.append(record)
        
        db.session.bulk_save_objects(records)
        db.session.commit()
        print(f"  ✓ Created {len(records)} organic metric records\n")
    
    def generate_signals(self):
        """Generate performance signals from golden events"""
        print("[7/7] Generating signals...")
        
        signals = []
        for event in GOLDEN_EVENTS:
            signal_data = event.get('signal', {})
            signal_date = self.start_date + timedelta(days=event['date_offset'])
            
            signal = Signal(
                date_detected=signal_date,
                signal_type=event['type'],
                title=signal_data.get('title', f"Signal: {event['name']}"),
                description=event['description'],
                severity=signal_data.get('severity', 'info'),
                affected_entity_type='channel',
                recommended_action=signal_data.get('recommended_action', 'Review performance'),
                priority_score=np.random.uniform(70, 95),
                confidence=np.random.uniform(0.75, 0.95),
                is_dismissed=False
            )
            signal.set_metrics({'event': event['name']})
            signal.set_predicted_impact(signal_data.get('predicted_impact', {}))
            signals.append(signal)
        
        db.session.bulk_save_objects(signals)
        db.session.commit()
        print(f"  ✓ Created {len(signals)} performance signals\n")
    
    def print_summary(self):
        """Print generation summary"""
        print("\nDatabase Summary:")
        print(f"  Channels: {MarketingChannel.query.count()}")
        print(f"  Campaigns: {Campaign.query.count()}")
        print(f"  Creatives: {Creative.query.count()}")
        print(f"  Daily Performance: {DailyCampaignPerformance.query.count():,}")
        print(f"  User Installs: {UserInstall.query.count():,}")
        print(f"  User Sessions: {UserSession.query.count():,}")
        print(f"  Organic Metrics: {DailyOrganicMetric.query.count()}")
        print(f"  Signals: {Signal.query.count()}")
