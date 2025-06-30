"""
Asynchronous Usage Example
Demonstrates how to use asynchronous features of SubModel SDK
"""

import os
import asyncio
import submodel
from submodel import create_async_client
from submodel.exceptions import SubModelError

# Set your API key
submodel.api_key = os.getenv("SUBMODEL_API_KEY")

async def create_and_monitor_instance():
    """Create and monitor instance status"""
    async with create_async_client() as client:  # No need to pass api_key here
        # Create instance
        instance = await client.instance.create(
            billing_method="payg",
            mode="pod",
            plan="gpu-rtx4090-24g-1",
            image="ubuntu-22.04"
        )
        inst_id = instance["data"]["inst_id"]
        print(f"Instance created successfully, ID: {inst_id}")
        
        # Wait for instance ready
        while True:
            detail = await client.instance.get_instance(inst_id)
            status = detail["data"]["status"]
            print(f"Instance status: {status}")
            
            if status == "running":
                break
            elif status in ["failed", "error"]:
                raise SubModelError(f"Instance startup failed: {status}")
                
            await asyncio.sleep(5)
        
        return inst_id

async def parallel_instance_creation(num_instances: int = 3):
    """Create multiple instances in parallel"""
    async with create_async_client() as client:
        tasks = []
        for i in range(num_instances):
            task = client.instance.create(
                billing_method="payg",
                mode="pod",
                plan="gpu-rtx4090-24g-1",
                image="ubuntu-22.04",
                conf={"inst_label": f"test-instance-{i}"}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return [result["data"]["inst_id"] for result in results]

async def main():
    try:
        # 1. Create and monitor single instance
        print("Creating and monitoring instance...")
        inst_id = await create_and_monitor_instance()
        print(f"Instance {inst_id} is ready")
        
        # 2. Create multiple instances in parallel
        print("\nCreating multiple instances in parallel...")
        instance_ids = await parallel_instance_creation(3)
        print(f"Successfully created {len(instance_ids)} instances: {instance_ids}")
        
        # 3. Get status of all instances asynchronously
        async with create_async_client() as client:
            print("\nGetting status of all instances...")
            tasks = [
                client.instance.get_instance(id_)
                for id_ in instance_ids
            ]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                inst_id = result["data"]["inst_id"]
                status = result["data"]["status"]
                print(f"Instance {inst_id}: {status}")
                
    except SubModelError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # On Windows, use WindowsSelectorEventLoopPolicy for asyncio
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())