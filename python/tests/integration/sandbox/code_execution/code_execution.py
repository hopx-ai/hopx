"""
Integration tests for basic code execution.

Tests cover:
- Running simple code
- Error handling
- Timeout handling
- Environment variables in code execution
- Different programming languages
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestCodeExecution:
    """Test basic code execution."""

    def test_run_simple_code(self, sandbox):
        """Test running simple Python code."""
        result = sandbox.run_code("print('Hello, World!')")

        assert result.success is True
        assert "Hello, World!" in result.stdout
        assert result.exit_code == 0
        assert result.execution_time is not None

    def test_run_code_with_error(self, sandbox):
        """Test running code that produces an error."""
        result = sandbox.run_code("raise ValueError('Test error')")

        assert result.success is False
        assert result.exit_code != 0
        assert "ValueError" in result.stderr or "Test error" in result.stderr

    def test_run_code_with_timeout(self, sandbox):
        """Test code execution timeout."""
        # Code that runs longer than timeout
        result = sandbox.run_code(
            "import time; time.sleep(10)",
            timeout=2,  # 2 second timeout
        )

        # Should timeout or fail
        assert result.success is False or result.exit_code != 0

    def test_run_code_with_env_vars(self, sandbox):
        """Test code execution with environment variables."""
        result = sandbox.run_code(
            "import os; print(os.getenv('TEST_VAR'))",
            env={"TEST_VAR": "test_value"},
        )

        assert result.success is True
        assert "test_value" in result.stdout

    def test_run_code_different_languages(self, sandbox):
        """Test running code in different languages."""
        # Python (default)
        result = sandbox.run_code("print('Python')", language="python")
        assert result.success is True
        assert "Python" in result.stdout

        # Bash
        result = sandbox.run_code("echo 'Bash'", language="bash")
        assert result.success is True
        assert "Bash" in result.stdout

