"""Asynchronous SubModel API Client"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from .exceptions import raise_for_error
from .utils import log_request, log_response, logger

class AsyncSubModelClient:
    """Asynchronous SubModel API Client"""
    
    def __init__(self, 
                 token: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 max_retries: int = 3,
                 backoff_factor: float = 0.5):
        """Initialize the client
        
        Args:
            token: Login token
            api_key: API key
            max_retries: Maximum number of retries
            backoff_factor: Retry backoff factor
        """
        self.base_url = "https://api.submodel.ai/api/v1"
        self.token = token
        self.api_key = api_key
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._session = None
        
        if not (token or api_key):
            raise ValueError("Either token or api_key must be provided")
            
        logger.info("Initialized AsyncSubModel client")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["x-token"] = self.token
        if self.api_key:
            headers["x-apikey"] = self.api_key
        return headers
    
    async def _retry_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make a request with retry mechanism

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters
            
        Returns:
            API response data
        """
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        last_exception = None
        for attempt in range(self.max_retries + 1):  # Include initial attempt
            try:
                log_request(method, url, headers=headers, **kwargs)
                
                async with self._session.request(method, url, headers=headers, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    log_response(data)
                    raise_for_error(data)
                    return data

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt == self.max_retries:  # Last attempt failed
                    logger.error(f"Request failed ({str(e)}), max retries ({self.max_retries}) reached")
                    raise last_exception
                
                retry_delay = self.backoff_factor * (2 ** attempt)
                logger.warning(f"Request failed ({str(e)}), retrying in {retry_delay:.2f} seconds (attempt {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(retry_delay)
        
        if last_exception:
            raise last_exception
        return None  # Never reached, but keeps type checker happy
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Send HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Request parameters
            
        Returns:
            API response data
            
        Raises:
            APIError: When API returns an error
            AuthenticationError: When authentication fails
            ResourceNotFoundError: When requested resource doesn't exist
            QuotaExceededError: When quota is exceeded
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return await self._retry_request(method, url, **kwargs)
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Send GET request"""
        return await self._request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Send POST request"""
        return await self._request("POST", endpoint, **kwargs)
    
    async def __aenter__(self):
        """Enter async context"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def auth(self):
        """Get authentication management instance"""
        from .auth import Auth
        if not hasattr(self, '_auth'):
            self._auth = Auth(self)
        return self._auth

    @property
    def instance(self):
        """Get instance management instance"""
        from .instance import Instance
        if not hasattr(self, '_instance'):
            self._instance = Instance(self)
        return self._instance

def create_async_client(token: Optional[str] = None, 
                       api_key: Optional[str] = None, 
                       **kwargs) -> AsyncSubModelClient:
    """Create async client"""
    return AsyncSubModelClient(token=token, api_key=api_key, **kwargs)