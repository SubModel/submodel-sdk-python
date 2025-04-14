import unittest
import asyncio
from unittest.mock import patch, AsyncMock
import aiohttp
from submodel.sdk.async_client import AsyncSubModelClient, create_async_client
from submodel.sdk.exceptions import AuthenticationError

class TestAsyncClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Async setup method"""
        self.client = AsyncSubModelClient(token="test-token")
        await self.client.__aenter__()

    async def asyncTearDown(self):
        """Async cleanup method"""
        await self.client.__aexit__(None, None, None)

    @patch('aiohttp.ClientSession.request')
    async def test_authentication_error(self, mock_request):
        """Test authentication error handling"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": 40100,
            "message": "Authentication failed"
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context

        with self.assertRaises(AuthenticationError):
            await self.client.get("test/endpoint")

    @patch('aiohttp.ClientSession.request')
    async def test_get_request(self, mock_request):
        """Test basic request"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": 20000,
            "data": "success"
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context

        result = await self.client.get("test/endpoint")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"], "success")

    @patch('aiohttp.ClientSession.request')
    async def test_retry_mechanism(self, mock_request):
        """Test retry mechanism"""
        # Set retry parameters
        self.client.max_retries = 2
        self.client.backoff_factor = 0.1

        # Mock success response
        success_response = AsyncMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={
            "code": 20000,
            "data": "success"
        })

        # Mock error response
        error_response = AsyncMock()
        error_response.__aenter__.side_effect = aiohttp.ClientError("Connection failed")

        # Set response sequence: two failures, then success
        success_context = AsyncMock()
        success_context.__aenter__.return_value = success_response

        responses = [error_response, error_response, success_context]
        mock_request.side_effect = responses

        # Execute request
        result = await self.client.get("test/endpoint")
        
        # Verify results
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"], "success")
        self.assertEqual(mock_request.call_count, 3)  # Verify total attempts

    @patch('aiohttp.ClientSession.request')
    async def test_session_management(self, mock_request):
        """Test session management"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": 20000,
            "data": "success"
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context

        # Create new client using context manager
        async with create_async_client(token="test-token") as client:
            result = await client.get("test/endpoint")
            self.assertEqual(result["code"], 20000)
            self.assertTrue(client._session is not None)

        # Verify session is closed
        self.assertIsNone(client._session)

if __name__ == '__main__':
    unittest.main()