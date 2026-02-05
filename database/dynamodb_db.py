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
    def __init__(
        self,
        region_name='us-east-1',
        users_table='CinemaPulse-Users',
        movies_table='CinemaPulse-Movies',
        feedback_table='CinemaPulse-Feedback'
    ):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)

        self.users_table = self.dynamodb.Table(users_table)
        self.movies_table = self.dynamodb.Table(movies_table)
        self.feedback_table = self.dynamodb.Table(feedback_table)

    # ========== HELPER ==========

    @staticmethod
    def decimal_to_float(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, dict):
            return {k: DynamoDBDatabase.decimal_to_float(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [DynamoDBDatabase.decimal_to_float(i) for i in obj]
        return obj

    # ========== USERS ==========

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        try:
            res = self.users_table.get_item(Key={'user_email': email})
            return self.decimal_to_float(res.get('Item'))
        except Exception as e:
            print("User fetch error:", e)
            return None

    def create_user(self, email: str, role='viewer') -> bool:
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
            print("User create error:", e)
            return False

    # ========== MOVIES ==========

    def get_all_movies(self) -> List[Dict]:
        try:
            res = self.movies_table.scan()
            movies = res.get('Items', [])
            movies.sort(key=lambda x: x.get('avg_rating', 0), reverse=True)
            return self.decimal_to_float(movies)
        except Exception as e:
            print("Movies fetch error:", e)
            return []

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        try:
            res = self.movies_table.get_item(Key={'movie_id': movie_id})
            return self.decimal_to_float(res.get('Item'))
        except Exception as e:
            print("Movie fetch error:", e)
            return None

    def update_movie_rating(self, movie_id: int):
        try:
            res = self.feedback_table.query(
                KeyConditionExpression=Key('movie_id').eq(movie_id)
            )
            feedback = res.get('Items', [])
            if not feedback:
                return

            avg = sum(f['rating'] for f in feedback) / len(feedback)

            self.movies_table.update_item(
                Key={'movie_id': movie_id},
                UpdateExpression='SET avg_rating = :a, total_reviews = :t',
                ExpressionAttributeValues={
                    ':a': Decimal(str(round(avg, 1))),
                    ':t': len(feedback)
                }
            )
        except Exception as e:
            print("Rating update error:", e)

    # ========== FEEDBACK ==========

    def create_feedback(self, movie_id: int, user_email: str, rating: int,
                        comment: str, sentiment='neutral') -> Optional[str]:
        try:
            ts = datetime.utcnow().isoformat()
            self.feedback_table.put_item(
                Item={
                    'movie_id': movie_id,
                    'timestamp': ts,
                    'user_email': user_email,
                    'rating': rating,
                    'comment': comment,
                    'sentiment': sentiment
                }
            )
            self.update_movie_rating(movie_id)
            return ts
        except Exception as e:
            print("Feedback error:", e)
            return None

    def get_feedback_by_movie(self, movie_id: int) -> List[Dict]:
        try:
            res = self.feedback_table.query(
                KeyConditionExpression=Key('movie_id').eq(movie_id),
                ScanIndexForward=False
            )
            return self.decimal_to_float(res.get('Items', []))
        except Exception as e:
            print("Feedback fetch error:", e)
            return []

    # ========== ANALYTICS ==========

    def get_analytics(self) -> Dict:
        try:
            movies = self.movies_table.scan().get('Items', [])
            feedback = self.feedback_table.scan().get('Items', [])

            total_movies = len(movies)
            total_reviews = len(feedback)

            if total_reviews > 0:
                overall_avg = sum(f['rating'] for f in feedback) / total_reviews
                positive = sum(1 for f in feedback if f['rating'] >= 4)
                positive_pct = (positive / total_reviews) * 100
            else:
                overall_avg = 0
                positive_pct = 0

            return {
                'total_movies': total_movies,
                'total_reviews': total_reviews,
                'overall_avg_rating': round(float(overall_avg), 1),
                'positive_percentage': round(float(positive_pct), 1)
            }
        except Exception as e:
            print("Analytics error:", e)
            return {
                'total_movies': 0,
                'total_reviews': 0,
                'overall_avg_rating': 0,
                'positive_percentage': 0
            }
