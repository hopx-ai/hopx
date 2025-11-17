#!/usr/bin/env python3
"""
Template Building Example

Shows how to build a custom template and create VMs from it.
"""

import os
import asyncio
import time
from hopx_ai import Template, wait_for_port


async def main():
    print("Template Building Example\n")

    # Generate unique template name
    template_name = f"example-python-app-{int(time.time())}"
    print(f"Template name: {template_name}\n")

    # 1. Define a Python web app template
    print("1. Defining template...")
    template = (
        Template()
        .from_python_image("3.11")
        .run_cmd("mkdir -p /app")
        .set_workdir("/app")
        .run_cmd("""cat > main.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Hello from Hopx!</h1>")

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()
EOF""")
        .set_env("PORT", "8000")
        .set_start_cmd("python main.py", wait_for_port(8000))
    )

    print(f"   Template defined with {len(template.get_steps())} build steps")

    # 2. Build the template
    print("\n2. Building template...")

    from hopx_ai.template import BuildOptions

    result = await Template.build(
        template,
        BuildOptions(
            name=template_name,
            api_key=os.environ.get("HOPX_API_KEY", ""),
            base_url=os.environ.get("HOPX_BASE_URL", "https://api.hopx.dev"),
            cpu=2,
            memory=2048,
            disk_gb=10,
            context_path=os.getcwd(),
            on_log=lambda log: print(f"   [{log.get('level', 'INFO')}] {log.get('message', '')}"),
            on_progress=lambda progress: print(f"   Progress: {progress}%"),
        ),
    )

    print("\n   Template built")
    print(f"   Template ID: {result.template_id}")
    print(f"   Build ID: {result.build_id}")
    print(f"   Duration: {result.duration}ms")

    # 3. Create sandbox from template
    print("\n3. Creating sandbox from template...")

    from hopx_ai import AsyncSandbox

    sandbox = await AsyncSandbox.create(
        template=template_name,  # Use the template we just built
        env_vars={
            "DATABASE_URL": "postgresql://localhost/mydb",
            "API_KEY": "secret123",
        },
    )

    print("   Sandbox created")
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
    print("   Sandbox destroyed")

    print("\nDone")


if __name__ == "__main__":
    asyncio.run(main())

