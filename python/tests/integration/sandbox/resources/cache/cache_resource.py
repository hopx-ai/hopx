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


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def sandbox(api_key):
    """Create a sandbox for testing and clean up after."""
    sandbox = Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    )
    yield sandbox
    try:
        sandbox.kill()
    except Exception:
        pass


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

