#!/usr/bin/env python3
"""
Basic Preview URL Usage

Get preview URLs for services running inside Hopx sandboxes.

Before running:
    export HOPX_API_KEY="your_api_key_here"
"""

from hopx_ai import Sandbox

print("Preview URL Basic Usage\n")

# Create sandbox
sandbox = Sandbox.create(template="code-interpreter")
print(f"Sandbox created: {sandbox.sandbox_id}")

# Get agent URL (default port 7777)
agent_url = sandbox.agent_url
print(f"Agent URL: {agent_url}")

# Get preview URL for custom port
api_url = sandbox.get_preview_url(3000)
print(f"API URL (port 3000): {api_url}")

web_url = sandbox.get_preview_url(8080)
print(f"Web URL (port 8080): {web_url}")

# Cleanup
sandbox.kill()
print("\nDone")
