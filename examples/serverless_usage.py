"""
Serverless Usage Example
Demonstrates how to use SubModel SDK's Serverless functionality
"""

import os
from submodel import create_client, serverless
from submodel.exceptions import SubModelError

# Get authentication info from environment variables
token = os.getenv("SUBMODEL_TOKEN")
api_key = os.getenv("SUBMODEL_API_KEY")

def deploy_serverless():
    """Deploy Serverless instance"""
    client = create_client(token=token, api_key=api_key)
    
    # Create Serverless instance
    instance = client.instance.create(
        mode="serverless",
        plan="gpu-rtx4090-24g-1",
        conf={
            "serverless": {
                "allowedCudaVersions": "12.1",
                "computeType": "GPU",
                "gpuCount": 1,
                "gpuIds": "AMPERE_24",
                "workersMax": 5,
                "workersMin": 0
            }
        }
    )
    
    return instance["data"]["inst_id"]

# Define handler function
@serverless.handler
def process_image(job):
    """Example function for image processing"""
    input_data = job.get("input", {})
    image_url = input_data.get("image_url")
    
    if not image_url:
        return {"error": "Missing image URL"}
    
    # This should be actual image processing logic
    result = {
        "status": "success",
        "processed": True,
        "image_url": image_url,
        "metadata": {
            "size": "1024x1024",
            "format": "jpeg"
        }
    }
    
    return result

def test_serverless():
    """Test Serverless functionality"""
    client = create_client(token=token, api_key=api_key)
    
    try:
        # 1. Deploy Serverless instance
        print("Deploying Serverless instance...")
        inst_id = deploy_serverless()
        print(f"Instance deployed successfully, ID: {inst_id}")
        
        # 2. Create Serverless endpoint
        from submodel import ServerlessEndpoint
        endpoint = ServerlessEndpoint(client, inst_id)
        
        # 3. Asynchronous call
        print("\nSending async request...")
        job = endpoint.run({
            "image_url": "https://example.com/test.jpg"
        })
        job_id = job["data"]["id"]
        print(f"Task submitted, ID: {job_id}")
        
        # 4. Get task status
        print("\nGetting task status...")
        status = endpoint.get_status(job_id)
        print(f"Task status: {status['data']['status']}")
        
        # 5. Synchronous call
        print("\nSending sync request...")
        result = endpoint.run_sync({
            "image_url": "https://example.com/test2.jpg"
        })
        print(f"Task result: {result['data']}")
        
        # 6. Get endpoint metrics
        print("\nGetting endpoint metrics...")
        metrics = endpoint.get_metrics()
        print(f"Current metrics: {metrics['data']}")
        
    except SubModelError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run test
    test_serverless()
    
    # To start Serverless worker
    # serverless.set_instance("your-instance-id")
    # serverless.start()