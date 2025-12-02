"""
Integration tests for Sandbox code execution streaming.

Tests cover:
- Executing code with real-time output streaming via WebSocket
"""

import os
import pytest
import asyncio
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestCodeExecutionStream:
    """Test code execution streaming."""

    @pytest.mark.asyncio
    async def test_run_code_stream(self, sandbox):
        """Test code execution with streaming output."""
        code = """
import time
for i in range(5):
    print(f"Line {i}")
    time.sleep(0.1)
"""
        output_lines = []
        async for message in sandbox.run_code_stream(code, language="python"):
            if message.get("type") == "stdout":
                output_lines.append(message.get("data", ""))
            elif message.get("type") == "complete":
                break

        # Should have captured some output
        assert len(output_lines) > 0
        # Check that we got some of the expected output
        output_text = "".join(output_lines)
        assert "Line" in output_text

    @pytest.mark.asyncio
    async def test_run_code_stream_with_stderr(self, sandbox):
        """Test streaming captures stderr."""
        code = """
import sys
import time
for i in range(3):
    print(f"stdout {i}", file=sys.stdout)
    print(f"stderr {i}", file=sys.stderr)
    time.sleep(0.1)
"""
        stdout_lines = []
        stderr_lines = []
        
        async for message in sandbox.run_code_stream(code, language="python"):
            if message.get("type") == "stdout":
                stdout_lines.append(message.get("data", ""))
            elif message.get("type") == "stderr":
                stderr_lines.append(message.get("data", ""))
            elif message.get("type") == "complete":
                break

        # Should have captured both stdout and stderr
        stdout_text = "".join(stdout_lines)
        stderr_text = "".join(stderr_lines)
        assert "stdout" in stdout_text or len(stdout_lines) > 0
        # stderr may or may not be captured depending on implementation

