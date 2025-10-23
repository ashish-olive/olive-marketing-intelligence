"""
Olive Marketing Intelligence - Backend API
Flask application with ML inference capabilities
"""
import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.data_layer.models import (
    db, MarketingChannel, Campaign, DailyCampaignPerformance,
    UserInstall, DailyOrganicMetric, Signal
)
from shared.data_layer.config import AppConfig


def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(AppConfig)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=AppConfig.CORS_ORIGINS)
    
    # Initialize database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created/verified successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("App will start without database - some endpoints may fail")
    
    return app


app = create_app()


# ============================================================
# EXECUTIVE DASHBOARD ENDPOINTS
# ============================================================

@app.route('/api/executive/summary', methods=['GET'])
def executive_summary():
    """Get executive summary metrics"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Total spend
    total_spend = db.session.query(func.sum(DailyCampaignPerformance.spend)).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).scalar() or 0
    
    # Total installs
    total_installs = db.session.query(func.sum(DailyCampaignPerformance.installs)).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).scalar() or 0
    
    # Blended CAC
    blended_cac = total_spend / total_installs if total_installs > 0 else 0
    
    # Total revenue
    total_revenue = db.session.query(func.sum(DailyCampaignPerformance.revenue_30d)).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).scalar() or 0
    
    # ROAS
    roas = total_revenue / total_spend if total_spend > 0 else 0
    
    # Organic installs
    organic_installs = db.session.query(func.sum(DailyOrganicMetric.organic_installs)).filter(
        DailyOrganicMetric.date >= start_date,
        DailyOrganicMetric.date <= end_date
    ).scalar() or 0
    
    return jsonify({
        'total_spend': round(total_spend, 2),
        'total_installs': int(total_installs),
        'organic_installs': int(organic_installs),
        'blended_cac': round(blended_cac, 2),
        'roas_30d': round(roas, 2),
        'ltv_cac_ratio': round(roas * 5, 2),  # Simplified
        'period_days': days
    })


@app.route('/api/executive/trends', methods=['GET'])
def executive_trends():
    """Get daily trends for executive dashboard"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Daily aggregates
    daily_data = db.session.query(
        DailyCampaignPerformance.date,
        func.sum(DailyCampaignPerformance.spend).label('spend'),
        func.sum(DailyCampaignPerformance.installs).label('installs'),
        func.avg(DailyCampaignPerformance.cpi).label('cpi')
    ).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).group_by(DailyCampaignPerformance.date).order_by(DailyCampaignPerformance.date).all()
    
    trends = [{
        'date': str(row.date),
        'spend': round(row.spend, 2),
        'installs': int(row.installs),
        'cpi': round(row.cpi, 2)
    } for row in daily_data]
    
    return jsonify(trends)


# ============================================================
# PAID MEDIA ENDPOINTS
# ============================================================

