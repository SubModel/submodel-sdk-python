class SubModelError(Exception):
    """Base exception class for SubModel SDK"""
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(SubModelError):
    """Parameter validation error"""
    pass

class AuthenticationError(SubModelError):
    """Authentication error"""
    pass

class APIError(SubModelError):
    """API call error"""
    pass

class RateLimitError(APIError):
    """API rate limit error"""
    pass

class ResourceNotFoundError(APIError):
    """Resource not found error"""
    pass

class ResourceExistsError(APIError):
    """Resource already exists error"""
    pass

class ServerError(APIError):
    """Server side error"""
    pass

class NetworkError(SubModelError):
    """Network related error"""
    pass

class RetryError(SubModelError):
    """Retry failure error"""
    pass

class QuotaExceededError(APIError):
    """Quota exceeded error"""
    pass

class ServerlessError(APIError):
    """Serverless related error"""
    pass

class DeviceError(APIError):
    """Device related error"""
    pass

def raise_for_error(response_data):
    """Raise appropriate exception based on API response status code
    
    Args:
        response_data: API response data
        
    Raises:
        AuthenticationError: When authentication fails
        RateLimitError: When API rate limit exceeded
        ResourceNotFoundError: When resource doesn't exist
        ResourceExistsError: When resource already exists
        ServerError: When server error occurs
        APIError: For other API errors
    """
    code = response_data.get('code', 0)
    message = response_data.get('message', 'Unknown error')
    
    if code == 40100:
        raise AuthenticationError(message, code)
    elif code == 40300:
        raise RateLimitError(message, code)
    elif code == 40400:
        raise ResourceNotFoundError(message, code)
    elif code == 40900:
        raise ResourceExistsError(message, code)
    elif code >= 50000:
        raise ServerError(message, code)
    elif code != 20000:  # 20000 means success
        raise APIError(message, code)