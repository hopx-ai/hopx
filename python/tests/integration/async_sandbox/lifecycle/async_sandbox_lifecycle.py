"""
Integration tests for AsyncSandbox lifecycle operations.

Tests cover:
- Pause and resume operations (async)
- Timeout management (async)
- Sandbox destruction (async)
- Context manager usage
"""

import os
import pytest
import asyncio
from hopx_ai import AsyncSandbox
from hopx_ai.errors import NotFoundError, HopxError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncSandboxLifecycle:
    """Test async sandbox lifecycle operations."""

    @pytest.mark.asyncio
    async def test_pause_and_resume(self, async_sandbox):
        """Test pausing and resuming a sandbox."""
        # Pause
        await async_sandbox.pause()
        await asyncio.sleep(2)  # Wait for state change

        info = await async_sandbox.get_info()
        assert info.status == "paused"

        # Resume
        await async_sandbox.resume()
        await asyncio.sleep(2)  # Wait for state change

        info = await async_sandbox.get_info()
        assert info.status == "running"

    @pytest.mark.asyncio
    async def test_set_timeout(self, async_sandbox):
        """Test setting sandbox timeout."""
        new_timeout = 900  # 15 minutes
        await async_sandbox.set_timeout(new_timeout)

        info = await async_sandbox.get_info()
        assert info.timeout_seconds == new_timeout

    @pytest.mark.asyncio
    async def test_kill_sandbox(self, api_key, cleanup_async_sandbox):
        """Test destroying a sandbox."""
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_async_sandbox.append(sandbox)

        sandbox_id = sandbox.sandbox_id
        await sandbox.kill()

        # Verify sandbox is destroyed
        await asyncio.sleep(2)  # Wait for state change
        with pytest.raises((NotFoundError, HopxError)):
            await AsyncSandbox.connect(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=BASE_URL,
            )

    @pytest.mark.asyncio
    async def test_context_manager_auto_cleanup(self, api_key):
        """Test that context manager automatically cleans up."""
        sandbox_id = None
        async with AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        ) as sandbox:
            sandbox_id = sandbox.sandbox_id
            info = await sandbox.get_info()
            assert info.status in ("running", "creating")
        
        # After exiting context, sandbox should be killed
        await asyncio.sleep(2)
        with pytest.raises((NotFoundError, HopxError)):
            await AsyncSandbox.connect(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=BASE_URL,
            )

