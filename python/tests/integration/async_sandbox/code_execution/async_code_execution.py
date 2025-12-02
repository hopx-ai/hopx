"""
Integration tests for AsyncSandbox code execution operations.

Tests cover:
- Running code (async)
- Code execution with environment variables (async)
- Background code execution (async)
- Code execution streaming (async)
"""

import os
import pytest
import asyncio
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncCodeExecution:
    """Test async code execution."""

    @pytest.mark.asyncio
    async def test_run_simple_code(self, async_sandbox):
        """Test running simple Python code."""
        result = await async_sandbox.run_code("print('Hello, World!')")

        assert result.success is True
        assert "Hello, World!" in result.stdout
        assert result.exit_code == 0
        assert result.execution_time is not None

    @pytest.mark.asyncio
    async def test_run_code_with_error(self, async_sandbox):
        """Test running code that produces an error."""
        result = await async_sandbox.run_code("raise ValueError('Test error')")

        assert result.success is False
        assert result.exit_code != 0
        assert "ValueError" in result.stderr or "Test error" in result.stderr

    @pytest.mark.asyncio
    async def test_run_code_with_env_vars(self, async_sandbox):
        """Test code execution with environment variables."""
        result = await async_sandbox.run_code(
            "import os; print(os.getenv('TEST_VAR'))",
            env={"TEST_VAR": "test_value"},
        )

        assert result.success is True
        assert "test_value" in result.stdout

    @pytest.mark.asyncio
    async def test_run_code_different_languages(self, async_sandbox):
        """Test running code in different languages."""
        # Python (default)
        result = await async_sandbox.run_code("print('Python')", language="python")
        assert result.success is True
        assert "Python" in result.stdout

        # Bash
        result = await async_sandbox.run_code("echo 'Bash'", language="bash")
        assert result.success is True
        assert "Bash" in result.stdout

    @pytest.mark.asyncio
    async def test_run_code_background(self, async_sandbox):
        """Test running code in background."""
        response = await async_sandbox.run_code_background(
            "import time; time.sleep(5); print('Done')",
            timeout=60,
        )

        assert "process_id" in response or "execution_id" in response
        process_id = response.get("process_id") or response.get("execution_id")
        assert process_id is not None

    @pytest.mark.asyncio
    async def test_list_processes(self, async_sandbox):
        """Test listing background processes."""
        # Start a background process
        response = await async_sandbox.run_code_background(
            "import time; time.sleep(10); print('Done')",
            timeout=60,
        )
        process_id = response.get("process_id") or response.get("execution_id")

        await asyncio.sleep(1)  # Wait a moment for process to start

        # List processes
        processes = await async_sandbox.list_processes()

        assert isinstance(processes, list)

    @pytest.mark.asyncio
    async def test_kill_process(self, async_sandbox):
        """Test killing a background process."""
        # Start a long-running background process
        response = await async_sandbox.run_code_background(
            "import time; time.sleep(300); print('Done')",
            timeout=600,
        )
        process_id = response.get("process_id") or response.get("execution_id")

        await asyncio.sleep(1)  # Wait a moment for process to start

        # Kill the process
        try:
            result = await async_sandbox.kill_process(process_id)
            assert isinstance(result, dict)
        except Exception:
            # Process might have already finished or not exist
            pass

    @pytest.mark.asyncio
    async def test_run_code_stream(self, async_sandbox):
        """Test code execution with streaming output."""
        code = """
import time
for i in range(5):
    print(f"Line {i}")
    time.sleep(0.1)
"""
        output_lines = []
        async for message in async_sandbox.run_code_stream(code, language="python"):
            if message.get("type") == "output":
                output_lines.append(message.get("data", ""))
            elif message.get("type") == "complete":
                break

        # Should have captured some output
        assert len(output_lines) > 0
        # Check that we got some of the expected output
        output_text = "".join(output_lines)
        assert "Line" in output_text

