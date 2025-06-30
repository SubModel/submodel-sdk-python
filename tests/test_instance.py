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
    def test_delete_instance(self, mock_request):
        """Test instance deletion"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"message": "Instance deleted successfully"}
        }
        mock_request.return_value = mock_response

        result = self.instance.delete_instance("test-id")
        self.assertEqual(result["code"], 20000)
        
        # Verify POST request to delete endpoint
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertIn("inst/delete/test-id", args[1])

    @patch('requests.request')
    def test_get_pods(self, mock_request):
        """Test get instance pods"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "pods": [
                    {"pod_id": "pod-1", "status": "running"},
                    {"pod_id": "pod-2", "status": "pending"}
                ]
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.get_pods("test-inst-id")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(len(result["data"]["pods"]), 2)
        
        # Verify GET request to container endpoint
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertIn("inst/cont/test-inst-id", args[1])

    @patch('requests.request')
    def test_get_pod_logs(self, mock_request):
        """Test get pod logs"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "logs": "Application started successfully\nListening on port 8080"
            }
        }
        mock_request.return_value = mock_response

        result = self.instance.get_pod_logs("test-inst-id", "test-pod-id")
        self.assertEqual(result["code"], 20000)
        self.assertIn("Application started", result["data"]["logs"])
        
        # Verify GET request to logs endpoint
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertIn("inst/test-inst-id/pod/test-pod-id/logs", args[1])

    @patch('requests.request')
    def test_terminate_pod(self, mock_request):
        """Test terminate pod"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"message": "Pod terminated successfully"}
        }
        mock_request.return_value = mock_response

        result = self.instance.terminate_pod("test-inst-id", "test-pod-id")
        self.assertEqual(result["code"], 20000)
        
        # Verify GET request to terminate endpoint
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertIn("inst/test-inst-id/pod/test-pod-id/terminate", args[1])

    @patch('requests.request')
    def test_control_instance_all_actions(self, mock_request):
        """Test all valid control actions"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"message": "Action completed"}
        }
        mock_request.return_value = mock_response

        valid_actions = [
            "run", "stop", "release", "restart", "remote_cmd",
            "setlabel", "set_ports", "change_image", "set_ex_setting", "set_envs"
        ]
        
        for action in valid_actions:
            mock_request.reset_mock()
            
            result = self.instance.control_instance(action, "test-inst-id", param="value")
            self.assertEqual(result["code"], 20000)
            
            # Verify POST request to action endpoint
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            self.assertEqual(args[0], "POST")
            self.assertIn(f"inst/action/{action}/test-inst-id", args[1])
            self.assertEqual(kwargs["json"], {"param": "value"})

    def test_control_instance_invalid_action(self):
        """Test control instance with invalid action"""
        with self.assertRaises(ValueError) as cm:
            self.instance.control_instance("invalid_action", "test-inst-id")
        
        self.assertIn("Invalid action", str(cm.exception))
        self.assertIn("Must be one of", str(cm.exception))

    @patch('requests.request')
    def test_create_instance_with_defaults(self, mock_request):
        """Test instance creation with default parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"inst_id": "test-instance-id"}
        }
        mock_request.return_value = mock_response

        # Call create without any parameters to test defaults
        result = self.instance.create()
        self.assertEqual(result["code"], 20000)
        
        # Verify default parameters were used
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        json_data = kwargs["json"]
        self.assertEqual(json_data["billing_method"], "payg")
        self.assertEqual(json_data["mode"], "pod")
        self.assertEqual(json_data["plan"], "gpu-rtx4090-24g-1")
        self.assertEqual(json_data["image"], "ubuntu-22.04")
        self.assertEqual(json_data["pod_num"], 1)
        self.assertEqual(json_data["area"], [])
        self.assertEqual(json_data["conf"], {})

    @patch('requests.request')
    def test_create_instance_with_custom_params(self, mock_request):
        """Test instance creation with custom parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"inst_id": "test-instance-id"}
        }
        mock_request.return_value = mock_response

        # Test with custom parameters and kwargs
        result = self.instance.create(
            billing_method="monthly",
            mode="baremetal",
            plan="gpu-a100-80g-1",
            image="python-3.9",
            pod_num=2,
            area=["us-west", "eu-central"],
            conf={"env": "production", "auto_scale": True},
            custom_param="custom_value",
            another_param=123
        )
        self.assertEqual(result["code"], 20000)
        
        # Verify all parameters were passed correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        json_data = kwargs["json"]
        self.assertEqual(json_data["billing_method"], "monthly")
        self.assertEqual(json_data["mode"], "baremetal")
        self.assertEqual(json_data["plan"], "gpu-a100-80g-1")
        self.assertEqual(json_data["image"], "python-3.9")
        self.assertEqual(json_data["pod_num"], 2)
        self.assertEqual(json_data["area"], ["us-west", "eu-central"])
        self.assertEqual(json_data["conf"], {"env": "production", "auto_scale": True})
        self.assertEqual(json_data["custom_param"], "custom_value")
        self.assertEqual(json_data["another_param"], 123)

    @patch('requests.request')
    def test_list_instances_with_custom_params(self, mock_request):
        """Test list instances with custom parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"items": [], "total": 0}
        }
        mock_request.return_value = mock_response

        # Test with custom pagination and mode
        result = self.instance.list_instances(page=3, limit=25, mode="baremetal")
        self.assertEqual(result["code"], 20000)
        
        # Verify custom parameters were used
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        params = kwargs["params"]
        self.assertEqual(params["page"], 3)
        self.assertEqual(params["limit"], 25)
        self.assertEqual(params["mode"], "baremetal")

    @patch('requests.request')
    def test_control_instance_with_complex_kwargs(self, mock_request):
        """Test control instance with complex kwargs"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {"message": "Remote command executed"}
        }
        mock_request.return_value = mock_response

        # Test remote_cmd action with complex parameters
        result = self.instance.control_instance(
            "remote_cmd", 
            "test-inst-id",
            command="docker run -d nginx",
            timeout=300,
            env_vars={"NODE_ENV": "production", "PORT": "3000"},
            working_dir="/app"
        )
        self.assertEqual(result["code"], 20000)
        
        # Verify complex kwargs were passed
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        json_data = kwargs["json"]
        self.assertEqual(json_data["command"], "docker run -d nginx")
        self.assertEqual(json_data["timeout"], 300)
        self.assertEqual(json_data["env_vars"]["NODE_ENV"], "production")
        self.assertEqual(json_data["working_dir"], "/app")

if __name__ == '__main__':
    unittest.main()