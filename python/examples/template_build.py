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
            name="my-python-app",
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
    
    # 3. Create sandbox from template
    print("\n3. Creating sandbox from template...")

    from hopx_ai import AsyncSandbox

    sandbox = await AsyncSandbox.create(
        template="my-python-app",  # Use template name/alias
        env_vars={
            "DATABASE_URL": "postgresql://localhost/mydb",
            "API_KEY": "secret123",
        },
    )

    print("   ✅ Sandbox created!")
    print(f"   Sandbox ID: {sandbox.sandbox_id}")
    info = await sandbox.get_info()
    print(f"   Status: {info.status}")
    print(f"   Agent URL: {await sandbox.agent_url}")

    # 4. Use the sandbox
    print("\n4. Testing sandbox...")
    result = await sandbox.run_code("""
import os
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"API_KEY: {'*' * len(os.environ.get('API_KEY', ''))}")
print("Web app is running on port 8000!")
""", language="python")

    print(f"   Output:\n{result.stdout}")

    # 5. Cleanup
    print("\n5. Cleaning up...")
    await sandbox.kill()
    print("   ✅ Sandbox destroyed")
    
    print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())

