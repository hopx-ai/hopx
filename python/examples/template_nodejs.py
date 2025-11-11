#!/usr/bin/env python3
"""
Node.js Template Example

Build a custom Node.js template with Express
"""

import os
import asyncio
from hopx_ai import Template, wait_for_port
from hopx_ai.template import BuildOptions, CreateVMOptions


async def main():
    print("🚀 Node.js Template Example\n")
    
    template = (
        Template()
        .from_node_image("18-alpine")
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
            alias="nodejs-express-app",
            api_key=os.environ["HOPX_API_KEY"],
            on_log=lambda log: print(f"[{log['level']}] {log['message']}"),
        ),
    )
    
    print(f"✅ Template built: {result.template_id}")
    
    # Create multiple instances
    print("\nCreating 3 VM instances...")
    vms = await asyncio.gather(
        result.create_vm(CreateVMOptions(alias="instance-1")),
        result.create_vm(CreateVMOptions(alias="instance-2")),
        result.create_vm(CreateVMOptions(alias="instance-3")),
    )
    
    print("\n✅ VMs created:")
    for vm in vms:
        print(f"   - {vm.vm_id}: {vm.ip}")
    
    # Cleanup
    print("\nCleaning up...")
    await asyncio.gather(*[vm.delete() for vm in vms])
    print("✅ All VMs deleted")


if __name__ == "__main__":
    asyncio.run(main())

