"""
Analytics Routes
Handles analytics data (admin only)
"""

from flask import Blueprint, jsonify, session
from services.db_service import db_service

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Get analytics data
    Admin only access
    
    Returns:
    {
        "success": true,
        "analytics": {
            "total_movies": 4,
            "total_reviews": 20,
            "overall_avg_rating": 4.6,
            "positive_percentage": 95.0
        },
        "movies": [
            {
                "id": 1,
                "title": "...",
                "rating": 4.8,
                "total_reviews": 5
            }
        ]
    }
    """
    try:
        # Check if user is logged in
        if 'user_email' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        # Role-based access (admin only for analytics)
        user_role = session.get('user_role')
        if user_role != 'admin':
            return jsonify({
                'success': False, 
                'error': 'Access denied. Admin privileges required.'
            }), 403
        
        # Get analytics data
        analytics = db_service.get_analytics()
        
        # Get all movies for detailed stats
        movies = db_service.get_all_movies()
        
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie.get('id') or movie.get('movie_id'),
                'title': movie.get('title'),
                'rating': float(movie.get('avg_rating', 0)),
                'total_reviews': movie.get('total_reviews', 0)
            })
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'movies': formatted_movies
        }), 200
        
    except Exception as e:
        print(f"Error getting analytics: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch analytics'}), 500