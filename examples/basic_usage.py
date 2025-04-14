"""Basic Usage Example
Demonstrates how to use SubModel SDK with basic features
"""

import os
import submodel
from submodel import Client

# Set your API key
submodel.api_key = os.getenv("SUBMODEL_API_KEY")

# Create a client
client = Client()

def main():
    try:
        # Create instance
        instance = client.instance.create(
            billing_method="payg",
            mode="pod",
            plan="gpu-rtx4090-24g-1",
            image="ubuntu-22.04"
        )
        inst_id = instance["data"]["inst_id"]
        print(f"Instance created successfully, ID: {inst_id}")
        
        # Get instance details
        detail = client.instance.get_instance(inst_id)
        print(f"Instance status: {detail['data']['status']}")
        
        # List all instances
        instances = client.instance.list_instances()
        print(f"\nTotal instances: {len(instances['data'])}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()