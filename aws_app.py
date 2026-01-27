"""
CinemaPulse AWS Application Entry Point
"""

import os
os.environ["ENV_MODE"] = "aws"

from app import app
from flask_session import Session

# ✅ SAFE SESSION CONFIG
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=False,   # 🔥 FIX
    SESSION_COOKIE_SECURE=False
)

Session(app)

if __name__ == "__main__":
    print("✓ CinemaPulse running on AWS EC2")
    app.run(
        host="0.0.0.0",
        port=5000,   # keep this
        debug=False
    )
