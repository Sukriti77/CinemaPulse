from database.dynamodb_db import DynamoDBDatabase
from config import get_config
from datetime import datetime

config = get_config()

db = DynamoDBDatabase(
    region_name=config.AWS_REGION,
    users_table=config.DYNAMODB_USERS_TABLE,
    movies_table=config.DYNAMODB_MOVIES_TABLE,
    feedback_table=config.DYNAMODB_FEEDBACK_TABLE
)

# Seed users
users = [
    {
        "user_email": "admin@cinemapulse.com",
        "role": "admin",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "user_email": "viewer@cinemapulse.com",
        "role": "viewer",
        "created_at": datetime.utcnow().isoformat()
    }
]

for user in users:
    try:
        db.users_table.put_item(
            Item=user,
            ConditionExpression="attribute_not_exists(user_email)"
        )
        print(f"✅ Added {user['user_email']}")
    except Exception:
        print(f"⚠️ {user['user_email']} already exists")

print("🎉 DynamoDB users seeded")

