#!/usr/bin/env python3
"""
Debug logging example.

Shows how to enable detailed logging to see API requests.
"""

import logging
from hopx_ai import Sandbox

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

print("🔍 Debug Logging Example\n")
print("Watch the DEBUG logs below to see API calls:\n")

# Create sandbox - you'll see detailed logs!
sandbox = Sandbox.create(
    template="code-interpreter",
    api_key="hopx_f0dfeb804627ca3c1ccdd3d43d2913c9"
)

print(f"\n✅ Created: {sandbox.sandbox_id}")

# Get info - more logs!
info = sandbox.get_info()
print(f"📊 Status: {info.status}")

# Delete - final logs!
sandbox.kill()
print("\n✅ Deleted!")

print("\n💡 Debug logs show:")
print("   - HTTP method and URL")
print("   - Request body")
print("   - Response status and timing")
print("   - Response body")
print("   - Retry attempts (if any)")

