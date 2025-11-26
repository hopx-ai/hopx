"""
Integration tests for Sandbox token management operations.

Tests cover:
- Getting current JWT token
- Refreshing JWT token
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestTokenManagement:
    """Test token management operations."""

    def test_get_token(self, sandbox):
        """Test getting current JWT token."""
        # Token should be available after sandbox operations
        # Access agent to ensure token is generated
        sandbox.get_info()
        
        token = sandbox.get_token()
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens typically start with "eyJ" (base64 encoded JSON)
        assert token.startswith("eyJ") or len(token) > 20

    def test_refresh_token(self, sandbox):
        """Test refreshing JWT token."""
        # Get initial token
        initial_token = sandbox.get_token()
        
        # Refresh token
        sandbox.refresh_token()
        
        # Get new token
        new_token = sandbox.get_token()
        
        # Tokens should be different (or same if not expired)
        assert isinstance(new_token, str)
        assert len(new_token) > 0
        # Note: If token hasn't expired, it might be the same
        # The important thing is that refresh_token() doesn't error

