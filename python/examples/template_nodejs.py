#!/usr/bin/env python3
"""
Node.js Template Example

Build a custom Node.js template with Express
"""

import os
import asyncio
from hopx_ai import Template, wait_for_port, AsyncSandbox
from hopx_ai.template import BuildOptions


async def main():
    print("🚀 Node.js Template Example\n")

    template = (
        Template()
        .from_node_image("20")  # Uses ubuntu/node:20-22.04_edge (Debian-based)
        .copy("package.json", "/app/package.json")
        .copy("src/", "/app/src/")
        .set_workdir("/app")
        .npm_install()
        .set_env("NODE_ENV", "production")
        .set_env("PORT", "3000")
        .set_start_cmd("node src/index.js", wait_for_port(3000, 60000))
    )

    print("Building Node.js template...")
    result = await Template.build(
        template,
        BuildOptions(
            name="nodejs-express-app",
            api_key=os.environ["HOPX_API_KEY"],
            on_log=lambda log: print(f"[{log['level']}] {log['message']}"),
        ),
    )

    print(f"✅ Template built: {result.template_id}")

    # Create multiple sandbox instances
    print("\nCreating 3 sandbox instances...")
    sandboxes = await asyncio.gather(
        AsyncSandbox.create(template="nodejs-express-app", env_vars={"INSTANCE": "1"}),
        AsyncSandbox.create(template="nodejs-express-app", env_vars={"INSTANCE": "2"}),
        AsyncSandbox.create(template="nodejs-express-app", env_vars={"INSTANCE": "3"}),
    )

    print("\n✅ Sandboxes created:")
    for i, sandbox in enumerate(sandboxes, 1):
        info = await sandbox.get_info()
        print(f"   - Instance {i}: {sandbox.sandbox_id} (Status: {info.status})")

    # Cleanup
    print("\nCleaning up...")
    await asyncio.gather(*[sandbox.kill() for sandbox in sandboxes])
    print("✅ All sandboxes destroyed")


if __name__ == "__main__":
    asyncio.run(main())

