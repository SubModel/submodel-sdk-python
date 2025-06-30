import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from submodel.cli.cli import cli
from submodel.sdk.exceptions import AuthenticationError, APIError

#import submodel.cli.cli

def create_mock_client():
    """Create mock client object"""
    mock_client = MagicMock()
    mock_client.auth = MagicMock()
    mock_client.instance = MagicMock()
    mock_client.device = MagicMock()
    return mock_client

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.mock_client = create_mock_client()

    @patch('submodel.cli.cli.create_client')
    def test_auth_login(self, mock_create_client):
        mock_create_client.return_value = self.mock_client
        self.mock_client.auth.login.return_value = {
            "code": 20000,
            "data": {"token": "test-token"}
        }

        result = self.runner.invoke(cli, [
            '--token', 'test-token',
            'auth', 'login', 'testuser', 'password'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test-token', result.output)
        self.mock_client.auth.login.assert_called_once_with('testuser', 'password')

    @patch('submodel.cli.cli.create_client')
    def test_instance_create(self, mock_create_client):
        mock_create_client.return_value = self.mock_client
        self.mock_client.instance.create.return_value = {
            "code": 20000,
            "data": {"inst_id": "test-id"}
        }

        result = self.runner.invoke(cli, [
            '--token', 'test-token',
            'instance', 'create',
            '--billing-method', 'payg',
            '--mode', 'pod'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test-id', result.output)

    @patch('submodel.cli.cli.create_client')
    def test_instance_list(self, mock_create_client):
        mock_create_client.return_value = self.mock_client
        self.mock_client.instance.list_instances.return_value = {
            "code": 20000,
            "data": {
                "items": [
                    {"inst_id": "id1", "status": "running"},
                    {"inst_id": "id2", "status": "stopped"}
                ]
            }
        }

        result = self.runner.invoke(cli, [
            '--token', 'test-token',
            'instance', 'list'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('id1', result.output)
        self.assertIn('id2', result.output)

    @patch('submodel.cli.cli.create_client')
    def test_device_list(self, mock_create_client):
        mock_create_client.return_value = self.mock_client
        self.mock_client.device.list_devices.return_value = {
            "code": 20000,
            "data": {
                "items": [
                    {"id": "dev1", "status": "online"},
                    {"id": "dev2", "status": "offline"}
                ]
            }
        }

        result = self.runner.invoke(cli, [
            '--token', 'test-token',
            'device', 'list'
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('dev1', result.output)
        self.assertIn('dev2', result.output)

    @patch('submodel.cli.cli.create_client')
    def test_cli_without_auth(self, mock_create_client):
        """Test behavior without authentication"""
        mock_create_client.side_effect = ValueError("Missing authentication")
        
        result = self.runner.invoke(cli, ['instance', 'list'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Authentication required', result.output)

    @patch('submodel.cli.cli.create_client')
    def test_error_handling(self, mock_create_client):
        """Test error handling"""
        mock_create_client.return_value = self.mock_client
        
        # Mock authentication error
        self.mock_client.instance.list_instances.side_effect = AuthenticationError("Authentication failed")
        result = self.runner.invoke(cli, ['--token', 'invalid-token', 'instance', 'list'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('Authentication failed', result.output)

        # Mock API error
        self.mock_client.instance.list_instances.side_effect = APIError("API error", 50000)
        result = self.runner.invoke(cli, ['--token', 'test-token', 'instance', 'list'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('API error', result.output)

    @patch('submodel.cli.cli.create_client')
    def test_debug_mode(self, mock_create_client):
        """Test debug mode"""
        # Set up logger
        import logging
        logger = logging.getLogger("submodel")
        logger.setLevel(logging.DEBUG)
        logger.handlers = []  # Clear all existing handlers
        
        # Create a temporary log handler to capture logs
        import io
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        try:
            # Set up mock objects
            mock_create_client.return_value = self.mock_client
            self.mock_client.instance.list_instances.side_effect = Exception("Debug mode test error")
            
            # Execute command
            result = self.runner.invoke(cli, ['--debug', '--token', 'test-token', 'instance', 'list'])
            
            # Verify exit code
            self.assertEqual(result.exit_code, 1)
            
            # Get and verify log output
            log_output = log_stream.getvalue()
            self.assertTrue(log_output, "No logs were captured")
            self.assertIn('Debug mode enabled', log_output)
        
        finally:
            # Clean up logger configuration
            logger.removeHandler(handler)
            handler.close()

if __name__ == '__main__':
    unittest.main()