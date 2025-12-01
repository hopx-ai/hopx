"""
Integration tests for Desktop debug operations.

Tests cover:
- Getting debug logs
- Getting debug process information
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopDebug:
    """Test Desktop debug operations."""

    def test_get_debug_logs(self, sandbox):
        """Test getting debug logs."""
        try:
            logs = sandbox.desktop.get_debug_logs()
            assert isinstance(logs, list)
            # May have 0 or more log entries
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_debug_processes(self, sandbox):
        """Test getting debug process information."""
        try:
            processes = sandbox.desktop.get_debug_processes()
            assert isinstance(processes, list)
            # May have 0 or more processes
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

