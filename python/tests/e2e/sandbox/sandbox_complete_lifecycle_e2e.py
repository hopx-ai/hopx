"""
End-to-end test for complete sandbox lifecycle.

Tests a realistic user flow:
1. Create sandbox
2. Execute code
3. Manage files
4. Set environment variables
5. Run commands
6. Cleanup
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


def test_complete_sandbox_lifecycle(api_key, cleanup_sandbox):
    """Test complete sandbox lifecycle from creation to destruction."""
    # 1. Create sandbox
    sandbox = Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
        timeout_seconds=600,
        env_vars={"E2E_TEST": "true"},
    )
    cleanup_sandbox.append(sandbox)

    assert sandbox.sandbox_id is not None

    # 2. Get sandbox info
    info = sandbox.get_info()
    assert info.status in ("running", "creating")
    assert info.public_host is not None

    # 3. Execute code
    result = sandbox.run_code("print('Hello from E2E test')")
    assert result.success is True
    assert "Hello from E2E test" in result.stdout

    # 4. Create and read files
    test_content = "E2E test file content"
    sandbox.files.write("/workspace/e2e_test.txt", test_content)
    read_content = sandbox.files.read("/workspace/e2e_test.txt")
    assert read_content == test_content

    # 5. Set and verify environment variables
    sandbox.env.set("E2E_VAR", "e2e_value")
    value = sandbox.env.get("E2E_VAR")
    assert value == "e2e_value"

    # 6. Run commands
    cmd_result = sandbox.commands.run("echo 'Command executed'")
    assert cmd_result.success is True
    assert "Command executed" in cmd_result.stdout

    # 7. Get metrics
    metrics = sandbox.get_metrics_snapshot()
    assert isinstance(metrics, dict)

    # 8. Cleanup (kill sandbox)
    sandbox.kill()

    # Verify sandbox is destroyed
    # Note: This might fail if sandbox takes time to be destroyed
    # In a real scenario, you might want to poll for status


def test_sandbox_context_manager(api_key):
    """Test sandbox as context manager (auto-cleanup)."""
    sandbox_id = None

    with Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    ) as sandbox:
        sandbox_id = sandbox.sandbox_id

        # Use sandbox
        info = sandbox.get_info()
        assert info.status in ("running", "creating")

        result = sandbox.run_code("print('Context manager test')")
        assert result.success is True

    # Sandbox should be automatically killed after context exit
    # Note: We can't easily verify this without trying to connect,
    # which might fail for other reasons. The important thing is
    # that the context manager doesn't raise an error.


def test_code_execution_workflow(api_key):
    """Test a realistic code execution workflow."""
    sandbox = None

    try:
        sandbox = Sandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )

        # Step 1: Install a package (if needed)
        # Note: code-interpreter template should have common packages

        # Step 2: Write a Python script
        script_content = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 3)
print(f"Sum: {result}")
        """
        sandbox.files.write("/workspace/calculator.py", script_content)

        # Step 3: Execute the script
        result = sandbox.run_code(
            "exec(open('/workspace/calculator.py').read())"
        )

        assert result.success is True
        assert "Sum: 8" in result.stdout

        # Step 4: Run it as a command
        cmd_result = sandbox.commands.run("python3 /workspace/calculator.py")
        assert cmd_result.success is True
        assert "Sum: 8" in cmd_result.stdout

    finally:
        if sandbox:
            try:
                sandbox.kill()
            except Exception:
                pass


def test_file_operations_workflow(api_key):
    """Test a realistic file operations workflow."""
    sandbox = None

    try:
        sandbox = Sandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )

        # Step 1: Create directory structure
        sandbox.files.mkdir("/workspace/project")
        sandbox.files.mkdir("/workspace/project/src")

        # Step 2: Create multiple files
        sandbox.files.write("/workspace/project/README.md", "# Project\n\nTest project")
        sandbox.files.write("/workspace/project/src/main.py", "print('Hello from main')")

        # Step 3: Verify files exist
        assert sandbox.files.exists("/workspace/project/README.md") is True
        assert sandbox.files.exists("/workspace/project/src/main.py") is True

        # Step 4: Read and verify content
        readme = sandbox.files.read("/workspace/project/README.md")
        assert "Project" in readme

        main = sandbox.files.read("/workspace/project/src/main.py")
        assert "Hello from main" in main

        # Step 5: Execute code that uses the files
        result = sandbox.run_code(
            "exec(open('/workspace/project/src/main.py').read())",
            working_dir="/workspace/project",
        )
        assert result.success is True
        assert "Hello from main" in result.stdout

    finally:
        if sandbox:
            try:
                sandbox.kill()
            except Exception:
                pass


def test_environment_variables_workflow(api_key):
    """Test a realistic environment variables workflow."""
    sandbox = None

    try:
        sandbox = Sandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )

        # Step 1: Set multiple environment variables
        sandbox.env.set_all({
            "APP_NAME": "test_app",
            "APP_VERSION": "1.0.0",
            "DEBUG": "false",
        })

        # Step 2: Verify all are set
        env_vars = sandbox.env.get_all()
        assert env_vars.get("APP_NAME") == "test_app"
        assert env_vars.get("APP_VERSION") == "1.0.0"
        assert env_vars.get("DEBUG") == "false"

        # Step 3: Update one variable
        sandbox.env.update({"DEBUG": "true"})
        assert sandbox.env.get("DEBUG") == "true"
        assert sandbox.env.get("APP_NAME") == "test_app"  # Should be preserved

        # Step 4: Use env vars in code execution
        result = sandbox.run_code(
            "import os; print(f'App: {os.getenv(\"APP_NAME\")} v{os.getenv(\"APP_VERSION\")}')"
        )
        assert result.success is True
        assert "test_app" in result.stdout
        assert "1.0.0" in result.stdout

        # Step 5: Delete a variable
        sandbox.env.delete("DEBUG")
        assert sandbox.env.get("DEBUG") is None

    finally:
        if sandbox:
            try:
                sandbox.kill()
            except Exception:
                pass

