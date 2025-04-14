from setuptools import setup, find_packages
import os
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

VERSION = "0.1.0"

setup(
    name="submodel",
    version=VERSION,
    description="Python SDK for SubModel API",
    long_description=long_description,
    long_description_content_type="text/markdown",    url="https://github.com/submodel/submodel-python",
    author="SubModel Team",
    author_email="support@submodel.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        # HTTP/Networking
        "requests>=2.28.0",    # Synchronous HTTP requests
        "aiohttp>=3.8.0",      # Asynchronous HTTP requests
        
        # Command Line Interface
        "click>=8.0.0",        # CLI framework
        "tqdm>=4.65.0",        # Progress bar
        "python-dotenv>=0.19.0",  # Environment variables management
        "pydantic>=2.0.0",     # Data validation and settings management
        "pytz>=2023.3",        # Timezone support
        "colorama>=0.4.4",     # Windows terminal colors
    ],
    extras_require={
        "dev": [
            "black>=22.3.0",
            "pytest>=7.3.1",
            "pytest-asyncio>=0.20.3",
            "pytest-cov>=4.0.0",
            "pre-commit>=3.2.1",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'submodel=submodel.cli:cli',
        ],
    },
)