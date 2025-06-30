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

<<<<<<< HEAD
=======
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = AsyncSubModelClient(api_key="test-api-key")
        self.assertEqual(client.api_key, "test-api-key")
        self.assertIsNone(client.token)
        self.assertEqual(client.max_retries, 3)
        self.assertEqual(client.backoff_factor, 0.5)
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters"""
        client = AsyncSubModelClient(
            token="test-token", 
            max_retries=5, 
            backoff_factor=1.0
        )
        self.assertEqual(client.max_retries, 5)
        self.assertEqual(client.backoff_factor, 1.0)
    
    def test_init_without_credentials(self):
        """Test initialization without token or API key raises error"""
        with self.assertRaises(ValueError) as cm:
            AsyncSubModelClient()
        self.assertIn("Either token or api_key must be provided", str(cm.exception))
    
    def test_get_headers_with_token(self):
        """Test headers generation with token"""
        client = AsyncSubModelClient(token="test-token")
        headers = client._get_headers()
        self.assertEqual(headers["x-token"], "test-token")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertNotIn("x-apikey", headers)
    
    def test_get_headers_with_api_key(self):
        """Test headers generation with API key"""
        client = AsyncSubModelClient(api_key="test-api-key")
        headers = client._get_headers()
        self.assertEqual(headers["x-apikey"], "test-api-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertNotIn("x-token", headers)
    
    def test_get_headers_with_both(self):
        """Test headers generation with both token and API key"""
        client = AsyncSubModelClient(token="test-token", api_key="test-api-key")
        headers = client._get_headers()
        self.assertEqual(headers["x-token"], "test-token")
        self.assertEqual(headers["x-apikey"], "test-api-key")
        self.assertEqual(headers["Content-Type"], "application/json")
    
    @patch('aiohttp.ClientSession.request')
    async def test_request_without_session(self, mock_request):
        """Test request when session is not initialized"""
        client = AsyncSubModelClient(token="test-token")
        # Don't enter context manager to keep _session as None
        
        with self.assertRaises(RuntimeError) as context:
            await client.get("test/endpoint")
        
        self.assertIn("Client not initialized", str(context.exception))
    
    @patch('aiohttp.ClientSession.request')
    async def test_retry_mechanism_with_timeout(self, mock_request):
        """Test retry mechanism with timeout errors"""
        # Mock request to raise timeout error first few times, then succeed
        responses = [
            asyncio.TimeoutError("Request timeout"),
            asyncio.TimeoutError("Request timeout"),
            AsyncMock()  # Success on third attempt
        ]
        
        success_response = AsyncMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={
            "code": 20000,
            "data": "success"
        })
        
        success_context = AsyncMock()
        success_context.__aenter__.return_value = success_response
        
        def side_effect(*args, **kwargs):
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return success_context
        
        mock_request.side_effect = side_effect
        
        # Should succeed after retries
        result = await self.client.get("test/endpoint")
        self.assertEqual(result["code"], 20000)
        self.assertEqual(mock_request.call_count, 3)
    
    @patch('aiohttp.ClientSession.request')
    async def test_retry_mechanism_max_retries_exceeded(self, mock_request):
        """Test retry mechanism when max retries exceeded"""
        # Create client with fewer retries for faster test
        async with AsyncSubModelClient(token="test-token", max_retries=1) as client:
            # Mock all requests to fail
            mock_request.side_effect = aiohttp.ClientError("Connection failed")
            
            with self.assertRaises(aiohttp.ClientError):
                await client.get("test/endpoint")
            
            # Should try initial + 1 retry = 2 attempts
            self.assertEqual(mock_request.call_count, 2)
    
    @patch('aiohttp.ClientSession.request')
    async def test_retry_with_client_error(self, mock_request):
        """Test retry mechanism with client errors"""
        mock_request.side_effect = aiohttp.ClientError("Network error")
        
        with self.assertRaises(aiohttp.ClientError):
            await self.client.get("test/endpoint")
        
        # Should retry max_retries + 1 times
        self.assertEqual(mock_request.call_count, self.client.max_retries + 1)
    
    @patch('aiohttp.ClientSession.request')
    async def test_post_request(self, mock_request):
        """Test POST request"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "code": 20000,
            "data": "post success"
        })
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context
        
        result = await self.client.post("test/endpoint", json={"test": "data"})
        self.assertEqual(result["code"], 20000)
        self.assertEqual(result["data"], "post success")
    
    async def test_context_manager_multiple_entries(self):
        """Test context manager with multiple entries"""
        client = AsyncSubModelClient(token="test-token")
        
        # First entry
        async with client as c1:
            self.assertIsNotNone(c1._session)
            session1 = c1._session
            
            # Second entry should reuse session
            async with client as c2:
                self.assertIs(c2._session, session1)
    
    def test_create_async_client_function(self):
        """Test create_async_client factory function"""
        client = create_async_client(token="test-token")
        self.assertIsInstance(client, AsyncSubModelClient)
        self.assertEqual(client.token, "test-token")
        
        client_with_api_key = create_async_client(api_key="test-api-key")
        self.assertIsInstance(client_with_api_key, AsyncSubModelClient)
        self.assertEqual(client_with_api_key.api_key, "test-api-key")
    
    def test_initialization_edge_cases(self):
        """Test various initialization scenarios"""
        # Test with both token and api_key
        client = AsyncSubModelClient(token="token", api_key="key")
        self.assertEqual(client.token, "token")
        self.assertEqual(client.api_key, "key")
        
        # Test with custom retry settings
        client = AsyncSubModelClient(
            token="token", 
            max_retries=5, 
            backoff_factor=1.0
        )
        self.assertEqual(client.max_retries, 5)
        self.assertEqual(client.backoff_factor, 1.0)
    
    @patch('aiohttp.ClientSession.request')
    async def test_header_merging(self, mock_request):
        """Test that custom headers are merged with default headers"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"code": 20000})
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context
        
        # Make request with custom headers
        custom_headers = {"Custom-Header": "custom-value"}
        await self.client.get("test/endpoint", headers=custom_headers)
        
        # Verify headers were merged
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        self.assertIn("Content-Type", headers)
        self.assertIn("x-token", headers)
        self.assertIn("Custom-Header", headers)
        self.assertEqual(headers["Custom-Header"], "custom-value")
    
    def test_api_key_authentication(self):
        """Test API key authentication header generation"""
        client = AsyncSubModelClient(api_key="test-api-key")
        headers = client._get_headers()
        
        self.assertIn("x-apikey", headers)
        self.assertEqual(headers["x-apikey"], "test-api-key")
        self.assertNotIn("x-token", headers)
    
    def test_token_authentication(self):
        """Test token authentication header generation"""
        client = AsyncSubModelClient(token="test-token")
        headers = client._get_headers()
        
        self.assertIn("x-token", headers)
        self.assertEqual(headers["x-token"], "test-token")
        self.assertNotIn("x-apikey", headers)
    
    @patch('aiohttp.ClientSession.request')
    async def test_endpoint_url_formatting(self, mock_request):
        """Test URL formatting for different endpoint formats"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"code": 20000})
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_request.return_value = mock_context
        
        # Test endpoint without leading slash
        await self.client.get("test/endpoint")
        call_args = mock_request.call_args
        url = call_args[0][1]
        self.assertEqual(url, "https://api.submodel.ai/api/v1/test/endpoint")
        
        # Test endpoint with leading slash
        await self.client.get("/test/endpoint")
        call_args = mock_request.call_args  
        url = call_args[0][1]
        self.assertEqual(url, "https://api.submodel.ai/api/v1/test/endpoint")
    
    async def test_session_cleanup_on_exception(self):
        """Test that session is cleaned up even when exception occurs in context"""
        client = AsyncSubModelClient(token="test-token")
        
        try:
            async with client:
                self.assertIsNotNone(client._session)
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Session should be cleaned up
        self.assertIsNone(client._session)

>>>>>>> private-repo/main
if __name__ == '__main__':
    unittest.main()