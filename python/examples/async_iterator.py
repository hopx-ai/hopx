#!/usr/bin/env python3
"""
Async lazy iterator example.

Shows how to use async iterators for better memory usage.

Note: Set HOPX_API_KEY environment variable before running.
"""

import os
import asyncio
from hopx_ai import AsyncSandbox


async def main():
    print("🔄 Async Iterator Demo\n")

    # Create a few sandboxes first
    print("Creating 3 sandboxes...")
    for i in range(3):
        sandbox = await AsyncSandbox.create(template="code-interpreter")
        print(f"   ✅ Created: {sandbox.sandbox_id}")

    # Now iterate lazily (fetches pages as needed)
    print("\nIterating over sandboxes (lazy loading)...")
    count = 0
    async for sandbox in AsyncSandbox.iter():
        info = await sandbox.get_info()
        print(f"   • {sandbox.sandbox_id}: {info.status}")
        count += 1

        if count >= 5:  # Stop after 5 - doesn't fetch all pages!
            print("   (stopping early - remaining pages not fetched)")
            break

    print("\n✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())

