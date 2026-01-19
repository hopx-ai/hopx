"""
Integration tests for Sandbox connection operations.

Tests cover:
- Connecting to existing sandbox
- Error handling for non-existent sandbox
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import NotFoundError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestSandboxConnection:
    """Test sandbox connection operations."""

    def test_connect_to_existing_sandbox(self, sandbox, api_key):
        """Test connecting to an existing sandbox."""
        # Disconnect and reconnect
        sandbox_id = sandbox.sandbox_id

        # Connect to the same sandbox
        reconnected = Sandbox.connect(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=BASE_URL,
        )

        assert reconnected.sandbox_id == sandbox_id
        info = reconnected.get_info()
        assert info.status in ("running", "paused")
        # Cleanup the reconnected sandbox
        try:
            reconnected.kill()
        except Exception:
            pass

    def test_connect_to_nonexistent_sandbox(self, api_key):
        """Test connecting to non-existent sandbox raises error."""
        with pytest.raises(NotFoundError):
            Sandbox.connect(
                sandbox_id="nonexistent-sandbox-12345",
                api_key=api_key,
                base_url=BASE_URL,
            )

