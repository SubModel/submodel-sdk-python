"""SubModel API Client"""

import requests
from typing import Dict, Any, Optional
from .exceptions import raise_for_error
from .utils import log_request, log_response, logger, retry

class SubModelClient:
    """SubModel API Client"""
    
    def __init__(self, 
                 token: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 max_retries: int = 3,
                 backoff_factor: float = 0.5):
        """Initialize the client
        
        Args:
            token: Access token
            api_key: API key
            max_retries: Maximum number of retries
            backoff_factor: Retry backoff factor
        """
        self.base_url = "https://api.submodel.ai/api/v1"
        self.token = token
        self.api_key = api_key
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        if not (token or api_key):
            raise ValueError("Either token or api_key must be provided")
            
        logger.info("Initialized SubModel client")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["x-token"] = self.token
        if self.api_key:
            headers["x-apikey"] = self.api_key
        return headers
    
    @retry()
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
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
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
            
        # Log request
        log_request(method, url, headers=headers, **kwargs)
            
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        data = response.json()
        # Log response
        log_response(data)
        
        # Check API errors
        raise_for_error(data)
        
        return data
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Send GET request"""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Send POST request"""
        return self._request("POST", endpoint, **kwargs)

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

    @property
    def device(self):
        """Get device management instance"""
        from .device import Device
        if not hasattr(self, '_device'):
            self._device = Device(self)
        return self._device

    @property
    def area(self):
        """Get area management instance"""
        from .device import Area
        if not hasattr(self, '_area'):
            self._area = Area(self)
        return self._area

    @property
    def baremetal(self):
        """Get baremetal management instance"""
        from .device import Baremetal
        if not hasattr(self, '_baremetal'):
            self._baremetal = Baremetal(self)
        return self._baremetal

def create_client(token: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 **kwargs) -> SubModelClient:
    """Create SubModel API client"""
    return SubModelClient(token=token, api_key=api_key, **kwargs)

class APIError(Exception):
    """API Error"""
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(f"API Error {code}: {message}")