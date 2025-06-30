"""
Instance Management Module
~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides functionality for managing SubModel instances.
"""

from typing import Dict, Any, Optional, List
from .utils import log_request, log_response

class Instance:
    """Instance management class"""
    
    def __init__(self, client):
        """Initialize Instance manager
        
        Args:
            client: SubModel client instance
        """
        self.client = client
    
    def create(self, 
               billing_method: str = "payg",
               mode: str = "pod",
               plan: str = "gpu-rtx4090-24g-1",
               image: str = "ubuntu-22.04",
               pod_num: int = 1,
               area: Optional[List[str]] = None,
               conf: Optional[Dict[str, Any]] = None,
               **kwargs) -> Dict[str, Any]:
        """Create a new instance
        
        Args:
            billing_method: Billing method, 'payg' or 'monthly'
            mode: Instance mode, 'pod' or 'baremetal'
            plan: Instance plan (GPU model)
            image: OS image
            pod_num: Number of pods
            area: List of area IDs
            conf: Additional configuration parameters
            **kwargs: Additional parameters
            
        Returns:
            API response containing instance details
        """
        data = {
            "billing_method": billing_method,
            "mode": mode,
            "plan": plan,
            "image": image,
            "pod_num": pod_num,
<<<<<<< HEAD
=======
            
>>>>>>> private-repo/main
            "area": area or [],
            "conf": conf or {},
            **kwargs
        }
        return self.client.post("inst/create", json=data)
    
    def list_instances(self, page: int = 1, limit: int = 10, mode: str = "pod") -> Dict[str, Any]:
        """List instances
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            mode: Instance mode (pod/baremetal)
            
        Returns:
            API response containing list of instances
        """
        params = {"page": page, "limit": limit, "mode": mode}
        return self.client.get("inst/list", params=params)
    
    def get_instance(self, inst_id: str) -> Dict[str, Any]:
        """Get instance details
        
        Args:
            inst_id: Instance ID
            
        Returns:
            API response containing instance details
        """
        return self.client.get(f"inst/detail/{inst_id}")
    
    def delete_instance(self, inst_id: str) -> Dict[str, Any]:
        """Delete an instance
        
        Args:
            inst_id: Instance ID
            
        Returns:
            API response indicating deletion status
        """
        return self.client.post(f"inst/delete/{inst_id}")
    
    def control_instance(self, action: str, inst_id: str, **kwargs) -> Dict[str, Any]:
        """Control instance
        
        Args:
            action: Action type, available values:
                - run: Start instance
                - stop: Stop instance
                - release: Release instance
                - restart: Restart instance
                - remote_cmd: Remote command
                - setlabel: Set label
                - set_ports: Set ports
                - change_image: Change image
                - set_ex_setting: Set extended configuration
                - set_envs: Set environment variables
            inst_id: Instance ID
            **kwargs: Additional parameters
            
        Returns:
            API response indicating operation status
        """
        valid_actions = [
            "run", "stop", "release", "restart", "remote_cmd",
            "setlabel", "set_ports", "change_image", "set_ex_setting", "set_envs"
        ]
        if action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")
            
        return self.client.post(f"inst/action/{action}/{inst_id}", json=kwargs)
    
    def get_pods(self, inst_id: str) -> Dict[str, Any]:
        """Get instance pods
        
        Args:
            inst_id: Instance ID
            
        Returns:
            API response containing pod list
        """
        return self.client.get(f"inst/cont/{inst_id}")
    
    def get_pod_logs(self, inst_id: str, pod_id: str) -> Dict[str, Any]:
        """Get Pod logs
        
        Args:
            inst_id: Instance ID
            pod_id: Pod ID
            
        Returns:
            API response containing pod logs
        """
        return self.client.get(f"inst/{inst_id}/pod/{pod_id}/logs")
    
    def terminate_pod(self, inst_id: str, pod_id: str) -> Dict[str, Any]:
        """Terminate Pod
        
        Args:
            inst_id: Instance ID
            pod_id: Pod ID
            
        Returns:
            API response indicating termination status
        """
        return self.client.get(f"inst/{inst_id}/pod/{pod_id}/terminate")
