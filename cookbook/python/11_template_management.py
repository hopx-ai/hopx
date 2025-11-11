#!/usr/bin/env python3
"""
HOPX.AI Python SDK - Template Management

This example demonstrates:
1. Listing available templates
2. Getting template details and checking status
3. Creating sandboxes from templates
"""

import os
from hopx_ai import Sandbox

# Get API key from environment
API_KEY = os.environ.get('HOPX_API_KEY')
if not API_KEY:
    raise ValueError("HOPX_API_KEY environment variable not set")


def list_all_templates():
    """List all available templates"""
    print("="*60)
    print("1. LIST ALL TEMPLATES")
    print("="*60)
    
    templates = Sandbox.list_templates(api_key=API_KEY)
    
    print(f"Found {len(templates)} template(s):\n")
    
    for template in templates:
        print(f"📦 {template.name}")
        print(f"   ID: {template.id}")
        print(f"   Display Name: {template.display_name}")
        if hasattr(template, 'status') and template.status:
            print(f"   Status: {template.status}")
        print(f"   Is Active: {template.is_active}")
        if hasattr(template, 'category') and template.category:
            print(f"   Category: {template.category}")
        if hasattr(template, 'description') and template.description:
            print(f"   Description: {template.description}")
        print()
    
    return templates


def get_template_details():
    """Get details for a specific template"""
    print("="*60)
    print("2. GET TEMPLATE DETAILS")
    print("="*60)
    
    template_name = "code-interpreter"
    print(f"Getting details for '{template_name}'...\n")
    
    template = Sandbox.get_template(template_name, api_key=API_KEY)
    
    print(f"✅ Template: {template.name}")
    print(f"   Display Name: {template.display_name}")
    if hasattr(template, 'status') and template.status:
        print(f"   Status: {template.status}")
    print(f"   Is Active: {template.is_active}")
    if hasattr(template, 'category') and template.category:
        print(f"   Category: {template.category}")
    if hasattr(template, 'description') and template.description:
        print(f"   Description: {template.description}")
    print()
    
    # Important: Check status before using template
    if hasattr(template, 'status'):
        if template.status == 'active':
            print("   ✅ Template is ACTIVE - ready to use!")
        elif template.status == 'building':
            print("   ⏳ Template is still BUILDING - wait before using")
        elif template.status == 'publishing':
            print("   ⏳ Template is PUBLISHING - almost ready")
        elif template.status == 'failed':
            print("   ❌ Template build FAILED - cannot use")
    elif template.is_active:
        print("   ✅ Template is active (via is_active flag)")
    
    print()
    
    return template


def create_sandbox_from_template(template_name: str):
    """Create sandbox from template"""
    print("="*60)
    print(f"3. CREATE SANDBOX FROM TEMPLATE: {template_name}")
    print("="*60)
    
    # IMPORTANT: Always check template status before creating sandbox
    template = Sandbox.get_template(template_name, api_key=API_KEY)
    
    if hasattr(template, 'status') and template.status != 'active':
        print(f"❌ Template status is '{template.status}' - must be 'active'")
        print("   Wait for template to finish building before creating sandbox")
        return None
    
    sandbox = Sandbox.create(
        template=template_name,
        api_key=API_KEY
    )
    
    print(f"✅ Sandbox created from template '{template_name}'")
    print(f"   Sandbox ID: {sandbox.sandbox_id}")
    
    info = sandbox.get_info()
    print(f"   Status: {info.status}")
    print(f"   Agent URL: {info.public_host}")
    print(f"   Template ID: {info.template_id}")
    print()
    
    # Test code execution
    print("Testing code execution...")
    result = sandbox.run_code("print('Hello from', __import__('platform').platform())")
    if result.success:
        print(f"✅ Code execution test passed")
        print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ Code execution test failed")
        print(f"   Error: {result.stderr}")
    
    print()
    
    return sandbox


def template_status_guide():
    """Guide on template statuses"""
    print("="*60)
    print("4. TEMPLATE STATUS GUIDE")
    print("="*60)
    
    print("""
Template Lifecycle Statuses:

1. 🔨 building
   - Template is being built
   - Cannot create sandboxes yet
   - Wait for completion

2. 📦 publishing  
   - Build complete, preparing template
   - Almost ready
   - Wait a few more seconds

3. ✅ active
   - Template is ready to use
   - Can create sandboxes
   - This is what you want!

4. ❌ failed
   - Build failed
   - Cannot use this template
   - Check build logs for errors

Best Practice:
--------------
Always check template.status == 'active' before creating a sandbox:

    template = Sandbox.get_template("my-template")
    
    if template.status == 'active':
        sandbox = Sandbox.create(template="my-template")
    else:
        print(f"Wait... status is {template.status}")
""")
    print()


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("PYTHON SDK - TEMPLATE MANAGEMENT")
    print("="*60)
    print()
    
    # Example 1: List all templates
    templates = list_all_templates()
    
    # Example 2: Get template details
    template = get_template_details()
    
    # Example 3: Create sandbox from template
    sandbox = None
    try:
        sandbox = create_sandbox_from_template("code-interpreter")
    finally:
        if sandbox:
            print("Cleaning up...")
            sandbox.kill()
            print("✅ Sandbox deleted")
    
    # Example 4: Status guide
    template_status_guide()
    
    print("="*60)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
