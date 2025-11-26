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

