"""
Database Service - Abstraction Layer
Automatically switches between SQLite (local) and DynamoDB (AWS)
"""

from config import get_config

class DatabaseService:
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one database instance"""
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database based on environment"""
        if self._initialized:
            return
        
        config = get_config()
        
        if config.ENV_MODE == 'local':
            # Use SQLite for local development
            from database.sqlite_db import SQLiteDatabase
            self.db = SQLiteDatabase(config.SQLITE_DB_PATH)
            print("✓ Using SQLite database (LOCAL mode)")
        
        elif config.ENV_MODE == 'aws':
            # Use DynamoDB for AWS deployment
            from database.dynamodb_db import DynamoDBDatabase
            self.db = DynamoDBDatabase(
                region_name=config.AWS_REGION,
                users_table=config.DYNAMODB_USERS_TABLE,
                movies_table=config.DYNAMODB_MOVIES_TABLE,
                feedback_table=config.DYNAMODB_FEEDBACK_TABLE
            )
            print("✓ Using DynamoDB (AWS mode)")
        
        else:
            raise ValueError(f"Unknown ENV_MODE: {config.ENV_MODE}")
        
        self._initialized = True
    
    # ========== USER OPERATIONS ==========
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.db.get_user_by_email(email)
    
    def create_user(self, email, role='viewer'):
        """Create new user"""
        return self.db.create_user(email, role)
    
    # ========== MOVIE OPERATIONS ==========
    
    def get_all_movies(self):
        """Get all movies"""
        return self.db.get_all_movies()
    
    def get_movie_by_id(self, movie_id):
        """Get movie by ID"""
        return self.db.get_movie_by_id(movie_id)
    
    # ========== FEEDBACK OPERATIONS ==========
    
    def create_feedback(self, movie_id, user_email, rating, comment, sentiment='neutral'):
        """Create new feedback"""
        return self.db.create_feedback(movie_id, user_email, rating, comment, sentiment)
    
    def get_feedback_by_movie(self, movie_id):
        """Get all feedback for a movie"""
        return self.db.get_feedback_by_movie(movie_id)
    
    # ========== ANALYTICS OPERATIONS ==========
    
    def get_analytics(self):
        """Get analytics data"""
        return self.db.get_analytics()


# Singleton instance
db_service = DatabaseService()