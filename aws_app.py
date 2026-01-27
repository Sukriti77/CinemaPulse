"""
CinemaPulse AWS Application Entry Point
Runs on EC2 using IAM, DynamoDB, SNS
"""

import os

# Force AWS mode
os.environ["ENV_MODE"] = "aws"

from app import app
from flask_session import Session

# Session config for EC2
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_SECURE=False  # EC2 HTTP
)

Session(app)

if __name__ == "__main__":
    print("✓ CinemaPulse running on AWS EC2")
    app.run(
        host="0.0.0.0",
        port=80,
        debug=False
    )
