#!/usr/bin/env python3
"""
Debug Logging

Enable detailed logging to see API requests.

Note: Set HOPX_API_KEY environment variable before running.
"""

import logging
import os
from hopx_ai import Sandbox

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

print("Debug Logging\n")
print("Watch the DEBUG logs below to see API calls:\n")

# Create sandbox
sandbox = Sandbox.create(template="code-interpreter")

print(f"\nCreated: {sandbox.sandbox_id}")

# Get info
info = sandbox.get_info()
print(f"Status: {info.status}")

# Delete
sandbox.kill()
print("\nDeleted")

print("\nDebug logs show:")
print("   - HTTP method and URL")
print("   - Request body")
print("   - Response status and timing")
print("   - Response body")
print("   - Retry attempts (if any)")

