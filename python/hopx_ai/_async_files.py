"""Async file operations for sandboxes."""

from typing import Optional, List, Dict, Any, AsyncIterator
import logging
from ._async_agent_client import AsyncAgentHTTPClient

logger = logging.getLogger(__name__)


class AsyncFiles:
    """Async file operations for sandboxes."""
    
    def __init__(self, sandbox):
        """Initialize with sandbox reference."""
        self._sandbox = sandbox
        logger.debug("AsyncFiles initialized")
    
    async def _get_client(self) -> AsyncAgentHTTPClient:
        """Get agent client from sandbox."""
        await self._sandbox._ensure_agent_client()
        return self._sandbox._agent_client
    
    async def write(self, path: str, content: str) -> None:
        """Write content to file."""
        client = await self._get_client()
        await client.post(
            "/files/write",
            json={"path": path, "content": content},
            operation="write file",
            context={"path": path}
        )
    
    async def read(self, path: str) -> str:
        """Read file content."""
        client = await self._get_client()
        response = await client.get(
            f"/files/read?path={path}",
            operation="read file",
            context={"path": path}
        )
        return response.get("content", "")
    
    async def list(self, path: str = "/") -> List[Dict[str, Any]]:
        """List files in directory."""
        client = await self._get_client()
        response = await client.get(
            f"/files/list?path={path}",
            operation="list files",
            context={"path": path}
        )
        return response.get("files", [])
    
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        client = await self._get_client()
        response = await client.get(
            f"/files/exists?path={path}",
            operation="check file exists",
            context={"path": path}
        )
        return response.get("exists", False)
    
    async def mkdir(self, path: str, parents: bool = True) -> None:
        """Create directory."""
        client = await self._get_client()
        await client.post(
            "/files/mkdir",
            json={"path": path, "parents": parents},
            operation="create directory",
            context={"path": path}
        )
    
    async def remove(self, path: str, recursive: bool = False) -> None:
        """Remove file or directory."""
        client = await self._get_client()
        await client.post(
            "/files/remove",
            json={"path": path, "recursive": recursive},
            operation="remove file",
            context={"path": path}
        )
