"""
Integration tests for AsyncSandbox connection operations.

Tests cover:
- Connecting to existing sandbox (async)
- Error handling for non-existent sandbox (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox
from hopx_ai.errors import NotFoundError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncSandboxConnection:
    """Test async sandbox connection operations."""

    @pytest.mark.asyncio
    async def test_connect_to_existing_sandbox(self, async_sandbox, api_key):
        """Test connecting to an existing sandbox."""
        # Disconnect and reconnect
        sandbox_id = async_sandbox.sandbox_id

        # Connect to the same sandbox
        reconnected = await AsyncSandbox.connect(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=BASE_URL,
        )

        assert reconnected.sandbox_id == sandbox_id
        # Cleanup the reconnected sandbox
        try:
            await reconnected.kill()
        except Exception:
            pass
        info = await reconnected.get_info()
        assert info.status in ("running", "paused")

    @pytest.mark.asyncio
    async def test_connect_to_nonexistent_sandbox(self, api_key):
        """Test connecting to non-existent sandbox raises error."""
        with pytest.raises(NotFoundError):
            await AsyncSandbox.connect(
                sandbox_id="nonexistent-sandbox-12345",
                api_key=api_key,
                base_url=BASE_URL,
            )

