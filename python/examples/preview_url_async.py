#!/usr/bin/env python3
"""
Async Preview URL Usage

This example demonstrates async/await usage with preview URLs.

Before running:
    export HOPX_API_KEY="your_api_key_here"
"""

import asyncio
from hopx_ai import AsyncSandbox

async def main():
    print("🌐 Async Preview URL Usage\n")

    # Create sandbox
    async with await AsyncSandbox.create(template="code-interpreter") as sandbox:
        print(f"✅ Sandbox created: {sandbox.sandbox_id}")

        # Get agent URL (async)
        agent_url = await sandbox.agent_url
        print(f"📡 Agent URL: {agent_url}")

        # Get preview URLs for custom ports (async)
        api_url = await sandbox.get_preview_url(3000)
        print(f"🔗 API URL (port 3000): {api_url}")

        web_url = await sandbox.get_preview_url(8080)
        print(f"🌐 Web URL (port 8080): {web_url}")

    print("\n✅ Done! (sandbox auto-cleaned)")

if __name__ == "__main__":
    asyncio.run(main())
