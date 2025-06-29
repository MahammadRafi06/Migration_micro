#!/usr/bin/env python3
"""
Comment Service - Microservice for comment management
Handles CRUD operations for task-related comments and collaborative discussions
"""

import os
import logging
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///comment_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
    PROJECT_TASK_SERVICE_URL = os.environ.get('PROJECT_TASK_SERVICE_URL', 'http://localhost:5002')
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
        logging.FileHandler('comment_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_id = db.Column(db.Integer, nullable=False)  # Reference to project-task service
    author_id = db.Column(db.Integer, nullable=False)  # Reference to user service
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'task_id': self.task_id,
            'author_id': self.author_id
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

def verify_task_access(task_id: int, user_id: int) -> dict:
    """Verify task access with Project & Task Service"""
    try:
        response = requests.post(
            f"{app.config['PROJECT_TASK_SERVICE_URL']}/api/tasks/{task_id}/verify",
            json={'task_id': task_id, 'user_id': user_id},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Failed to verify task access: {e}")
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

# Comment Routes
@app.route('/api/tasks/<int:task_id>/comments', methods=['POST'])
@token_required
def add_comment(task_id):
    """Add a comment to a task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Task not found or access denied'}), 404
        
        if not data.get('content') or not data['content'].strip():
            return jsonify({'error': 'Comment content is required'}), 400
        
        comment = Comment(
            content=data['content'].strip(),
            task_id=task_id,
            author_id=user_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        log_activity(user_id, 'add_comment', 'comment', comment.id, {
            'task_id': task_id,
            'content_snippet': comment.content[:50]
        })
        
        # Get author info for response
        author_info = get_user_info(user_id, request.token)
        comment_dict = comment.to_dict()
        comment_dict['author_name'] = author_info.get('username') if author_info else 'Unknown'
        
        logger.info(f"Comment added to task {task_id} by user {user_id}")
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to add comment: {e}")
        return jsonify({'error': 'Failed to add comment'}), 500

@app.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
@token_required
def get_comments(task_id):
    """Get all comments for a task"""
    try:
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Task not found or access denied'}), 404
        
        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.asc()).all()
        
        # Enrich comments with author information
        enriched_comments = []
        for comment in comments:
            comment_dict = comment.to_dict()
            author_info = get_user_info(comment.author_id, request.token)
            comment_dict['author_name'] = author_info.get('username') if author_info else 'Unknown'
            enriched_comments.append(comment_dict)
        
        return jsonify({'comments': enriched_comments})
        
    except Exception as e:
        logger.error(f"Failed to get comments for task {task_id}: {e}")
        return jsonify({'error': 'Failed to retrieve comments'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['GET'])
@token_required
def get_comment(comment_id):
    """Get a specific comment"""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(comment.task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Enrich comment with author information
        comment_dict = comment.to_dict()
        author_info = get_user_info(comment.author_id, request.token)
        comment_dict['author_name'] = author_info.get('username') if author_info else 'Unknown'
        
        return jsonify({'comment': comment_dict})
        
    except Exception as e:
        logger.error(f"Failed to get comment {comment_id}: {e}")
        return jsonify({'error': 'Failed to retrieve comment'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
@token_required
def update_comment(comment_id):
    """Update a comment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user_id = request.current_user['id']
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        # Check if user is the author or has admin access
        current_user = request.current_user
        if comment.author_id != user_id:
            # Check if user has access to the task (project owner) or is admin
            task_access = verify_task_access(comment.task_id, user_id)
            if not (task_access and task_access.get('has_access')) and not current_user.get('is_admin'):
                return jsonify({'error': 'You do not have permission to edit this comment'}), 403
        
        if 'content' in data:
            if not data['content'].strip():
                return jsonify({'error': 'Comment content cannot be empty'}), 400
            
            comment.content = data['content'].strip()
            comment.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_activity(user_id, 'update', 'comment', comment.id, {
                'content_snippet': comment.content[:50]
            })
            
            # Enrich comment with author information
            comment_dict = comment.to_dict()
            author_info = get_user_info(comment.author_id, request.token)
            comment_dict['author_name'] = author_info.get('username') if author_info else 'Unknown'
            
            logger.info(f"Comment {comment_id} updated by user {user_id}")
            return jsonify({
                'message': 'Comment updated successfully',
                'comment': comment_dict
            })
        else:
            return jsonify({'error': 'No content provided for update'}), 400
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update comment {comment_id}: {e}")
        return jsonify({'error': 'Failed to update comment'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        user_id = request.current_user['id']
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        # Check if user is the author or has admin access
        current_user = request.current_user
        if comment.author_id != user_id:
            # Check if user has access to the task (project owner) or is admin
            task_access = verify_task_access(comment.task_id, user_id)
            if not (task_access and task_access.get('has_access')) and not current_user.get('is_admin'):
                return jsonify({'error': 'You do not have permission to delete this comment'}), 403
        
        comment_content_snippet = comment.content[:50]
        task_id = comment.task_id
        
        db.session.delete(comment)
        db.session.commit()
        
        log_activity(user_id, 'delete', 'comment', comment_id, {
            'task_id': task_id,
            'content_snippet': comment_content_snippet
        })
        
        logger.info(f"Comment {comment_id} deleted by user {user_id}")
        return jsonify({'message': 'Comment deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete comment {comment_id}: {e}")
        return jsonify({'error': 'Failed to delete comment'}), 500

# Utility endpoints for other services
@app.route('/api/comments/count/<int:task_id>', methods=['GET'])
def get_comment_count(task_id):
    """Get comment count for a task (for other services)"""
    try:
        count = Comment.query.filter_by(task_id=task_id).count()
        return jsonify({'task_id': task_id, 'comment_count': count})
    except Exception as e:
        logger.error(f"Failed to get comment count for task {task_id}: {e}")
        return jsonify({'error': 'Failed to get comment count'}), 500

@app.route('/api/comments/bulk-delete', methods=['POST'])
def bulk_delete_comments():
    """Bulk delete comments for tasks (for other services when tasks are deleted)"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({'error': 'No task IDs provided'}), 400
        
        deleted_count = Comment.query.filter(Comment.task_id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        logger.info(f"Bulk deleted {deleted_count} comments for tasks: {task_ids}")
        return jsonify({
            'message': f'Successfully deleted {deleted_count} comments',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to bulk delete comments: {e}")
        return jsonify({'error': 'Failed to bulk delete comments'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'service': 'comment-service',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'comment-service',
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
        port=int(os.environ.get('PORT', 5003)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
