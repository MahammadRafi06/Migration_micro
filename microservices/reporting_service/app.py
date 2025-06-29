#!/usr/bin/env python3
"""
Reporting Service - Microservice for generating analytical insights and reports
Compiles and delivers comprehensive reports by aggregating data from other services
"""

import os
import logging
import secrets
import json
from datetime import datetime, timedelta, date
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import redis
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///reporting_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    
    # Redis and Celery for report generation
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/3')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/3')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
    
    # Service URLs
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
    PROJECT_TASK_SERVICE_URL = os.environ.get('PROJECT_TASK_SERVICE_URL', 'http://localhost:5002')
    COMMENT_SERVICE_URL = os.environ.get('COMMENT_SERVICE_URL', 'http://localhost:5003')
    ATTACHMENT_SERVICE_URL = os.environ.get('ATTACHMENT_SERVICE_URL', 'http://localhost:5004')
    ACTIVITY_LOG_SERVICE_URL = os.environ.get('ACTIVITY_LOG_SERVICE_URL', 'http://localhost:5006')

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
        logging.FileHandler('reporting_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # project, user, system, custom
    status = db.Column(db.String(20), default='pending')  # pending, generating, completed, failed
    parameters = db.Column(db.JSON)  # Report parameters
    data = db.Column(db.JSON)  # Generated report data
    generated_by = db.Column(db.Integer, nullable=False)  # User ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    file_path = db.Column(db.String(500))  # Optional file export path
    expires_at = db.Column(db.DateTime)  # Report expiration
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'report_type': self.report_type,
            'status': self.status,
            'parameters': self.parameters,
            'data': self.data,
            'generated_by': self.generated_by,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'file_path': self.file_path,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50), nullable=False)
    template_config = db.Column(db.JSON)  # Template configuration
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type,
            'template_config': self.template_config,
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

def get_service_data(service_url: str, endpoint: str, headers: dict = None) -> dict:
    """Get data from a service endpoint"""
    try:
        response = requests.get(f"{service_url}{endpoint}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get data from {service_url}{endpoint}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting data from {service_url}{endpoint}: {e}")
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
@celery.task(bind=True)
def generate_project_report(self, report_id: int):
    """Generate comprehensive project report"""
    try:
        report = Report.query.get(report_id)
        if not report:
            logger.error(f"Report {report_id} not found")
            return {'status': 'error', 'message': 'Report not found'}
        
        report.status = 'generating'
        db.session.commit()
        
        project_id = report.parameters.get('project_id')
        if not project_id:
            raise ValueError("Project ID is required for project report")
        
        # Get project data
        headers = {'Authorization': f'Bearer {report.parameters.get("token")}'}
        
        project_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            f'/api/projects/{project_id}',
            headers
        )
        
        if not project_data:
            raise ValueError("Failed to get project data")
        
        project = project_data.get('project')
        
        # Get tasks data
        tasks_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            f'/api/projects/{project_id}/tasks',
            headers
        )
        
        tasks = tasks_data.get('tasks', []) if tasks_data else []
        
        # Calculate project metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
        pending_tasks = len([t for t in tasks if t['status'] == 'pending'])
        in_progress_tasks = len([t for t in tasks if t['status'] == 'in_progress'])
        cancelled_tasks = len([t for t in tasks if t['status'] == 'cancelled'])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate time metrics
        total_estimated_hours = sum(t.get('estimated_hours', 0) or 0 for t in tasks)
        total_actual_hours = sum(t.get('actual_hours', 0) or 0 for t in tasks)
        
        # Priority breakdown
        priority_counts = {}
        for task in tasks:
            priority = task.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Get comments count for each task
        comment_counts = {}
        attachment_counts = {}
        
        for task in tasks:
            task_id = task['id']
            
            # Get comment count
            comment_data = get_service_data(
                app.config['COMMENT_SERVICE_URL'],
                f'/api/comments/count/{task_id}'
            )
            comment_counts[task_id] = comment_data.get('comment_count', 0) if comment_data else 0
            
            # Get attachment count
            attachment_data = get_service_data(
                app.config['ATTACHMENT_SERVICE_URL'],
                f'/api/attachments/count/{task_id}'
            )
            attachment_counts[task_id] = attachment_data.get('attachment_count', 0) if attachment_data else 0
        
        # Build comprehensive report
        report_data = {
            'project': project,
            'summary': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'cancelled_tasks': cancelled_tasks,
                'completion_rate': round(completion_rate, 2),
                'total_estimated_hours': total_estimated_hours,
                'total_actual_hours': total_actual_hours,
                'efficiency_ratio': round((total_actual_hours / total_estimated_hours * 100), 2) if total_estimated_hours > 0 else 0
            },
            'priority_breakdown': priority_counts,
            'tasks': tasks,
            'task_comments': comment_counts,
            'task_attachments': attachment_counts,
            'total_comments': sum(comment_counts.values()),
            'total_attachments': sum(attachment_counts.values()),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Cache in Redis if available
        if redis_client:
            try:
                cache_key = f"project_report:{project_id}"
                redis_client.setex(cache_key, 3600, json.dumps(report_data))  # 1 hour cache
                logger.info(f"Cached project report {project_id} in Redis")
            except Exception as redis_e:
                logger.warning(f"Failed to cache report in Redis: {redis_e}")
        
        # Update report
        report.status = 'completed'
        report.data = report_data
        report.completed_at = datetime.utcnow()
        report.expires_at = datetime.utcnow() + timedelta(days=7)  # Expire in 7 days
        db.session.commit()
        
        logger.info(f"Generated project report for project {project_id}")
        return {'status': 'success', 'report_id': report_id}
        
    except Exception as e:
        logger.error(f"Failed to generate project report {report_id}: {e}")
        
        # Update report with error
        report = Report.query.get(report_id)
        if report:
            report.status = 'failed'
            report.error_message = str(e)
            report.completed_at = datetime.utcnow()
            db.session.commit()
        
        return {'status': 'error', 'message': str(e)}

