import requests
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserServiceClient:
    """Client for communicating with the user service from doctor service."""
    
    def __init__(self, base_url: str = "http://localhost:8001/api"):
        self.base_url = base_url.rstrip('/')
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[Any, Any]]:
        """Get user by UUID."""
        try:
            response = requests.get(f"{self.base_url}/users/{user_id}/")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    def get_user_by_auth_id(self, auth_user_id: int) -> Optional[Dict[Any, Any]]:
        """Get user by auth service user ID."""
        try:
            response = requests.get(f"{self.base_url}/users/auth/{auth_user_id}/")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching user by auth ID {auth_user_id}: {e}")
            return None
    
    def create_doctor_user(self, user_data: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
        """Create a new doctor user."""
        try:
            response = requests.post(f"{self.base_url}/users/doctors/create/", json=user_data)
            if response.status_code == 201:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error creating doctor user: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
        """Update user information."""
        try:
            response = requests.patch(f"{self.base_url}/users/{user_id}/", json=user_data)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
