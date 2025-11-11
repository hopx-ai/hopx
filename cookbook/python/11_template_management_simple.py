#!/usr/bin/env python3
"""
HOPX.AI Python SDK - Template Management (Simple Test)

This example demonstrates:
1. Listing templates
2. Getting template details
3. Creating sandbox from template
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
    print("LIST ALL TEMPLATES")
    print("="*60)
    
    templates = Sandbox.list_templates(api_key=API_KEY)
    
    print(f"Found {len(templates)} template(s):\n")
    
    for template in templates:
        print(f"📦 {template.name}")
        print(f"   ID: {template.id}")
        print(f"   Display Name: {template.display_name}")
        if hasattr(template, 'category') and template.category:
            print(f"   Category: {template.category}")
        if hasattr(template, 'language') and template.language:
            print(f"   Language: {template.language}")
        if hasattr(template, 'description') and template.description:
            print(f"   Description: {template.description}")
        print()
    
    return templates


def get_template_details():
    """Get details for a specific template"""
    print("="*60)
    print("GET TEMPLATE DETAILS")
    print("="*60)
    
    template_name = "code-interpreter"
    print(f"Getting details for '{template_name}'...\n")
    
    template = Sandbox.get_template(template_name, api_key=API_KEY)
    
    print(f"✅ Template: {template.name}")
    print(f"   Display Name: {template.display_name}")
    if hasattr(template, 'category') and template.category:
        print(f"   Category: {template.category}")
    if hasattr(template, 'language') and template.language:
        print(f"   Language: {template.language}")
    if hasattr(template, 'description') and template.description:
        print(f"   Description: {template.description}")
    print()
    
    return template


def create_sandbox_from_template(template_name: str):
    """Create sandbox from template"""
    print("="*60)
    print(f"CREATE SANDBOX FROM TEMPLATE: {template_name}")
    print("="*60)
    
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


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("PYTHON SDK - TEMPLATE MANAGEMENT (SIMPLE TEST)")
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
    
    print("="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
