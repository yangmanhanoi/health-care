import requests
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserServiceClient:
    """Client for communicating with the user service from other services."""
    
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
    
    def get_user_by_email(self, email: str) -> Optional[Dict[Any, Any]]:
        """Get user by email."""
        try:
            response = requests.get(f"{self.base_url}/users/email/{email}/")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching user by email {email}: {e}")
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
    
    def create_patient_user(self, user_data: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
        """Create a new patient user."""
        try:
            response = requests.post(f"{self.base_url}/users/patients/create/", json=user_data)
            if response.status_code == 201:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Error creating patient user: {e}")
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
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            response = requests.post(f"{self.base_url}/users/{user_id}/login/")
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    def log_activity(self, user_id: str, activity_type: str, description: str = "", 
                     ip_address: str = None, user_agent: str = None) -> bool:
        """Log user activity."""
        try:
            data = {
                'user': user_id,
                'activity_type': activity_type,
                'description': description,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            response = requests.post(f"{self.base_url}/activities/", json=data)
            return response.status_code == 201
        except requests.RequestException as e:
            logger.error(f"Error logging activity for user {user_id}: {e}")
            return False
    
    def get_doctors(self) -> list:
        """Get all doctor users."""
        try:
            response = requests.get(f"{self.base_url}/users/doctors/")
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching doctors: {e}")
            return []
    
    def get_patients(self) -> list:
        """Get all patient users."""
        try:
            response = requests.get(f"{self.base_url}/users/patients/")
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching patients: {e}")
            return []
