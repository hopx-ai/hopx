#!/usr/bin/env python3
"""
Template Building with Log Monitoring

Build a template and monitor logs using the get_logs() method.
"""

import os
import asyncio
from hopx_ai import Template
from hopx_ai.template import BuildOptions


async def main():
    print("Building Template with Log Monitoring\n")

    # 1. Define template
    template = (
        Template()
        .from_python_image("3.11-slim")
        .run_cmd("apt-get update && apt-get install -y curl")
        .run_cmd("pip install flask gunicorn")
        .set_workdir("/app")
    )

    # 2. Start building
    print("Starting build...")
    result = await Template.build(
        template,
        BuildOptions(
            name=f"example-template-{int(asyncio.get_event_loop().time())}",
            api_key=os.environ.get("HOPX_API_KEY", ""),
            base_url=os.environ.get("HOPX_BASE_URL", "https://api.hopx.dev"),
            cpu=2,
            memory=2048,
            disk_gb=10,
        )
    )

    print(f"Build started")
    print(f"   Template ID: {result.template_id}")
    print(f"   Build ID: {result.build_id}")
    print()

    # 3. Monitor logs using the get_logs() method
    print("Monitoring build logs...\n")
    
    offset = 0
    while True:
        # Get logs from current offset
        logs_response = await result.get_logs(offset=offset)
        
        # Print new logs if any
        if logs_response.logs:
            print(logs_response.logs, end='')
        
        # Update offset for next iteration
        offset = logs_response.offset
        
        # Check if build is complete
        if logs_response.complete:
            print("\nBuild complete")
            print(f"   Status: {logs_response.status}")
            break

        # Wait before polling again
        await asyncio.sleep(2)

    print()
    print(f"Template ready: {result.template_id}")
    print(f"   Build duration: {result.duration}ms")


if __name__ == "__main__":
    asyncio.run(main())

