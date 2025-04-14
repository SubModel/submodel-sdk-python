"""
SubModel SDK Core
~~~~~~~~~~~~~~~

Core functionality for SubModel API
"""

import os
from typing import Optional

# Global configuration
api_key: Optional[str] = os.getenv("SUBMODEL_API_KEY")
token: Optional[str] = os.getenv("SUBMODEL_TOKEN")

from .client import SubModelClient as Client
from .async_client import AsyncSubModelClient as AsyncClient, create_async_client
from .auth import Auth
from .device import Device, Area, Baremetal
from .instance import Instance
from .serverless import ServerlessHandler, ServerlessEndpoint
from .exceptions import (
    SubModelError,
    APIError,
    AuthenticationError,
    ResourceNotFoundError,
    QuotaExceededError,
)

__all__ = [
    "Client", 
    "AsyncClient", 
    "create_async_client", 
    "Auth",
    "Device", 
    "Area", 
    "Baremetal", 
    "Instance",
    "ServerlessHandler", 
    "ServerlessEndpoint",
    "SubModelError",
    "APIError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "QuotaExceededError",
]
