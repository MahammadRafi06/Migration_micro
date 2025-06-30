#!/usr/bin/env python3
"""
User Service - Microservice for user management
Handles user registration, authentication, authorization, and profile management
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///user_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', 'False')
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
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
        logging.FileHandler('user_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }

# JWT Utilities
def generate_jwt_token(user_id: int) -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
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
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = User.query.get(request.current_user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

# Web authentication decorator for HTML pages
def web_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login_page'))
        
        payload = verify_jwt_token(session['user_token'])
        if not payload:
            session.pop('user_token', None)
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login_page'))
        
        request.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated

def web_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = User.query.get(request.current_user_id)
        if not user or not user.is_admin:
            flash('Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# HTML Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_token' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    """Show login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Show registration page"""
    return render_template('register.html')

@app.route('/dashboard')
@web_login_required
def dashboard():
    """User dashboard"""
    user = User.query.get(request.current_user_id)
    return render_template('dashboard.html', user=user)

@app.route('/profile')
@web_login_required
def profile_page():
    """User profile page"""
    user = User.query.get(request.current_user_id)
    return render_template('profile.html', user=user)

@app.route('/admin')
@web_login_required
@web_admin_required
def admin_panel():
    """Admin panel"""
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_token', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login_page'))

# Web form handlers
@app.route('/web/login', methods=['POST'])
def web_login():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Username and password are required.', 'error')
        return redirect(url_for('login_page'))
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        flash('Invalid username or password.', 'error')
        return redirect(url_for('login_page'))
    
    if not user.is_active:
        flash('Your account has been disabled.', 'error')
        return redirect(url_for('login_page'))
    
    # Update login info
    user.last_login = datetime.utcnow()
    user.login_count += 1
    db.session.commit()
    
    # Generate JWT token and store in session
    token = generate_jwt_token(user.id)
    session['user_token'] = token
    
    log_activity(user.id, 'login', 'user', user.id)
    
    flash(f'Welcome back, {user.full_name}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/web/register', methods=['POST'])
def web_register():
    """Handle registration form submission"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    full_name = request.form.get('full_name')
    
    # Validation
    if not all([username, email, password, confirm_password, full_name]):
        flash('All fields are required.', 'error')
        return redirect(url_for('register_page'))
    
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('register_page'))
    
    if len(password) < 8:
        flash('Password must be at least 8 characters long.', 'error')
        return redirect(url_for('register_page'))
    
    if '@' not in email or '.' not in email:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('register_page'))
    
    # Check existing users
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'error')
        return redirect(url_for('register_page'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'error')
        return redirect(url_for('register_page'))
    
    try:
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity(user.id, 'create', 'user', user.id, {'username': user.username})
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login_page'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {e}")
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('register_page'))

@app.route('/web/profile/update', methods=['POST'])
@web_login_required
def web_update_profile():
    """Handle profile update form submission"""
    user = User.query.get(request.current_user_id)
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    
    if not full_name or not email:
        flash('Full name and email are required.', 'error')
        return redirect(url_for('profile_page'))
    
    # Check if email already exists for another user
    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        flash('Email already exists.', 'error')
        return redirect(url_for('profile_page'))
    
    try:
        user.full_name = full_name
        user.email = email
        db.session.commit()
        
        log_activity(user.id, 'update', 'user', user.id, {'full_name': full_name, 'email': email})
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile_page'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update failed: {e}")
        flash('Profile update failed. Please try again.', 'error')
        return redirect(url_for('profile_page'))

@app.route('/web/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@web_login_required
@web_admin_required
def web_toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    user.is_active = not user.is_active
    db.session.commit()
    
    log_activity(request.current_user_id, 'admin_update', 'user', user_id, {'is_active': user.is_active})
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/web/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@web_login_required
@web_admin_required
def web_toggle_admin_status(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    log_activity(request.current_user_id, 'admin_update', 'user', user_id, {'is_admin': user.is_admin})
    
    status = 'granted admin privileges' if user.is_admin else 'removed admin privileges'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin_panel'))

# API Routes (existing routes remain unchanged)
@app.route('/api/', methods=['GET'])
def api_login_page():
    """Show login page for API"""
    logger.error(f"User accessed login page")
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Validation
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Basic validation
        if '@' not in data['email'] or '.' not in data['email']:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check existing users
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        log_activity(user.id, 'create', 'user', user.id, {'username': user.username})
        
        logger.info(f"New user registered: {user.username}")
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Update login info
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        log_activity(user.id, 'login', 'user', user.id)
        
        logger.info(f"User logged in: {user.username}")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Login failed: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token (for other services)"""
    try:
        data = request.get_json()
        token = data.get('token') if data else None
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return jsonify({'error': 'Token verification failed'}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    """Get user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return jsonify({'error': 'Failed to get user'}), 500

@app.route('/api/users/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Get current user details"""
    try:
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        return jsonify({'error': 'Failed to get user'}), 500

@app.route('/api/users/me', methods=['PUT'])
@jwt_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            if User.query.filter(User.email == data['email'], User.id != user.id).first():
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        
        db.session.commit()
        
        log_activity(user.id, 'update', 'user', user.id, data)
        
        logger.info(f"User profile updated: {user.username}")
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
@jwt_required
@admin_required
def admin_get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({'users': [u.to_dict() for u in users]})
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required
@admin_required
def admin_update_user(user_id):
    """Update user (admin only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        
        db.session.commit()
        
        log_activity(request.current_user_id, 'admin_update', 'user', user_id, data)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update user: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'service': 'user-service',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'user-service',
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
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created")

if __name__ == '__main__':
    init_db()
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5001)),
        debug=os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    )