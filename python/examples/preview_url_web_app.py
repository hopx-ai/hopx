#!/usr/bin/env python3
"""
Web App Deployment with Preview URLs

This example shows how to deploy a web application inside a sandbox
and get its public URL for external access.

Before running:
    export HOPX_API_KEY="your_api_key_here"
"""

import time
from hopx_ai import Sandbox

print("🚀 Deploying Web App in Sandbox\n")

# Create sandbox
sandbox = Sandbox.create(template="code-interpreter")
print(f"✅ Sandbox created: {sandbox.sandbox_id}")

# Start a simple HTTP server on port 8080
print("\n📦 Starting HTTP server on port 8080...")

server_code = """
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Hopx Sandbox App</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2563eb; }}
        .info {{ background: #f0f9ff; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>🎉 Hello from Hopx Sandbox!</h1>
    <div class="info">
        <p><strong>Sandbox ID:</strong> {os.environ.get('HOSTNAME', 'unknown')}</p>
        <p><strong>Port:</strong> 8080</p>
        <p>This server is running inside a secure Hopx sandbox.</p>
    </div>
</body>
</html>
'''
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass

PORT = 8080
with HTTPServer(('0.0.0.0', PORT), Handler) as httpd:
    print(f'Server listening on port {PORT}')
    httpd.serve_forever()
"""

result = sandbox.run_code_background(
    code=server_code,
    language="python",
    name="web-server",
    timeout=300
)

print(f"✅ Server started (process: {result.get('process_id')})")

# Wait for server to be ready
print("⏳ Waiting for server to start...")
time.sleep(3)

# Get the preview URL
url = sandbox.get_preview_url(8080)
print(f"\n🌐 Your app is live at: {url}")
print("\n💡 Open this URL in your browser to see the app!")

# Keep running for 30 seconds so you can test
print("\n⏰ Server will run for 30 seconds...")
print("   Press Ctrl+C to stop early\n")

try:
    time.sleep(30)
except KeyboardInterrupt:
    print("\n⏹️  Interrupted by user")

# Cleanup
print("\n🧹 Cleaning up...")
sandbox.kill()
print("✅ Done!")
