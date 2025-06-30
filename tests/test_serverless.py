import unittest
import json
from unittest.mock import patch, MagicMock, Mock
import time
import requests
from submodel.sdk.client import create_client
from submodel.sdk.auth import Auth
from submodel.sdk.instance import Instance
from submodel.sdk.serverless import ServerlessHandler, ServerlessEndpoint
import os

class TestServerlessHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ServerlessHandler()
    
    def test_init(self):
        """Test ServerlessHandler initialization"""
        handler = ServerlessHandler()
        self.assertIsNone(handler._handler)
        self.assertIsNone(handler._inst_id)
        self.assertEqual(handler._max_iterations, 100)
    
    def test_handler_decorator(self):
        """Test handler decorator"""
        @self.handler.handler
        def test_func(job):
            return {"result": "success"}
        
        self.assertEqual(self.handler._handler, test_func)
        # Test decorator returns the original function
        self.assertEqual(test_func({"test": "data"}), {"result": "success"})
    
    def test_set_instance(self):
        """Test set_instance method"""
        self.handler.set_instance("test-instance-123")
        self.assertEqual(self.handler._inst_id, "test-instance-123")
    
    def test_set_max_iterations(self):
        """Test set_max_iterations method"""
        self.handler.set_max_iterations(50)
        self.assertEqual(self.handler._max_iterations, 50)
    
    def test_start_no_instance(self):
        """Test start method without instance ID"""
        @self.handler.handler
        def test_func(job):
            return {"result": "success"}
            
        with self.assertRaises(ValueError) as context:
            self.handler.start()
        self.assertIn("Instance ID not set", str(context.exception))
    
    def test_start_no_handler(self):
        """Test start method without handler"""
        self.handler.set_instance("test-instance")
        
        with self.assertRaises(ValueError) as context:
            self.handler.start()
        self.assertIn("No handler registered", str(context.exception))
    
    @patch('builtins.print')
    def test_get_job_input_with_json_env(self, mock_print):
        """Test _get_job_input with valid JSON in environment"""
        test_data = {"test": "data", "value": 123}
        with patch.dict(os.environ, {'SUBMODEL_INPUT': json.dumps(test_data)}):
            result = self.handler._get_job_input()
        self.assertEqual(result, test_data)
    
    @patch('builtins.print')
    def test_get_job_input_with_invalid_json_env(self, mock_print):
        """Test _get_job_input with invalid JSON in environment"""
        with patch.dict(os.environ, {'SUBMODEL_INPUT': 'invalid json'}):
            result = self.handler._get_job_input()
        self.assertEqual(result, {"input": "invalid json"})
    
    @patch('builtins.print')
    def test_get_job_input_no_env(self, mock_print):
        """Test _get_job_input without environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            result = self.handler._get_job_input()
        self.assertEqual(result, {"input": {}})
    
    @patch('builtins.print')
    def test_return_result(self, mock_print):
        """Test _return_result method"""
        test_result = {"status": "success", "data": [1, 2, 3]}
        self.handler._return_result(test_result)
        expected_output = json.dumps({"output": test_result})
        mock_print.assert_called_once_with(expected_output)
    
    @patch('builtins.print')
    def test_return_error(self, mock_print):
        """Test _return_error method"""
        error_msg = "Test error message"
        self.handler._return_error(error_msg)
        expected_output = json.dumps({"error": error_msg})
        mock_print.assert_called_once_with(expected_output)
    
    def test_handle_iterations_simple_result(self):
        """Test _handle_iterations with simple result (no iteration)"""
        @self.handler.handler
        def simple_handler(job):
            return {"result": "simple"}
        
        result = self.handler._handle_iterations({"input": "test"})
        self.assertEqual(result, {"result": "simple"})
    
    def test_handle_iterations_non_dict_result(self):
        """Test _handle_iterations with non-dict result"""
        @self.handler.handler
        def string_handler(job):
            return "string result"
        
        result = self.handler._handle_iterations({"input": "test"})
        self.assertEqual(result, "string result")
    
    def test_handle_iterations_with_continue(self):
        """Test _handle_iterations with continue_iteration flag"""
        call_count = 0
        
        @self.handler.handler
        def iterative_handler(job):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"step": call_count, "continue_iteration": True}
            else:
                return {"final_result": "completed", "total_steps": call_count}
        
        result = self.handler._handle_iterations({"input": "test"})
        self.assertEqual(result, {"final_result": "completed", "total_steps": 3})
        self.assertEqual(call_count, 3)
    
    def test_handle_iterations_max_limit_reached(self):
        """Test _handle_iterations reaching maximum iteration limit"""
        self.handler.set_max_iterations(5)
        
        @self.handler.handler
        def infinite_handler(job):
            return {"step": job.get("iteration", 0), "continue_iteration": True}
        
        result = self.handler._handle_iterations({"input": "test"})
        self.assertIn("error", result)
        self.assertIn("Maximum iteration limit reached", result["error"])
        self.assertIn("last_result", result)
    
    def test_handle_iterations_input_evolution(self):
        """Test _handle_iterations with evolving input data"""
        steps = []
        
        @self.handler.handler
        def tracking_handler(job):
            steps.append(job)
            iteration = job.get("iteration", 0)
            if iteration < 2:
                return {"data": f"step_{iteration}", "continue_iteration": True}
            else:
                return {"final": "done"}
        
        result = self.handler._handle_iterations({"input": "initial"})
          # Check that input evolved correctly
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], {"input": "initial"})
        self.assertEqual(steps[1]["iteration"], 1)
        self.assertEqual(steps[2]["iteration"], 2)
        self.assertEqual(result, {"final": "done"})
    
    @patch('builtins.print')
    def test_start_successful_execution(self, mock_print):
        """Test start method with successful execution"""
        @self.handler.handler
        def test_handler(job):
            return {"result": "success"}
        
        self.handler.set_instance("test-instance")
        
        # Mock _get_job_input to simulate processing one job and then raise KeyboardInterrupt to exit
        with patch.object(self.handler, '_get_job_input') as mock_get_input:
            call_count = 0
            def side_effect():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return {"input": "test"}
                elif call_count == 2:
                    # Return None to trigger continue, then interrupt on next iteration
                    return None
                else:
                    # Simulate external interrupt to stop the infinite loop
                    raise KeyboardInterrupt("Test interrupt")
            
            mock_get_input.side_effect = side_effect
            
            # The start method should process one job and handle the interrupt
            with self.assertRaises(KeyboardInterrupt):
                self.handler.start()
        
        # Verify that the handler processed one job successfully
        mock_print.assert_called_with('{"output": {"result": "success"}}')
    
    @patch('builtins.print')
    def test_start_with_exception(self, mock_print):
        """Test start method handling exceptions"""
        @self.handler.handler
        def failing_handler(job):
            raise RuntimeError("Handler failed")
        
        self.handler.set_instance("test-instance")
        
        # Mock _get_job_input to return data once then trigger exception
        with patch.object(self.handler, '_get_job_input') as mock_get_input:
            # First call returns data, subsequent calls raise exception to break loop
            call_count = 0
            def side_effect():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return {"input": "test"}
                raise KeyboardInterrupt()  # Use this to break the loop
            
            mock_get_input.side_effect = side_effect
            
            with self.assertRaises(KeyboardInterrupt):
                self.handler.start()
        
        # Check that error was printed
        mock_print.assert_called_with('{"error": "Handler failed"}')

class TestServerlessEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.endpoint = ServerlessEndpoint(self.client, "test-instance")
        
    def test_init(self):
        """Test ServerlessEndpoint initialization"""
        endpoint = ServerlessEndpoint(self.client, "test-instance-123")
        self.assertEqual(endpoint.client, self.client)
        self.assertEqual(endpoint.inst_id, "test-instance-123")
        
    @patch('requests.request')
    def test_run(self, mock_request):
        """Test asynchronous task execution"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"id": "test-job"}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.run({"prompt": "test"})
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["id"], "test-job")
        
    @patch('requests.request')
    def test_run_sync(self, mock_request):
        """Test synchronous task execution"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"result": "test"}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.run_sync({"prompt": "test"})
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["result"], "test")
        
    @patch('requests.request')
    def test_get_status(self, mock_request):
        """Test getting task status"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"status": "completed"}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.get_status("test-job")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["status"], "completed")
        
    @patch('requests.request')
    def test_cancel(self, mock_request):
        """Test canceling task"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"status": "cancelled"}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.cancel("test-job")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["status"], "cancelled")
        
    @patch('requests.request')
    def test_get_health(self, mock_request):
        """Test getting health status"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"healthy": True}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.get_health()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["healthy"], True)
        
    @patch('requests.request')
    def test_get_metrics(self, mock_request):
        """Test getting metrics"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"cpu": 50, "memory": 30}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.get_metrics()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["cpu"], 50)
        
    @patch('requests.request')
    def test_get_requests(self, mock_request):
        """Test getting request list"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"requests": []}}
        mock_request.return_value = mock_response
        
        result = self.endpoint.get_requests()
        self.assertEqual(result["code"], 20000)
        self.assertIn("requests", result["data"])

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token", api_key="test-key")
        self.auth = Auth(self.client)

    @patch('requests.request')
    def test_login(self, mock_request):
        """Test login functionality"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000, "data": {"token": "test"}}
        mock_request.return_value = mock_response
        
        result = self.auth.login("test", "password")
        self.assertEqual(result["code"], 20000)

class TestInstance(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token", api_key="test-key")
        self.instance = Instance(self.client)

    @patch('requests.request')
    def test_create_instance(self, mock_request):
        """Test instance creation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 20000}
        mock_request.return_value = mock_response
        
        result = self.instance.create(
            billing_method="payg",
            mode="pod",
            plan="gpu-rtx4090-24g-1"
        )
        self.assertEqual(result["code"], 20000)

if __name__ == '__main__':
    unittest.main()