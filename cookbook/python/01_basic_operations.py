"""
01. Basic Operations - Python SDK

This example covers:
- Sandbox creation
- Agent initialization
- Getting sandbox info
- Health checks
- Sandbox deletion
- Context managers for auto-cleanup
"""

from hopx_ai import Sandbox
import os

# Set your API key
API_KEY = os.getenv("HOPX_API_KEY", "hopx_live_Lap0VJrWLii8.KSN6iLWELs13jHt960gSK9Eq63trgPApqMf7yLGVTNo")


def setup_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")


def ensure_workspace(sandbox):
    """Ensure /workspace exists - call at start of each test"""
    try:
        setup_workspace(sandbox)
    except Exception:
        pass  # Ignore if already exists or fails


def basic_creation():
    """Basic sandbox creation and deletion"""
    print("=" * 60)
    print("1. BASIC SANDBOX CREATION")
    print("=" * 60)
    
    # Create sandbox with minimal options
    sandbox = Sandbox.create(
        template="code-interpreter",
        api_key=API_KEY
    )
    
    print(f"✅ Sandbox ID: {sandbox.sandbox_id}")
    
    # Get sandbox info
    info = sandbox.get_info()
    print(f"✅ Status: {info.status}")
    print(f"✅ Agent URL: {info.public_host}")
    print(f"✅ Template: {info.template_name}")
    
    # Cleanup
    sandbox.kill()
    print("✅ Sandbox deleted\n")


def advanced_creation():
    """Advanced sandbox creation with custom options"""
    print("=" * 60)
    print("2. ADVANCED SANDBOX CREATION")
    print("=" * 60)
    
    sandbox = Sandbox.create(
        template="code-interpreter",  # Template defines CPU/RAM/Disk resources
        api_key=API_KEY,
        # region="us-west-2",         # Specific region (commented - use default)
        timeout_seconds=600,                  # 10 minute timeout
        env_vars={                    # Pre-set environment variables
            "PYTHONPATH": "/workspace",
            "DEBUG": "true"
        }
    )
    
    print(f"✅ Sandbox ID: {sandbox.sandbox_id}")
    
    # Get detailed info (resources loaded from template)
    info = sandbox.get_info()
    print(f"✅ Template: {info.template_name or 'code-interpreter'}")
    
    # Resources come from template
    if info.resources:
        print(f"✅ vCPU: {info.resources.vcpu} (from template)")
        print(f"✅ Memory: {info.resources.memory_mb}MB (from template)")
    
    # Get metrics snapshot (commented - agent might need a moment to be fully ready)
    # metrics = sandbox.get_metrics_snapshot()
    # print(f"✅ CPU Usage: {metrics.get('cpu_usage_percent', 'N/A')}%")
    
    # Cleanup
    sandbox.kill()
    print("✅ Sandbox deleted\n")


def context_manager_usage():
    """Use context manager for automatic cleanup"""
    print("=" * 60)
    print("3. CONTEXT MANAGER (AUTO-CLEANUP)")
    print("=" * 60)
    
    # Sandbox automatically deleted when exiting 'with' block
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        print(f"✅ Sandbox ID: {sandbox.sandbox_id}")
        
        # Do work here
        result = sandbox.run_code("print('Hello from sandbox!')")
        print(f"✅ Output: {result.stdout.strip()}")
        
        # No need to call sandbox.kill() - automatic cleanup!
    
    print("✅ Sandbox automatically deleted on exit\n")


def get_existing_sandbox():
    """Get reference to existing sandbox by ID"""
    print("=" * 60)
    print("4. GET EXISTING SANDBOX")
    print("=" * 60)
    
    # Create sandbox
    sandbox1 = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    sandbox_id = sandbox1.sandbox_id
    print(f"✅ Created sandbox: {sandbox_id}")
    
    # Get reference to same sandbox by ID
    sandbox2 = Sandbox.connect(sandbox_id, api_key=API_KEY)
    print(f"✅ Retrieved sandbox: {sandbox2.sandbox_id}")
    
    # Verify they're the same
    info1 = sandbox1.get_info()
    info2 = sandbox2.get_info()
    assert info1.public_host == info2.public_host
    print("✅ Same sandbox confirmed!")
    
    # Cleanup
    sandbox1.kill()
    print("✅ Sandbox deleted\n")


def error_handling():
    """Proper error handling"""
    print("=" * 60)
    print("5. ERROR HANDLING")
    print("=" * 60)
    
    from hopx_ai.errors import (
        AuthenticationError,
        NotFoundError,
        ResourceLimitError,
        HopxError
    )
    
    try:
        # This will succeed
        sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
        print(f"✅ Sandbox created: {sandbox.sandbox_id}")
        
        # Try to get non-existent file (will raise FileNotFoundError)
        try:
            content = sandbox.files.read("/non-existent-file.txt")
        except NotFoundError as e:
            print(f"✅ Caught FileNotFoundError: {e.message}")
            print(f"   Request ID: {e.request_id}")
        
        # Cleanup
        sandbox.kill()
        print("✅ Sandbox deleted")
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e.message}")
    except ResourceLimitError as e:
        print(f"❌ Resource limit exceeded: {e.message}")
    except HopxError as e:
        print(f"❌ API error: {e.message}")
        print(f"   Status code: {e.status_code}")
        print(f"   Request ID: {e.request_id}")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - BASIC OPERATIONS")
    print("=" * 60 + "\n")
    
    basic_creation()
    advanced_creation()
    context_manager_usage()
    get_existing_sandbox()
    error_handling()
    
    print("=" * 60)
    print("✅ ALL BASIC OPERATIONS DEMONSTRATED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