@app.route('/api/paid/channels', methods=['GET'])
def paid_channels():
    """Get channel performance comparison"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    channels = db.session.query(
        MarketingChannel.name,
        MarketingChannel.display_name,
        func.sum(DailyCampaignPerformance.spend).label('spend'),
        func.sum(DailyCampaignPerformance.installs).label('installs'),
        func.avg(DailyCampaignPerformance.cpi).label('cpi'),
        func.avg(DailyCampaignPerformance.roas_30d).label('roas')
    ).select_from(MarketingChannel
    ).join(Campaign, Campaign.channel_id == MarketingChannel.id
    ).join(DailyCampaignPerformance, DailyCampaignPerformance.campaign_id == Campaign.id
    ).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).group_by(MarketingChannel.id, MarketingChannel.name, MarketingChannel.display_name).all()
    
    result = [{
        'channel': row.name,
        'display_name': row.display_name,
        'spend': round(row.spend, 2),
        'installs': int(row.installs),
        'cpi': round(row.cpi, 2),
        'roas': round(row.roas, 2)
    } for row in channels]
    
    return jsonify(result)


@app.route('/api/paid/campaigns', methods=['GET'])
def paid_campaigns():
    """Get campaign performance"""
    days = int(request.args.get('days', 30))
    channel = request.args.get('channel')
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    query = db.session.query(
        Campaign.name,
        MarketingChannel.name.label('channel'),
        func.sum(DailyCampaignPerformance.spend).label('spend'),
        func.sum(DailyCampaignPerformance.installs).label('installs'),
        func.avg(DailyCampaignPerformance.cpi).label('cpi'),
        func.avg(DailyCampaignPerformance.roas_30d).label('roas')
    ).select_from(Campaign
    ).join(MarketingChannel, Campaign.channel_id == MarketingChannel.id
    ).join(DailyCampaignPerformance, DailyCampaignPerformance.campaign_id == Campaign.id
    ).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    )
    
    if channel:
        query = query.filter(MarketingChannel.name == channel)
    
    campaigns = query.group_by(Campaign.id, Campaign.name, MarketingChannel.name).all()
    
    result = [{
        'campaign': row.name,
        'channel': row.channel,
        'spend': round(row.spend, 2),
        'installs': int(row.installs),
        'cpi': round(row.cpi, 2),
        'roas': round(row.roas, 2)
    } for row in campaigns]
    
    return jsonify(result)


# ============================================================
# ORGANIC ENDPOINTS
# ============================================================

@app.route('/api/organic/summary', methods=['GET'])
def organic_summary():
    """Get organic performance summary"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    metrics = db.session.query(
        func.sum(DailyOrganicMetric.organic_installs).label('total_installs'),
        func.avg(DailyOrganicMetric.app_store_rank).label('avg_rank'),
        func.avg(DailyOrganicMetric.sentiment_score).label('avg_sentiment'),
        func.sum(DailyOrganicMetric.social_mentions).label('total_mentions')
    ).filter(
        DailyOrganicMetric.date >= start_date,
        DailyOrganicMetric.date <= end_date
    ).first()
    
    return jsonify({
        'organic_installs': int(metrics.total_installs or 0),
        'avg_app_store_rank': round(metrics.avg_rank or 0, 1),
        'avg_sentiment': round(metrics.avg_sentiment or 0, 2),
        'total_social_mentions': int(metrics.total_mentions or 0)
    })


@app.route('/api/organic/trends', methods=['GET'])
def organic_trends():
    """Get organic daily trends"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    daily_data = DailyOrganicMetric.query.filter(
        DailyOrganicMetric.date >= start_date,
        DailyOrganicMetric.date <= end_date
    ).order_by(DailyOrganicMetric.date).all()
    
    trends = [{
        'date': str(row.date),
        'organic_installs': row.organic_installs,
        'app_store_rank': row.app_store_rank,
        'sentiment_score': round(row.sentiment_score, 2)
    } for row in daily_data]
    
    return jsonify(trends)


# ============================================================
# FUNNEL ENDPOINTS
# ============================================================

@app.route('/api/funnel/summary', methods=['GET'])
def funnel_summary():
    """Get funnel summary metrics"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Aggregate funnel metrics
    metrics = db.session.query(
        func.sum(DailyCampaignPerformance.impressions).label('total_impressions'),
        func.sum(DailyCampaignPerformance.clicks).label('total_clicks'),
        func.sum(DailyCampaignPerformance.installs).label('total_installs'),
        func.sum(DailyCampaignPerformance.spend).label('total_spend'),
        func.avg(DailyCampaignPerformance.ctr).label('avg_ctr'),
        func.avg(DailyCampaignPerformance.cvr).label('avg_cvr'),
        func.avg(DailyCampaignPerformance.retention_d1).label('avg_d1'),
        func.avg(DailyCampaignPerformance.retention_d7).label('avg_d7')
    ).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).first()
    
    impressions = int(metrics.total_impressions or 0)
    clicks = int(metrics.total_clicks or 0)
    installs = int(metrics.total_installs or 0)
    spend = float(metrics.total_spend or 0)
    
    # Calculate derived metrics
    cpm = (spend / (impressions / 1000)) if impressions > 0 else 0
    cpc = (spend / clicks) if clicks > 0 else 0
    cpi = (spend / installs) if installs > 0 else 0
    
    return jsonify({
        'impressions': impressions,
        'clicks': clicks,
        'installs': installs,
        'spend': round(spend, 2),
        'cpm': round(cpm, 2),
        'cpc': round(cpc, 2),
        'cpi': round(cpi, 2),
        'ctr': round((metrics.avg_ctr or 0) * 100, 2),
        'cvr': round((metrics.avg_cvr or 0) * 100, 2),
        'retention_d1': round((metrics.avg_d1 or 0) * 100, 2),
        'retention_d7': round((metrics.avg_d7 or 0) * 100, 2)
    })


