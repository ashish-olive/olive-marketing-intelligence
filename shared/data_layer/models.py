"""
SQLAlchemy models for Olive Marketing Intelligence Platform
Supports both cloud data generation and local API usage
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index, JSON
import json

db = SQLAlchemy()


class MarketingChannel(db.Model):
    """Marketing channels (Meta, Google, TikTok, Programmatic)"""
    __tablename__ = 'marketing_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    
    # Channel characteristics (for data generation)
    base_cpi = db.Column(db.Float, nullable=False)
    cpi_variance = db.Column(db.Float, nullable=False)
    daily_volume = db.Column(db.Integer, nullable=False)
    weekend_multiplier = db.Column(db.Float, nullable=False)
    quality_score = db.Column(db.Float, nullable=False)  # D7 retention baseline
    ltv_multiplier = db.Column(db.Float, nullable=False)
    creative_fatigue_days = db.Column(db.Integer, nullable=False)
    
    # JSON field for additional properties
    properties = db.Column(db.Text)  # JSON string
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='channel', lazy='dynamic')
    
    def get_properties(self):
        """Parse JSON properties"""
        return json.loads(self.properties) if self.properties else {}
    
    def set_properties(self, props):
        """Set JSON properties"""
        self.properties = json.dumps(props)


class Campaign(db.Model):
    """Marketing campaigns"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('marketing_channels.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    
    # Campaign details
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)  # learning, active, fatigued, paused
    
    # Budget
    daily_budget = db.Column(db.Float, nullable=False)
    total_budget = db.Column(db.Float)
    
    # Creative reference
    creative_id = db.Column(db.Integer, db.ForeignKey('creatives.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    daily_performance = db.relationship('DailyCampaignPerformance', backref='campaign', lazy='dynamic')
    user_installs = db.relationship('UserInstall', backref='campaign', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_campaign_channel', 'channel_id'),
        Index('idx_campaign_dates', 'start_date', 'end_date'),
    )


class Creative(db.Model):
    """Ad creatives"""
    __tablename__ = 'creatives'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    creative_type = db.Column(db.String(50), nullable=False)  # video, image, carousel
    
    created_date = db.Column(db.Date, nullable=False)
    performance_score = db.Column(db.Float)  # 0-100
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='creative', lazy='dynamic')


class DailyCampaignPerformance(db.Model):
    """Daily performance metrics per campaign"""
    __tablename__ = 'daily_campaign_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Spend & impressions
    spend = db.Column(db.Float, nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    installs = db.Column(db.Integer, nullable=False)
    
    # Calculated metrics
    cpi = db.Column(db.Float, nullable=False)
    ctr = db.Column(db.Float, nullable=False)  # Click-through rate
    cvr = db.Column(db.Float, nullable=False)  # Conversion rate
    
    # Quality metrics (aggregated from users)
    retention_d1 = db.Column(db.Float)
    retention_d7 = db.Column(db.Float)
    retention_d30 = db.Column(db.Float)
    
    # Revenue metrics
    revenue_7d = db.Column(db.Float)
    revenue_30d = db.Column(db.Float)
    ltv_predicted = db.Column(db.Float)
    roas_7d = db.Column(db.Float)
    roas_30d = db.Column(db.Float)
    
    __table_args__ = (
        Index('idx_daily_perf_date', 'date'),
        Index('idx_daily_perf_campaign_date', 'campaign_id', 'date'),
    )


class UserInstall(db.Model):
    """User install records with full attribution"""
    __tablename__ = 'user_installs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, unique=True)
    
    # Attribution
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    creative_id = db.Column(db.Integer, db.ForeignKey('creatives.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('marketing_channels.id'), nullable=False)
    
    install_date = db.Column(db.Date, nullable=False)
    install_source = db.Column(db.String(50), nullable=False)  # paid, organic
    
    # Device & geo
    device_type = db.Column(db.String(50), nullable=False)
    os_version = db.Column(db.String(50))
    device_model = db.Column(db.String(100))
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    # Behavioral metrics
    d1_active = db.Column(db.Boolean, default=False)
    d3_active = db.Column(db.Boolean, default=False)
    d7_active = db.Column(db.Boolean, default=False)
    d30_active = db.Column(db.Boolean, default=False)
    
    retention_d1 = db.Column(db.Float)
    retention_d7 = db.Column(db.Float)
    retention_d30 = db.Column(db.Float)
    
    session_count_7d = db.Column(db.Integer, default=0)
    session_count_30d = db.Column(db.Integer, default=0)
    avg_session_duration = db.Column(db.Float)  # minutes
    total_playtime_minutes = db.Column(db.Float)
    
    # Monetization
    is_payer = db.Column(db.Boolean, default=False)
    first_purchase_day = db.Column(db.Integer)  # Days since install
    total_revenue = db.Column(db.Float, default=0.0)
    ltv_7d = db.Column(db.Float, default=0.0)
    ltv_30d = db.Column(db.Float, default=0.0)
    ltv_90d = db.Column(db.Float, default=0.0)
    ltv_180d = db.Column(db.Float, default=0.0)
    
    arpu = db.Column(db.Float)  # Average revenue per user
    arppu = db.Column(db.Float)  # Average revenue per paying user
    
    # Churn indicators
    is_churned = db.Column(db.Boolean, default=False)
    churn_date = db.Column(db.Date)
    days_to_churn = db.Column(db.Integer)
    churn_reason = db.Column(db.String(100))
    
    # ML features (for training)
    user_segment = db.Column(db.String(50))  # power_user, regular, casual, churner
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('UserSession', backref='user', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_user_install_date', 'install_date'),
        Index('idx_user_campaign', 'campaign_id'),
        Index('idx_user_channel', 'channel_id'),
        Index('idx_user_country', 'country'),
        Index('idx_user_segment', 'user_segment'),
    )


class UserSession(db.Model):
    """User session records"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('user_installs.user_id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    
    session_date = db.Column(db.Date, nullable=False)
    session_start_time = db.Column(db.DateTime, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    
    # Engagement
    events_triggered = db.Column(db.Text)  # JSON array
    revenue_this_session = db.Column(db.Float, default=0.0)
    features_used = db.Column(db.Text)  # JSON array
    session_quality_score = db.Column(db.Float)  # 0-100
    
    __table_args__ = (
        Index('idx_session_user', 'user_id'),
        Index('idx_session_date', 'session_date'),
    )
    
    def get_events(self):
        """Parse JSON events"""
        return json.loads(self.events_triggered) if self.events_triggered else []
    
    def set_events(self, events):
        """Set JSON events"""
        self.events_triggered = json.dumps(events)


class DailyOrganicMetric(db.Model):
    """Daily organic performance metrics"""
    __tablename__ = 'daily_organic_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Organic installs
    organic_installs = db.Column(db.Integer, nullable=False)
    
    # App store metrics
    app_store_rank = db.Column(db.Integer)
    app_store_rating = db.Column(db.Float)
    app_store_reviews = db.Column(db.Integer)
    
    # Social metrics
    social_mentions = db.Column(db.Integer)
    sentiment_score = db.Column(db.Float)  # -1 to 1
    
    # Influencer events (JSON)
    influencer_events = db.Column(db.Text)  # JSON array
    
    # Paid halo contribution
    paid_halo_contribution = db.Column(db.Float)  # % of organic from paid
    
    __table_args__ = (
        Index('idx_organic_date', 'date'),
    )
    
    def get_influencer_events(self):
        """Parse JSON influencer events"""
        return json.loads(self.influencer_events) if self.influencer_events else []
    
    def set_influencer_events(self, events):
        """Set JSON influencer events"""
        self.influencer_events = json.dumps(events)


class Signal(db.Model):
    """Pre-calculated performance signals (insights)"""
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    date_detected = db.Column(db.Date, nullable=False)
    signal_type = db.Column(db.String(100), nullable=False)
    
    # Signal content
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), nullable=False)  # info, warning, critical
    
    # Affected entity
    affected_entity_type = db.Column(db.String(50))  # channel, campaign, creative
    affected_entity_id = db.Column(db.Integer)
    
    # Metrics (JSON)
    metrics = db.Column(db.Text)  # JSON: before/after values
    
    # Recommendation
    recommended_action = db.Column(db.Text, nullable=False)
    predicted_impact = db.Column(db.Text)  # JSON: expected outcomes
    
    # Priority scoring
    priority_score = db.Column(db.Float)  # 0-100
    confidence = db.Column(db.Float)  # 0-1
    
    # Status
    is_dismissed = db.Column(db.Boolean, default=False)
    dismissed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_signal_date', 'date_detected'),
        Index('idx_signal_type', 'signal_type'),
        Index('idx_signal_severity', 'severity'),
    )
    
    def get_metrics(self):
        """Parse JSON metrics"""
        return json.loads(self.metrics) if self.metrics else {}
    
    def set_metrics(self, metrics_dict):
        """Set JSON metrics"""
        self.metrics = json.dumps(metrics_dict)
    
    def get_predicted_impact(self):
        """Parse JSON predicted impact"""
        return json.loads(self.predicted_impact) if self.predicted_impact else {}
    
    def set_predicted_impact(self, impact_dict):
        """Set JSON predicted impact"""
        self.predicted_impact = json.dumps(impact_dict)
