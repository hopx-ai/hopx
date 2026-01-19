"""
Integration tests for Desktop window operations.

Tests cover:
- Focusing windows
- Closing windows
- Resizing windows
- Minimizing windows
- Setting screen resolution
- Getting clipboard history
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopWindowOperations:
    """Test Desktop window operations."""

    def test_focus_window(self, desktop_sandbox):
        """Test focusing a window."""
        try:
            windows = desktop_sandbox.desktop.get_windows()
            if windows:
                window_id = windows[0].window_id if hasattr(windows[0], "window_id") else windows[0].get("id")
                if window_id:
                    desktop_sandbox.desktop.focus_window(window_id)
                    # Focus should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_resize_window(self, desktop_sandbox):
        """Test resizing a window."""
        try:
            windows = desktop_sandbox.desktop.get_windows()
            if windows:
                window_id = windows[0].window_id if hasattr(windows[0], "window_id") else windows[0].get("id")
                if window_id:
                    desktop_sandbox.desktop.resize_window(window_id, width=800, height=600)
                    # Resize should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_minimize_window(self, desktop_sandbox):
        """Test minimizing a window."""
        try:
            windows = desktop_sandbox.desktop.get_windows()
            if windows:
                window_id = windows[0].window_id if hasattr(windows[0], "window_id") else windows[0].get("id")
                if window_id:
                    desktop_sandbox.desktop.minimize_window(window_id)
                    # Minimize should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_set_resolution(self, desktop_sandbox):
        """Test setting screen resolution."""
        try:
            # Get available resolutions first
            resolutions = desktop_sandbox.desktop.get_available_resolutions()
            if resolutions:
                # Try to set to first available resolution
                width, height = resolutions[0]
                display_info = desktop_sandbox.desktop.set_resolution(width, height)
                assert display_info is not None
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_clipboard_history(self, desktop_sandbox):
        """Test getting clipboard history."""
        try:
            # Set some clipboard content first
            desktop_sandbox.desktop.set_clipboard("Test clipboard entry 1")
            desktop_sandbox.desktop.set_clipboard("Test clipboard entry 2")
            
            # Get clipboard history
            history = desktop_sandbox.desktop.get_clipboard_history()
            assert isinstance(history, list)
            # May have 0 or more entries depending on implementation
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

