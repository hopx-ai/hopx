"""
Integration tests for AsyncSandbox Commands resource.

Tests cover:
- Running shell commands (async)
- Error handling for failed commands (async)
- Background command execution (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncCommandsResource:
    """Test async command execution."""

    @pytest.mark.asyncio
    async def test_run_command(self, async_sandbox):
        """Test running a shell command."""
        result = await async_sandbox.commands.run("echo 'Hello from command'")

        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 0
        assert "Hello from command" in result.stdout

    @pytest.mark.asyncio
    async def test_run_command_with_error(self, async_sandbox):
        """Test running a command that fails."""
        result = await async_sandbox.commands.run("exit 1")

        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 1

    @pytest.mark.asyncio
    async def test_run_command_background(self, async_sandbox):
        """Test running a command in background."""
        result = await async_sandbox.commands.run(
            "sleep 5 && echo 'Done'",
            background=True,
        )

        # Background execution returns immediately
        # Note: CommandResult.success may be None, check exit_code instead
        assert result.exit_code == 0

