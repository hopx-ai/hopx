#!/usr/bin/env python3
"""
List and manage existing sandboxes.

Shows how to list, filter, and reconnect to sandboxes.
"""

from hopx_ai import Sandbox

print("📋 List Sandboxes Example\n")

# 1. List all sandboxes
print("1. All sandboxes:")
all_sandboxes = Sandbox.list()
print(f"   Found {len(all_sandboxes)} sandboxes")
for sb in all_sandboxes:
    info = sb.get_info()
    print(f"   • {sb.sandbox_id}: {info.status}")

# 2. Filter by status
print("\n2. Running sandboxes only:")
running = Sandbox.list(status="running")
for sb in running:
    info = sb.get_info()
    print(f"   • {sb.sandbox_id}: {info.public_host}")

# 3. Reconnect to existing sandbox
if all_sandboxes:
    print("\n3. Reconnecting to existing sandbox:")
    first_id = all_sandboxes[0].sandbox_id
    sandbox = Sandbox.connect(first_id)
    info = sandbox.get_info()
    print(f"   Reconnected to: {sandbox.sandbox_id}")
    print(f"   Status: {info.status}")
    print(f"   URL: {info.public_host}")

print("\n✨ Done!")

