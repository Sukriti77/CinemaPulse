"""
Authentication Service
Handles user registration, login, and admin creation
"""

import hashlib
import secrets
from services.db_service import db_service
from config import get_config


class AuthService:

    @staticmethod
    def hash_password(password: str, salt: str = None):
        """Hash password using SHA-256 with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_salt = f"{password}{salt}".encode("utf-8")
        hashed = hashlib.sha256(pwd_salt).hexdigest()
        return hashed, salt

    @staticmethod
    def verify_password(password, hashed_password, salt):
        """Verify password against stored hash"""
        new_hash, _ = AuthService.hash_password(password, salt)
        return new_hash == hashed_password

    @staticmethod
    def register_user(email, password, name, role="viewer"):
        """
        Register a new user (viewer/admin)
        Works for both SQLite (local) and DynamoDB (AWS)
        """
        config = get_config()

        if not email or "@" not in email:
            return {"success": False, "message": "Invalid email"}

        if not password or len(password) < 6:
            return {"success": False, "message": "Password too short"}

        if not name or len(name) < 2:
            return {"success": False, "message": "Invalid name"}

        if db_service.get_user_by_email(email):
            return {"success": False, "message": "User already exists"}

        hashed, salt = AuthService.hash_password(password)

        # ✅ LOCAL MODE (SQLite)
        if config.ENV_MODE == "local":
            conn = db_service.db.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO users (email, password, salt, name, role)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (email, hashed, salt, name, role),
                )
                conn.commit()
                return {
                    "success": True,
                    "message": "Registration successful",
                    "user": {
                        "email": email,
                        "name": name,
                        "role": role
                    },
                }
            except Exception as e:
                print(f"Registration error: {e}")
                return {"success": False, "message": "Registration failed"}
            finally:
                conn.close()

        # ✅ AWS MODE (DynamoDB)
        else:
            created = db_service.create_user(email, role)
            return {
                "success": created,
                "message": "Registration successful" if created else "Registration failed",
                "user": {
                    "email": email,
                    "name": name,
                    "role": role
                },
            }

    @staticmethod
    def login_user(email, password):
        """
        Authenticate user
        SQLite → password + salt verification
        DynamoDB → role-based demo authentication
        """
        user = db_service.get_user_by_email(email)
        if not user:
            return {"success": False, "message": "Invalid credentials"}

        # SQLite authentication
        if "password" in user and "salt" in user:
            if not AuthService.verify_password(password, user["password"], user["salt"]):
                return {"success": False, "message": "Invalid credentials"}

        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "email": user.get("user_email", user.get("email")),
                "name": user.get("name", "User"),
                "role": user.get("role", "viewer"),
            },
        }

    @staticmethod
    def create_admin(email: str, password: str, name: str) -> dict:
        """
        Create admin user
        Wrapper over register_user with role='admin'
        """
        return AuthService.register_user(
            email=email,
            password=password,
            name=name,
            role="admin"
        )


# Singleton instance
auth_service = AuthService()
