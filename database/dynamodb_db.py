"""
DynamoDB Database Implementation for AWS Deployment
Uses boto3 with IAM roles (no hardcoded credentials)
"""

import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal

class DynamoDBDatabase:
    def __init__(self, region_name='us-east-1', 
                 users_table='CinemaPulse-Users',
                 movies_table='CinemaPulse-Movies',
                 feedback_table='CinemaPulse-Feedback'):
        """
        Initialize DynamoDB client
        Uses IAM role credentials automatically (no access keys needed)
        """
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        
        self.users_table = self.dynamodb.Table(users_table)
        self.movies_table = self.dynamodb.Table(movies_table)
        self.feedback_table = self.dynamodb.Table(feedback_table)
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    def decimal_to_float(obj):
        """Convert DynamoDB Decimal to float"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: DynamoDBDatabase.decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBDatabase.decimal_to_float(item) for item in obj]
        return obj
    
    # ========== USER OPERATIONS ==========
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email (partition key)"""
        try:
            response = self.users_table.get_item(Key={'user_email': email})
            return self.decimal_to_float(response.get('Item'))
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def create_user(self, email: str, role: str = 'viewer') -> bool:
        """Create new user"""
        try:
            self.users_table.put_item(
                Item={
                    'user_email': email,
                    'role': role,
                    'created_at': datetime.utcnow().isoformat()
                },
                ConditionExpression='attribute_not_exists(user_email)'
            )
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    # ========== MOVIE OPERATIONS ==========
    
    def get_all_movies(self) -> List[Dict]:
        """Get all movies (scan operation)"""
        try:
            response = self.movies_table.scan()
            movies = response.get('Items', [])
            
            # Sort by rating (descending)
            movies.sort(key=lambda x: x.get('avg_rating', 0), reverse=True)
            
            return self.decimal_to_float(movies)
        except Exception as e:
            print(f"Error getting movies: {e}")
            return []
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        """Get movie by ID (partition key)"""
        try:
            response = self.movies_table.get_item(Key={'movie_id': movie_id})
            return self.decimal_to_float(response.get('Item'))
        except Exception as e:
            print(f"Error getting movie: {e}")
            return None
    
    def update_movie_rating(self, movie_id: int):
        """Recalculate and update movie average rating"""
        try:
            # Get all feedback for this movie
            response = self.feedback_table.query(
                KeyConditionExpression=Key('movie_id').eq(movie_id)
            )
            feedback_items = response.get('Items', [])
            
            if not feedback_items:
                return
            
            # Calculate average
            total_rating = sum(item['rating'] for item in feedback_items)
            avg_rating = total_rating / len(feedback_items)
            
            # Update movie
            self.movies_table.update_item(
                Key={'movie_id': movie_id},
                UpdateExpression='SET avg_rating = :avg, total_reviews = :total',
                ExpressionAttributeValues={
                    ':avg': Decimal(str(round(avg_rating, 1))),
                    ':total': len(feedback_items)
                }
            )
        except Exception as e:
            print(f"Error updating movie rating: {e}")
    
    # ========== FEEDBACK OPERATIONS ==========
    
    def create_feedback(self, movie_id: int, user_email: str, rating: int, 
                       comment: str, sentiment: str = 'neutral') -> str:
        """
        Create new feedback
        Returns: timestamp (used as sort key)
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.feedback_table.put_item(
                Item={
                    'movie_id': movie_id,
                    'timestamp': timestamp,
                    'user_email': user_email,
                    'rating': rating,
                    'comment': comment,
                    'sentiment': sentiment
                }
            )
            
            # Update movie rating
            self.update_movie_rating(movie_id)
            
            return timestamp
        except Exception as e:
            print(f"Error creating feedback: {e}")
            return None
    
    def get_feedback_by_movie(self, movie_id: int) -> List[Dict]:
        """Get all feedback for a movie"""
        try:
            response = self.feedback_table.query(
                KeyConditionExpression=Key('movie_id').eq(movie_id),
                ScanIndexForward=False  # Sort descending by timestamp
            )
            return self.decimal_to_float(response.get('Items', []))
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []
    
    # ========== ANALYTICS OPERATIONS ==========
    
    def get_analytics(self) -> Dict:
        """Get analytics data"""
        try:
            # Get all movies
            movies_response = self.movies_table.scan()
            movies = movies_response.get('Items', [])
            
            # Get all feedback
            feedback_response = self.feedback_table.scan()
            all_feedback = feedback_response.get('Items', [])
            
            # Calculate statistics
            total_movies = len(movies)
            total_reviews = len(all_feedback)
            
            # Overall average rating
            if movies:
                overall_avg = sum(m.get('avg_rating', 0) for m in movies) / len(movies)
            else:
                overall_avg = 0
            
            # Positive feedback percentage
            if all_feedback:
                positive_count = sum(1 for f in all_feedback if f['rating'] >= 4)
                positive_percentage = (positive_count / len(all_feedback)) * 100
            else:
                positive_percentage = 0
            
            return {
                'total_movies': total_movies,
                'total_reviews': total_reviews,
                'overall_avg_rating': round(float(overall_avg), 1),
                'positive_percentage': round(positive_percentage, 1)
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {
                'total_movies': 0,
                'total_reviews': 0,
                'overall_avg_rating': 0,
                'positive_percentage': 0
            }
    
    # ========== INITIALIZATION (for AWS deployment) ==========
    
    def seed_default_data(self):
        """
        Seed default data to DynamoDB
        Run this once during AWS setup
        """
        # Insert default users
        default_users = [
            {'user_email': 'admin@cinemapulse.com', 'role': 'admin'},
            {'user_email': 'viewer@cinemapulse.com', 'role': 'viewer'}
        ]
        
        for user in default_users:
            try:
                self.users_table.put_item(
                    Item={**user, 'created_at': datetime.utcnow().isoformat()},
                    ConditionExpression='attribute_not_exists(user_email)'
                )
            except:
                pass  # User already exists
        
        # Insert default movies
        default_movies = [
            {
                'movie_id': 1,
                'title': 'The Shawshank Redemption',
                'description': 'Two imprisoned men bond over a number of years.',
                'poster_url': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400',
                'avg_rating': Decimal('4.8'),
                'total_reviews': 0
            },
            {
                'movie_id': 2,
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets.',
                'poster_url': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400',
                'avg_rating': Decimal('4.5'),
                'total_reviews': 0
            },
            {
                'movie_id': 3,
                'title': 'The Dark Knight',
                'description': 'Batman faces the Joker.',
                'poster_url': 'https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=400',
                'avg_rating': Decimal('4.7'),
                'total_reviews': 0
            },
            {
                'movie_id': 4,
                'title': 'Interstellar',
                'description': 'Explorers travel through a wormhole.',
                'poster_url': 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400',
                'avg_rating': Decimal('4.6'),
                'total_reviews': 0
            }
        ]
        
        for movie in default_movies:
            try:
                self.movies_table.put_item(
                    Item={**movie, 'created_at': datetime.utcnow().isoformat()},
                    ConditionExpression='attribute_not_exists(movie_id)'
                )
            except:
                pass  # Movie already exists