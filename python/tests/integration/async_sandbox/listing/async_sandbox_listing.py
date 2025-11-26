"""
Integration tests for AsyncSandbox listing operations.

Tests cover:
- Listing all sandboxes (async)
- Filtering sandboxes by status (async)
- Lazy iteration over sandboxes (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")


class TestAsyncSandboxListing:
    """Test async sandbox listing operations."""

    @pytest.mark.asyncio
    async def test_list_sandboxes(self, api_key):
        """Test listing all sandboxes."""
        sandboxes = await AsyncSandbox.list(
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(sandboxes, list)
        for sb in sandboxes:
            assert isinstance(sb, AsyncSandbox)
            assert sb.sandbox_id is not None

    @pytest.mark.asyncio
    async def test_list_sandboxes_with_status_filter(self, api_key):
        """Test listing sandboxes with status filter."""
        running = await AsyncSandbox.list(
            status="running",
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(running, list)
        for sb in running:
            info = await sb.get_info()
            assert info.status == "running"

    @pytest.mark.asyncio
    async def test_iter_sandboxes(self, api_key):
        """Test lazy async iteration over sandboxes."""
        count = 0
        async for sandbox in AsyncSandbox.iter(
            status="running",
            api_key=api_key,
            base_url=BASE_URL,
        ):
            assert isinstance(sandbox, AsyncSandbox)
            count += 1
            if count >= 5:  # Limit to first 5 for test speed
                break

        assert count > 0

