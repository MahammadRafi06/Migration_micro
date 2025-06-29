#!/usr/bin/env python3
"""
Activity Log Service - Microservice for activity logging and audit trail
Provides immutable audit trail of user and system actions across the application
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import redis
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///activity_log_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # Redis and Celery for cleanup tasks
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/2')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/2')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    
    # Data retention
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', 90))
    
    # Service URLs
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')

# Application setup
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Celery setup
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

class FlaskCeleryTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = FlaskCeleryTask

# Redis connection
try:
    redis_client = redis.from_url(app.config['REDIS_URL'])
    redis_client.ping()
    logger = logging.getLogger(__name__)
    logger.info("Successfully connected to Redis")
except redis.exceptions.ConnectionError as e:
    logging.error(f"Redis connection failed: {e}")
    redis_client = None

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('activity_log_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    details = db.Column(db.JSON)  # JSON data for flexible storage
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, index=True)  # Can be null for system actions
    session_id = db.Column(db.String(100))  # Optional session tracking
    service_name = db.Column(db.String(50))  # Which service logged this activity
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'service_name': self.service_name
        }

class ActivitySummary(db.Model):
    __tablename__ = 'activity_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    total_activities = db.Column(db.Integer, default=0)
    unique_users = db.Column(db.Integer, default=0)
    top_actions = db.Column(db.JSON)  # Store top actions with counts
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_activities': self.total_activities,
            'unique_users': self.unique_users,
            'top_actions': self.top_actions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Utility functions
def verify_user_token(token: str) -> dict:
    """Verify token with User Service"""
    try:
        response = requests.post(
            f"{app.config['USER_SERVICE_URL']}/api/verify-token",
            json={'token': token},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Failed to verify token: {e}")
        return None

def get_user_info(user_id: int) -> dict:
    """Get user info from User Service"""
    try:
        response = requests.get(
            f"{app.config['USER_SERVICE_URL']}/api/users/{user_id}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('user')
        return None
    except Exception as e:
        logger.error(f"Failed to get user info for user {user_id}: {e}")
        return None

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_data = verify_user_token(token)
        if not user_data or not user_data.get('valid'):
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.current_user = user_data['user']
        request.token = token
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

# Celery Tasks
@celery.task
def cleanup_old_logs():
    """Clean up old activity logs based on retention policy"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=app.config['LOG_RETENTION_DAYS'])
        
        # Count logs to be deleted
        count_to_delete = ActivityLog.query.filter(ActivityLog.created_at < cutoff_date).count()
        
        if count_to_delete > 0:
            # Delete old logs
            deleted_count = ActivityLog.query.filter(ActivityLog.created_at < cutoff_date).delete()
            db.session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old activity logs (older than {cutoff_date})")
            return {'status': 'success', 'deleted_count': deleted_count}
        else:
            logger.info("No old activity logs to clean up")
            return {'status': 'success', 'deleted_count': 0}
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to cleanup old logs: {e}")
        return {'status': 'error', 'message': str(e)}

