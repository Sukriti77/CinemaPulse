"""
Movie Routes
Handles movie data endpoints
"""

from flask import Blueprint, jsonify
from services.db_service import db_service

movie_bp = Blueprint('movie', __name__)

@movie_bp.route('/api/movies', methods=['GET'])
def get_movies():
    """
    Get all movies
    
    Returns:
    {
        "success": true,
        "movies": [
            {
                "id": 1,
                "title": "Movie Title",
                "description": "...",
                "poster_url": "...",
                "avg_rating": 4.5,
                "total_reviews": 10
            }
        ]
    }
    """
    try:
        movies = db_service.get_all_movies()
        
        # Convert for frontend (handle both SQLite and DynamoDB formats)
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie.get('id') or movie.get('movie_id'),
                'title': movie.get('title'),
                'description': movie.get('description'),
                'poster': movie.get('poster_url'),
                'genre': movie.get('genre', 'General'),
                'rating': float(movie.get('avg_rating', 0)),
                'total_reviews': movie.get('total_reviews', 0)
            })
        
        return jsonify({
            'success': True,
            'movies': formatted_movies
        }), 200
        
    except Exception as e:
        print(f"Error getting movies: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch movies'}), 500


@movie_bp.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """
    Get movie by ID with reviews
    
    Returns:
    {
        "success": true,
        "movie": {
            "id": 1,
            "title": "...",
            "description": "...",
            "poster": "...",
            "rating": 4.5,
            "total_reviews": 10,
            "reviews": [...]
        }
    }
    """
    try:
        # Get movie
        movie = db_service.get_movie_by_id(movie_id)
        
        if not movie:
            return jsonify({'success': False, 'error': 'Movie not found'}), 404
        
        # Get feedback/reviews
        feedback = db_service.get_feedback_by_movie(movie_id)
        
        # Format reviews
        reviews = []
        for f in feedback:
            reviews.append({
                'name': f.get('user_email', '').split('@')[0].title(),  # Use email username as name
                'rating': f.get('rating'),
                'comment': f.get('comment'),
                'timestamp': f.get('timestamp', '')
            })
        
        # Format movie data
        formatted_movie = {
            'id': movie.get('id') or movie.get('movie_id'),
            'title': movie.get('title'),
            'description': movie.get('description'),
            'poster': movie.get('poster_url'),
            'genre': movie.get('genre', 'General'),
            'rating': float(movie.get('avg_rating', 0)),
            'total_reviews': movie.get('total_reviews', 0),
            'reviews': reviews
        }
        
        return jsonify({
            'success': True,
            'movie': formatted_movie
        }), 200
        
    except Exception as e:
        print(f"Error getting movie: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch movie'}), 500