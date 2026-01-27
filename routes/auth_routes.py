"""
Authentication Routes
Handles login, signup, and session management
"""

from flask import Blueprint, request, jsonify, session
from services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__)

# ================= SIGNUP =================

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json(force=True)

        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()

        result = auth_service.register_user(email, password, name)

        if not result['success']:
            return jsonify(result), 400

        # ✅ SESSION FIX
        session.clear()
        session['user_email'] = result['user']['email']
        session['user_role'] = result['user']['role']
        session.permanent = False

        return jsonify(result), 201

    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'success': False, 'message': 'Signup failed'}), 500


# ================= LOGIN =================

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)

        email = data.get('email', '').strip()
        password = data.get('password', '')

        result = auth_service.login_user(email, password)

        if not result['success']:
            return jsonify(result), 401

        # ✅ SESSION FIX (CRITICAL)
        session.clear()
        session['user_email'] = result['user']['email']
        session['user_role'] = result['user']['role']
        session.permanent = False

        return jsonify(result), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500


# ================= LOGOUT =================

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200


# ================= SESSION CHECK =================

@auth_bp.route('/api/session', methods=['GET'])
def check_session():
    if 'user_email' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'email': session['user_email'],
                'role': session.get('user_role', 'viewer')
            }
        }), 200

    return jsonify({'logged_in': False}), 200
