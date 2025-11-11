"""Interactive terminal access via WebSocket."""

import logging
from typing import Optional, AsyncIterator, Dict, Any

try:
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketClientProtocol = Any  # type: ignore

from ._ws_client import WebSocketClient

logger = logging.getLogger(__name__)


class Terminal:
    """
    Interactive terminal resource with PTY support via WebSocket.
    
    Provides real-time terminal access to the sandbox for interactive commands.
    
    Features:
    - Full PTY support
    - Real-time output streaming
    - Terminal resize support
    - Process exit notifications
    
    Example:
        >>> import asyncio
        >>> 
        >>> async def interactive_terminal():
        ...     sandbox = Sandbox.create(template="code-interpreter")
        ...     
        ...     # Connect to terminal
        ...     async with await sandbox.terminal.connect() as ws:
        ...         # Send command
        ...         await sandbox.terminal.send_input(ws, "ls -la\\n")
        ...         
        ...         # Receive output
        ...         async for message in sandbox.terminal.iter_output(ws):
        ...             if message['type'] == 'output':
        ...                 print(message['data'], end='')
        ...             elif message['type'] == 'exit':
        ...                 print(f"\\nProcess exited: {message['code']}")
        ...                 break
        >>> 
        >>> asyncio.run(interactive_terminal())
    """
    
    def __init__(self, ws_client: WebSocketClient):
        """
        Initialize Terminal resource.
        
        Args:
            ws_client: WebSocket client
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets library is required for terminal features. "
                "Install with: pip install websockets"
            )
        
        self._ws_client = ws_client
        logger.debug("Terminal resource initialized")
    
    async def connect(
        self,
        *,
        timeout: Optional[int] = 30
    ) -> WebSocketClientProtocol:
        """
        Connect to interactive terminal.
        
        Args:
            timeout: Connection timeout in seconds
        
        Returns:
            WebSocket connection (use with async context manager)
        
        Example:
            >>> async with await sandbox.terminal.connect() as ws:
            ...     await sandbox.terminal.send_input(ws, "echo 'Hello'\\n")
            ...     async for msg in sandbox.terminal.iter_output(ws):
            ...         print(msg['data'], end='')
            ...         if msg['type'] == 'exit':
            ...             break
        """
        return await self._ws_client.connect("/terminal", timeout=timeout)
    
    async def send_input(
        self,
        ws: WebSocketClientProtocol,
        data: str
    ) -> None:
        """
        Send input to terminal.
        
        Args:
            ws: WebSocket connection
            data: Input data (include \\n for commands)
        
        Example:
            >>> await terminal.send_input(ws, "ls -la\\n")
            >>> await terminal.send_input(ws, "cd /workspace\\n")
        """
        await self._ws_client.send_message(ws, {
            "type": "input",
            "data": data
        })
    
    async def resize(
        self,
        ws: WebSocketClientProtocol,
        cols: int,
        rows: int
    ) -> None:
        """
        Resize terminal window.
        
        Args:
            ws: WebSocket connection
            cols: Number of columns
            rows: Number of rows
        
        Example:
            >>> await terminal.resize(ws, cols=120, rows=40)
        """
        await self._ws_client.send_message(ws, {
            "type": "resize",
            "cols": cols,
            "rows": rows
        })
    
    async def iter_output(
        self,
        ws: WebSocketClientProtocol
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate over terminal output messages.
        
        Args:
            ws: WebSocket connection
        
        Yields:
            Message dictionaries:
            - {"type": "output", "data": "..."}
            - {"type": "exit", "code": 0}
        
        Example:
            >>> async for message in terminal.iter_output(ws):
            ...     if message['type'] == 'output':
            ...         print(message['data'], end='')
            ...     elif message['type'] == 'exit':
            ...         print(f"Exit code: {message['code']}")
            ...         break
        """
        async for message in self._ws_client.iter_messages(ws):
            yield message
    
    def __repr__(self) -> str:
        return f"<Terminal ws_client={self._ws_client}>"

