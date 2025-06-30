import pytest
from unittest.mock import Mock, patch
from submodel.sdk.endpoint import ServerlessEndpoint, Instance
from submodel.sdk.client import SubModelClient


class TestServerlessEndpoint:
    """Test ServerlessEndpoint class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client"""
        return Mock(spec=SubModelClient)
    
    @pytest.fixture
    def endpoint(self, mock_client):
        """Create endpoint instance"""
        return ServerlessEndpoint(mock_client, "test-inst-id")
    
    def test_init(self, mock_client):
        """Test initialization"""
        endpoint = ServerlessEndpoint(mock_client, "test-id")
        assert endpoint.client == mock_client
        assert endpoint.inst_id == "test-id"
    
    def test_run(self, endpoint, mock_client):
        """Test run method"""
        input_data = {"key": "value"}
        expected_response = {"job_id": "123", "status": "running"}
        mock_client.post.return_value = expected_response
        
        result = endpoint.run(input_data)
        
        mock_client.post.assert_called_once_with(
            "sl/test-inst-id/run", 
            json={"input": input_data}
        )
        assert result == expected_response
    
    def test_run_sync(self, endpoint, mock_client):
        """Test run_sync method"""
        input_data = {"key": "value"}
        expected_response = {"result": "success"}
        mock_client.post.return_value = expected_response
        
        result = endpoint.run_sync(input_data)
        
        mock_client.post.assert_called_once_with(
            "sl/test-inst-id/runsync", 
            json={"input": input_data}
        )
        assert result == expected_response
    
    def test_get_status(self, endpoint, mock_client):
        """Test get_status method"""
        job_id = "job-123"
        expected_response = {"status": "completed", "result": "success"}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_status(job_id)
        
        mock_client.get.assert_called_once_with(f"sl/test-inst-id/status/{job_id}")
        assert result == expected_response
    
    def test_cancel(self, endpoint, mock_client):
        """Test cancel method"""
        job_id = "job-123"
        expected_response = {"status": "cancelled"}
        mock_client.get.return_value = expected_response
        
        result = endpoint.cancel(job_id)
        
        mock_client.get.assert_called_once_with(f"sl/test-inst-id/cancel/{job_id}")
        assert result == expected_response
    
    def test_get_health(self, endpoint, mock_client):
        """Test get_health method"""
        expected_response = {"healthy": True}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_health()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/health")
        assert result == expected_response
    
    def test_get_metrics(self, endpoint, mock_client):
        """Test get_metrics method"""
        expected_response = {"cpu_usage": 50, "memory_usage": 30}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_metrics()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/metrics")
        assert result == expected_response
    
    def test_get_requests(self, endpoint, mock_client):
        """Test get_requests method"""
        expected_response = {"requests": [{"id": "req-1", "status": "completed"}]}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_requests()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/_requests")
        assert result == expected_response
    
    def test_get_request_details(self, endpoint, mock_client):
        """Test get_request_details method"""
        request_id = "req-123"
        expected_response = {"id": request_id, "status": "completed", "result": "success"}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_request_details(request_id)
        
        mock_client.get.assert_called_once_with(f"sl/test-inst-id/_requests/{request_id}")
        assert result == expected_response
    
    def test_list_models(self, endpoint, mock_client):
        """Test list_models method"""
        expected_response = {"models": [{"id": "model-1", "name": "test-model"}]}
        mock_client.get.return_value = expected_response
        
        result = endpoint.list_models()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/models")
        assert result == expected_response
    
    def test_get_model_info(self, endpoint, mock_client):
        """Test get_model_info method"""
        model_id = "model-123"
        expected_response = {"id": model_id, "name": "test-model", "version": "1.0"}
        mock_client.get.return_value = expected_response
        
        result = endpoint.get_model_info(model_id)
        
        mock_client.get.assert_called_once_with(f"sl/test-inst-id/models/{model_id}")
        assert result == expected_response


