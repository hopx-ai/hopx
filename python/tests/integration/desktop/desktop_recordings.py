"""
Integration tests for Desktop recording operations.

Tests cover:
- Starting and stopping screen recordings
- Getting recording status
- Downloading recordings
"""

import os
import pytest
import time
from hopx_ai import Sandbox
from hopx_ai.errors import DesktopNotAvailableError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
# Use desktop-enabled template (ID: 399) by default
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", "399")


class TestDesktopRecordings:
    """Test Desktop recording operations."""

    def test_start_recording(self, sandbox):
        """Test starting screen recording."""
        try:
            recording_info = sandbox.desktop.start_recording(fps=10, format="mp4")
            assert recording_info is not None
            recording_id = recording_info.recording_id if hasattr(recording_info, "recording_id") else recording_info.get("recording_id")
            assert recording_id is not None
            
            # Stop recording
            time.sleep(1)  # Record for a moment
            sandbox.desktop.stop_recording(recording_id)
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_get_recording_status(self, sandbox):
        """Test getting recording status."""
        try:
            # Start recording
            recording_info = sandbox.desktop.start_recording()
            recording_id = recording_info.recording_id if hasattr(recording_info, "recording_id") else recording_info.get("recording_id")
            
            # Get status
            status = sandbox.desktop.get_recording_status(recording_id)
            assert status is not None
            
            # Stop recording
            sandbox.desktop.stop_recording(recording_id)
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

    def test_download_recording(self, sandbox):
        """Test downloading recorded video."""
        try:
            # Start recording
            recording_info = sandbox.desktop.start_recording()
            recording_id = recording_info.recording_id if hasattr(recording_info, "recording_id") else recording_info.get("recording_id")
            
            time.sleep(2)  # Record for a moment
            
            # Stop recording
            sandbox.desktop.stop_recording(recording_id)
            
            # Wait a bit for recording to finalize
            time.sleep(2)
            
            # Download recording
            video_bytes = sandbox.desktop.download_recording(recording_id)
            assert isinstance(video_bytes, bytes)
            assert len(video_bytes) > 0
        except DesktopNotAvailableError:
            pytest.skip("Desktop not available in this template")

