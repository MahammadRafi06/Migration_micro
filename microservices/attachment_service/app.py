#!/usr/bin/env python3
"""
Attachment Service - Microservice for file attachment management
Handles secure storage, retrieval, and management of task-related file attachments
"""

import os
import logging
import secrets
import hashlib
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///attachment_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
    PROJECT_TASK_SERVICE_URL = os.environ.get('PROJECT_TASK_SERVICE_URL', 'http://localhost:5002')
    ACTIVITY_LOG_SERVICE_URL = os.environ.get('ACTIVITY_LOG_SERVICE_URL', 'http://localhost:5006')

# Application setup
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('attachment_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Models
class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Stored unique filename
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    file_hash = db.Column(db.String(64))  # SHA-256 hash
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, nullable=False)  # Reference to project-task service
    uploaded_by = db.Column(db.Integer, nullable=False)  # Reference to user service
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'created_at': self.created_at.isoformat(),
            'task_id': self.task_id,
            'uploaded_by': self.uploaded_by
        }

# Utility functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

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

# Attachment Routes
@app.route('/api/tasks/<int:task_id>/attachments', methods=['POST'])
@token_required
def upload_attachment(task_id):
    """Upload file attachment to a task"""
    try:
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Task not found or access denied'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided in the request'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed extensions: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        try:
            file.save(file_path)
        except Exception as e:
            logger.error(f"Failed to save file {original_filename}: {e}")
            return jsonify({'error': 'Failed to save file to server storage'}), 500
        
        # Calculate file hash and size
        file_hash = calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create attachment record
        attachment = Attachment(
            filename=unique_filename,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=file.content_type,
            file_hash=file_hash,
            task_id=task_id,
            uploaded_by=user_id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        log_activity(user_id, 'upload', 'attachment', attachment.id, {
            'filename': original_filename,
            'task_id': task_id,
            'file_size': file_size
        })
        
        # Enrich attachment with uploader info
        attachment_dict = attachment.to_dict()
        uploader_info = get_user_info(user_id, request.token)
        attachment_dict['uploaded_by_username'] = uploader_info.get('username') if uploader_info else 'Unknown'
        
        logger.info(f"File uploaded: {original_filename} for task {task_id} by user {user_id}")
        return jsonify({
            'message': 'File uploaded successfully',
            'attachment': attachment_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to upload attachment: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500

@app.route('/api/tasks/<int:task_id>/attachments', methods=['GET'])
@token_required
def get_task_attachments(task_id):
    """Get all attachments for a task"""
    try:
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Task not found or access denied'}), 404
        
        attachments = Attachment.query.filter_by(task_id=task_id).order_by(Attachment.created_at.desc()).all()
        
        # Enrich attachments with uploader information
        enriched_attachments = []
        for attachment in attachments:
            attachment_dict = attachment.to_dict()
            uploader_info = get_user_info(attachment.uploaded_by, request.token)
            attachment_dict['uploaded_by_username'] = uploader_info.get('username') if uploader_info else 'Unknown'
            enriched_attachments.append(attachment_dict)
        
        return jsonify({'attachments': enriched_attachments})
        
    except Exception as e:
        logger.error(f"Failed to get attachments for task {task_id}: {e}")
        return jsonify({'error': 'Failed to retrieve attachments'}), 500

@app.route('/api/attachments/<int:attachment_id>', methods=['GET'])
@token_required
def get_attachment(attachment_id):
    """Get attachment details"""
    try:
        attachment = Attachment.query.get(attachment_id)
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404
        
        user_id = request.current_user['id']
        
        # Verify task access
        task_access = verify_task_access(attachment.task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Enrich attachment with uploader information
        attachment_dict = attachment.to_dict()
        uploader_info = get_user_info(attachment.uploaded_by, request.token)
        attachment_dict['uploaded_by_username'] = uploader_info.get('username') if uploader_info else 'Unknown'
        
        return jsonify({'attachment': attachment_dict})
        
    except Exception as e:
        logger.error(f"Failed to get attachment {attachment_id}: {e}")
        return jsonify({'error': 'Failed to retrieve attachment'}), 500

@app.route('/api/attachments/<int:attachment_id>/download')
@token_required
def download_attachment(attachment_id):
    """Download a file attachment"""
    try:
        user_id = request.current_user['id']
        attachment = Attachment.query.get(attachment_id)
        
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404
        
        # Verify task access
        task_access = verify_task_access(attachment.task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Access denied'}), 403
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found on disk for attachment {attachment_id}: {file_path}")
            return jsonify({'error': 'File not found on server'}), 404
        
        log_activity(user_id, 'download', 'attachment', attachment.id, {
            'filename': attachment.original_filename
        })
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=attachment.original_filename,
            mimetype=attachment.mime_type or 'application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Failed to download attachment {attachment_id}: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/api/attachments/<int:attachment_id>', methods=['DELETE'])
@token_required
def delete_attachment(attachment_id):
    """Delete a file attachment"""
    try:
        user_id = request.current_user['id']
        attachment = Attachment.query.get(attachment_id)
        
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404
        
        # Verify task access
        task_access = verify_task_access(attachment.task_id, user_id)
        if not task_access or not task_access.get('has_access'):
            return jsonify({'error': 'Access denied'}), 403
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
        original_filename = attachment.original_filename
        task_id = attachment.task_id
        
        db.session.delete(attachment)
        db.session.commit()
        
        # Delete file from disk after database record is removed
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"File deleted from disk: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file from disk: {e}")
        else:
            logger.warning(f"File not found on disk during deletion: {file_path}")
        
        log_activity(user_id, 'delete', 'attachment', attachment_id, {
            'filename': original_filename,
            'task_id': task_id
        })
        
        logger.info(f"Attachment deleted: {original_filename} (ID: {attachment_id}) by user {user_id}")
        return jsonify({'message': 'Attachment deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete attachment {attachment_id}: {e}")
        return jsonify({'error': 'Failed to delete attachment'}), 500

# Utility endpoints for other services
@app.route('/api/attachments/count/<int:task_id>', methods=['GET'])
def get_attachment_count(task_id):
    """Get attachment count for a task (for other services)"""
    try:
        count = Attachment.query.filter_by(task_id=task_id).count()
        return jsonify({'task_id': task_id, 'attachment_count': count})
    except Exception as e:
        logger.error(f"Failed to get attachment count for task {task_id}: {e}")
        return jsonify({'error': 'Failed to get attachment count'}), 500

@app.route('/api/attachments/bulk-delete', methods=['POST'])
def bulk_delete_attachments():
    """Bulk delete attachments for tasks (for other services when tasks are deleted)"""
    try:
        data = request.get_json()
        task_ids = data.get('task_ids', [])
        
        if not task_ids:
            return jsonify({'error': 'No task IDs provided'}), 400
        
        # Get attachments to delete
        attachments = Attachment.query.filter(Attachment.task_id.in_(task_ids)).all()
        
        # Delete files from disk
        deleted_files = 0
        for attachment in attachments:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    logger.error(f"Failed to delete file {file_path}: {e}")
        
        # Delete database records
        deleted_count = Attachment.query.filter(Attachment.task_id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        logger.info(f"Bulk deleted {deleted_count} attachments ({deleted_files} files) for tasks: {task_ids}")
        return jsonify({
            'message': f'Successfully deleted {deleted_count} attachments',
            'deleted_count': deleted_count,
            'deleted_files': deleted_files
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to bulk delete attachments: {e}")
        return jsonify({'error': 'Failed to bulk delete attachments'}), 500

@app.route('/api/attachments/stats', methods=['GET'])
def get_attachment_stats():
    """Get attachment statistics (for reporting service)"""
    try:
        total_attachments = Attachment.query.count()
        total_size = db.session.query(db.func.sum(Attachment.file_size)).scalar() or 0
        
        # Get stats by file type
        type_stats = db.session.query(
            db.func.substr(Attachment.original_filename, db.func.instr(Attachment.original_filename, '.') + 1),
            db.func.count(),
            db.func.sum(Attachment.file_size)
        ).group_by(
            db.func.substr(Attachment.original_filename, db.func.instr(Attachment.original_filename, '.') + 1)
        ).all()
        
        file_types = []
        for ext, count, size in type_stats:
            if ext and '.' not in ext:  # Simple validation
                file_types.append({
                    'extension': ext.lower(),
                    'count': count,
                    'total_size': size or 0
                })
        
        return jsonify({
            'total_attachments': total_attachments,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_types': file_types
        })
        
    except Exception as e:
        logger.error(f"Failed to get attachment stats: {e}")
        return jsonify({'error': 'Failed to get attachment statistics'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        
        # Check upload directory
        upload_dir_writable = os.access(app.config['UPLOAD_FOLDER'], os.W_OK)
        
        return jsonify({
            'status': 'healthy',
            'service': 'attachment-service',
            'timestamp': datetime.utcnow().isoformat(),
            'upload_directory': app.config['UPLOAD_FOLDER'],
            'upload_dir_writable': upload_dir_writable
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'attachment-service',
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

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File Too Large', 'message': 'The uploaded file exceeds the maximum allowed size'}), 413

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
        port=int(os.environ.get('PORT', 5004)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )
