"""
Integration tests for AsyncSandbox token management operations.

Tests cover:
- Getting current JWT token (async)
- Refreshing JWT token (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox
from hopx_ai._token_cache import get_cached_token

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncTokenManagement:
    """Test async token management operations."""

    @pytest.mark.asyncio
    async def test_get_token(self, async_sandbox):
        """Test getting current JWT token."""
        # Token should be available after sandbox operations
        # Access agent to ensure token is generated
        await async_sandbox.get_info()
        
        # Get token from cache (workaround until get_token() is implemented)
        token_data = get_cached_token(async_sandbox.sandbox_id)
        assert token_data is not None, "Token should exist after get_info()"
        token = token_data.token
        
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens typically start with "eyJ" (base64 encoded JSON)
        assert token.startswith("eyJ") or len(token) > 20

    @pytest.mark.asyncio
    async def test_refresh_token(self, async_sandbox):
        """Test refreshing JWT token."""
        # Access agent to ensure token is generated
        await async_sandbox.get_info()
        
        # Get initial token from cache
        initial_token_data = get_cached_token(async_sandbox.sandbox_id)
        assert initial_token_data is not None, "Token should exist after get_info()"
        initial_token = initial_token_data.token
        initial_expires_at = initial_token_data.expires_at
        
        # Verify initial token is valid
        assert isinstance(initial_token, str)
        assert len(initial_token) > 0
        # JWT tokens typically start with "eyJ" (base64 encoded JSON)
        assert initial_token.startswith("eyJ") or len(initial_token) > 20
        
        # Refresh token
        await async_sandbox.refresh_token()
        
        # Get new token from cache
        new_token_data = get_cached_token(async_sandbox.sandbox_id)
        assert new_token_data is not None, "Token should exist after refresh"
        new_token = new_token_data.token
        new_expires_at = new_token_data.expires_at
        
        # Verify new token is valid
        assert isinstance(new_token, str)
        assert len(new_token) > 0
        assert new_token.startswith("eyJ") or len(new_token) > 20
        
        # Verify token was refreshed (new expiration time should be later)
        assert new_expires_at > initial_expires_at, \
            "New token should have later expiration time after refresh"
        
        # Verify async_sandbox still works with refreshed token
        info = await async_sandbox.get_info()
        assert info is not None

