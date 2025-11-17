#!/usr/bin/env python3
"""
Node.js Template Example

Build a custom Node.js template with Express
"""

import os
import asyncio
import time
from hopx_ai import Template, wait_for_port, AsyncSandbox
from hopx_ai.template import BuildOptions


async def main():
    print("Node.js Template Example\n")

    # Generate unique template name
    template_name = f"nodejs-express-{int(time.time())}"
    print(f"Template name: {template_name}\n")

    # Build template with embedded file content
    template = (
        Template(from_image="node:20-bookworm")  # Standard Node.js 20 image (Debian-based)
        .run_cmd("mkdir -p /app/src")
        .set_workdir("/app")
        .run_cmd("""cat > package.json << 'EOF'
{
  "name": "hopx-express-app",
  "version": "1.0.0",
  "main": "src/index.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF""")
        .run_cmd("""cat > src/index.js << 'EOF'
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;
const INSTANCE = process.env.INSTANCE || '1';

app.get('/', (req, res) => {
    res.json({
        message: 'Hello from Hopx Node.js!',
        instance: INSTANCE,
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log('Server running on port ' + PORT);
});
EOF""")
        .run_cmd("npm install")  # Use npm from PATH (works across Node images)
        .set_env("NODE_ENV", "production")
        .set_env("PORT", "3000")
        .set_start_cmd("node src/index.js", wait_for_port(3000, 60000))
    )

    print("Building Node.js template...")
    print("Note: Takes 5-10 minutes\n")

    result = await Template.build(
        template,
        BuildOptions(
            name=template_name,
            api_key=os.environ["HOPX_API_KEY"],
            on_log=lambda log: print(f"  [{log.get('level', 'INFO')}] {log.get('message', '')}"),
        ),
    )

    print(f"Template built: {result.template_id}")

    # Create multiple sandbox instances
    print("\nCreating 3 sandbox instances...")
    sandboxes = await asyncio.gather(
        AsyncSandbox.create(template=template_name, env_vars={"INSTANCE": "1"}),
        AsyncSandbox.create(template=template_name, env_vars={"INSTANCE": "2"}),
        AsyncSandbox.create(template=template_name, env_vars={"INSTANCE": "3"}),
    )

    print("\nSandboxes created:")
    for i, sandbox in enumerate(sandboxes, 1):
        info = await sandbox.get_info()
        print(f"   - Instance {i}: {sandbox.sandbox_id} (Status: {info.status})")

    # Cleanup
    print("\nCleaning up...")
    await asyncio.gather(*[sandbox.kill() for sandbox in sandboxes])
    print("All sandboxes destroyed")


if __name__ == "__main__":
    asyncio.run(main())

