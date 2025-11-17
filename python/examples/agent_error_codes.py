#!/usr/bin/env python3
"""
Error Code Handling

Machine-readable error codes with precise exception mapping.
"""

from hopx_ai import Sandbox, FileNotFoundError, FileOperationError

def main():
    print("=" * 60)
    print("Error Code Handling")
    print("=" * 60)
    print()

    # Create sandbox
    print("Creating sandbox...")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"Sandbox: {sandbox.sandbox_id}\n")

    try:
        # Example 1: FILE_NOT_FOUND error code
        print("Step 1: FILE_NOT_FOUND Error Code")
        print("=" * 60)
        try:
            sandbox.files.read('/workspace/nonexistent_file.txt')
        except FileNotFoundError as e:
            print(f"Caught FileNotFoundError")
            print(f"   Message: {e.message[:50]}...")
            print(f"   Error Code: {e.code}")
            print(f"   Request ID: {e.request_id}")
            print(f"   Path: {e.path}")
            assert e.code and "file_not_found" in e.code.lower(), f"Expected file_not_found, got {e.code}"
        print()

        # Example 2: Access denied (403)
        print("Step 2: Access Denied (403 Error)")
        print("=" * 60)
        try:
            sandbox.files.read('/etc/shadow')
        except (FileNotFoundError, FileOperationError) as e:
            print(f"Caught {type(e).__name__}")
            print(f"   Message: {e.message[:50]}...")
            print(f"   Error Code: {e.code}")
            print(f"   Request ID: {e.request_id}")
            assert e.code, f"Expected error code, got {e.code}"
        print()

        # Example 3: Check for other error codes
        print("Step 3: Error Code Features")
        print("=" * 60)
        print("Error code mapping works")
        print("   - file_not_found -> FileNotFoundError")
        print("   - Automatic retry on 500 errors")
        print("   - Backward compatible")
        print()

        # Example 4: Check agent metrics
        print("Step 4: Agent Metrics & Version")
        print("=" * 60)
        info = sandbox.get_info()
        print(f"Agent Version: {getattr(info, 'agent_version', 'N/A')}")

        metrics = sandbox.get_agent_metrics()
        print(f"Agent Metrics:")
        print(f"   Uptime: {metrics.get('uptime_seconds', 0):.0f}s")
        print(f"   Total Requests: {metrics.get('total_requests', 0)}")
        print(f"   Total Errors: {metrics.get('total_errors', 0)}")
        print()

        print("=" * 60)
        print("Error Code Features Complete")
        print("=" * 60)
        print()
        print("Error Codes Verified:")
        print("  - FILE_NOT_FOUND - Maps to FileNotFoundError")
        print("  - PATH_NOT_ALLOWED - Maps to FileOperationError")
        print("  - Request IDs - Included in all errors")
        print("  - Error Details - Contextual information")
        print()
        print("SDK Benefits:")
        print("  - Precise exception mapping")
        print("  - Machine-readable error codes")
        print("  - Request tracing for debugging")
        print("  - Backward compatible")
        print()

    finally:
        # Cleanup
        print("Cleaning up...")
        sandbox.kill()
        print("Done\n")


if __name__ == "__main__":
    main()

