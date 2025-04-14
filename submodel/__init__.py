"""
SubModel Python SDK
~~~~~~~~~~~~~~~~

A Python SDK for accessing SubModel API

:copyright: (c) 2025 by SubModel Team.
:license: MIT, see LICENSE for more details.
"""

import os
import importlib.metadata

try:
    __version__ = importlib.metadata.version("submodel")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"  # 默认版本

# 导出SDK核心组件，方便用户直接从submodel导入
from .sdk.client import SubModelClient, create_client
from .sdk.async_client import AsyncSubModelClient, create_async_client
from .sdk.exceptions import (
    SubModelError,
    APIError,
    AuthenticationError,
    ResourceNotFoundError,
    QuotaExceededError,
)

__all__ = [
    "SubModelClient",
    "AsyncSubModelClient",
    "create_client",
    "create_async_client",
    "SubModelError",
    "APIError", 
    "AuthenticationError",
    "ResourceNotFoundError",
    "QuotaExceededError",
]
