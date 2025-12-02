"""
Integration tests for Cache resource.

Tests cover:
- Getting cache statistics
- Clearing cache
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestCacheResource:
    """Test cache operations."""

    def test_cache_stats(self, sandbox):
        """Test getting cache statistics."""
        stats = sandbox.cache.stats()

        assert isinstance(stats, dict)
        # Cache stats might have various fields

    def test_clear_cache(self, sandbox):
        """Test clearing cache."""
        result = sandbox.cache.clear()

        assert isinstance(result, dict)

