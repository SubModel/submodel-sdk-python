from typing import Dict, Any, Optional
from .client import SubModelClient

class Job:
    def __init__(self, client: SubModelClient, inst_id: str, job_id: str):
        self.client = client
        self.inst_id = inst_id
        self.job_id = job_id
    
    def get_status(self) -> Dict[str, Any]:
        """Get task status"""
        return self.client.get(f"sl/{self.inst_id}/status/{self.job_id}")
    
    def cancel(self) -> Dict[str, Any]:
        """Cancel task"""
        return self.client.get(f"sl/{self.inst_id}/cancel/{self.job_id}")
    
    def wait(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Wait for task completion
        
        Args:
            timeout: Timeout in seconds, None means no timeout
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: When waiting timeout
        """
        import time
        start_time = time.time()
        
        while True:
            status = self.get_status()
            if status.get("status") in ["completed", "failed", "cancelled"]:
                return status
                
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Job wait timeout")
                
            time.sleep(1)  # Avoid too frequent requests