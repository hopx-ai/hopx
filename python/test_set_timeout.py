#!/usr/bin/env python3
"""
Test set_timeout implementation
"""

import sys
sys.path.insert(0, '.')

from hopx_ai import Sandbox

API_KEY = "hopx_live_Z3rlowJbDXKP.2H6e0wxE0PlM0ltuPBPRgQJxMFXQ93dHV6gLpfPV6gU"

print("Testing set_timeout() implementation")
print("=" * 60)

# Create sandbox with 5 minute timeout
print("\n1. Creating sandbox with 5 minute timeout...")
sandbox = Sandbox.create(
    template_id="82",
    timeout_seconds=300,  # 5 minutes
    api_key=API_KEY
)
print(f"✅ Created: {sandbox.sandbox_id}")

# Extend to 10 minutes
print("\n2. Extending timeout to 10 minutes (600s)...")
try:
    sandbox.set_timeout(600)
    print("✅ Timeout extended successfully!")
except Exception as e:
    print(f"❌ Error: {e}")

# Try to remove timeout
print("\n3. Removing timeout (sandbox runs indefinitely)...")
try:
    sandbox.set_timeout(None)
    print("✅ Timeout removed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")

# Set back to 1 hour
print("\n4. Setting timeout to 1 hour (3600s)...")
try:
    sandbox.set_timeout(3600)
    print("✅ Timeout set to 1 hour!")
except Exception as e:
    print(f"❌ Error: {e}")

# Cleanup
print("\n5. Cleaning up...")
try:
    sandbox.kill()
    print("✅ Sandbox deleted")
except Exception as e:
    print(f"⚠️  Cleanup error: {e}")

print("\n" + "=" * 60)
print("✨ Test complete!")

