#!/usr/bin/env python3
"""
Quick start - create your first sandbox in seconds.

Before running:
    export HOPX_API_KEY="hopx_your_key_here"

Or pass api_key directly to Sandbox.create()
"""

from hopx_ai import Sandbox

print("🚀 HOPX.AI Quick Start\n")

# Create sandbox (API key from HOPX_API_KEY env var)
print("Creating sandbox...")
sandbox = Sandbox.create(template="code-interpreter")
print(f"✅ Created: {sandbox.sandbox_id}")

# Get info
info = sandbox.get_info()
print(f"🌐 URL: {info.public_host}")
print(f"📊 Status: {info.status}")
print(f"💾 Resources: {info.vcpu} vCPU, {info.memory_mb}MB RAM")

# Cleanup
print("\nCleaning up...")
sandbox.kill()
print("✅ Done!")

