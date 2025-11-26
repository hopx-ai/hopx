"""
Shared pytest configuration and fixtures for Hopx SDK tests.

This module provides common fixtures and configuration used across
integration and E2E tests.
"""

import os
import pytest
import time
from pathlib import Path
from hopx_ai import Sandbox

# Load .env file if it exists (for test environment variables)
try:
    from dotenv import load_dotenv
    
    # Try to load .env file from tests/integration/.env (same location as bash script)
    env_file = Path(__file__).parent / "integration" / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=False)  # Don't override existing env vars
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Test configuration
BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")

# Import debug utilities if available
try:
    from tests.integration.debug_utils import (
        timed_operation,
        ProgressIndicator,
        log_test_start,
        log_test_complete,
        DEBUG_ENABLED,
    )
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False
    DEBUG_ENABLED = False


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


@pytest.fixture(autouse=True)
def test_timer(request):
    """
    Automatic fixture that times each test and logs debug information.
    
    This fixture runs automatically for every test and provides timing
    information when HOPX_TEST_DEBUG environment variable is set.
    """
    if not DEBUG_AVAILABLE:
        yield
        return
    
    test_name = f"{request.node.parent.name}::{request.node.name}"
    start_time = time.time()
    
    log_test_start(test_name)
    
    yield
    
    duration = time.time() - start_time
    log_test_complete(test_name, duration)
    
    # Warn if test takes longer than 2 minutes
    if duration > 120:
        import logging
        logger = logging.getLogger("hopx.test.debug")
        logger.warning(
            f"⚠️  Test {test_name} took {duration:.2f}s (>2 minutes)"
        )


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
    
    # Enable verbose output if debug mode is enabled
    if DEBUG_AVAILABLE and DEBUG_ENABLED:
        # Set pytest to show more verbose output
        if hasattr(config.option, 'verbose'):
            config.option.verbose = max(config.option.verbose or 0, 1)

