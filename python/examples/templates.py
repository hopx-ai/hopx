#!/usr/bin/env python3
"""
Browse and Use Templates

List templates and create sandboxes from them.
"""

from hopx_ai import Sandbox

print("📦 Templates Example\n")

# 1. List all templates
print("1. Available templates:")
templates = Sandbox.list_templates()
for t in templates:
    print(f"   • {t.name}: {t.display_name}")
    if t.default_resources:
        print(f"     Default: {t.default_resources.vcpu} vCPU, {t.default_resources.memory_mb}MB")

# 2. Get specific template
print("\n2. Code Interpreter template details:")
template = Sandbox.get_template("code-interpreter")
print(f"   Name: {template.display_name}")
print(f"   Description: {template.description}")
if template.features:
    print(f"   Features: {', '.join(template.features[:5])}")

# 3. Create sandbox from template
print("\n3. Creating sandbox from template...")
sandbox = Sandbox.create(template=template.name)
info = sandbox.get_info()
print(f"   ✅ Created: {sandbox.sandbox_id}")
print(f"   URL: {info.public_host}")
if info.resources:
    print(f"   Resources: {info.resources.vcpu} vCPU, {info.resources.memory_mb}MB RAM")

# Cleanup
sandbox.kill()
print("\n✅ Sandbox created and cleaned up")

