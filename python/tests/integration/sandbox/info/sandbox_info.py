"""
Integration tests for Sandbox info retrieval.

Tests cover:
- Getting sandbox information
- Getting preview URLs
- Agent URL property
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
        timeout_seconds=600,  # 10 minutes
    )
    yield sandbox
    # Cleanup
    try:
        sandbox.kill()
    except Exception:
        pass  # Ignore cleanup errors


class TestSandboxInfo:
    """Test sandbox info retrieval."""

    def test_get_info(self, sandbox):
        """Test getting sandbox information."""
        info = sandbox.get_info()

        assert info.sandbox_id == sandbox.sandbox_id
        assert info.status is not None
        assert info.public_host is not None
        assert info.public_host.startswith("https://")

    def test_get_info_contains_resources(self, sandbox):
        """Test that sandbox info contains resource information."""
        info = sandbox.get_info()

        if info.resources:
            assert info.resources.vcpu > 0
            assert info.resources.memory_mb > 0
            assert info.resources.disk_mb > 0

    def test_get_preview_url(self, sandbox):
        """Test getting preview URL for a port."""
        url = sandbox.get_preview_url(port=8080)
        assert url.startswith("https://")
        assert "8080" in url
        assert sandbox.sandbox_id in url or "sandbox" in url.lower()

    def test_get_preview_url_default_port(self, sandbox):
        """Test getting preview URL with default port."""
        url = sandbox.get_preview_url()
        assert url.startswith("https://")
        assert "7777" in url

    def test_agent_url_property(self, sandbox):
        """Test agent_url property."""
        url = sandbox.agent_url
        assert url.startswith("https://")
        assert "7777" in url

