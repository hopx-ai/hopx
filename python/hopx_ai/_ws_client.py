"""WebSocket client for real-time streaming."""

import json
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncIterator
from urllib.parse import urlparse

try:
    import websockets
    from websockets.asyncio.client import connect, ClientConnection

    WEBSOCKETS_AVAILABLE = True
    # Use new asyncio API type (websockets 11.0+)
    WebSocketClientProtocol = ClientConnection
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketClientProtocol = Any  # type: ignore
    connect = None  # type: ignore

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    WebSocket client for Agent API streaming.

    Handles WebSocket connections with automatic reconnection,
    message protocol, and async iteration.
    """

    def __init__(
        self,
        agent_url: str,
        jwt_token: Optional[str] = None,
    ):
        """
        Initialize WebSocket client.

        Args:
            agent_url: Agent base URL (https://...)
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets library is required for WebSocket features. "
                "Install with: pip install websockets"
            )

        self.agent_url = agent_url.rstrip("/")
        self._jwt_token = jwt_token
        # Convert https:// to wss:// for WebSocket
        parsed = urlparse(self.agent_url)
        ws_scheme = "wss" if parsed.scheme == "https" else "ws"
        self.ws_base_url = f"{ws_scheme}://{parsed.netloc}"

        logger.debug(f"WebSocket client initialized: {self.ws_base_url}")

    def update_jwt_token(self, token: str) -> None:
        """
        Update JWT token for agent authentication.
        Used internally when token is refreshed.
        """
        self._jwt_token = token

    async def connect(
        self, endpoint: str, *, timeout: Optional[int] = None
    ) -> WebSocketClientProtocol:
        """
        Connect to WebSocket endpoint.

        Args:
            endpoint: WebSocket endpoint path (e.g., "/terminal")
            timeout: Connection timeout in seconds

        Returns:
            WebSocket connection
        """
        url = f"{self.ws_base_url}{endpoint}"
        logger.debug(f"Connecting to WebSocket: {url}")
        additional_headers = None
        if self._jwt_token:
            additional_headers = {"Authorization": f"Bearer {self._jwt_token}"}

        try:
            ws = await asyncio.wait_for(
                connect(
                    url,
                    additional_headers=additional_headers,
                ),
                timeout=timeout,
            )
            logger.debug(f"WebSocket connected: {endpoint}")
            return ws
        except asyncio.TimeoutError as e:
            from .errors import TimeoutError as HopxTimeoutError

            raise HopxTimeoutError(f"WebSocket connection timeout: {endpoint}") from e
        except Exception as e:
            from .errors import AgentError

            logger.error(f"WebSocket connection failed: {e}")
            raise AgentError(f"WebSocket connection failed: {e}") from e

    async def send_message(self, ws: WebSocketClientProtocol, message: Dict[str, Any]) -> None:
        """
        Send JSON message over WebSocket.

        Args:
            ws: WebSocket connection
            message: Message dictionary
        """
        await ws.send(json.dumps(message))
        logger.debug(f"Sent WS message: {message.get('type', 'unknown')}")

    async def receive_message(self, ws: WebSocketClientProtocol) -> Dict[str, Any]:
        """
        Receive and parse JSON message from WebSocket.

        Args:
            ws: WebSocket connection

        Returns:
            Parsed message dictionary
        """
        data = await ws.recv()
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        message = json.loads(data)
        logger.debug(f"Received WS message: {message.get('type', 'unknown')}")
        return message

    async def iter_messages(self, ws: WebSocketClientProtocol) -> AsyncIterator[Dict[str, Any]]:
        """
        Iterate over incoming messages.

        Args:
            ws: WebSocket connection

        Yields:
            Parsed message dictionaries

        Note:
            Empty messages and invalid JSON are skipped with a warning.
            This handles edge cases where the server sends keepalive pings
            or malformed data.
        """
        try:
            async for data in ws:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                # Skip empty messages
                if not data or not data.strip():
                    logger.debug("Skipping empty WebSocket message")
                    continue
                try:
                    message = json.loads(data)
                    logger.debug(f"Yielding WS message: {message.get('type', 'unknown')}")
                    yield message
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON in WebSocket message: {data[:100]}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            logger.debug("WebSocket connection closed")

    def __repr__(self) -> str:
        return f"<WebSocketClient url={self.ws_base_url}>"
