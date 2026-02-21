"""
Authentication Service for user management and admin control
"""

import hashlib
from datetime import datetime
from typing import Dict, Optional, List
from config import INDIAN_STATES, DEFAULT_CITIES
from services.database_service import DatabaseService


class AuthService:
    def __init__(self):
        self.db = DatabaseService()

    def is_first_user(self) -> bool:
        """Check if this is the first user signing up"""
        users = self.db.get_all_users()
        return len(users) == 0

    def create_user(self, user_data: Dict) -> Dict:
        """
        Create a new user account

        Args:
            user_data (dict): User information including name, email, password, state, city

        Returns:
            dict: Created user with ID and admin status
        """
        user_id = f"USER{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Check if this is the first user (make them admin)
        is_admin = self.is_first_user()

        # Hash the password
        password_hash = self._hash_password(user_data.get("password", ""))

        user = {
            "id": user_id,
            "created_at": datetime.now().isoformat(),
            "is_admin": is_admin,
            "state": user_data.get("state"),
            "city": user_data.get("city"),
            "password_hash": password_hash,
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
        }

        # Save to database
        self.db.create_user(user)

        # If admin, add to admins list
        if is_admin:
            admin_data = {
                "user_id": user_id,
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "granted_at": datetime.now().isoformat(),
                "is_super_admin": True,
            }
            self.db.create_admin(admin_data)

        return user

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.db.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self.db.get_user_by_email(email)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email and password

        Args:
            email (str): User email
            password (str): User password

        Returns:
            dict: User data if authentication successful, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            return None

        # Check if user has password hash (for backward compatibility)
        if "password_hash" not in user or not user["password_hash"]:
            # For existing users without password, accept any password
            return user

        if self.verify_password(password, user["password_hash"]):
            return user
        return None

    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        return self.db.is_admin(user_id)

    def get_user_city(self, user_id: str) -> Optional[str]:
        """Get user's default city"""
        user = self.get_user(user_id)
        return user.get("city") if user else None

    def get_user_state(self, user_id: str) -> Optional[str]:
        """Get user's state"""
        user = self.get_user(user_id)
        return user.get("state") if user else None

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.db.get_all_users()

    def get_all_admins(self) -> List[Dict]:
        """Get all admins"""
        return self.db.get_all_admins()

    def validate_place_in_city(self, place: str, city: str) -> bool:
        """
        Validate if a place exists in the given city using AI service

        Args:
            place (str): Place name to validate
            city (str): City name

        Returns:
            bool: True if place exists in city
        """
        from services.ai_service import AIService

        ai_service = AIService()
        return ai_service.validate_place_in_city(place, city)

    def get_city_suggestions(self, city: str) -> List[str]:
        """
        Get famous places suggestions for a city using AI service

        Args:
            city (str): City name

        Returns:
            list: List of famous places in the city
        """
        from services.ai_service import AIService

        ai_service = AIService()
        return ai_service.get_city_suggestions(city)

    def get_cities_for_state(self, state: str) -> List[str]:
        """Get cities for a given state"""
        return INDIAN_STATES.get(state, [])

    def get_states(self) -> List[str]:
        """Get all available states"""
        return list(INDIAN_STATES.keys())

    def get_default_city_for_state(self, state: str) -> str:
        """Get default city for a state"""
        return DEFAULT_CITIES.get(state, "")
