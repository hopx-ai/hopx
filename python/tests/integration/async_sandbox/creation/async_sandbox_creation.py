"""
Integration tests for AsyncSandbox creation operations.

Tests cover:
- Creating sandbox from template name (async)
- Creating sandbox with environment variables (async)
- Creating sandbox with timeout (async)
- Creating sandbox without internet access (async)
- Error handling for invalid templates (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox
from hopx_ai.errors import NotFoundError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncSandboxCreation:
    """Test async sandbox creation operations."""

    @pytest.mark.asyncio
    async def test_create_from_template_name(self, api_key, cleanup_async_sandbox):
        """Test creating sandbox from template name."""
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_async_sandbox.append(sandbox)
        
        assert sandbox.sandbox_id is not None
        assert isinstance(sandbox.sandbox_id, str)
        assert len(sandbox.sandbox_id) > 0

        # Verify sandbox exists
        info = await sandbox.get_info()
        assert info.status in ("running", "creating")
        assert info.public_host is not None

    @pytest.mark.asyncio
    async def test_create_with_env_vars(self, api_key, cleanup_async_sandbox):
        """Test creating sandbox with environment variables."""
        env_vars = {
            "TEST_VAR": "test_value",
            "ANOTHER_VAR": "another_value",
        }
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
            env_vars=env_vars,
        )
        cleanup_async_sandbox.append(sandbox)

        # Verify env vars are set
        env = await sandbox.env.get_all()
        assert env.get("TEST_VAR") == "test_value"
        assert env.get("ANOTHER_VAR") == "another_value"

    @pytest.mark.asyncio
    async def test_create_with_timeout(self, api_key, cleanup_async_sandbox):
        """Test creating sandbox with timeout."""
        timeout_seconds = 300  # 5 minutes
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=timeout_seconds,
        )
        cleanup_async_sandbox.append(sandbox)

        info = await sandbox.get_info()
        assert info.timeout_seconds == timeout_seconds

    @pytest.mark.asyncio
    async def test_create_without_internet(self, api_key, cleanup_async_sandbox):
        """Test creating sandbox without internet access."""
        sandbox = await AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
            internet_access=False,
        )
        cleanup_async_sandbox.append(sandbox)

        info = await sandbox.get_info()
        assert info.internet_access is False

    @pytest.mark.asyncio
    async def test_create_invalid_template(self, api_key):
        """Test creating sandbox with invalid template raises error."""
        with pytest.raises(NotFoundError):
            await AsyncSandbox.create(
                template="nonexistent-template-12345",
                api_key=api_key,
                base_url=BASE_URL,
            )

    @pytest.mark.asyncio
    async def test_create_with_context_manager(self, api_key):
        """Test creating sandbox with async context manager."""
        async with AsyncSandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        ) as sandbox:
            assert sandbox.sandbox_id is not None
            info = await sandbox.get_info()
            assert info.status in ("running", "creating")
        
        # Sandbox should be automatically killed after context exit
        # Verify it's destroyed
        with pytest.raises(NotFoundError):
            await AsyncSandbox.connect(
                sandbox_id=sandbox.sandbox_id,
                api_key=api_key,
                base_url=BASE_URL,
            )

