"""
Integration tests for Desktop input operations.

Tests cover:
- Mouse operations (click, move, drag, scroll)
- Keyboard operations (type, press, combinations)
- Clipboard operations
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopInput:
    """Test Desktop input operations."""

    def test_click(self, sandbox):
        """Test clicking at position."""
        try:
            sandbox.desktop.click(100, 100)
            # Click should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_move(self, sandbox):
        """Test moving mouse cursor."""
        try:
            sandbox.desktop.move(200, 200)
            # Move should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_drag(self, sandbox):
        """Test dragging from one position to another."""
        try:
            sandbox.desktop.drag(100, 100, 200, 200)
            # Drag should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_scroll(self, sandbox):
        """Test scrolling mouse wheel."""
        try:
            sandbox.desktop.scroll(amount=3, direction="down")
            # Scroll should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_type(self, sandbox):
        """Test typing text."""
        try:
            sandbox.desktop.type("Hello World")
            # Type should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_press(self, sandbox):
        """Test pressing a key."""
        try:
            sandbox.desktop.press("Return")
            # Press should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_combination(self, sandbox):
        """Test pressing key combination."""
        try:
            sandbox.desktop.combination(["ctrl"], "c")
            # Combination should succeed without error
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_clipboard_operations(self, sandbox):
        """Test clipboard operations."""
        try:
            # Set clipboard
            sandbox.desktop.set_clipboard("Test clipboard content")
            
            # Get clipboard
            content = sandbox.desktop.get_clipboard()
            assert content == "Test clipboard content"
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

