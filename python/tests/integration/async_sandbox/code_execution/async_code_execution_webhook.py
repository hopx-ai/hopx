"""
Integration tests for AsyncSandbox async code execution with webhook callback.

Tests cover:
- Executing code asynchronously with webhook callback (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncCodeExecutionWebhook:
    """Test async code execution with webhook callback."""

    @pytest.mark.asyncio
    async def test_run_code_async(self, async_sandbox):
        """Test executing code asynchronously with webhook callback."""
        # Use a test webhook URL
        callback_url = "https://httpbin.org/post"
        
        execution_id = await async_sandbox.run_code_async(
            code="print('Hello from async execution')",
            callback_url=callback_url,
            language="python",
            timeout_seconds=1800,
        )

        assert isinstance(execution_id, str)
        assert len(execution_id) > 0

