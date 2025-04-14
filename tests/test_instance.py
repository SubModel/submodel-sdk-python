import unittest
from unittest.mock import patch, MagicMock
from submodel.sdk.client import create_client
from submodel.sdk.exceptions import ResourceNotFoundError

class TestInstance(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.instance = self.client.instance

    @patch('requests.request')
    def test_create_instance(self, mock_request):
        """Test instance creation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "inst_id": "test-instance-id"
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.create(
            billing_method="payg",
            mode="pod",
            plan="gpu-rtx4090-24g-1",
            image="ubuntu-22.04",
            pod_num=1,
            conf={
                "root_pw": "test123",
                "inst_label": "test-instance",
                "auto_renewal": True
            }
        )
        
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["inst_id"], "test-instance-id")
        
        # Verify request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["json"]["billing_method"], "payg")
        self.assertEqual(kwargs["json"]["mode"], "pod")
        self.assertEqual(kwargs["json"]["plan"], "gpu-rtx4090-24g-1")

    @patch('requests.request')
    def test_list_instances(self, mock_request):
        """Test list instances"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "items": [
                    {"inst_id": "id1", "status": "running"},
                    {"inst_id": "id2", "status": "stopped"}
                ]
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.list_instances(page=1, limit=10)
        self.assertEqual(result["code"], 20000)
        self.assertEqual(len(result["data"]["items"]), 2)
        
        # Verify request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["page"], 1)
        self.assertEqual(kwargs["params"]["limit"], 10)
        self.assertEqual(kwargs["params"]["mode"], "pod")

    @patch('requests.request')
    def test_get_instance(self, mock_request):
        """Test get instance details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "inst_id": "test-id",
                "status": "running",
                "mode": "pod"
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.get_instance("test-id")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["inst_id"], "test-id")

    @patch('requests.request')
    def test_control_instance(self, mock_request):
        """Test instance control operations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": "success"
        }
        mock_request.return_value = mock_response

        # Test various control operations
        actions = ["run", "stop", "release", "restart"]
        for action in actions:
            result = self.instance.control_instance(action, "test-id")
            self.assertEqual(result["code"], 20000)
            
        # Test invalid operation
        with self.assertRaises(ValueError):
            self.instance.control_instance("invalid_action", "test-id")

    @patch('requests.request')
    def test_instance_not_found(self, mock_request):
        """Test instance not found error"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 40400,
            "message": "Instance not found"
        }
        mock_request.return_value = mock_response

        with self.assertRaises(ResourceNotFoundError) as context:
            self.instance.get_instance("non-existent-id")
        self.assertEqual(str(context.exception), "Instance not found")

    @patch('requests.request')
    def test_get_pod_logs(self, mock_request):
        """Test get container logs"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "logs": "Container logs..."
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.get_pod_logs("inst-id", "pod-id")
        self.assertEqual(result["code"], 20000)
        self.assertIn("logs", result["data"])
        
        # Verify request path
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn("inst-id", args[1])
        self.assertIn("pod-id", args[1])

if __name__ == '__main__':
    unittest.main()