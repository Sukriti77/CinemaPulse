"""
CinemaPulse Configuration
Handles environment-based configuration (LOCAL vs AWS)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (local development)
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Environment mode: 'local' or 'aws'
    ENV_MODE = os.environ.get('ENV_MODE', 'local')
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    
    # Flask settings
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'


class LocalConfig(Config):
    """Local development configuration"""
    ENV_MODE = 'local'
    
    # SQLite database
    DATABASE_TYPE = 'sqlite'
    SQLITE_DB_PATH = 'cinema_pulse.db'
    
    # No AWS services in local mode
    USE_DYNAMODB = False
    USE_SNS = False
    
    # Local server settings
    HOST = '0.0.0.0'
    PORT = 5000


class AWSConfig(Config):
    """AWS production configuration"""
    ENV_MODE = 'aws'
    
    # DynamoDB configuration
    DATABASE_TYPE = 'dynamodb'
    USE_DYNAMODB = True
    
    # AWS region
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-north-1')
    
    # DynamoDB table names
    DYNAMODB_USERS_TABLE = os.environ.get('DYNAMODB_USERS_TABLE', 'CinemaPulse-Users')
    DYNAMODB_MOVIES_TABLE = os.environ.get('DYNAMODB_MOVIES_TABLE', 'CinemaPulse-Movies')
    DYNAMODB_FEEDBACK_TABLE = os.environ.get('DYNAMODB_FEEDBACK_TABLE', 'CinemaPulse-Feedback')
    
    # SNS configuration
    USE_SNS = True
    SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
    
    # AWS server settings (EC2)
    HOST = '0.0.0.0'
    PORT = 5000


# Configuration selector
config_map = {
    'local': LocalConfig,
    'aws': AWSConfig
}

def get_config():
    """Get configuration based on ENV_MODE environment variable"""
    env_mode = os.environ.get('ENV_MODE', 'local')
    return config_map.get(env_mode, LocalConfig)
