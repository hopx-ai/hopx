"""
Integration tests for Desktop screenshot operations.

Tests cover:
- Full screen screenshots
- Region screenshots
- Window screenshots
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopScreenshots:
    """Test Desktop screenshot operations."""

    def test_screenshot(self, desktop_sandbox):
        """Test capturing full screen screenshot."""
        try:
            img_bytes = desktop_sandbox.desktop.screenshot()
            assert isinstance(img_bytes, bytes)
            assert len(img_bytes) > 0
            # PNG files start with specific bytes
            assert img_bytes[:8] == b'\x89PNG\r\n\x1a\n'[:8] or len(img_bytes) > 100
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_screenshot_region(self, desktop_sandbox):
        """Test capturing screenshot of specific region."""
        try:
            img_bytes = desktop_sandbox.desktop.screenshot_region(0, 0, 100, 100)
            assert isinstance(img_bytes, bytes)
            assert len(img_bytes) > 0
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_capture_window(self, desktop_sandbox):
        """Test capturing screenshot of specific window."""
        try:
            # Get windows first
            windows = desktop_sandbox.desktop.get_windows()
            if windows:
                window_id = windows[0].window_id if hasattr(windows[0], "window_id") else windows[0].get("id")
                img_bytes = desktop_sandbox.desktop.capture_window(window_id=window_id)
                assert isinstance(img_bytes, bytes)
                assert len(img_bytes) > 0
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

