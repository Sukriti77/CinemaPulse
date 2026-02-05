"""
Analytics Routes
Admin-only analytics API
"""

from flask import Blueprint, jsonify, session
from services.db_service import db_service

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        if 'user_email' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401

        if session.get('user_role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin privileges required.'
            }), 403

        analytics = db_service.get_analytics()
        movies = db_service.get_all_movies()

        formatted_movies = []
        for m in movies:
            formatted_movies.append({
                'id': m.get('movie_id'),
                'title': m.get('title'),
                'rating': float(m.get('avg_rating', 0)),
                'total_reviews': m.get('total_reviews', 0),
                'poster': m.get('poster_url', '/static/images/default-poster.jpg')
            })

        return jsonify({
            'success': True,
            'analytics': analytics,
            'movies': formatted_movies
        }), 200

    except Exception as e:
        print("Analytics route error:", e)
        return jsonify({'success': False, 'error': 'Failed to fetch analytics'}), 500
