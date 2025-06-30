# SubModel Python SDK

SubModel SDK is a Python library for interacting with the SubModel API.

## Installation

Create a Python virtual environment and install the SDK:

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate

# Install SDK
pip install submodel
```

## Quick Start

### Set up API Key

It is recommended to set the API key using environment variables:

```python
import os
import submodel

submodel.api_key = os.getenv("SUBMODEL_API_KEY")
```

### Basic Usage

```python
from submodel import Client

# Create client
client = Client()

# Create instance
instance = client.instance.create(
    billing_method="payg",
    mode="pod",
    plan="gpu-rtx4090-24g-1",
    image="ubuntu-22.04"
)

# Get instance details
inst_id = instance["data"]["inst_id"]
detail = client.instance.get_instance(inst_id)
```

### Async Usage

```python
import asyncio
from submodel import create_async_client

async def main():
    async with create_async_client() as client:
        instance = await client.instance.create(
            billing_method="payg",
            mode="pod",
            plan="gpu-rtx4090-24g-1",
            image="ubuntu-22.04"
        )
        print(f"Instance created: {instance['data']['inst_id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

If you want to participate in development, please install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT License

## More Information

For more examples and complete documentation, please see the [examples](examples/) directory.