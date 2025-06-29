#!/usr/bin/env python3
"""
Notification Service - Microservice for notification management
Handles asynchronous communication like emails for task updates and project changes
"""

import os
import logging
import secrets
import smtplib
from datetime import datetime
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import redis
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///notification_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # Redis and Celery
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your_app_password')
    MAIL_FROM = os.environ.get('MAIL_FROM', 'noreply@taskapp.com')
    
    # Service URLs
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
    PROJECT_TASK_SERVICE_URL = os.environ.get('PROJECT_TASK_SERVICE_URL', 'http://localhost:5002')
    ACTIVITY_LOG_SERVICE_URL = os.environ.get('ACTIVITY_LOG_SERVICE_URL', 'http://localhost:5006')

# Application setup
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Celery setup
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Task base class to ensure app context for Celery tasks
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
        logging.FileHandler('notification_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class NotificationQueue(db.Model):
    __tablename__ = 'notification_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)  # User ID
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # email, sms, push, etc.
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, cancelled
    priority = db.Column(db.String(10), default='normal')  # low, normal, high
    context_data = db.Column(db.JSON)  # Additional context for the notification
    scheduled_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_email': self.recipient_email,
            'recipient_id': self.recipient_id,
            'subject': self.subject,
            'body': self.body,
            'notification_type': self.notification_type,
            'status': self.status,
            'priority': self.priority,
            'context_data': self.context_data,
            'scheduled_at': self.scheduled_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat(),
            'error_message': self.error_message,
            'retry_count': self.retry_count
        }

class NotificationTemplate(db.Model):
    __tablename__ = 'notification_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subject_template = db.Column(db.String(500), nullable=False)
    body_template = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject_template': self.subject_template,
            'body_template': self.body_template,
            'notification_type': self.notification_type,
            'is_active': self.is_active,
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
        # For internal service calls, we might need a service token or different auth
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

def log_activity(user_id: int, action: str, entity_type: str, entity_id: int, details: dict = None):
    """Log activity to Activity Log Service"""
    try:
        activity_data = {
            'user_id': user_id,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent', '')[:500] if request else None
        }
        
        response = requests.post(
            f"{app.config['ACTIVITY_LOG_SERVICE_URL']}/api/activities",
            json=activity_data,
            timeout=5
        )
        if response.status_code != 201:
            logger.warning(f"Failed to log activity: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

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

# Celery Tasks
@celery.task(bind=True)
def send_email_task(self, notification_id: int):
    """Send email asynchronously"""
    try:
        notification = NotificationQueue.query.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return {'status': 'error', 'message': 'Notification not found'}
        
        if notification.status != 'pending':
            logger.warning(f"Notification {notification_id} already processed with status: {notification.status}")
            return {'status': 'skipped', 'message': 'Notification already processed'}
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_FROM']
        msg['To'] = notification.recipient_email
        msg['Subject'] = notification.subject
        
        msg.attach(MIMEText(notification.body, 'html' if '<html>' in notification.body.lower() else 'plain'))
        
        # Send email
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            if app.config['MAIL_USE_TLS']:
                server.starttls()
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            server.send_message(msg)
        
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Email sent successfully to {notification.recipient_email} (notification {notification_id})")
        return {'status': 'success', 'message': 'Email sent successfully'}
        
    except Exception as e:
        logger.error(f"Failed to send email for notification {notification_id}: {e}")
        
        # Update notification with error
        notification = NotificationQueue.query.get(notification_id)
        if notification:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.retry_count += 1
            db.session.commit()
        
        # Retry with exponential backoff
        if self.request.retries < 3:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1), max_retries=3)
        
        return {'status': 'error', 'message': str(e)}

@celery.task
def process_notification_queue():
    """Process pending notifications in the queue"""
    try:
        # Get pending notifications ordered by priority and created time
        notifications = NotificationQueue.query.filter_by(
            status='pending'
        ).filter(
            NotificationQueue.scheduled_at <= datetime.utcnow()
        ).order_by(
            NotificationQueue.priority.desc(),
            NotificationQueue.created_at.asc()
        ).limit(50).all()  # Process in batches
        
        processed_count = 0
        for notification in notifications:
            if notification.notification_type == 'email':
                send_email_task.delay(notification.id)
                processed_count += 1
            # Add other notification types here (SMS, push, etc.)
        
        logger.info(f"Queued {processed_count} notifications for processing")
        return {'status': 'success', 'processed_count': processed_count}
        
    except Exception as e:
        logger.error(f"Failed to process notification queue: {e}")
        return {'status': 'error', 'message': str(e)}

