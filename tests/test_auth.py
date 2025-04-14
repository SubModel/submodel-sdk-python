import unittest
from unittest.mock import patch, MagicMock
from submodel.sdk.client import create_client
from submodel.sdk.exceptions import AuthenticationError

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = create_client(token="test-token", api_key="test-key")

    @patch('requests.request')
    def test_register(self, mock_request):
        """Test registration functionality"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "token": "test-token",
                "expired": 1745179216
            }
        }
        mock_request.return_value = mock_response

        result = self.client.auth.register("testuser", "testpass")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["token"], "test-token")
          # Verify request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs["json"]["username"], "testuser")
        self.assertEqual(kwargs["json"]["password"], "testpass")

    @patch('requests.request')
    def test_login(self, mock_request):
        """Test login functionality"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "token": "test-token",
                "expired": 1745179216
            }
        }
        mock_request.return_value = mock_response

        result = self.client.auth.login("testuser", "testpass")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["token"], "test-token")

    @patch('requests.request')
    def test_get_user_info(self, mock_request):
        """Test getting user information"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": {
                "username": "testuser",
                "roles": ["user"],
                "uid": "test123"
            }
        }
        mock_request.return_value = mock_response

        result = self.client.auth.get_user_info()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"]["username"], "testuser")

    @patch('requests.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 40100,
            "message": "Authentication failed"
        }
        mock_request.return_value = mock_response

        with self.assertRaises(AuthenticationError) as context:
            self.client.auth.get_user_info()
        self.assertEqual(str(context.exception), "Authentication failed")

    @patch('requests.request')
    def test_api_key_operations(self, mock_request):
        """Test API Key related operations"""
        # 测试生成 API Key
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 20000,
            "data": "new-api-key"
        }
        mock_request.return_value = mock_response

        result = self.client.auth.generate_api_key()
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"], "new-api-key")

        # 测试列出 API Keys
        mock_response.json.return_value = {
            "code": 20000,
            "data": ["key1", "key2"]
        }
        result = self.client.auth.list_api_keys()
        self.assertEqual(len(result["data"]), 2)

        # 测试激活/停用 API Key
        mock_response.json.return_value = {
            "code": 20000,
            "data": "success"
        }
        result = self.client.auth.active_api_key("key1", True)
        self.assertEqual(result["code"], 20000)

if __name__ == '__main__':
    unittest.main()