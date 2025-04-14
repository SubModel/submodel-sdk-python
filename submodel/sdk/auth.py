"""Authentication Management Module"""

from typing import Dict, Any, Optional
from .exceptions import SubModelError

class Auth:
    """Authentication management class"""
    
    def __init__(self, client):
        """Initialize Auth manager
        
        Args:
            client: SubModel client instance
        """
        self.client = client
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """Register account
        
        Args:
            username: Username
            password: Password
        """
        return self.client.post("user/reg", json={
            "username": username,
            "password": password
        })
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login account
        
        Args:
            username: Username
            password: Password
        """
        return self.client.post("user/login", json={
            "username": username,
            "password": password
        })
    
    def logout(self) -> Dict[str, Any]:
        """Logout account"""
        return self.client.get("user/logout")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information"""
        return self.client.get("user/info")
    
    def generate_api_key(self) -> Dict[str, Any]:
        """Generate API Key"""
        return self.client.get("user/generate_api_key")
    
    def list_api_keys(self) -> Dict[str, Any]:
        """Get API Key list"""
        return self.client.get("user/list_api_key")
    
    def remove_api_key(self, key: str) -> Dict[str, Any]:
        """Delete API Key
        
        Args:
            key: API Key to delete
        """
        return self.client.get(f"user/remove_api_key/{key}")
    
    def active_api_key(self, key: str, active: bool) -> Dict[str, Any]:
        """Activate/deactivate API Key
        
        Args:
            key: API Key
            active: Whether to activate
        """
        return self.client.get(f"user/active_api_key/{key}/{str(active).lower()}")