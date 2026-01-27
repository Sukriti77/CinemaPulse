"""
CinemaPulse - Flask Application
Main entry point with API routes and session management
"""

from flask import Flask, render_template, session, redirect
from flask_session import Session
from config import get_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
config = get_config()
app.config.from_object(config)

# Initialize session
Session(app)

# ========== REGISTER API BLUEPRINTS ==========
from routes.auth_routes import auth_bp
from routes.movie_routes import movie_bp
from routes.feedback_routes import feedback_bp
from routes.analytics_routes import analytics_bp
from routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(admin_bp)

# ========== PAGE ROUTES (serve HTML templates) ==========

@app.route('/')
def login():
    """Login page - entry point"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard with movie list"""
    return render_template('index.html')

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Individual movie details page"""
    return render_template('movie.html', movie_id=movie_id)

@app.route('/feedback/<int:movie_id>')
def feedback_page(movie_id):
    """Feedback form for a specific movie"""
    return render_template('feedback.html', movie_id=movie_id)

@app.route('/thankyou')
def thankyou():
    """Confirmation page after feedback submission"""
    return render_template('thankyou.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Check if user is admin
    if 'user_email' not in session or session.get('user_role') != 'admin':
        return redirect('/')
    return render_template('analytics.html')

@app.route('/admin')
def admin():
    """Admin panel"""
    # Check if user is admin
    if 'user_email' not in session or session.get('user_role') != 'admin':
        return redirect('/')
    return render_template('admin.html')

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('login.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return {'error': 'Internal server error'}, 500

# ========== RUN APPLICATION ==========

if __name__ == '__main__':
    print(f"✓ CinemaPulse starting in {config.ENV_MODE.upper()} mode")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)