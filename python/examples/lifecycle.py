#!/usr/bin/env python3
"""
Sandbox lifecycle management example.

Demonstrates: create, stop, start, pause, resume, kill
"""

from hopx_ai import Sandbox
import time

print("🔄 Sandbox Lifecycle Demo\n")

# 1. Create sandbox
print("1. Creating sandbox...")
sandbox = Sandbox.create(
    template="code-interpreter",
    vcpu=2,
    memory_mb=2048,
    timeout=600  # 10 minutes
)
print(f"   ✅ Created: {sandbox.sandbox_id}")
print(f"   URL: {sandbox.get_info().public_host}")

# 2. Check status
info = sandbox.get_info()
print(f"\n2. Status: {info.status}")

# 3. Stop sandbox
print("\n3. Stopping sandbox...")
sandbox.stop()
print("   ✅ Stopped")

# 4. Start again
print("\n4. Starting sandbox...")
sandbox.start()
print("   ✅ Started")

# 5. Pause sandbox
print("\n5. Pausing sandbox...")
sandbox.pause()
print("   ✅ Paused")

# 6. Resume sandbox
print("\n6. Resuming sandbox...")
sandbox.resume()
print("   ✅ Resumed")

# 7. Destroy sandbox
print("\n7. Destroying sandbox...")
sandbox.kill()
print("   ✅ Destroyed")

print("\n✨ Lifecycle demo complete!")

