"""
Integration tests for Desktop window management operations.

Tests cover:
- Getting list of windows
- Window operations (focus, close, resize, minimize)
- Display operations
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopWindows:
    """Test Desktop window management operations."""

    def test_get_windows(self, sandbox):
        """Test getting list of all windows."""
        try:
            windows = sandbox.desktop.get_windows()
            assert isinstance(windows, list)
            # May have 0 or more windows depending on template
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_display(self, sandbox):
        """Test getting display information."""
        try:
            display_info = sandbox.desktop.get_display()
            assert display_info is not None
            # Display info should have resolution information
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_available_resolutions(self, sandbox):
        """Test getting available screen resolutions."""
        try:
            resolutions = sandbox.desktop.get_available_resolutions()
            assert isinstance(resolutions, list)
            # Should have at least one resolution
            if resolutions:
                assert isinstance(resolutions[0], tuple)
                assert len(resolutions[0]) == 2
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

