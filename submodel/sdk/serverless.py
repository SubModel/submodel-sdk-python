import json
import os
from typing import Dict, Any, Optional, Callable
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

class ServerlessHandler:
    def __init__(self):
        self._handler: Optional[Callable] = None
        self._inst_id: Optional[str] = None
        self._max_iterations: int = 100  # Maximum iteration limit
        
    def handler(self, func: Callable) -> Callable:
        """Decorator for registering handler function"""
        self._handler = func
        return func
    
    def set_instance(self, inst_id: str) -> None:
        """Set instance ID"""
        self._inst_id = inst_id
    
    def set_max_iterations(self, max_iterations: int) -> None:
        """Set maximum iterations"""
        self._max_iterations = max_iterations
    
    def start(self) -> None:
        """Start serverless worker"""
        if not self._inst_id:
            raise ValueError("Instance ID not set. Call set_instance() first.")
            
        if not self._handler:
            raise ValueError("No handler registered. Use @serverless.handler decorator first.")
            
        while True:
            try:
                # Get task input
                job_input = self._get_job_input()
                if not job_input:
                    continue
                
                # Execute iteration processing
                final_result = self._handle_iterations(job_input)
                
                # Return final result
                self._return_result(final_result)
                
            except Exception as e:
                self._return_error(str(e))

    def _handle_iterations(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle iteration logic
        
        Returns:
            Final processing result
        """
        current_input = initial_input
        iteration_count = 0
        
        while iteration_count < self._max_iterations:
            # Execute handler function
            result = self._handler(current_input)
            
            # Check result format
            if not isinstance(result, dict):
                return result
                
            # Check if continue iteration
            should_continue = result.pop("continue_iteration", False)
            if not should_continue:
                return result
                
            # Prepare input for next iteration
            current_input = {
                "input": result,
                "iteration": iteration_count + 1
            }
            iteration_count += 1
        
        # Maximum iteration limit reached
        return {
            "error": "Maximum iteration limit reached",
            "last_result": result
        }

    def _get_job_input(self) -> Dict[str, Any]:
        """Get task input"""
        # TODO: Implement getting task from SubModel API
        input_data = os.environ.get("SUBMODEL_INPUT")
        if input_data:
            try:
                return json.loads(input_data)
            except json.JSONDecodeError:
                return {"input": input_data}
        return {"input": {}}

    def _return_result(self, result: Any) -> None:
        """Return processing result"""
        output = {"output": result}
        print(json.dumps(output))

    def _return_error(self, error: str) -> None:
        """Return error message"""
        error_output = {"error": error}
        print(json.dumps(error_output))