@celery.task
def generate_daily_summary():
    """Generate daily activity summary"""
    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        
        # Check if summary already exists
        existing = ActivitySummary.query.filter_by(date=yesterday).first()
        if existing:
            logger.info(f"Daily summary for {yesterday} already exists")
            return {'status': 'skipped', 'message': 'Summary already exists'}
        
        # Calculate summary data
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        activities = ActivityLog.query.filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at < end_date
        ).all()
        
        if not activities:
            logger.info(f"No activities found for {yesterday}")
            return {'status': 'success', 'message': 'No activities to summarize'}
        
        # Calculate metrics
        total_activities = len(activities)
        unique_users = len(set(a.user_id for a in activities if a.user_id))
        
        # Top actions
        action_counts = {}
        for activity in activities:
            action_counts[activity.action] = action_counts.get(activity.action, 0) + 1
        
        top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_actions = [{'action': action, 'count': count} for action, count in top_actions]
        
        # Create summary
        summary = ActivitySummary(
            date=yesterday,
            total_activities=total_activities,
            unique_users=unique_users,
            top_actions=top_actions
        )
        
        db.session.add(summary)
        db.session.commit()
        
        logger.info(f"Generated daily summary for {yesterday}: {total_activities} activities, {unique_users} unique users")
        return {
            'status': 'success',
            'date': yesterday.isoformat(),
            'total_activities': total_activities,
            'unique_users': unique_users
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to generate daily summary: {e}")
        return {'status': 'error', 'message': str(e)}

# API Routes
@app.route('/api/activities', methods=['POST'])
def log_activity():
    """Log a new activity (called by other services)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Validation
        required_fields = ['action', 'entity_type', 'entity_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        activity = ActivityLog(
            user_id=data.get('user_id'),
            action=data['action'],
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            details=data.get('details'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            session_id=data.get('session_id'),
            service_name=data.get('service_name', 'unknown')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        logger.info(f"Activity logged: {activity.action} on {activity.entity_type}:{activity.entity_id} by user:{activity.user_id}")
        return jsonify({
            'message': 'Activity logged successfully',
            'activity_id': activity.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to log activity: {e}")
        return jsonify({'error': 'Failed to log activity'}), 500

@app.route('/api/activities', methods=['GET'])
@token_required
@admin_required
def get_activities():
    """Get activity logs with filtering (admin only)"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 1000)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = ActivityLog.query
        
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if action:
            query = query.filter(ActivityLog.action == action)
        if entity_type:
            query = query.filter(ActivityLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(ActivityLog.entity_id == entity_id)
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(ActivityLog.created_at >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(ActivityLog.created_at <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        # Order by latest first
        query = query.order_by(ActivityLog.created_at.desc())
        
        # Paginate
        activities = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enrich with user information
        enriched_activities = []
        for activity in activities.items:
            activity_dict = activity.to_dict()
            if activity.user_id:
                user_info = get_user_info(activity.user_id)
                activity_dict['username'] = user_info.get('username') if user_info else 'Unknown'
            else:
                activity_dict['username'] = 'System'
            enriched_activities.append(activity_dict)
        
        return jsonify({
            'activities': enriched_activities,
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get activities: {e}")
        return jsonify({'error': 'Failed to retrieve activities'}), 500

@app.route('/api/activities/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_activities(user_id):
    """Get activities for a specific user"""
    try:
        # Check if user can access these logs
        if user_id != request.current_user['id'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)
        action = request.args.get('action')
        entity_type = request.args.get('entity_type')
        
        query = ActivityLog.query.filter(ActivityLog.user_id == user_id)
        
        if action:
            query = query.filter(ActivityLog.action == action)
        if entity_type:
            query = query.filter(ActivityLog.entity_type == entity_type)
        
        activities = query.order_by(ActivityLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'activities': [a.to_dict() for a in activities.items],
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get user activities: {e}")
        return jsonify({'error': 'Failed to retrieve user activities'}), 500

@app.route('/api/activities/entity/<string:entity_type>/<int:entity_id>', methods=['GET'])
@token_required
@admin_required
def get_entity_activities(entity_type, entity_id):
    """Get activities for a specific entity (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)
        
        activities = ActivityLog.query.filter(
            ActivityLog.entity_type == entity_type,
            ActivityLog.entity_id == entity_id
        ).order_by(ActivityLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enrich with user information
        enriched_activities = []
        for activity in activities.items:
            activity_dict = activity.to_dict()
            if activity.user_id:
                user_info = get_user_info(activity.user_id)
                activity_dict['username'] = user_info.get('username') if user_info else 'Unknown'
            else:
                activity_dict['username'] = 'System'
            enriched_activities.append(activity_dict)
        
        return jsonify({
            'activities': enriched_activities,
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get entity activities: {e}")
        return jsonify({'error': 'Failed to retrieve entity activities'}), 500

@app.route('/api/activities/stats', methods=['GET'])
@token_required
@admin_required
def get_activity_stats():
    """Get activity statistics (admin only)"""
    try:
        # Time range parameters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic stats
        total_activities = ActivityLog.query.filter(ActivityLog.created_at >= start_date).count()
        unique_users = db.session.query(ActivityLog.user_id).filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.user_id.isnot(None)
        ).distinct().count()
        
        # Top actions
        action_stats = db.session.query(
            ActivityLog.action,
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.created_at >= start_date
        ).group_by(ActivityLog.action).order_by(db.text('count DESC')).limit(10).all()
        
        # Top entity types
        entity_stats = db.session.query(
            ActivityLog.entity_type,
            db.func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.created_at >= start_date
        ).group_by(ActivityLog.entity_type).order_by(db.text('count DESC')).limit(10).all()
        
        # Daily activity counts for the last 7 days
        daily_counts = []
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            start_dt = datetime.combine(date, datetime.min.time())
            end_dt = start_dt + timedelta(days=1)
            
            count = ActivityLog.query.filter(
                ActivityLog.created_at >= start_dt,
                ActivityLog.created_at < end_dt
            ).count()
            
            daily_counts.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return jsonify({
            'period_days': days,
            'total_activities': total_activities,
            'unique_users': unique_users,
            'top_actions': [{'action': action, 'count': count} for action, count in action_stats],
            'top_entity_types': [{'entity_type': entity_type, 'count': count} for entity_type, count in entity_stats],
            'daily_activity': list(reversed(daily_counts))
        })
        
    except Exception as e:
        logger.error(f"Failed to get activity stats: {e}")
        return jsonify({'error': 'Failed to retrieve activity statistics'}), 500

@app.route('/api/activities/summaries', methods=['GET'])
@token_required
@admin_required
def get_activity_summaries():
    """Get daily activity summaries (admin only)"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = (datetime.utcnow() - timedelta(days=days)).date()
        
        summaries = ActivitySummary.query.filter(
            ActivitySummary.date >= start_date
        ).order_by(ActivitySummary.date.desc()).all()
        
        return jsonify({
            'summaries': [s.to_dict() for s in summaries]
        })
        
    except Exception as e:
        logger.error(f"Failed to get activity summaries: {e}")
        return jsonify({'error': 'Failed to retrieve activity summaries'}), 500

# Maintenance endpoints
@app.route('/api/activities/cleanup', methods=['POST'])
@token_required
@admin_required
def trigger_cleanup():
    """Manually trigger cleanup of old logs (admin only)"""
    try:
        task = cleanup_old_logs.delay()
        return jsonify({
            'message': 'Cleanup task started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        logger.error(f"Failed to trigger cleanup: {e}")
        return jsonify({'error': 'Failed to trigger cleanup'}), 500

@app.route('/api/activities/generate-summary', methods=['POST'])
@token_required
@admin_required
def trigger_summary_generation():
    """Manually trigger daily summary generation (admin only)"""
    try:
        task = generate_daily_summary.delay()
        return jsonify({
            'message': 'Summary generation task started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        logger.error(f"Failed to trigger summary generation: {e}")
        return jsonify({'error': 'Failed to trigger summary generation'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        
        # Check Redis connection
        redis_status = 'disconnected'
        if redis_client:
            try:
                redis_client.ping()
                redis_status = 'connected'
            except:
                redis_status = 'disconnected'
        
        # Get basic stats
        total_logs = ActivityLog.query.count()
        recent_logs = ActivityLog.query.filter(
            ActivityLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return jsonify({
            'status': 'healthy',
            'service': 'activity-log-service',
            'timestamp': datetime.utcnow().isoformat(),
            'redis': redis_status,
            'total_logs': total_logs,
            'recent_logs_24h': recent_logs
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'activity-log-service',
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': str(error)}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal Server Error'}), 500

# Database initialization
def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

if __name__ == '__main__':
    init_db()
    
    # Schedule background tasks
    if redis_client:
        from celery.schedules import crontab
        celery.conf.beat_schedule = {
            'cleanup-old-logs': {
                'task': 'activity_log_service.cleanup_old_logs',
                'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
            },
            'generate-daily-summary': {
                'task': 'activity_log_service.generate_daily_summary',
                'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
            },
        }
        celery.conf.timezone = 'UTC'
        logger.info("Scheduled background tasks for log cleanup and summary generation")
    
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5006)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
