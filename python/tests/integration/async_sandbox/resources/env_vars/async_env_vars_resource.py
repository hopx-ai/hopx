"""
Integration tests for AsyncSandbox EnvironmentVariables resource.

Tests cover:
- Getting all environment variables (async)
- Setting all environment variables (async)
- Updating specific environment variables (async)
- Deleting environment variables (async)
- Getting single environment variable (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncEnvironmentVariables:
    """Test async environment variable operations."""

    @pytest.mark.asyncio
    async def test_get_all_env_vars(self, async_sandbox):
        """Test getting all environment variables."""
        env_vars = await async_sandbox.env.get_all()

        assert isinstance(env_vars, dict)
        # Should have at least some system env vars
        assert len(env_vars) > 0

    @pytest.mark.asyncio
    async def test_set_all_env_vars(self, async_sandbox):
        """Test setting all environment variables."""
        new_vars = {
            "VAR1": "value1",
            "VAR2": "value2",
        }

        result = await async_sandbox.env.set_all(new_vars)

        assert isinstance(result, dict)
        assert result.get("VAR1") == "value1"
        assert result.get("VAR2") == "value2"

    @pytest.mark.asyncio
    async def test_update_env_vars(self, async_sandbox):
        """Test updating specific environment variables."""
        # Set initial vars
        await async_sandbox.env.set_all({"VAR1": "initial", "VAR2": "initial2"})

        # Update one var
        await async_sandbox.env.update({"VAR1": "updated"})

        # Verify update
        env_vars = await async_sandbox.env.get_all()
        assert env_vars.get("VAR1") == "updated"
        assert env_vars.get("VAR2") == "initial2"  # Should be preserved

    @pytest.mark.asyncio
    async def test_delete_env_var(self, async_sandbox):
        """Test deleting an environment variable."""
        # Set a var
        await async_sandbox.env.set("TEST_DELETE", "value")

        # Verify it exists
        assert await async_sandbox.env.get("TEST_DELETE") == "value"

        # Delete it
        await async_sandbox.env.delete("TEST_DELETE")

        # Verify it's gone
        assert await async_sandbox.env.get("TEST_DELETE") is None

    @pytest.mark.asyncio
    async def test_get_single_env_var(self, async_sandbox):
        """Test getting a single environment variable."""
        await async_sandbox.env.set("TEST_GET", "test_value")

        value = await async_sandbox.env.get("TEST_GET")
        assert value == "test_value"

        # Test with default
        value = await async_sandbox.env.get("NONEXISTENT", default="default_value")
        assert value == "default_value"

