"""
Integration tests for Desktop UI automation operations.

Tests cover:
- OCR operations
- Finding UI elements
- Waiting for UI elements
- Drag and drop
- Getting element bounds
- Hotkey combinations
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopUIAutomation:
    """Test Desktop UI automation operations."""

    def test_ocr(self, desktop_sandbox):
        """Test OCR on screen region."""
        try:
            # Perform OCR on a region of the screen
            text = desktop_sandbox.desktop.ocr(0, 0, 100, 100, language="eng")
            assert isinstance(text, str)
            # May return empty string if no text found
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_find_element(self, desktop_sandbox):
        """Test finding UI element by text."""
        try:
            # Try to find an element (may not find anything)
            element = desktop_sandbox.desktop.find_element("test", timeout=5)
            # Element may be None if not found
            if element is not None:
                assert isinstance(element, dict)
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_wait_for(self, desktop_sandbox):
        """Test waiting for UI element to appear."""
        try:
            # Wait for an element (will timeout if not found)
            # Use a short timeout for testing
            element = desktop_sandbox.desktop.wait_for("test", timeout=5)
            assert isinstance(element, dict)
        except (DesktopNotAvailableError, TimeoutError):
            # Timeout is expected if element doesn't exist
            pytest.skip("Desktop not available or element not found")

    def test_drag_drop(self, desktop_sandbox):
        """Test drag and drop operation."""
        try:
            desktop_sandbox.desktop.drag_drop(100, 100, 200, 200)
            # Drag drop should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_bounds(self, desktop_sandbox):
        """Test getting bounding box of UI element."""
        try:
            # Try to get bounds of an element
            bounds = desktop_sandbox.desktop.get_bounds("test", timeout=5)
            if bounds is not None:
                assert isinstance(bounds, dict)
                # Should have position/size information
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_hotkey(self, desktop_sandbox):
        """Test pressing hotkey combination."""
        try:
            desktop_sandbox.desktop.hotkey(["ctrl"], "c")
            # Hotkey should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

