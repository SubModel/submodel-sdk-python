from typing import Dict, Any, List, Optional
from .client import SubModelClient

class ServerlessEndpoint:
    def __init__(self, client: SubModelClient, inst_id: str):
        self.client = client
        self.inst_id = inst_id
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run task asynchronously"""
        return self.client.post(f"sl/{self.inst_id}/run", json={"input": input_data})
    
    def run_sync(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run task synchronously"""
        return self.client.post(f"sl/{self.inst_id}/runsync", json={"input": input_data})
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get task status"""
        return self.client.get(f"sl/{self.inst_id}/status/{job_id}")
    
    def cancel(self, job_id: str) -> Dict[str, Any]:
        """Cancel task"""
        return self.client.get(f"sl/{self.inst_id}/cancel/{job_id}")
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status"""
        return self.client.get(f"sl/{self.inst_id}/health")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics"""
        return self.client.get(f"sl/{self.inst_id}/metrics")
    
    def get_requests(self) -> Dict[str, Any]:
        """Get request list"""
        return self.client.get(f"sl/{self.inst_id}/_requests")
    
    def get_request_details(self, request_id: str) -> Dict[str, Any]:
        """Get request details"""
        return self.client.get(f"sl/{self.inst_id}/_requests/{request_id}")
    
    def list_models(self) -> Dict[str, Any]:
        """Get model list"""
        return self.client.get(f"sl/{self.inst_id}/models")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information"""
        return self.client.get(f"sl/{self.inst_id}/models/{model_id}")

class Instance:
    def __init__(self, client: SubModelClient):
        self.client = client
    
    def create(self, 
               billing_method: str = "payg",
               mode: str = "pod",
               plan: str = "gpu-rtx4090-24g-1",
               image: str = "ubuntu-22.04",
               pod_num: int = 1,
               area: List[str] = None,
               conf: Dict[str, Any] = None,
               container_size: int = 5,
               volume_size: int = 5,
               volume_mount_path: str = "/workspace",
               **kwargs) -> Dict[str, Any]:
        """Create instance"""
        data = {
            "billing_method": billing_method,
            "mode": mode,
            "plan": plan,
            "image": image,
            "pod_num": pod_num,
            "area": area or [],
            "conf": conf or {},
            "container_size": container_size,
            "volume_size": volume_size,
            "volume_mount_path": volume_mount_path,
            **kwargs
        }
        return self.client.post("inst/create", json=data)
    
    def list_instances(self, page: int = 1, limit: int = 10, mode: str = "pod") -> Dict[str, Any]:
        """Get instance list"""
        params = {"page": page, "limit": limit, "mode": mode}
        return self.client.get("inst/list", params=params)
    
    def get_instance(self, inst_id: str) -> Dict[str, Any]:
        """Get instance details"""
        return self.client.get(f"inst/detail/{inst_id}")
    
    def get_pods(self, inst_id: str) -> Dict[str, Any]:
        """Get instance pods"""
        return self.client.get(f"inst/cont/{inst_id}")
    
    def get_pod_logs(self, inst_id: str, pod_id: str) -> Dict[str, Any]:
        """Get Pod logs"""
        return self.client.get(f"inst/{inst_id}/pod/{pod_id}/logs")
    
    def terminate_pod(self, inst_id: str, pod_id: str) -> Dict[str, Any]:
        """Terminate Pod"""
        return self.client.get(f"inst/{inst_id}/pod/{pod_id}/terminate")
    
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
        """
        valid_actions = [
            "run", "stop", "release", "restart", "remote_cmd",
            "setlabel", "set_ports", "change_image", "set_ex_setting", "set_envs"
        ]
        if action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")
            
        return self.client.post(f"inst/action/{action}/{inst_id}", json=kwargs)