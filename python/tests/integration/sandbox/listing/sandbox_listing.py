"""
Integration tests for Sandbox listing operations.

Tests cover:
- Listing all sandboxes
- Filtering sandboxes by status
- Lazy iteration over sandboxes
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


class TestSandboxListing:
    """Test sandbox listing operations."""

    def test_list_sandboxes(self, api_key):
        """Test listing all sandboxes."""
        sandboxes = Sandbox.list(
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(sandboxes, list)
        for sb in sandboxes:
            assert isinstance(sb, Sandbox)
            assert sb.sandbox_id is not None

    def test_list_sandboxes_with_status_filter(self, api_key):
        """Test listing sandboxes with status filter."""
        running = Sandbox.list(
            status="running",
            api_key=api_key,
            base_url=BASE_URL,
            limit=10,
        )

        assert isinstance(running, list)
        for sb in running:
            info = sb.get_info()
            assert info.status == "running"

    def test_iter_sandboxes(self, api_key):
        """Test lazy iteration over sandboxes."""
        count = 0
        for sandbox in Sandbox.iter(
            status="running",
            api_key=api_key,
            base_url=BASE_URL,
        ):
            assert isinstance(sandbox, Sandbox)
            count += 1
            if count >= 5:  # Limit to first 5 for test speed
                break

        assert count > 0

