"""
10. Best Practices - Python SDK

Production-ready patterns and recommendations:
- Context managers for cleanup
- Error handling strategies
- Performance optimization
- Security best practices
- Resource management
- Monitoring and logging
- Testing patterns
"""

from hopx_ai import Sandbox
from hopx_ai.errors import *
import os
import logging
import time

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")

def ensure_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    try:
        sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")
    except Exception:
        pass


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def use_context_managers():
    """ALWAYS use context managers for automatic cleanup"""
    print("=" * 60)
    print("1. CONTEXT MANAGERS (AUTOMATIC CLEANUP)")
    print("=" * 60)
    
    # ✅ GOOD: Context manager ensures cleanup
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        result = sandbox.run_code("print('Hello')")
        print(f"✅ Output: {result.stdout.strip()}")
    # Sandbox automatically deleted here
    
    print("✅ Sandbox auto-cleaned up!")
    print()


def handle_errors_properly():
    """Comprehensive error handling"""
    print("=" * 60)
    print("2. PROPER ERROR HANDLING")
    print("=" * 60)
    
    try:
        with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
            ensure_workspace(sandbox)
            # Try file operation
            try:
                content = sandbox.files.read("/non-existent.txt")
            except FileNotFoundError as e:
                logger.warning(f"File not found: {e.message} (Request ID: {e.request_id})")
                # Fallback: create the file
                sandbox.files.write("/non-existent.txt", "Default content")
                content = sandbox.files.read("/non-existent.txt")
                print(f"✅ Recovered with fallback: {content}")
            
            # Try code execution
            try:
                result = sandbox.run_code("1/0", timeout_seconds=5)
            except CodeExecutionError as e:
                logger.error(f"Code execution failed: {e.message}")
                print("✅ Caught code execution error")
            
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e.message}")
    except ResourceLimitError as e:
        logger.error(f"Resource limit exceeded: {e.message}")
    except HopxError as e:
        logger.error(f"API error: {e.message} (Status: {e.status_code})")
    
    print("✅ Comprehensive error handling demonstrated")
    print()


def optimize_performance():
    """Performance optimization techniques"""
    print("=" * 60)
    print("3. PERFORMANCE OPTIMIZATION")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # ✅ GOOD: Set environment variables once
        sandbox.env.set_all({
            "DATABASE_URL": "postgres://...",
            "REDIS_URL": "redis://...",
            "API_KEY": "sk-..."
        })
        
        # Now available in all executions (no need to pass each time)
        start = time.time()
        for i in range(5):
            result = sandbox.run_code("""
import os
db_url = os.getenv('DATABASE_URL')
# Use db_url...
            """)
        elapsed = time.time() - start
        
        print(f"✅ Executed 5 times in {elapsed:.2f}s")
        
        # ✅ GOOD: Reuse files instead of re-uploading
        sandbox.files.write("/workspace/config.json", '{"setting": "value"}')
        # Now use it multiple times
        for i in range(3):
            sandbox.run_code("import json; config = json.load(open('/workspace/config.json'))")
        
        print("✅ Reused file 3 times without re-upload")
        
        # ✅ GOOD: Use background execution for non-blocking operations
        exec_id = sandbox.run_code_background("""
import time
time.sleep(10)  # Long operation
        """)
        
        print(f"✅ Background execution started: {exec_id}")
        print("   (Can continue with other work)")
    
    print()


