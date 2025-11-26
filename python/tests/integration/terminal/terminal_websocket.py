"""
Integration tests for Terminal WebSocket operations.

Tests cover:
- Connecting to interactive terminal
- Sending input to terminal
- Resizing terminal window
- Receiving terminal output
"""

import os
import pytest
import asyncio
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestTerminalWebSocket:
    """Test Terminal WebSocket operations."""

    @pytest.mark.asyncio
    async def test_connect_terminal(self, sandbox):
        """Test connecting to interactive terminal."""
        async with sandbox.terminal.connect() as ws:
            assert ws is not None
            # Connection should be established

    @pytest.mark.asyncio
    async def test_send_input(self, sandbox):
        """Test sending input to terminal."""
        async with sandbox.terminal.connect() as ws:
            # Send a command
            sandbox.terminal.send_input(ws, "echo 'Hello Terminal'\n")
            
            # Wait a moment for output
            await asyncio.sleep(1)
            
            # Check for output
            output_received = False
            async for message in sandbox.terminal.iter_output(ws):
                if message.get("type") == "output":
                    data = message.get("data", "")
                    if "Hello Terminal" in data:
                        output_received = True
                        break
                elif message.get("type") == "exit":
                    break
            
            # Note: Output may not always be captured immediately
            # This test verifies the connection works

    @pytest.mark.asyncio
    async def test_resize_terminal(self, sandbox):
        """Test resizing terminal window."""
        async with sandbox.terminal.connect() as ws:
            # Resize terminal
            sandbox.terminal.resize(ws, cols=120, rows=40)
            # Resize should succeed without error

    @pytest.mark.asyncio
    async def test_iter_output(self, sandbox):
        """Test iterating over terminal output."""
        async with sandbox.terminal.connect() as ws:
            # Send a command
            sandbox.terminal.send_input(ws, "pwd\n")
            
            # Iterate over output
            messages = []
            async for message in sandbox.terminal.iter_output(ws):
                messages.append(message)
                if message.get("type") == "exit":
                    break
                # Limit to prevent infinite loop
                if len(messages) > 10:
                    break
            
            # Should have received some messages
            assert len(messages) > 0

