"""Async cache operations for sandboxes."""

from typing import Dict, Any
import logging
from ._async_agent_client import AsyncAgentHTTPClient

logger = logging.getLogger(__name__)


class AsyncCache:
    """Async cache operations."""

    def __init__(self, sandbox):
        """Initialize with sandbox reference."""
        self._sandbox = sandbox
        logger.debug("AsyncCache initialized")

    async def _get_client(self) -> AsyncAgentHTTPClient:
        """Get agent client from sandbox."""
        await self._sandbox._ensure_agent_client()
        return self._sandbox._agent_client

    async def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        client = await self._get_client()
        response = await client.get("/cache/stats", operation="get cache stats")
        return response

    async def clear(self) -> None:
        """Clear cache."""
        client = await self._get_client()
        await client.post("/cache/clear", operation="clear cache")
