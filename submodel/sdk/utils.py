import logging
import json
import time
from typing import Any, Dict, Optional, Callable, Type, Union
from functools import wraps
from requests.exceptions import RequestException

# Configure logging
logger = logging.getLogger("submodel")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def set_log_level(level: int) -> None:
    """Set logging level
    
    Args:
        level: Log level, e.g., logging.DEBUG, logging.INFO, etc.
    """
    logger.setLevel(level)
    handler.setLevel(level)

def log_request(method: str, url: str, **kwargs) -> None:
    """Log HTTP request
    
    Args:
        method: HTTP method
        url: Request URL
        **kwargs: Request parameters
    """
    logger.debug(f"Request: {method} {url}")
    if "json" in kwargs:
        logger.debug(f"Request Body: {json.dumps(kwargs['json'], ensure_ascii=False)}")
    if "params" in kwargs:
        logger.debug(f"Request Params: {kwargs['params']}")

def log_response(response_data: Dict[str, Any]) -> None:
    """Log API response
    
    Args:
        response_data: API response data
    """
    logger.debug(f"Response: {json.dumps(response_data, ensure_ascii=False)}")

def validate_params(params: Dict[str, Any], required: Dict[str, type]) -> None:
    """Validate parameters
    
    Args:
        params: Parameter dictionary
        required: Dictionary of required parameters and their types, e.g., {"name": str, "age": int}
        
    Raises:
        ValidationError: If parameter validation fails
    """
    from .exceptions import ValidationError
    
    for key, type_ in required.items():
        if key not in params:
            raise ValidationError(f"Missing required parameter: {key}")
        if not isinstance(params[key], type_):
            raise ValidationError(
                f"Parameter {key} must be of type {type_.__name__}, "
                f"got {type(params[key]).__name__}"
            )

def format_params(**kwargs) -> Dict[str, Any]:
    """Format request parameters by removing None values
    
    Args:
        **kwargs: Key-value parameters
        
    Returns:
        Cleaned parameter dictionary
    """
    return {k: v for k, v in kwargs.items() if v is not None}

def retry(
    max_retries: int = 3,
    delay: float = 0.5,
    retryable_exceptions: Union[Type[Exception], tuple] = Exception,
    backoff_factor: float = 2
) -> Callable:
    """Retry decorator
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay time (seconds)
        retryable_exceptions: Exception types that should trigger a retry
        backoff_factor: Multiplier for delay time between retries
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):  # +1 includes the initial attempt
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:  # This is the last attempt
                        logger.error(f"Maximum retry attempts exceeded ({max_retries})")
                        raise last_exception
                    
                    retry_delay = delay * (backoff_factor ** attempt)
                    logger.warning(f"Request failed ({str(e)}), retrying in {retry_delay:.2f} seconds (attempt {attempt + 1})")
                    time.sleep(retry_delay)
            
            if last_exception:
                raise last_exception
            return None  # This line will never be reached
            
        return wrapper
    return decorator