@app.route('/api/funnel/trends', methods=['GET'])
def funnel_trends():
    """Get funnel metrics over time"""
    days = int(request.args.get('days', 30))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    daily_data = db.session.query(
        DailyCampaignPerformance.date,
        func.sum(DailyCampaignPerformance.impressions).label('impressions'),
        func.sum(DailyCampaignPerformance.clicks).label('clicks'),
        func.sum(DailyCampaignPerformance.installs).label('installs'),
        func.avg(DailyCampaignPerformance.ctr).label('ctr'),
        func.avg(DailyCampaignPerformance.cvr).label('cvr')
    ).filter(
        DailyCampaignPerformance.date >= start_date,
        DailyCampaignPerformance.date <= end_date
    ).group_by(DailyCampaignPerformance.date
    ).order_by(DailyCampaignPerformance.date).all()
    
    trends = [{
        'date': str(row.date),
        'impressions': int(row.impressions or 0),
        'clicks': int(row.clicks or 0),
        'installs': int(row.installs or 0),
        'ctr': round((row.ctr or 0) * 100, 2),
        'cvr': round((row.cvr or 0) * 100, 2)
    } for row in daily_data]
    
    return jsonify(trends)


# ============================================================
# SIGNALS ENDPOINTS
# ============================================================

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get performance signals"""
    days = int(request.args.get('days', 7))
    severity = request.args.get('severity', 'all')
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    query = Signal.query.filter(
        Signal.date_detected >= start_date,
        Signal.date_detected <= end_date,
        Signal.is_dismissed == False
    )
    
    if severity != 'all':
        query = query.filter(Signal.severity == severity)
    
    signals = query.order_by(Signal.priority_score.desc()).all()
    
    result = [{
        'id': signal.id,
        'date': str(signal.date_detected),
        'type': signal.signal_type,
        'title': signal.title,
        'description': signal.description,
        'severity': signal.severity,
        'recommended_action': signal.recommended_action,
        'priority_score': round(signal.priority_score, 1),
        'confidence': round(signal.confidence, 2),
        'metrics': signal.get_metrics(),
        'predicted_impact': signal.get_predicted_impact()
    } for signal in signals]
    
    return jsonify(result)


@app.route('/api/signals/<int:signal_id>/dismiss', methods=['POST'])
def dismiss_signal(signal_id):
    """Dismiss a signal"""
    signal = Signal.query.get_or_404(signal_id)
    signal.is_dismissed = True
    signal.dismissed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})


# ============================================================
# SCENARIO ENDPOINTS
# ============================================================

@app.route('/api/scenarios/predict', methods=['POST'])
def predict_scenario():
    """Predict scenario outcomes (rule-based for now)"""
    data = request.json
    
    # Simple rule-based predictions
    budget_shift = data.get('budget_shift', {})
    
    # Calculate predicted impact
    predicted_impact = {
        'installs_change_pct': sum(budget_shift.values()) * 0.8,  # Simplified
        'cac_change_pct': -sum(budget_shift.values()) * 0.5,
        'estimated_monthly_impact': sum(budget_shift.values()) * 1000
    }
    
    return jsonify(predicted_impact)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database
        channel_count = MarketingChannel.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'channels': channel_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("OLIVE MARKETING INTELLIGENCE - BACKEND API")
    print("="*70)
    AppConfig.print_config()
    print("\nStarting server...")
    print(f"API available at: http://localhost:{AppConfig.API_PORT}")
    print(f"Health check: http://localhost:{AppConfig.API_PORT}/api/health")
    print("="*70 + "\n")
    
    # Database generation is now handled in create_app()
    
    app.run(
        host='0.0.0.0',
        port=AppConfig.API_PORT,
        debug=AppConfig.DEBUG
    )
