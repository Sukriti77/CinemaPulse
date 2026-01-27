"""
Admin Routes
Admin-only endpoints for managing movies
SQLite enabled locally, write operations disabled on AWS
"""

from config import get_config
config = get_config()

from flask import Blueprint, request, jsonify, session
from services.db_service import db_service
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin_api', __name__)

# Upload configuration
UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===================== UPLOAD POSTER =====================

@admin_bp.route('/api/admin/upload-poster', methods=['POST'])
def upload_poster():
    """Upload movie poster image (allowed on EC2)"""

    if 'user_email' not in session or session.get('user_role') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'File too large (max 5MB)'}), 400

    if file and allowed_file(file.filename):
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            filename = secure_filename(file.filename)
            import time
            filename = f"{int(time.time())}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            return jsonify({
                'success': True,
                'url': f'/static/images/uploads/{filename}',
                'message': 'Image uploaded successfully'
            }), 200

        except Exception as e:
            print(f"Upload error: {e}")
            return jsonify({'success': False, 'error': 'Failed to save file'}), 500

    return jsonify({'success': False, 'error': 'Invalid file type'}), 400


# ===================== ADD MOVIE =====================

@admin_bp.route('/api/admin/movies', methods=['POST'])
def add_movie():
    """Add new movie (SQLite only)"""

    if 'user_email' not in session or session.get('user_role') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    # 🚫 Disable write ops on AWS
    if config.ENV_MODE == "aws":
        return jsonify({
            "success": False,
            "error": "Admin write operations disabled in AWS demo"
        }), 403

    try:
        data = request.get_json()

        if not data.get('title') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Title and description are required'}), 400

        conn = db_service.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            INSERT INTO movies (title, description, poster_url, genre, avg_rating, total_reviews)
            VALUES (?, ?, ?, ?, 0, 0)
            ''',
            (
                data['title'],
                data['description'],
                data.get('poster_url', 'https://via.placeholder.com/400x600'),
                data.get('genre', 'General')
            )
        )

        movie_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'movie_id': movie_id,
            'message': 'Movie added successfully'
        }), 201

    except Exception as e:
        print(f"Error adding movie: {e}")
        return jsonify({'success': False, 'error': 'Failed to add movie'}), 500


# ===================== DELETE MOVIE =====================

@admin_bp.route('/api/admin/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """Delete movie (SQLite only)"""

    if 'user_email' not in session or session.get('user_role') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    # 🚫 Disable write ops on AWS
    if config.ENV_MODE == "aws":
        return jsonify({
            "success": False,
            "error": "Admin write operations disabled in AWS demo"
        }), 403

    try:
        conn = db_service.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM feedback WHERE movie_id = ?', (movie_id,))
        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Movie deleted successfully'
        }), 200

    except Exception as e:
        print(f"Error deleting movie: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete movie'}), 500


# ===================== GET ALL USERS =====================

@admin_bp.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users (SQLite only)"""

    if 'user_email' not in session or session.get('user_role') != 'admin':
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    # 🚫 Disable on AWS (no SQL)
    if config.ENV_MODE == "aws":
        return jsonify({
            "success": False,
            "error": "Admin user listing disabled in AWS demo"
        }), 403

    try:
        conn = db_service.db.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT email, name, role, created_at FROM users ORDER BY created_at DESC'
        )
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200

    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch users'}), 500
