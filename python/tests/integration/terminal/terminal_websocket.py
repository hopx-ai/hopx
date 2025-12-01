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
        async with await sandbox.terminal.connect() as ws:
            assert ws is not None
            # Connection should be established

    @pytest.mark.asyncio
    async def test_send_input(self, sandbox):
        """Test sending input to terminal."""
        async with await sandbox.terminal.connect() as ws:
            # Send command (following CLI pattern)
            await sandbox.terminal.send_input(ws, "echo 'Hello Terminal'\n")
            
            # Give the command time to start executing (like CLI does)
            await asyncio.sleep(0.1)
            
            # Send exit to close the shell after command completes (like CLI does)
            await sandbox.terminal.send_input(ws, "exit\n")
            
            # Check for output with timeout
            messages = []
            output_received = False
            
            async def read_messages():
                """Read messages from terminal output."""
                nonlocal output_received
                async for message in sandbox.terminal.iter_output(ws):
                    # Verify message structure
                    assert "type" in message, "Message should have 'type' field"
                    
                    if message.get("type") == "output":
                        assert "data" in message, "Output message should have 'data' field"
                        data = message.get("data", "")
                        messages.append(data)
                        if "Hello Terminal" in data:
                            output_received = True
                    elif message.get("type") == "exit":
                        return  # Break immediately on exit (like CLI does)
                    
                    # Safety limit to prevent infinite loop
                    if len(messages) > 100:
                        return
            
            # Wrap in timeout (like CLI does - 30 seconds)
            try:
                await asyncio.wait_for(read_messages(), timeout=30)
            except TimeoutError:
                # Handle timeout gracefully
                pass
            
            # Verify output was received
            assert output_received is True, "Expected output 'Hello Terminal' was not received"
            assert len(messages) > 0, "Should have received at least one output message"

    @pytest.mark.asyncio
    async def test_resize_terminal(self, sandbox):
        """Test resizing terminal window."""
        async with await sandbox.terminal.connect() as ws:
            # Resize terminal
            # This should succeed without raising an exception
            try:
                await sandbox.terminal.resize(ws, cols=120, rows=40)
                resize_successful = True
            except Exception as e:
                resize_successful = False
                raise AssertionError(f"Terminal resize failed: {e}")
            
            # Verify resize succeeded
            assert resize_successful is True, "Terminal resize should succeed without error"
            
            # Verify connection is still active after resize
            # Send a simple command to verify terminal is still responsive
            await sandbox.terminal.send_input(ws, "echo 'resize_test'\n")
            
            # Give the command time to start executing (like CLI does)
            await asyncio.sleep(0.1)
            
            # Send exit to close the shell after command completes (like CLI does)
            await sandbox.terminal.send_input(ws, "exit\n")
            
            # Check that terminal is still responsive with timeout
            messages = []
            
            async def read_messages():
                """Read messages from terminal output."""
                async for message in sandbox.terminal.iter_output(ws):
                    messages.append(message)
                    if message.get("type") == "exit":
                        return  # Break immediately on exit (like CLI does)
                    # Safety limit
                    if len(messages) > 100:
                        return
            
            # Wrap in timeout (like CLI does - 30 seconds)
            try:
                await asyncio.wait_for(read_messages(), timeout=30)
            except TimeoutError:
                # Handle timeout gracefully
                pass
            
            # Terminal should still be responsive after resize
            assert len(messages) > 0, "Terminal should be responsive after resize"

    @pytest.mark.asyncio
    async def test_iter_output(self, sandbox):
        """Test iterating over terminal output."""
        async with await sandbox.terminal.connect() as ws:
            # Send command (following CLI pattern)
            await sandbox.terminal.send_input(ws, "pwd\n")
            
            # Give the command time to start executing (like CLI does)
            await asyncio.sleep(0.1)
            
            # Send exit to close the shell after command completes (like CLI does)
            await sandbox.terminal.send_input(ws, "exit\n")
            
            # Iterate over output with timeout
            messages = []
            output_messages = []
            
            async def read_messages():
                """Read messages from terminal output."""
                async for message in sandbox.terminal.iter_output(ws):
                    # Verify message structure
                    assert "type" in message, "Message should have 'type' field"
                    assert isinstance(message.get("type"), str), "Message type should be a string"
                    
                    messages.append(message)
                    
                    if message.get("type") == "output":
                        assert "data" in message, "Output message should have 'data' field"
                        output_messages.append(message.get("data", ""))
                    elif message.get("type") == "exit":
                        assert "code" in message, "Exit message should have 'code' field"
                        assert isinstance(message.get("code"), int), "Exit code should be an integer"
                        return  # Break immediately on exit (like CLI does)
                    
                    # Safety limit to prevent infinite loop
                    if len(messages) > 100:
                        return
            
            # Wrap in timeout (like CLI does - 30 seconds)
            try:
                await asyncio.wait_for(read_messages(), timeout=30)
            except TimeoutError:
                # Handle timeout gracefully
                pass
            
            # Should have received some messages
            assert len(messages) > 0, "Should have received at least one message"
            
            # Verify we got output messages
            assert len(output_messages) > 0, "Should have received at least one output message"
            
            # Verify output content (pwd should show workspace or similar)
            output_text = "".join(output_messages)
            assert len(output_text) > 0, "Output text should not be empty"
            # pwd typically shows /workspace or similar path
            assert "/" in output_text or len(output_text.strip()) > 0, "pwd output should contain a path or some content"