@celery.task(bind=True)
def generate_system_overview_report(self, report_id: int):
    """Generate system-wide overview report"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return {'status': 'error', 'message': 'Report not found'}
        
        report.status = 'generating'
        db.session.commit()
        
        # Get data from all services
        headers = {'Authorization': f'Bearer {report.parameters.get("token")}'}
        
        # User statistics
        user_stats = get_service_data(
            app.config['USER_SERVICE_URL'],
            '/api/admin/users',
            headers
        )
        
        # Project and task statistics
        projects_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            '/api/projects',
            headers
        )
        
        # Activity statistics
        activity_stats = get_service_data(
            app.config['ACTIVITY_LOG_SERVICE_URL'],
            '/api/activities/stats?days=30',
            headers
        )
        
        # Attachment statistics
        attachment_stats = get_service_data(
            app.config['ATTACHMENT_SERVICE_URL'],
            '/api/attachments/stats'
        )
        
        # Calculate metrics
        total_users = len(user_stats.get('users', [])) if user_stats else 0
        active_users = len([u for u in user_stats.get('users', []) if u.get('is_active')]) if user_stats else 0
        
        projects = projects_data.get('projects', []) if projects_data else []
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') == 'active'])
        
        # Get all tasks from all projects
        all_tasks = []
        if projects:
            for project in projects:
                tasks_data = get_service_data(
                    app.config['PROJECT_TASK_SERVICE_URL'],
                    f'/api/projects/{project["id"]}/tasks',
                    headers
                )
                if tasks_data:
                    all_tasks.extend(tasks_data.get('tasks', []))
        
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.get('status') == 'completed'])
        
        # Build system overview
        system_overview = {
            'users': {
                'total': total_users,
                'active': active_users,
                'admin_count': len([u for u in user_stats.get('users', []) if u.get('is_admin')]) if user_stats else 0
            },
            'projects': {
                'total': total_projects,
                'active': active_projects,
                'completed': len([p for p in projects if p.get('status') == 'completed']),
                'archived': len([p for p in projects if p.get('status') == 'archived'])
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': len([t for t in all_tasks if t.get('status') == 'pending']),
                'in_progress': len([t for t in all_tasks if t.get('status') == 'in_progress']),
                'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
            },
            'activity': activity_stats if activity_stats else {'total_activities': 0, 'unique_users': 0},
            'attachments': attachment_stats if attachment_stats else {'total_attachments': 0, 'total_size_mb': 0},
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Update report
        report.status = 'completed'
        report.data = system_overview
        report.completed_at = datetime.utcnow()
        report.expires_at = datetime.utcnow() + timedelta(hours=6)  # Expire in 6 hours
        db.session.commit()
        
        logger.info(f"Generated system overview report")
        return {'status': 'success', 'report_id': report_id}
        
    except Exception as e:
        logger.error(f"Failed to generate system overview report: {e}")
        
        report = Report.query.get(report_id)
        if report:
            report.status = 'failed'
            report.error_message = str(e)
            report.completed_at = datetime.utcnow()
            db.session.commit()
        
        return {'status': 'error', 'message': str(e)}

# API Routes
@app.route('/api/reports', methods=['POST'])
@token_required
def generate_report():
    """Generate a new report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        
        # Validation
        required_fields = ['name', 'report_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user can generate this type of report
        if data['report_type'] in ['system', 'admin'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required for this report type'}), 403
        
        # Create report record
        report = Report(
            name=data['name'],
            report_type=data['report_type'],
            parameters=data.get('parameters', {}),
            generated_by=user_id,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Default 7 days expiration
        )
        
        # Add token to parameters for service calls
        report.parameters['token'] = request.token
        
        db.session.add(report)
        db.session.commit()
        
        # Queue report generation based on type
        if data['report_type'] == 'project':
            generate_project_report.delay(report.id)
        elif data['report_type'] == 'system':
            generate_system_overview_report.delay(report.id)
        else:
            report.status = 'failed'
            report.error_message = f"Unsupported report type: {data['report_type']}"
            db.session.commit()
            return jsonify({'error': 'Unsupported report type'}), 400
        
        logger.info(f"Report generation started: {report.name} (ID: {report.id}) by user {user_id}")
        return jsonify({
            'message': 'Report generation started',
            'report_id': report.id,
            'status': 'pending'
        }), 202
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to start report generation: {e}")
        return jsonify({'error': 'Failed to start report generation'}), 500

@app.route('/api/reports/<int:report_id>', methods=['GET'])
@token_required
def get_report(report_id):
    """Get a specific report"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check access permissions
        if report.generated_by != request.current_user['id'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if report has expired
        if report.expires_at and report.expires_at < datetime.utcnow():
            return jsonify({'error': 'Report has expired'}), 410
        
        return jsonify({'report': report.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get report {report_id}: {e}")
        return jsonify({'error': 'Failed to retrieve report'}), 500

@app.route('/api/reports', methods=['GET'])
@token_required
def get_user_reports():
    """Get reports for current user"""
    try:
        user_id = request.current_user['id']
        is_admin = request.current_user.get('is_admin', False)
        
        # Admin can see all reports, regular users only their own
        if is_admin:
            query = Report.query
        else:
            query = Report.query.filter(Report.generated_by == user_id)
        
        # Filter parameters
        report_type = request.args.get('report_type')
        status = request.args.get('status')
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        if status:
            query = query.filter(Report.status == status)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        reports = query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enrich with user information
        enriched_reports = []
        for report in reports.items:
            report_dict = report.to_dict()
            if is_admin:
                user_info = get_user_info(report.generated_by)
                report_dict['generated_by_username'] = user_info.get('username') if user_info else 'Unknown'
            enriched_reports.append(report_dict)
        
        return jsonify({
            'reports': enriched_reports,
            'pagination': {
                'page': page,
                'pages': reports.pages,
                'per_page': per_page,
                'total': reports.total
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        return jsonify({'error': 'Failed to retrieve reports'}), 500

@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
@token_required
def delete_report(report_id):
    """Delete a report"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if report.generated_by != request.current_user['id'] and not request.current_user.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        report_name = report.name
        db.session.delete(report)
        db.session.commit()
        
        logger.info(f"Report deleted: {report_name} (ID: {report_id})")
        return jsonify({'message': 'Report deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete report {report_id}: {e}")
        return jsonify({'error': 'Failed to delete report'}), 500

# Quick report endpoints
@app.route('/api/reports/quick/project-summary/<int:project_id>', methods=['GET'])
@token_required
def quick_project_summary(project_id):
    """Get quick project summary (cached if available)"""
    try:
        # Check Redis cache first
        cache_key = f"project_report:{project_id}"
        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Serving cached project summary for project {project_id}")
                    return jsonify(json.loads(cached_data))
            except Exception as redis_e:
                logger.warning(f"Redis cache error: {redis_e}")
        
        # Generate quick summary
        headers = {'Authorization': request.headers.get('Authorization')}
        
        project_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            f'/api/projects/{project_id}',
            headers
        )
        
        if not project_data:
            return jsonify({'error': 'Project not found or access denied'}), 404
        
        tasks_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            f'/api/projects/{project_id}/tasks',
            headers
        )
        
        tasks = tasks_data.get('tasks', []) if tasks_data else []
        
        # Quick metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        quick_summary = {
            'project': project_data.get('project'),
            'quick_metrics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round(completion_rate, 2),
                'pending_tasks': len([t for t in tasks if t['status'] == 'pending']),
                'in_progress_tasks': len([t for t in tasks if t['status'] == 'in_progress'])
            },
            'generated_at': datetime.utcnow().isoformat(),
            'cache_duration': '1 hour'
        }
        
        # Cache for future requests
        if redis_client:
            try:
                redis_client.setex(cache_key, 3600, json.dumps(quick_summary))
            except Exception as redis_e:
                logger.warning(f"Failed to cache quick summary: {redis_e}")
        
        return jsonify(quick_summary)
        
    except Exception as e:
        logger.error(f"Failed to generate quick project summary: {e}")
        return jsonify({'error': 'Failed to generate project summary'}), 500

