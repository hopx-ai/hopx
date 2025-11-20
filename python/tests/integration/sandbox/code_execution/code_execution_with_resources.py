"""
Integration tests for code execution with resource access.

Tests cover:
- Running code in specific working directory
- Code execution with global environment variables
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def sandbox(api_key):
    """Create a sandbox for testing and clean up after."""
    sandbox = Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    )
    yield sandbox
    try:
        sandbox.kill()
    except Exception:
        pass


class TestCodeExecutionWithResources:
    """Test code execution with resource access."""

    def test_run_code_in_working_dir(self, sandbox):
        """Test running code in specific working directory."""
        # Create a file first
        sandbox.files.write("/workspace/test.txt", "test content")

        # Run code that reads from working directory
        result = sandbox.run_code(
            "with open('test.txt', 'r') as f: print(f.read())",
            working_dir="/workspace",
        )

        assert result.success is True
        assert "test content" in result.stdout

    def test_run_code_with_global_env(self, sandbox):
        """Test code execution with global environment variables."""
        # Set global env var
        sandbox.env.set("GLOBAL_VAR", "global_value")

        # Run code that uses it
        result = sandbox.run_code("import os; print(os.getenv('GLOBAL_VAR'))")

        assert result.success is True
        assert "global_value" in result.stdout

