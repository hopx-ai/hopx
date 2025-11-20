"""
Integration tests for Sandbox lifecycle operations.

Tests cover:
- Pause and resume operations
- Timeout management
- Sandbox destruction
"""

import os
import pytest
import time
from hopx_ai import Sandbox
from hopx_ai.errors import NotFoundError, HopxError

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


class TestSandboxLifecycle:
    """Test sandbox lifecycle operations."""

    def test_pause_and_resume(self, sandbox):
        """Test pausing and resuming a sandbox."""
        # Pause
        sandbox.pause()
        time.sleep(2)  # Wait for state change

        info = sandbox.get_info()
        assert info.status == "paused"

        # Resume
        sandbox.resume()
        time.sleep(2)  # Wait for state change

        info = sandbox.get_info()
        assert info.status == "running"

    def test_set_timeout(self, sandbox):
        """Test setting sandbox timeout."""
        new_timeout = 900  # 15 minutes
        sandbox.set_timeout(new_timeout)

        info = sandbox.get_info()
        assert info.timeout_seconds == new_timeout

    def test_kill_sandbox(self, api_key):
        """Test destroying a sandbox."""
        sandbox = Sandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )

        sandbox_id = sandbox.sandbox_id
        sandbox.kill()

        # Verify sandbox is destroyed
        time.sleep(2)  # Wait for state change
        with pytest.raises((NotFoundError, HopxError)):
            Sandbox.connect(
                sandbox_id=sandbox_id,
                api_key=api_key,
                base_url=BASE_URL,
            )