class TestInstance:
    """Test Instance class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client"""
        return Mock(spec=SubModelClient)
    
    @pytest.fixture
    def instance(self, mock_client):
        """Create instance"""
        return Instance(mock_client)
    
    def test_init(self, mock_client):
        """Test initialization"""
        instance = Instance(mock_client)
        assert instance.client == mock_client
    
    def test_create_with_defaults(self, instance, mock_client):
        """Test create method with default parameters"""
        expected_response = {"inst_id": "new-inst-123", "status": "created"}
        mock_client.post.return_value = expected_response
        
        result = instance.create()
        
        expected_data = {
            "billing_method": "payg",
            "mode": "pod",
            "plan": "gpu-rtx4090-24g-1",
            "image": "ubuntu-22.04",
            "pod_num": 1,
            "area": [],
            "conf": {},
            "container_size": 5,
            "volume_size": 5,
            "volume_mount_path": "/workspace"
        }
        mock_client.post.assert_called_once_with("inst/create", json=expected_data)
        assert result == expected_response
    
    def test_create_with_custom_params(self, instance, mock_client):
        """Test create method with custom parameters"""
        expected_response = {"inst_id": "new-inst-123", "status": "created"}
        mock_client.post.return_value = expected_response
        
        result = instance.create(
            billing_method="subscription",
            mode="serverless",
            plan="cpu-4c-8g",
            image="python-3.9",
            pod_num=2,
            area=["us-west"],
            conf={"env": "test"},
            container_size=10,
            volume_size=20,
            volume_mount_path="/data",
            custom_param="value"
        )
        
        expected_data = {
            "billing_method": "subscription",
            "mode": "serverless",
            "plan": "cpu-4c-8g",
            "image": "python-3.9",
            "pod_num": 2,
            "area": ["us-west"],
            "conf": {"env": "test"},
            "container_size": 10,
            "volume_size": 20,
            "volume_mount_path": "/data",
            "custom_param": "value"
        }
        mock_client.post.assert_called_once_with("inst/create", json=expected_data)
        assert result == expected_response
    
    def test_list_instances(self, instance, mock_client):
        """Test list_instances method"""
        expected_response = {"instances": [{"id": "inst-1", "status": "running"}]}
        mock_client.get.return_value = expected_response
        
        result = instance.list_instances(page=2, limit=20, mode="serverless")
        
        expected_params = {"page": 2, "limit": 20, "mode": "serverless"}
        mock_client.get.assert_called_once_with("inst/list", params=expected_params)
        assert result == expected_response
    
    def test_list_instances_defaults(self, instance, mock_client):
        """Test list_instances method with defaults"""
        expected_response = {"instances": []}
        mock_client.get.return_value = expected_response
        
        result = instance.list_instances()
        
        expected_params = {"page": 1, "limit": 10, "mode": "pod"}
        mock_client.get.assert_called_once_with("inst/list", params=expected_params)
        assert result == expected_response
    
    def test_get_instance(self, instance, mock_client):
        """Test get_instance method"""
        inst_id = "inst-123"
        expected_response = {"id": inst_id, "status": "running", "plan": "gpu-rtx4090-24g-1"}
        mock_client.get.return_value = expected_response
        
        result = instance.get_instance(inst_id)
        
        mock_client.get.assert_called_once_with(f"inst/detail/{inst_id}")
        assert result == expected_response
    
    def test_get_pods(self, instance, mock_client):
        """Test get_pods method"""
        inst_id = "inst-123"
        expected_response = {"pods": [{"id": "pod-1", "status": "running"}]}
        mock_client.get.return_value = expected_response
        
        result = instance.get_pods(inst_id)
        
        mock_client.get.assert_called_once_with(f"inst/cont/{inst_id}")
        assert result == expected_response
    
    def test_get_pod_logs(self, instance, mock_client):
        """Test get_pod_logs method"""
        inst_id = "inst-123"
        pod_id = "pod-456"
        expected_response = {"logs": "Application started successfully"}
        mock_client.get.return_value = expected_response
        
        result = instance.get_pod_logs(inst_id, pod_id)
        
        mock_client.get.assert_called_once_with(f"inst/{inst_id}/pod/{pod_id}/logs")
        assert result == expected_response
    
    def test_terminate_pod(self, instance, mock_client):
        """Test terminate_pod method"""
        inst_id = "inst-123"
        pod_id = "pod-456"
        expected_response = {"status": "terminating"}
        mock_client.get.return_value = expected_response
        
        result = instance.terminate_pod(inst_id, pod_id)
        
        mock_client.get.assert_called_once_with(f"inst/{inst_id}/pod/{pod_id}/terminate")
        assert result == expected_response
    
    def test_control_instance_valid_actions(self, instance, mock_client):
        """Test control_instance method with valid actions"""
        inst_id = "inst-123"
        expected_response = {"status": "success"}
        mock_client.post.return_value = expected_response
        
        valid_actions = [
            "run", "stop", "release", "restart", "remote_cmd",
            "setlabel", "set_ports", "change_image", "set_ex_setting", "set_envs"
        ]
        
        for action in valid_actions:
            mock_client.reset_mock()
            kwargs = {"param": "value"}
            
            result = instance.control_instance(action, inst_id, **kwargs)
            
            mock_client.post.assert_called_once_with(
                f"inst/action/{action}/{inst_id}", 
                json=kwargs
            )
            assert result == expected_response
    
    def test_control_instance_invalid_action(self, instance, mock_client):
        """Test control_instance method with invalid action"""
        inst_id = "inst-123"
        
        with pytest.raises(ValueError) as exc_info:
            instance.control_instance("invalid_action", inst_id)
        
        assert "Invalid action" in str(exc_info.value)
        mock_client.post.assert_not_called()
    
    def test_control_instance_with_kwargs(self, instance, mock_client):
        """Test control_instance method with additional kwargs"""
        inst_id = "inst-123"
        expected_response = {"status": "success"}
        mock_client.post.return_value = expected_response
        
        kwargs = {
            "command": "ls -la",
            "timeout": 30,
            "env": {"VAR": "value"}
        }
        
        result = instance.control_instance("remote_cmd", inst_id, **kwargs)
        
        mock_client.post.assert_called_once_with(
            f"inst/action/remote_cmd/{inst_id}", 
            json=kwargs
        )
        assert result == expected_response