def security_best_practices():
    """Security recommendations"""
    print("=" * 60)
    print("4. SECURITY BEST PRACTICES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        print("✅ Best Practice #1: NEVER hardcode secrets in code")
        
        # ❌ BAD
        # sandbox.run_code('api_key = "sk-secret-123"')
        
        # ✅ GOOD: Pass via environment variables
        result = sandbox.run_code(
            'import os; api_key = os.getenv("API_KEY")',
            env={"API_KEY": "sk-secret-123"}
        )
        print("   Secrets passed via env ✅")
        
        print("\n✅ Best Practice #2: Use sandbox environment variables for persistent secrets")
        
        # Set once, available everywhere
        sandbox.env.set("SECRET_KEY", "very-secret-key")
        
        # Now available in all code executions
        result = sandbox.run_code('import os; key = os.getenv("SECRET_KEY")')
        print("   Persistent secrets configured ✅")
        
        print("\n✅ Best Practice #3: Set execution timeouts")
        
        # Always set timeouts to prevent infinite execution
        try:
            result = sandbox.run_code(
                "import time; time.sleep(100)",
                timeout_seconds=2  # 2 second timeout
            )
        except Exception:
            print("   Timeout prevented infinite execution ✅")
        
        print("\n✅ Best Practice #4: Validate inputs")
        
        user_code = "print('Hello')"
        
        # Validate before execution
        if len(user_code) > 100000:  # Example limit
            print("   Code too large, rejected")
        else:
            result = sandbox.run_code(user_code)
            print("   Input validated ✅")
    
    print()


def resource_management():
    """Manage resources efficiently"""
    print("=" * 60)
    print("5. RESOURCE MANAGEMENT")
    print("=" * 60)
    
    # ✅ GOOD: Request appropriate resources
    with Sandbox.create(
        template="code-interpreter",
        api_key=API_KEY,
        timeout_seconds=300       # Set reasonable timeout
        # Note: vcpu/memory come from template (cannot be overridden)
    ) as sandbox:
        ensure_workspace(sandbox)
        print("✅ Sandbox created with appropriate resources")
        
        # Monitor resource usage
        processes = sandbox.list_processes()
        print(f"✅ Running processes: {len(processes)}")
        
        # Get metrics
        metrics = sandbox.get_metrics_snapshot()
        print(f"✅ Total executions: {metrics.total_executions}")
        print(f"✅ Failed executions: {metrics.failed_executions}")
        
        # Clean up unused files
        files = sandbox.files.list("/workspace")
        print(f"✅ Workspace files: {len(files)}")
        
        # Remove temp files
        for f in files:
            if f.name.startswith("temp_"):
                sandbox.files.remove(f.path)
        
        print("✅ Cleaned up temp files")
    
    print()


def monitoring_and_logging():
    """Implement monitoring and logging"""
    print("=" * 60)
    print("6. MONITORING AND LOGGING")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        logger.info(f"Sandbox created: {sandbox.sandbox_id}")
        
        try:
            # Log execution
            logger.info("Executing code...")
            start = time.time()
            
            result = sandbox.run_code("""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
print(df.sum())
            """)
            
            elapsed = time.time() - start
            
            logger.info(f"Execution completed in {elapsed:.2f}s")
            logger.info(f"Success: {result.success}, Exit code: {result.exit_code}")
            
            # Log metrics
            metrics = sandbox.get_metrics_snapshot()
            logger.info(f"Total executions: {metrics.total_executions}")
            logger.info(f"Uptime: {metrics.uptime_seconds}s")
            
            print("✅ All operations logged")
            
        except Exception as e:
            logger.error(f"Operation failed: {e}", exc_info=True)
        
        finally:
            logger.info("Cleaning up sandbox")
    
    print()


def testing_patterns():
    """Patterns for testing with sandboxes"""
    print("=" * 60)
    print("7. TESTING PATTERNS")
    print("=" * 60)
    
    def setup_sandbox():
        """Test setup fixture"""
        sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
        ensure_workspace(sandbox)
        # Common setup
        sandbox.env.set_all({
            "TEST_MODE": "true",
            "DEBUG": "true"
        })
        return sandbox
    
    def teardown_sandbox(sandbox):
        """Test teardown fixture"""
        sandbox.kill()
    
    # Test 1: Code execution
    sandbox = setup_sandbox()
    try:
        result = sandbox.run_code("print('test')")
        assert result.success, "Code execution should succeed"
        assert "test" in result.stdout, "Output should contain 'test'"
        print("✅ Test 1 passed: Code execution")
    finally:
        teardown_sandbox(sandbox)
    
    # Test 2: File operations
    sandbox = setup_sandbox()
    try:
        sandbox.files.write("/workspace/test.txt", "content")
        assert sandbox.files.exists("/workspace/test.txt"), "File should exist"
        content = sandbox.files.read("/workspace/test.txt")
        assert content == "content", "Content should match"
        print("✅ Test 2 passed: File operations")
    finally:
        teardown_sandbox(sandbox)
    
    # Test 3: Environment variables
    sandbox = setup_sandbox()
    try:
        sandbox.env.set("TEST_VAR", "test_value")
        value = sandbox.env.get("TEST_VAR")
        assert value == "test_value", "Env var should match"
        print("✅ Test 3 passed: Environment variables")
    finally:
        teardown_sandbox(sandbox)
    
    print("✅ All tests passed!")
    print()


def production_checklist():
    """Production readiness checklist"""
    print("=" * 60)
    print("8. PRODUCTION CHECKLIST")
    print("=" * 60)
    
    checklist = """
    ✅ Error Handling:
       □ Try/except blocks for all API calls
       □ Specific exception types (FileNotFoundError, etc.)
       □ Fallback strategies
       □ Request ID logging
    
    ✅ Resource Management:
       □ Context managers for cleanup
       □ Appropriate vcpu/memory allocation
       □ Execution timeouts set
       □ File cleanup after use
    
    ✅ Security:
       □ Secrets via environment variables
       □ No hardcoded credentials
       □ Input validation
       □ Timeout limits
    
    ✅ Performance:
       □ Environment variables set once
       □ File reuse (don't re-upload)
       □ Background execution for long tasks
       □ Connection pooling (automatic)
    
    ✅ Monitoring:
       □ Logging configured
       □ Metrics collection
       □ Health checks
       □ Error tracking
    
    ✅ Testing:
       □ Unit tests for critical paths
       □ Integration tests with sandboxes
       □ Error scenario tests
       □ Performance benchmarks
    """
    
    print(checklist)
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - BEST PRACTICES")
    print("=" * 60 + "\n")
    
    use_context_managers()
    handle_errors_properly()
    optimize_performance()
    security_best_practices()
    resource_management()
    monitoring_and_logging()
    testing_patterns()
    production_checklist()
    
    print("=" * 60)
    print("✅ ALL BEST PRACTICES DEMONSTRATED!")
    print("=" * 60)
    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("""
1. Always use context managers (with statement)
2. Handle errors with specific exception types
3. Never hardcode secrets - use environment variables
4. Set execution timeouts to prevent infinite loops
5. Monitor metrics and log operations
6. Clean up resources (files, processes)
7. Test error scenarios, not just happy paths
8. Optimize by reusing files and env vars
9. Request appropriate resources (vcpu/memory)
10. Validate inputs before execution
    """)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

