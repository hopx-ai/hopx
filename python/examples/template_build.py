#!/usr/bin/env python3
"""
Template Building Example

Shows how to build a custom template and create VMs from it.
"""

import os
import asyncio
from hopx_ai import Template, wait_for_port


async def main():
    print("🚀 Template Building Example\n")
    
    # 1. Define a Python web app template
    print("1. Defining template...")
    template = (
        Template()
        .from_python_image("3.11")
        .copy("app/", "/app/")
        .pip_install()
        .set_env("PORT", "8000")
        .set_start_cmd("python /app/main.py", wait_for_port(8000))
    )
    
    print(f"   ✅ Template defined with {len(template.get_steps())} steps")
    
    # 2. Build the template
    print("\n2. Building template...")
    
    from hopx_ai.template import BuildOptions
    
    result = await Template.build(
        template,
        BuildOptions(
            alias="my-python-app",
            api_key=os.environ.get("HOPX_API_KEY", ""),
            base_url=os.environ.get("HOPX_BASE_URL", "https://api.hopx.dev"),
            cpu=2,
            memory=2048,
            disk_gb=10,
            context_path=os.getcwd(),
            on_log=lambda log: print(f"   [{log['level']}] {log['message']}"),
            on_progress=lambda progress: print(f"   Progress: {progress}%"),
        ),
    )
    
    print("\n   ✅ Template built successfully!")
    print(f"   Template ID: {result.template_id}")
    print(f"   Build ID: {result.build_id}")
    print(f"   Duration: {result.duration}ms")
    
    # 3. Create VM from template
    print("\n3. Creating VM from template...")
    
    from hopx_ai.template import CreateVMOptions
    
    vm = await result.create_vm(
        CreateVMOptions(
            alias="instance-1",
            env_vars={
                "DATABASE_URL": "postgresql://localhost/mydb",
                "API_KEY": "secret123",
            },
        )
    )
    
    print("   ✅ VM created!")
    print(f"   VM ID: {vm.vm_id}")
    print(f"   IP: {vm.ip}")
    print(f"   Agent URL: {vm.agent_url}")
    
    # 4. Use the VM
    print("\n4. Testing VM...")
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{vm.agent_url}/health") as response:
            health = await response.json()
            print(f"   Health status: {health}")
    
    # 5. Cleanup
    print("\n5. Cleaning up...")
    await vm.delete()
    print("   ✅ VM deleted")
    
    print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())

