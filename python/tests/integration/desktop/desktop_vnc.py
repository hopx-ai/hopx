"""
Integration tests for Desktop VNC operations.

Tests cover:
- Starting and stopping VNC server
- Getting VNC status and URL
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopVNC:
    """Test Desktop VNC operations."""

    def test_start_vnc(self, desktop_sandbox):
        """Test starting VNC server."""
        try:
            vnc_info = desktop_sandbox.desktop.start_vnc()
            assert vnc_info is not None
            assert hasattr(vnc_info, "url") or "url" in vnc_info
            # VNC URL should be accessible
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_vnc_status(self, desktop_sandbox):
        """Test getting VNC server status."""
        try:
            # Start VNC first
            desktop_sandbox.desktop.start_vnc()
            
            # Get status
            vnc_info = desktop_sandbox.desktop.get_vnc_status()
            assert vnc_info is not None
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_vnc_url(self, desktop_sandbox):
        """Test getting VNC connection URL."""
        try:
            # Start VNC first
            desktop_sandbox.desktop.start_vnc()
            
            # Get URL
            url = desktop_sandbox.desktop.get_vnc_url()
            assert isinstance(url, str)
            assert "vnc" in url.lower() or url.startswith("vnc://")
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_stop_vnc(self, desktop_sandbox):
        """Test stopping VNC server."""
        try:
            # Start VNC first
            desktop_sandbox.desktop.start_vnc()
            
            # Stop VNC
            desktop_sandbox.desktop.stop_vnc()
            
            # Verify it's stopped (may raise error or return None)
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