# Template rendering
def render_template(template_name: str, context: dict) -> tuple:
    """Render notification template with context"""
    try:
        template = NotificationTemplate.query.filter_by(name=template_name, is_active=True).first()
        if not template:
            logger.error(f"Template {template_name} not found or inactive")
            return None, None
        
        subject = template.subject_template
        body = template.body_template
        
        # Simple template variable replacement
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        return subject, body
        
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}")
        return None, None

# API Routes
@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Queue a notification for sending"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Validation
        required_fields = ['recipient_id', 'notification_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get recipient info
        recipient = get_user_info(data['recipient_id'])
        if not recipient:
            return jsonify({'error': 'Recipient user not found'}), 404
        
        notification = NotificationQueue(
            recipient_email=recipient['email'],
            recipient_id=data['recipient_id'],
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            notification_type=data['notification_type'],
            priority=data.get('priority', 'normal'),
            context_data=data.get('context_data'),
            scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else datetime.utcnow()
        )
        
        # If template is provided, render it
        if data.get('template_name'):
            context = data.get('context_data', {})
            subject, body = render_template(data['template_name'], context)
            if subject and body:
                notification.subject = subject
                notification.body = body
        
        db.session.add(notification)
        db.session.commit()
        
        logger.info(f"Notification queued for user {data['recipient_id']}: {notification.subject}")
        return jsonify({
            'message': 'Notification queued successfully',
            'notification_id': notification.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to queue notification: {e}")
        return jsonify({'error': 'Failed to queue notification'}), 500

@app.route('/api/notifications/send-template', methods=['POST'])
def send_template_notification():
    """Send notification using a template"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        required_fields = ['recipient_id', 'template_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get recipient info
        recipient = get_user_info(data['recipient_id'])
        if not recipient:
            return jsonify({'error': 'Recipient user not found'}), 404
        
        # Render template
        context = data.get('context', {})
        context.update({
            'user_name': recipient.get('full_name', recipient.get('username')),
            'user_email': recipient.get('email')
        })
        
        subject, body = render_template(data['template_name'], context)
        if not subject or not body:
            return jsonify({'error': 'Failed to render template'}), 400
        
        notification = NotificationQueue(
            recipient_email=recipient['email'],
            recipient_id=data['recipient_id'],
            subject=subject,
            body=body,
            notification_type=data.get('notification_type', 'email'),
            priority=data.get('priority', 'normal'),
            context_data=context,
            scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        logger.info(f"Template notification queued for user {data['recipient_id']}: {subject}")
        return jsonify({
            'message': 'Template notification queued successfully',
            'notification_id': notification.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to queue template notification: {e}")
        return jsonify({'error': 'Failed to queue notification'}), 500

@app.route('/api/notifications/<int:notification_id>/status', methods=['GET'])
@token_required
def get_notification_status(notification_id):
    """Get notification status"""
    try:
        notification = NotificationQueue.query.get(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Check if user has access to this notification
        if notification.recipient_id != request.current_user['id'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'notification': notification.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get notification status: {e}")
        return jsonify({'error': 'Failed to get notification status'}), 500

@app.route('/api/notifications/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_notifications(user_id):
    """Get notifications for a user"""
    try:
        # Check if user has access
        if user_id != request.current_user['id'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        notifications = NotificationQueue.query.filter_by(
            recipient_id=user_id
        ).order_by(
            NotificationQueue.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications.items],
            'pagination': {
                'page': page,
                'pages': notifications.pages,
                'per_page': per_page,
                'total': notifications.total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get user notifications: {e}")
        return jsonify({'error': 'Failed to get notifications'}), 500

# Template management routes
@app.route('/api/notification-templates', methods=['GET'])
@token_required
def get_templates():
    """Get notification templates"""
    try:
        templates = NotificationTemplate.query.filter_by(is_active=True).all()
        return jsonify({'templates': [t.to_dict() for t in templates]})
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        return jsonify({'error': 'Failed to get templates'}), 500

@app.route('/api/notification-templates', methods=['POST'])
@token_required
def create_template():
    """Create notification template (admin only)"""
    try:
        if not request.current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        required_fields = ['name', 'subject_template', 'body_template', 'notification_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        template = NotificationTemplate(
            name=data['name'],
            subject_template=data['subject_template'],
            body_template=data['body_template'],
            notification_type=data['notification_type']
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create template: {e}")
        return jsonify({'error': 'Failed to create template'}), 500

# Webhook endpoints for other services
@app.route('/api/webhooks/task-assigned', methods=['POST'])
def task_assigned_webhook():
    """Handle task assignment notifications"""
    try:
        data = request.get_json()
        
        # Queue notification using template
        notification_data = {
            'recipient_id': data['assignee_id'],
            'template_name': 'task_assigned',
            'context': {
                'task_title': data['task_title'],
                'project_name': data.get('project_name', 'Unknown Project'),
                'assigned_by': data.get('assigned_by_name', 'System'),
                'due_date': data.get('due_date', 'Not specified')
            },
            'priority': 'normal'
        }
        
        # Call our own API to queue the notification
        response = requests.post(
            f"{request.url_root}api/notifications/send-template",
            json=notification_data
        )
        
        if response.status_code == 201:
            return jsonify({'message': 'Notification queued'}), 200
        else:
            logger.error(f"Failed to queue task assignment notification: {response.text}")
            return jsonify({'error': 'Failed to queue notification'}), 500
            
    except Exception as e:
        logger.error(f"Task assignment webhook failed: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@app.route('/api/webhooks/task-completed', methods=['POST'])
def task_completed_webhook():
    """Handle task completion notifications"""
    try:
        data = request.get_json()
        
        notification_data = {
            'recipient_id': data['project_owner_id'],
            'template_name': 'task_completed',
            'context': {
                'task_title': data['task_title'],
                'project_name': data.get('project_name', 'Unknown Project'),
                'completed_by': data.get('completed_by_name', 'System'),
                'completion_date': data.get('completion_date', datetime.utcnow().strftime('%Y-%m-%d'))
            },
            'priority': 'normal'
        }
        
        response = requests.post(
            f"{request.url_root}api/notifications/send-template",
            json=notification_data
        )
        
        if response.status_code == 201:
            return jsonify({'message': 'Notification queued'}), 200
        else:
            return jsonify({'error': 'Failed to queue notification'}), 500
            
    except Exception as e:
        logger.error(f"Task completion webhook failed: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

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
        
        return jsonify({
            'status': 'healthy',
            'service': 'notification-service',
            'timestamp': datetime.utcnow().isoformat(),
            'redis': redis_status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'notification-service',
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
    """Initialize database with default templates"""
    with app.app_context():
        db.create_all()
        
        # Create default notification templates
        default_templates = [
            {
                'name': 'task_assigned',
                'subject_template': 'Task Assigned: {{task_title}}',
                'body_template': '''
                <html>
                <body>
                    <p>Hello {{user_name}},</p>
                    
                    <p>You have been assigned a new task:</p>
                    
                    <h3>{{task_title}}</h3>
                    <p><strong>Project:</strong> {{project_name}}</p>
                    <p><strong>Assigned by:</strong> {{assigned_by}}</p>
                    <p><strong>Due Date:</strong> {{due_date}}</p>
                    
                    <p>Please log in to your task management system to view more details.</p>
                    
                    <p>Best regards,<br>Task Management System</p>
                </body>
                </html>
                ''',
                'notification_type': 'email'
            },
            {
                'name': 'task_completed',
                'subject_template': 'Task Completed: {{task_title}}',
                'body_template': '''
                <html>
                <body>
                    <p>Hello {{user_name}},</p>
                    
                    <p>A task in your project has been completed:</p>
                    
                    <h3>{{task_title}}</h3>
                    <p><strong>Project:</strong> {{project_name}}</p>
                    <p><strong>Completed by:</strong> {{completed_by}}</p>
                    <p><strong>Completion Date:</strong> {{completion_date}}</p>
                    
                    <p>Great progress on your project!</p>
                    
                    <p>Best regards,<br>Task Management System</p>
                </body>
                </html>
                ''',
                'notification_type': 'email'
            }
        ]
        
        for template_data in default_templates:
            existing = NotificationTemplate.query.filter_by(name=template_data['name']).first()
            if not existing:
                template = NotificationTemplate(**template_data)
                db.session.add(template)
        
        db.session.commit()
        logger.info("Database initialized with default templates")

if __name__ == '__main__':
    init_db()
    
    # Schedule background queue processing
    if redis_client:
        # Process notification queue every 2 minutes
        from celery.schedules import crontab
        celery.conf.beat_schedule = {
            'process-notification-queue': {
                'task': 'notification_service.process_notification_queue',
                'schedule': 120.0,  # every 2 minutes
            },
        }
        celery.conf.timezone = 'UTC'
        logger.info("Scheduled notification queue processing")
    
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5005)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
