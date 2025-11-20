"""
Shared pytest configuration and fixtures for Hopx SDK tests.

This module provides common fixtures and configuration used across
integration and E2E tests.
"""

import os
import pytest
from hopx_ai import Sandbox

# Test configuration
BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture(scope="session")
def api_key():
    """
    Get API key from environment variable.
    
    Skips tests if HOPX_API_KEY is not set.
    """
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def test_base_url():
    """Get test base URL from environment or use default."""
    return BASE_URL


@pytest.fixture
def test_template():
    """Get test template name from environment or use default."""
    return TEST_TEMPLATE


@pytest.fixture
def sandbox_factory(api_key, test_base_url, test_template):
    """
    Factory fixture for creating sandboxes.
    
    Returns a function that creates a sandbox with default settings.
    """
    def _create_sandbox(**kwargs):
        """Create a sandbox with optional overrides."""
        defaults = {
            "template": test_template,
            "api_key": api_key,
            "base_url": test_base_url,
            "timeout_seconds": 600,  # 10 minutes
        }
        defaults.update(kwargs)
        return Sandbox.create(**defaults)
    
    return _create_sandbox


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

