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
        """Test running a command in background and verify it continues running."""
        import asyncio
        
        # Use a command that writes a number every 0.1 seconds to verify it's running
        test_file = "/workspace/background_counter.txt"
        # Command writes numbers 1-10, one every 0.1 seconds = 1 second total
        result = await async_sandbox.commands.run(
            f"for i in {{1..10}}; do echo $i >> {test_file}; sleep 0.1; done",
            background=True,
        )

        # Background execution returns immediately
        assert result.exit_code == 0
        assert "Background process started" in result.stdout
        
        # Watch the file for ~1.5 seconds to verify output is evolving (total test time ~2.5s)
        previous_content = ""
        check_interval = 0.5  # Check every 0.5 seconds
        max_checks = 3  # Check 3 times = 1.5 seconds total watching
        check_count = 0
        content_changed = False
        
        while check_count < max_checks:
            await asyncio.sleep(check_interval)
            check_count += 1
            
            # Check if file exists and read its content
            if await async_sandbox.files.exists(test_file):
                current_content = await async_sandbox.files.read(test_file)
                
                # Verify content is evolving (should have more lines as time passes)
                if current_content != previous_content:
                    # Content changed - process is running
                    content_changed = True
                    previous_content = current_content
                    # Verify we're seeing incrementing numbers
                    lines = [line.strip() for line in current_content.strip().split('\n') if line.strip()]
                    if lines:
                        # Verify numbers are incrementing correctly
                        for i, line in enumerate(lines, 1):
                            assert line == str(i), \
                                f"Expected number {i} at line {i}, got '{line}'"
            else:
                # File doesn't exist yet - that's okay for first check
                if check_count >= 2:
                    pytest.fail(f"File {test_file} should exist after {check_count * check_interval} seconds")
        
        # Verify that content actually changed (proves process was running)
        assert content_changed, "Background process output should have changed over time"
        
        # Verify final content has multiple numbers (proves it ran for a while)
        if await async_sandbox.files.exists(test_file):
            final_content = await async_sandbox.files.read(test_file)
            lines = [line.strip() for line in final_content.strip().split('\n') if line.strip()]
            # After command completes (1 second) + watching (2 seconds), we should have all 10 numbers
            assert len(lines) >= 10, \
                f"Expected at least 10 numbers after command completion, got {len(lines)}"
        
        # Clean up (ignore errors - this is just cleanup)
        try:
            if await async_sandbox.files.exists(test_file):
                await async_sandbox.files.remove(test_file)
        except Exception:
            # Ignore cleanup errors - test has already verified the functionality
            pass

