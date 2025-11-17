#!/usr/bin/env python3
"""
Context Manager

Auto cleanup - sandbox is automatically destroyed when exiting the 'with' block.
"""

from hopx_ai import Sandbox

print("Context Manager\n")

# Sandbox will be automatically destroyed after the block
with Sandbox.create(template="code-interpreter") as sandbox:
    info = sandbox.get_info()
    print(f"Sandbox created: {sandbox.sandbox_id}")
    print(f"Running at: {info.public_host}")
    print(f"Status: {info.status}")
    
    # Use sandbox here...
    print("\nDoing work in sandbox...")

# Sandbox is automatically killed here
print("\nSandbox automatically cleaned up")

