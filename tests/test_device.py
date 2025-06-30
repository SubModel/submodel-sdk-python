import unittest
from unittest.mock import patch, MagicMock
from submodel import create_client

class TestDevice(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.device = self.client.device
    
    @patch('requests.request')
    def test_list_devices(self, mock_request):
        """Test listing devices"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "items": [
                    {"id": "device1", "status": "online"},
                    {"id": "device2", "status": "offline"}
                ]
            }
        }
        mock_request.return_value = mock_response

        result = self.device.list_devices(page=1, limit=10)
        self.assertEqual(result["code"], 20000)
        self.assertEqual(len(result["data"]["items"]), 2)
          # Verify request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["page"], 1)
        self.assertEqual(kwargs["params"]["limit"], 10)

    @patch('requests.request')
    def test_get_device(self, mock_request):
        """Test getting device details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "id": "device1",
                "status": "online",
                "machine_id": "test123"
            }
        }
        mock_request.return_value = mock_response

        result = self.device.get_device("device1")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["id"], "device1")

    @patch('requests.request')
    def test_control_device(self, mock_request):
        """Test device control operations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": "success"
        }
        mock_request.return_value = mock_response

        actions = ["run", "stop", "release", "set_label"]
        for action in actions:
            result = self.device.control_device(action, "device1")
            self.assertEqual(result["code"], 20000)        # Test invalid operation
        with self.assertRaises(ValueError):
            self.device.control_device("invalid_action", "device1")

class TestArea(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.area = self.client.area

    @patch('requests.request')
    def test_list_areas(self, mock_request):
        """Test listing available areas"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "items": [
                    {"id": "area1", "name": "Zone A"},
                    {"id": "area2", "name": "Zone B"}
                ]
            }
        }
        mock_request.return_value = mock_response

        result = self.area.list_areas()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(len(result["data"]["items"]), 2)

    @patch('requests.request')
    def test_get_area(self, mock_request):
        """Test getting area details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "id": "area1",
                "name": "Zone A",
                "status": "active"
            }
        }
        mock_request.return_value = mock_response

        result = self.area.get_area("area1")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["id"], "area1")

class TestBaremetal(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token")
        self.baremetal = self.client.baremetal

    @patch('requests.request')
    def test_list_baremetals(self, mock_request):
        """Test listing physical servers"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "page": 1,
                "limit": 10,
                "total": 2,
                "items": [
                    {"id": "bm1", "type": "gpu"},
                    {"id": "bm2", "type": "cpu"}
                ]
            }
        }
        mock_request.return_value = mock_response

        result = self.baremetal.list_baremetals()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(len(result["data"]["items"]), 2)
        
        # 验证请求参数
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["params"]["mode"], "baremetal")

if __name__ == '__main__':
    unittest.main()