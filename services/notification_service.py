"""
Notification Service - SNS Integration
Sends notifications when new feedback is submitted (AWS only)
"""

import boto3
from config import get_config
from datetime import datetime

class NotificationService:
    def __init__(self):
        """Initialize SNS client"""
        config = get_config()
        self.enabled = config.USE_SNS
        
        if self.enabled:
            self.sns_client = boto3.client('sns', region_name=config.AWS_REGION)
            self.topic_arn = config.SNS_TOPIC_ARN
            print("✓ SNS notifications enabled")
        else:
            print("✓ SNS notifications disabled (LOCAL mode)")
    
    def send_feedback_notification(self, movie_title, user_email, rating, comment):
        """
        Send notification when new feedback is submitted
        
        Args:
            movie_title: Movie name
            user_email: User who submitted feedback
            rating: Rating (1-5)
            comment: Feedback comment
        """
        if not self.enabled:
            # In local mode, just log
            print(f"[MOCK SNS] New feedback: {movie_title} - {rating}/5 from {user_email}")
            return True
        
        try:
            # Prepare message
            subject = f"New Feedback: {movie_title} - {rating}/5 ⭐"
            
            message = f"""
CinemaPulse Feedback Notification
==================================

Movie: {movie_title}
Rating: {rating}/5 stars
User: {user_email}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Comment:
{comment}

---
This is an automated notification from CinemaPulse.
            """
            
            # Publish to SNS topic
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            print(f"✓ SNS notification sent: MessageId {response['MessageId']}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending SNS notification: {e}")
            return False
    
    def send_alert(self, subject, message):
        """
        Send generic alert notification
        
        Args:
            subject: Alert subject
            message: Alert message
        """
        if not self.enabled:
            print(f"[MOCK SNS] Alert: {subject}")
            return True
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            print(f"✓ SNS alert sent: MessageId {response['MessageId']}")
            return True
        except Exception as e:
            print(f"✗ Error sending SNS alert: {e}")
            return False


# Singleton instance
notification_service = NotificationService()