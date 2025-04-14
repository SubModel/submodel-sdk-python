from typing import Dict, Any, Optional, List
from .client import SubModelClient

class Device:
    def __init__(self, client: SubModelClient):
        self.client = client
    
    def list_devices(self, page: int = 1, limit: int = 10, search: str = None) -> Dict[str, Any]:
        """Get device list"""
        params = {
            "page": page,
            "limit": limit
        }
        if search:
            params["search"] = search
        return self.client.get("device/list", params=params)
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """Get device details"""
        return self.client.get(f"device/detail/{device_id}")
    
    def control_device(self, action: str, device_id: str, project: str = "global", **kwargs) -> Dict[str, Any]:
        """Control device
        
        Args:
            action: Action type, available values:
                - run: Run device
                - stop: Stop device
                - release: Release device
                - remote_cmd: Remote command
                - set_label: Set label
                - reset_token: Reset token
                - set_conf: Set configuration
                - set_status: Set status
        """
        valid_actions = [
            "run", "stop", "release", "remote_cmd", 
            "set_label", "reset_token", "set_conf", "set_status"
        ]
        if action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")
            
        return self.client.get(f"device/action/{action}/{device_id}/{project}", params=kwargs)

class Area:
    def __init__(self, client: SubModelClient):
        self.client = client
    
    def list_areas(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get available area list"""
        params = {"page": page, "limit": limit}
        return self.client.get("area/list", params=params)
    
    def get_area(self, area_id: str) -> Dict[str, Any]:
        """Get area details"""
        return self.client.get(f"area/detail/{area_id}")

class Baremetal:
    def __init__(self, client: SubModelClient):
        self.client = client
    
    def list_baremetals(self, page: int = 1, limit: int = 10, mode: str = "baremetal") -> Dict[str, Any]:
        """Get bare metal server list"""
        params = {
            "page": page,
            "limit": limit,
            "mode": mode
        }
        return self.client.get("baremetal/list", params=params)