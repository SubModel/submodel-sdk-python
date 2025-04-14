import unittest
from unittest.mock import patch, MagicMock
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
    
    def test_handler_decorator(self):
        """Test handler decorator"""
        @self.handler.handler
        def test_func(job):
            return {"result": "success"}
        
        self.assertEqual(self.handler._handler, test_func)
    
    def test_instance_required(self):
        """Test instance ID requirement"""
        @self.handler.handler
        def test_func(job):
            return {"result": "success"}
            
        with self.assertRaises(ValueError):
            self.handler.start()
            
    @patch('builtins.print')
    def test_handler_execution(self, mock_print):
        """Test handler execution"""
        @self.handler.handler
        def test_func(job):
            return {"result": job["input"]["test"]}
            
        self.handler.set_instance("test-instance")
        
        # Mock environment variables
        with patch.dict(os.environ, {'SUBMODEL_INPUT': '{"input":{"test":"data"}}'}):
            self.handler._get_job_input()
            result = self.handler._handler({"input": {"test": "data"}})
            self.handler._return_result(result)
            
        mock_print.assert_called_once_with('{"output": {"result": "data"}}')

class TestServerlessEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.endpoint = ServerlessEndpoint(self.client, "test-instance")
        
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