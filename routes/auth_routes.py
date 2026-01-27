"""
Authentication Routes
Handles login, signup, and session management
"""

from flask import Blueprint, request, jsonify, session
from services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """
    User registration endpoint
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123",
        "name": "John Doe"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Register user
        result = auth_service.register_user(email, password, name)
        
        if result['success']:
            # Set session
            session['user_email'] = result['user']['email']
            session['user_name'] = result['user']['name']
            session['user_role'] = result['user']['role']
            session.permanent = False
        
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'success': False, 'message': 'Signup failed'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Authenticate user
        result = auth_service.login_user(email, password)
        
        if result['success']:
            # Set session
            session['user_email'] = result['user']['email']
            session['user_name'] = result['user']['name']
            session['user_role'] = result['user']['role']
            session.permanent = False
        
        return jsonify(result), 200 if result['success'] else 401
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'success': True}), 200


@auth_bp.route('/api/session', methods=['GET'])
def check_session():
    """
    Check if user is logged in
    
    Returns:
    {
        "logged_in": true,
        "user": {
            "email": "user@example.com",
            "role": "viewer"
        }
    }
    """
    if 'user_email' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'email': session['user_email'],
                'role': session['user_role']
            }
        }), 200
    else:
        return jsonify({'logged_in': False}), 200