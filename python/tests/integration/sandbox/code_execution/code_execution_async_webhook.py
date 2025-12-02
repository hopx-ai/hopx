"""
Integration tests for Sandbox async code execution with webhook callback.

Tests cover:
- Executing code asynchronously with webhook callback
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestCodeExecutionAsyncWebhook:
    """Test async code execution with webhook callback."""

    def test_run_code_async(self, sandbox):
        """Test executing code asynchronously with webhook callback."""
        # Note: This requires a publicly accessible webhook URL
        # For testing, we'll just verify the method returns an execution_id
        # In a real scenario, you'd set up a webhook endpoint
        
        # Use a test webhook URL (this won't actually receive the callback in tests)
        # In production, this would be your server endpoint
        callback_url = "https://httpbin.org/post"  # Public test endpoint
        
        result = sandbox.run_code_async(
            code="print('Hello from async execution'); import time; time.sleep(1)",
            callback_url=callback_url,
            language="python",
            timeout=1800,  # 30 minutes
        )

        assert isinstance(result, dict)
        assert "execution_id" in result
        assert result.get("status") in ("queued", "running", "pending")
        assert "callback_url" in result

    def test_run_code_async_with_custom_headers(self, sandbox):
        """Test async execution with custom callback headers."""
        callback_url = "https://httpbin.org/post"
        
        result = sandbox.run_code_async(
            code="print('Test with headers')",
            callback_url=callback_url,
            callback_headers={
                "X-Custom-Header": "test-value",
                "Authorization": "Bearer test-token",
            },
        )

        assert isinstance(result, dict)
        assert "execution_id" in result

