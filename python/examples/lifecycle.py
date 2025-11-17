#!/usr/bin/env python3
"""
Sandbox Lifecycle Management

Create, pause, resume, kill sandboxes.
"""

from hopx_ai import Sandbox
import time

print("Sandbox Lifecycle\n")

# 1. Create sandbox
print("1. Creating sandbox...")
sandbox = Sandbox.create(
    template="code-interpreter",
    timeout_seconds=600  # 10 minutes auto-kill timeout
)
print(f"   Created: {sandbox.sandbox_id}")
info = sandbox.get_info()
print(f"   URL: {info.public_host}")
if info.resources:
    print(f"   Resources: {info.resources.vcpu} vCPU, {info.resources.memory_mb}MB RAM")

# 2. Check status
info = sandbox.get_info()
print(f"\n2. Status: {info.status}")

# 3. Pause sandbox
print("\n3. Pausing sandbox...")
sandbox.pause()
print("   Paused")

# 4. Resume sandbox
print("\n4. Resuming sandbox...")
sandbox.resume()
print("   Resumed")

# 5. Destroy sandbox
print("\n5. Destroying sandbox...")
sandbox.kill()
print("   Destroyed")

print("\nLifecycle complete")

