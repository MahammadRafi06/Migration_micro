#!/usr/bin/env python3
"""
Project & Task Service - Microservice for project and task management
Handles CRUD operations for projects and tasks, workflows, statuses, and priorities
"""

import os
import logging
import secrets
from datetime import datetime, date
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///project_task_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
    ACTIVITY_LOG_SERVICE_URL = os.environ.get('ACTIVITY_LOG_SERVICE_URL', 'http://localhost:5006')

# Application setup
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('project_task_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, nullable=False)  # Reference to user service
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'owner_id': self.owner_id,
            'task_count': self.tasks.count()
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(10), default='medium')
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer)  # Reference to user service
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'project_id': self.project_id,
            'assignee_id': self.assignee_id
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

def get_user_info(user_id: int, token: str) -> dict:
    """Get user info from User Service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{app.config['USER_SERVICE_URL']}/api/users/{user_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('user')
        return None
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
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
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:500]
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

# Project Routes
@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects():
    """Get all projects for current user"""
    try:
        user_id = request.current_user['id']
        projects = Project.query.filter_by(owner_id=user_id).all()
        
        return jsonify({
            'projects': [p.to_dict() for p in projects]
        })
        
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        return jsonify({'error': 'Failed to retrieve projects'}), 500

@app.route('/api/projects', methods=['POST'])
@token_required
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        
        # Validation
        if not data.get('name') or not data['name'].strip():
            return jsonify({'error': 'Project name is required'}), 400
        
        project = Project(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            status=data.get('status', 'active'),
            priority=data.get('priority', 'medium'),
            owner_id=user_id
        )
        
        # Validate dates
        try:
            if data.get('start_date'):
                project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if data.get('end_date'):
                project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate status and priority
        allowed_statuses = ['active', 'completed', 'archived']
        if project.status not in allowed_statuses:
            return jsonify({'error': f'Invalid status. Must be one of {allowed_statuses}'}), 400
        
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if project.priority not in allowed_priorities:
            return jsonify({'error': f'Invalid priority. Must be one of {allowed_priorities}'}), 400
        
        db.session.add(project)
        db.session.commit()
        
        log_activity(user_id, 'create', 'project', project.id, {'name': project.name})
        
        logger.info(f"Project created: {project.name} by user {user_id}")
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create project: {e}")
        return jsonify({'error': 'Failed to create project'}), 500

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    """Get a specific project"""
    try:
        user_id = request.current_user['id']
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'project': project.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        return jsonify({'error': 'Failed to retrieve project'}), 500

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@token_required
def update_project(project_id):
    """Update a project"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Update fields
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({'error': 'Project name cannot be empty'}), 400
            project.name = data['name'].strip()
        
        if 'description' in data:
            project.description = data['description'].strip()
        
        if 'status' in data:
            allowed_statuses = ['active', 'completed', 'archived']
            if data['status'] not in allowed_statuses:
                return jsonify({'error': f'Invalid status. Must be one of {allowed_statuses}'}), 400
            project.status = data['status']
        
        if 'priority' in data:
            allowed_priorities = ['low', 'medium', 'high', 'critical']
            if data['priority'] not in allowed_priorities:
                return jsonify({'error': f'Invalid priority. Must be one of {allowed_priorities}'}), 400
            project.priority = data['priority']
        
        # Update dates
        try:
            if 'start_date' in data:
                project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
            if 'end_date' in data:
                project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(user_id, 'update', 'project', project.id, data)
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update project {project_id}: {e}")
        return jsonify({'error': 'Failed to update project'}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id):
    """Delete a project"""
    try:
        user_id = request.current_user['id']
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project_name = project.name
        db.session.delete(project)
        db.session.commit()
        
        log_activity(user_id, 'delete', 'project', project_id, {'name': project_name})
        
        return jsonify({'message': 'Project deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete project {project_id}: {e}")
        return jsonify({'error': 'Failed to delete project'}), 500

# Task Routes
@app.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@token_required
def get_tasks(project_id):
    """Get all tasks for a project"""
    try:
        user_id = request.current_user['id']
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        tasks = project.tasks.all()
        return jsonify({'tasks': [t.to_dict() for t in tasks]})
        
    except Exception as e:
        logger.error(f"Failed to get tasks for project {project_id}: {e}")
        return jsonify({'error': 'Failed to retrieve tasks'}), 500

@app.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@token_required
def create_task(project_id):
    """Create a new task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Validation
        if not data.get('title') or not data['title'].strip():
            return jsonify({'error': 'Task title is required'}), 400
        
        task = Task(
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            project_id=project_id,
            estimated_hours=data.get('estimated_hours')
        )
        
        # Validate assignee
        if data.get('assignee_id'):
            assignee_info = get_user_info(data['assignee_id'], request.token)
            if not assignee_info:
                return jsonify({'error': 'Assignee user not found'}), 400
            task.assignee_id = data['assignee_id']
        
        # Parse due date
        try:
            if data.get('due_date'):
                task.due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400
        
        # Validate status and priority
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if task.status not in allowed_statuses:
            return jsonify({'error': f'Invalid status. Must be one of {allowed_statuses}'}), 400
        
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if task.priority not in allowed_priorities:
            return jsonify({'error': f'Invalid priority. Must be one of {allowed_priorities}'}), 400
        
        db.session.add(task)
        db.session.commit()
        
        log_activity(user_id, 'create', 'task', task.id, {'title': task.title, 'project_id': project_id})
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create task: {e}")
        return jsonify({'error': 'Failed to create task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = request.current_user['id']
        task = Task.query.join(Project).filter(
            Task.id == task_id,
            Project.owner_id == user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        return jsonify({'error': 'Failed to retrieve task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    """Update a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        task = Task.query.join(Project).filter(
            Task.id == task_id,
            Project.owner_id == user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Update fields
        if 'title' in data:
            if not data['title'].strip():
                return jsonify({'error': 'Task title cannot be empty'}), 400
            task.title = data['title'].strip()
        
        if 'description' in data:
            task.description = data['description'].strip()
        
        if 'status' in data:
            old_status = task.status
            allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if data['status'] not in allowed_statuses:
                return jsonify({'error': f'Invalid status. Must be one of {allowed_statuses}'}), 400
            task.status = data['status']
            
            # Handle completion
            if old_status != 'completed' and data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
            elif old_status == 'completed' and data['status'] != 'completed':
                task.completed_at = None
        
        if 'priority' in data:
            allowed_priorities = ['low', 'medium', 'high', 'critical']
            if data['priority'] not in allowed_priorities:
                return jsonify({'error': f'Invalid priority. Must be one of {allowed_priorities}'}), 400
            task.priority = data['priority']
        
        if 'assignee_id' in data:
            if data['assignee_id'] is not None:
                assignee_info = get_user_info(data['assignee_id'], request.token)
                if not assignee_info:
                    return jsonify({'error': 'Assignee user not found'}), 400
                task.assignee_id = data['assignee_id']
            else:
                task.assignee_id = None
        
        if 'estimated_hours' in data:
            try:
                task.estimated_hours = float(data['estimated_hours']) if data['estimated_hours'] is not None else None
                if task.estimated_hours is not None and task.estimated_hours < 0:
                    return jsonify({'error': 'Estimated hours cannot be negative'}), 400
            except ValueError:
                return jsonify({'error': 'Estimated hours must be a number'}), 400
        
        if 'actual_hours' in data:
            try:
                task.actual_hours = float(data['actual_hours']) if data['actual_hours'] is not None else None
                if task.actual_hours is not None and task.actual_hours < 0:
                    return jsonify({'error': 'Actual hours cannot be negative'}), 400
            except ValueError:
                return jsonify({'error': 'Actual hours must be a number'}), 400
        
        if 'due_date' in data:
            try:
                task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format'}), 400
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(user_id, 'update', 'task', task.id, data)
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update task {task_id}: {e}")
        return jsonify({'error': 'Failed to update task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = request.current_user['id']
        task = Task.query.join(Project).filter(
            Task.id == task_id,
            Project.owner_id == user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        
        log_activity(user_id, 'delete', 'task', task_id, {'title': task_title})
        
        return jsonify({'message': 'Task deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete task {task_id}: {e}")
        return jsonify({'error': 'Failed to delete task'}), 500

# Utility endpoint for other services
@app.route('/api/tasks/<int:task_id>/verify', methods=['POST'])
def verify_task_access():
    """Verify if a user has access to a task (for other services)"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        user_id = data.get('user_id')
        
        if not task_id or not user_id:
            return jsonify({'error': 'task_id and user_id required'}), 400
        
        task = Task.query.join(Project).filter(
            Task.id == task_id,
            Project.owner_id == user_id
        ).first()
        
        return jsonify({
            'has_access': task is not None,
            'task': task.to_dict() if task else None
        })
        
    except Exception as e:
        logger.error(f"Failed to verify task access: {e}")
        return jsonify({'error': 'Failed to verify access'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'service': 'project-task-service',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'project-task-service',
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
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5002)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
