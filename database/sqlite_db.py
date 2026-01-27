"""
SQLite Database Implementation for Local Development
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class SQLiteDatabase:
    def __init__(self, db_path='cinema_pulse.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'viewer')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                poster_url TEXT,
                genre TEXT DEFAULT 'General',
                avg_rating REAL DEFAULT 0,
                total_reviews INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                sentiment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert default data
        self.seed_default_data()
    
    def seed_default_data(self):
        """Insert default users and movies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) as count FROM users')
        if cursor.fetchone()['count'] > 0:
            conn.close()
            return
        
        # Import auth service for password hashing
        import hashlib
        import secrets
        
        def hash_password(password):
            salt = secrets.token_hex(16)
            pwd_salt = f"{password}{salt}".encode('utf-8')
            hashed = hashlib.sha256(pwd_salt).hexdigest()
            return hashed, salt
        
        # Insert default users with hashed passwords
        admin_pwd, admin_salt = hash_password('admin123')
        viewer_pwd, viewer_salt = hash_password('viewer123')
        
        default_users = [
            ('admin@cinemapulse.com', admin_pwd, admin_salt, 'Admin User', 'admin'),
            ('viewer@cinemapulse.com', viewer_pwd, viewer_salt, 'Viewer User', 'viewer')
        ]
        cursor.executemany('INSERT INTO users (email, password, salt, name, role) VALUES (?, ?, ?, ?, ?)', default_users)
        
        # Insert default movies
        default_movies = [
            ('The Shawshank Redemption', 
             'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
             'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400',
             'Drama',
             4.8, 2),
            ('Inception',
             'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.',
             'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400',
             'Sci-Fi',
             4.5, 2),
            ('The Dark Knight',
             'When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests.',
             'https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400',
             'Action',
             4.7, 2),
            ('Interstellar',
             'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
             'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400',
             'Sci-Fi',
             4.6, 2)
        ]
        cursor.executemany('''
            INSERT INTO movies (title, description, poster_url, genre, avg_rating, total_reviews) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', default_movies)
        
        # Insert sample feedback
        sample_feedback = [
            (1, 'admin@cinemapulse.com', 5, 'Absolutely masterful storytelling!', 'positive'),
            (1, 'viewer@cinemapulse.com', 5, 'A timeless classic that never gets old.', 'positive'),
            (2, 'admin@cinemapulse.com', 5, 'Mind-bending and brilliant!', 'positive'),
            (2, 'viewer@cinemapulse.com', 4, 'Complex but rewarding watch.', 'positive'),
            (3, 'admin@cinemapulse.com', 5, 'Heath Ledger\'s performance is legendary.', 'positive'),
            (3, 'viewer@cinemapulse.com', 5, 'The best superhero movie ever made.', 'positive'),
            (4, 'admin@cinemapulse.com', 5, 'Scientifically stunning and emotionally powerful.', 'positive'),
            (4, 'viewer@cinemapulse.com', 4, 'Beautiful visuals and touching story.', 'positive')
        ]
        cursor.executemany('''
            INSERT INTO feedback (movie_id, user_email, rating, comment, sentiment) 
            VALUES (?, ?, ?, ?, ?)
        ''', sample_feedback)
        
        conn.commit()
        conn.close()
    
    # ========== USER OPERATIONS ==========
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def create_user(self, email: str, role: str = 'viewer') -> bool:
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, role) VALUES (?, ?)', (email, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    # ========== MOVIE OPERATIONS ==========
    
    def get_all_movies(self) -> List[Dict]:
        """Get all movies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies ORDER BY avg_rating DESC')
        movies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return movies
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        """Get movie by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        movie = cursor.fetchone()
        conn.close()
        return dict(movie) if movie else None
    
    def update_movie_rating(self, movie_id: int):
        """Recalculate and update movie average rating"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_reviews
            FROM feedback
            WHERE movie_id = ?
        ''', (movie_id,))
        
        result = cursor.fetchone()
        avg_rating = round(result['avg_rating'], 1) if result['avg_rating'] else 0
        total_reviews = result['total_reviews']
        
        cursor.execute('''
            UPDATE movies 
            SET avg_rating = ?, total_reviews = ?
            WHERE id = ?
        ''', (avg_rating, total_reviews, movie_id))
        
        conn.commit()
        conn.close()
    
    # ========== FEEDBACK OPERATIONS ==========
    
    def create_feedback(self, movie_id: int, user_email: str, rating: int, 
                       comment: str, sentiment: str = 'neutral') -> int:
        """Create new feedback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (movie_id, user_email, rating, comment, sentiment)
            VALUES (?, ?, ?, ?, ?)
        ''', (movie_id, user_email, rating, comment, sentiment))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update movie rating
        self.update_movie_rating(movie_id)
        
        return feedback_id
    
    def get_feedback_by_movie(self, movie_id: int) -> List[Dict]:
        """Get all feedback for a movie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback 
            WHERE movie_id = ? 
            ORDER BY timestamp DESC
        ''', (movie_id,))
        feedback = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return feedback
    
    # ========== ANALYTICS OPERATIONS ==========
    
    def get_analytics(self) -> Dict:
        """Get analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total movies
        cursor.execute('SELECT COUNT(*) as count FROM movies')
        total_movies = cursor.fetchone()['count']
        
        # Total reviews
        cursor.execute('SELECT COUNT(*) as count FROM feedback')
        total_reviews = cursor.fetchone()['count']
        
        # Average rating across all movies
        cursor.execute('SELECT AVG(avg_rating) as avg FROM movies')
        overall_avg = cursor.fetchone()['avg']
        
        # Positive feedback percentage
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive
            FROM feedback
        ''')
        feedback_stats = cursor.fetchone()
        positive_percentage = (feedback_stats['positive'] / feedback_stats['total'] * 100) if feedback_stats['total'] > 0 else 0
        
        conn.close()
        
        return {
            'total_movies': total_movies,
            'total_reviews': total_reviews,
            'overall_avg_rating': round(overall_avg, 1) if overall_avg else 0,
            'positive_percentage': round(positive_percentage, 1)
        }