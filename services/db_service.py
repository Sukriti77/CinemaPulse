"""
Database Service - Abstraction Layer
Automatically switches between SQLite (local) and DynamoDB (AWS)
"""

from config import get_config

class DatabaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        config = get_config()
        
        if config.ENV_MODE == 'local':
            from database.sqlite_db import SQLiteDatabase
            self.db = SQLiteDatabase(config.SQLITE_DB_PATH)
            print("✓ Using SQLite database (LOCAL mode)")
        
        elif config.ENV_MODE == 'aws':
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

    # ========= USER =========
    def get_user_by_email(self, email):
        return self.db.get_user_by_email(email)

    def create_user(self, email, role='viewer'):
        return self.db.create_user(email, role)

    # ========= MOVIES =========
    def get_all_movies(self):
        return self.db.get_all_movies()

    def get_movie_by_id(self, movie_id):
        """
        IMPORTANT:
        DynamoDB movie_id is NUMBER
        """
        try:
            return self.db.get_movie_by_id(int(movie_id))
        except Exception as e:
            print("❌ Error getting movie by id:", e)
            return None

    # ========= FEEDBACK =========
    def create_feedback(self, movie_id, user_email, rating, comment, sentiment='neutral'):
        try:
            return self.db.create_feedback(
                movie_id=int(movie_id),
                user_email=user_email,
                rating=rating,
                comment=comment,
                sentiment=sentiment
            )
        except Exception as e:
            print("❌ Error creating feedback:", e)
            return None

    def get_feedback_by_movie(self, movie_id):
        try:
            return self.db.get_feedback_by_movie(int(movie_id))
        except Exception as e:
            print("❌ Error fetching feedback:", e)
            return []

    # ========= ANALYTICS =========
    def get_analytics(self):
        return self.db.get_analytics()


# Singleton instance
db_service = DatabaseService()
