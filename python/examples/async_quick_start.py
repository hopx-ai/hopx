#!/usr/bin/env python3
"""
Async quick start - for FastAPI, aiohttp, etc.

Before running:
    export HOPX_API_KEY="hopx_your_key_here"
    pip install hopx-ai
"""

import asyncio
from hopx_ai import AsyncSandbox


async def main():
    print("🚀 HOPX.AI Async Quick Start\n")
    
    # Create sandbox
    sandbox = await AsyncSandbox.create(template="code-interpreter")
    
    try:
        print(f"✅ Created: {sandbox.sandbox_id}")
        
        # Get info
        info = await sandbox.get_info()
        print(f"🌐 URL: {info.public_host}")
        print(f"📊 Status: {info.status}")
        print(f"💾 Resources: {info.vcpu} vCPU, {info.memory_mb}MB")
    finally:
        # Cleanup
        await sandbox.kill()
        print("\n✅ Sandbox cleaned up!")


if __name__ == "__main__":
    asyncio.run(main())

