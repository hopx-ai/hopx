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

    def test_kill_sandbox(self, api_key, cleanup_sandbox):
        """Test destroying a sandbox."""
        sandbox = Sandbox.create(
            template=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )
        cleanup_sandbox.append(sandbox)

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

