"""
Integration tests for AsyncSandbox listing operations.

Tests cover:
- Listing all sandboxes (async)
- Filtering sandboxes by status (async)
- Lazy iteration over sandboxes (async)
- Handling empty results when no sandboxes exist
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncSandboxListing:
    """Test async sandbox listing operations."""

    @pytest.mark.asyncio
    async def test_list_sandboxes(self, api_key, cleanup_async_sandbox):
        """Test listing all sandboxes."""
        # Create a sandbox to ensure at least one exists
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_async_sandbox.append(sandbox)

        # List all sandboxes
        sandboxes = await AsyncSandbox.list(
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(sandboxes, list)
        assert len(sandboxes) > 0  # Should have at least the one we created
        for sb in sandboxes:
            assert isinstance(sb, AsyncSandbox)
            assert sb.sandbox_id is not None

    @pytest.mark.asyncio
    async def test_list_sandboxes_empty(self, api_key):
        """Test listing sandboxes when none exist (should return empty list)."""
        # List with a filter that won't match anything
        sandboxes = await AsyncSandbox.list(
            status="stopped",  # Assuming no stopped sandboxes exist
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        # Should return empty list, not crash
        assert isinstance(sandboxes, list)
        # Note: This test verifies the SDK handles empty results gracefully
        # The actual length depends on whether stopped sandboxes exist

    @pytest.mark.asyncio
    async def test_list_sandboxes_with_status_filter(self, api_key, cleanup_async_sandbox):
        """Test listing sandboxes with status filter."""
        # Create a running sandbox
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_async_sandbox.append(sandbox)

        # List running sandboxes
        running = await AsyncSandbox.list(
            status="running",
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(running, list)
        # Should have at least the one we created
        assert len(running) > 0
        for sb in running:
            info = await sb.get_info()
            assert info.status == "running"

    @pytest.mark.asyncio
    async def test_list_sandboxes_with_status_filter_empty(self, api_key):
        """Test listing sandboxes with status filter when none match (should return empty list)."""
        # List paused sandboxes (assuming none exist)
        paused = await AsyncSandbox.list(
            status="paused",
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        # Should return empty list, not crash
        assert isinstance(paused, list)
        # Note: This test verifies the SDK handles empty results gracefully
        # The actual length depends on whether paused sandboxes exist

    @pytest.mark.asyncio
    async def test_iter_sandboxes(self, api_key, cleanup_async_sandbox):
        """Test lazy async iteration over sandboxes."""
        # Create a running sandbox
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_async_sandbox.append(sandbox)

        # Iterate over running sandboxes
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

        assert count > 0  # Should have at least the one we created

    @pytest.mark.asyncio
    async def test_iter_sandboxes_empty(self, api_key):
        """Test lazy async iteration when no sandboxes match (should yield nothing)."""
        # Iterate over paused sandboxes (assuming none exist)
        count = 0
        async for sandbox in AsyncSandbox.iter(
            status="paused",
            api_key=api_key,
            base_url=BASE_URL,
        ):
            assert isinstance(sandbox, AsyncSandbox)
            count += 1
            if count >= 5:  # Limit to first 5 for test speed
                break

        # Should handle empty results gracefully (count may be 0)
        # This test verifies the SDK doesn't crash when iterating over empty results

