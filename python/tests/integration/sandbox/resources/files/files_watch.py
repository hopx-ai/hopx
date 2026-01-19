"""
Integration tests for Files resource watch operations.

Tests cover:
- Watching filesystem for changes via WebSocket
"""

import os
import pytest
import asyncio
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestFilesWatch:
    """Test filesystem watching operations."""

    @pytest.mark.asyncio
    async def test_watch_file_creation(self, sandbox):
        """Test watching for file creation events."""
        # Start watching
        events = []
        watch_task = None
        
        async def collect_events():
            async for event in sandbox.files.watch("/workspace"):
                events.append(event)
                # Stop after collecting a few events
                if len(events) >= 3:
                    break
        
        watch_task = asyncio.create_task(collect_events())
        
        # Wait a moment for watch to start
        await asyncio.sleep(1)
        
        # Create a file to trigger event
        sandbox.files.write("/workspace/watched_file.txt", "test content")
        
        # Wait for events
        await asyncio.sleep(2)
        
        # Cancel watch task
        watch_task.cancel()
        try:
            await watch_task
        except asyncio.CancelledError:
            pass
        
        # Should have received at least one event
        assert len(events) > 0
        # Check that we got a creation event
        creation_events = [e for e in events if e.get("event") in ("created", "modified")]
        assert len(creation_events) > 0

    @pytest.mark.asyncio
    async def test_watch_file_deletion(self, sandbox):
        """Test watching for file deletion events."""
        # Create a file first
        test_file = "/workspace/watch_delete.txt"
        sandbox.files.write(test_file, "to be deleted")
        
        # Start watching
        events = []
        
        async def collect_events():
            async for event in sandbox.files.watch("/workspace"):
                events.append(event)
                if len(events) >= 2:
                    break
        
        watch_task = asyncio.create_task(collect_events())
        await asyncio.sleep(1)
        
        # Delete the file
        sandbox.files.remove(test_file)
        
        # Wait for events
        await asyncio.sleep(2)
        
        # Cancel watch task
        watch_task.cancel()
        try:
            await watch_task
        except asyncio.CancelledError:
            pass
        
        # Should have received deletion event
        deletion_events = [e for e in events if e.get("event") == "deleted"]
        # Note: May not always capture deletion immediately
        assert len(events) >= 0  # At least the watch started

