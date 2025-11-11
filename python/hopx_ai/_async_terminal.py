"""Async interactive terminal access via WebSocket."""

import logging
from typing import Optional, AsyncIterator, Dict, Any

try:
    from websockets.client import WebSocketClientProtocol
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketClientProtocol = Any  # type: ignore

logger = logging.getLogger(__name__)


class AsyncTerminal:
    """
    Async interactive terminal resource with PTY support via WebSocket.
    
    Provides real-time terminal access to the sandbox for interactive commands.
    
    Features:
    - Full PTY support
    - Real-time output streaming
    - Terminal resize support
    - Process exit notifications
    
    Example:
        >>> async def interactive_terminal():
        ...     sandbox = await AsyncSandbox.create(template="code-interpreter")
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
    """
    
    def __init__(self, sandbox):
        """
        Initialize AsyncTerminal resource.
        
        Args:
            sandbox: Parent AsyncSandbox instance
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets library is required for terminal features. "
                "Install with: pip install websockets"
            )
        
        self._sandbox = sandbox
        self._ws_url = None
        logger.debug("AsyncTerminal resource initialized")
    
    async def _get_ws_url(self) -> str:
        """Get WebSocket URL from sandbox."""
        if self._ws_url is None:
            info = await self._sandbox.get_info()
            agent_url = info.public_host.rstrip('/')
            # Convert https:// to wss://
            self._ws_url = agent_url.replace('https://', 'wss://').replace('http://', 'ws://')
        return self._ws_url
    
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
        ws_url = await self._get_ws_url()
        
        # Connect to WebSocket (no auth needed - agent handles it)
        ws = await websockets.connect(
            f"{ws_url}/terminal",
            open_timeout=timeout
        )
        
        return ws
    
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
        import json
        await ws.send(json.dumps({
            "type": "input",
            "data": data
        }))
    
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
        import json
        await ws.send(json.dumps({
            "type": "resize",
            "cols": cols,
            "rows": rows
        }))
    
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
        import json
        async for message in ws:
            try:
                data = json.loads(message)
                yield data
            except json.JSONDecodeError:
                # Skip invalid messages
                continue
    
    def __repr__(self) -> str:
        return f"<AsyncTerminal sandbox={self._sandbox.sandbox_id}>"