@app.route('/api/reports/quick/dashboard', methods=['GET'])
@token_required
def quick_dashboard():
    """Get quick dashboard metrics for current user"""
    try:
        user_id = request.current_user['id']
        headers = {'Authorization': request.headers.get('Authorization')}
        
        # Get user's projects
        projects_data = get_service_data(
            app.config['PROJECT_TASK_SERVICE_URL'],
            '/api/projects',
            headers
        )
        
        projects = projects_data.get('projects', []) if projects_data else []
        
        # Get all user's tasks
        all_tasks = []
        for project in projects:
            tasks_data = get_service_data(
                app.config['PROJECT_TASK_SERVICE_URL'],
                f'/api/projects/{project["id"]}/tasks',
                headers
            )
            if tasks_data:
                # Filter tasks assigned to current user
                user_tasks = [t for t in tasks_data.get('tasks', []) if t.get('assignee_id') == user_id]
                all_tasks.extend(user_tasks)
        
        # Calculate metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') == 'active'])
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.get('status') == 'completed'])
        overdue_tasks = []
        
        # Check for overdue tasks
        today = datetime.utcnow()
        for task in all_tasks:
            if task.get('due_date') and task.get('status') not in ['completed', 'cancelled']:
                due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                if due_date < today:
                    overdue_tasks.append(task)
        
        dashboard_metrics = {
            'user_id': user_id,
            'username': request.current_user.get('username'),
            'projects': {
                'total': total_projects,
                'active': active_projects
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': len([t for t in all_tasks if t.get('status') == 'pending']),
                'in_progress': len([t for t in all_tasks if t.get('status') == 'in_progress']),
                'overdue': len(overdue_tasks)
            },
            'overdue_tasks': [
                {
                    'id': t['id'],
                    'title': t['title'],
                    'due_date': t['due_date'],
                    'project_id': t['project_id']
                } for t in overdue_tasks[:5]  # Limit to 5 most recent
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_metrics)
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard metrics: {e}")
        return jsonify({'error': 'Failed to generate dashboard metrics'}), 500

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
        total_reports = Report.query.count()
        pending_reports = Report.query.filter_by(status='pending').count()
        
        return jsonify({
            'status': 'healthy',
            'service': 'reporting-service',
            'timestamp': datetime.utcnow().isoformat(),
            'redis': redis_status,
            'total_reports': total_reports,
            'pending_reports': pending_reports
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'reporting-service',
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

@app.errorhandler(410)
def gone(error):
    return jsonify({'error': 'Gone', 'message': 'Resource has expired'}), 410

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal Server Error'}), 500

# Database initialization
def init_db():
    """Initialize database with default templates"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

if __name__ == '__main__':
    init_db()
    
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5007)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
