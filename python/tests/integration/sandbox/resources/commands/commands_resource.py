"""
Integration tests for Commands resource.

Tests cover:
- Running shell commands
- Error handling for failed commands
- Background command execution
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestCommandsResource:
    """Test command execution."""

    def test_run_command(self, sandbox):
        """Test running a shell command."""
        result = sandbox.commands.run("echo 'Hello from command'")

        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 0
        assert "Hello from command" in result.stdout

    def test_run_command_with_error(self, sandbox):
        """Test running a command that fails."""
        result = sandbox.commands.run("exit 1")

        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 1

    def test_run_command_background(self, sandbox):
        """Test running a command in background."""
        result = sandbox.commands.run(
            "sleep 5 && echo 'Done'",
            background=True,
        )

        # Background execution returns immediately
        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 0

