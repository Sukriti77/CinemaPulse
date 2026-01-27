"""
Feedback Routes
Handles feedback submission
"""

from flask import Blueprint, request, jsonify, session
from services.db_service import db_service
from services.notification_service import notification_service
from services.sentiment_service import analyze_sentiment
feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit movie feedback
    
    Expected JSON:
    {
        "movie_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "rating": 5,
        "comment": "Great movie!"
    }
    
    Returns:
    {
        "success": true,
        "message": "Feedback submitted successfully"
    }
    """
    try:
        # Check if user is logged in
        if 'user_email' not in session:
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        data = request.get_json()
        
        # Extract data
        movie_id = data.get('movie_id')
        email = data.get('email', session['user_email'])
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        
        # Validation
        if not movie_id or not rating or not comment:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if movie exists
        movie = db_service.get_movie_by_id(movie_id)
        if not movie:
            return jsonify({'success': False, 'error': 'Movie not found'}), 404
        
        # Simple sentiment analysis (basic)
        sentiment_result = analyze_sentiment(comment, rating, method='vader')
        sentiment = sentiment_result['sentiment']

        # Save feedback
        feedback_id = db_service.create_feedback(
            movie_id=movie_id,
            user_email=email,
            rating=rating,
            comment=comment,
            sentiment=sentiment
        )
        
        if not feedback_id:
            return jsonify({'success': False, 'error': 'Failed to save feedback'}), 500
        
        # Send SNS notification (AWS only, mocked in local)
        notification_service.send_feedback_notification(
            movie_title=movie.get('title'),
            user_email=email,
            rating=rating,
            comment=comment
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_id
        }), 201
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'success': False, 'error': 'Failed to submit feedback'}), 500