"""Async file operations for sandboxes."""

import base64
from typing import Optional, List, Dict, Any, AsyncIterator
import logging
from ._async_agent_client import AsyncAgentHTTPClient
from .models import FileInfo

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

    async def write(self, path: str, content: str, mode: str = "0644") -> None:
        """
        Write text content to file.

        For binary files, use write_bytes() instead.

        Args:
            path: File path
            content: File contents (string)
            mode: File permissions (default: '0644')
        """
        client = await self._get_client()
        await client.post(
            "/files/write",
            json={"path": path, "content": content, "mode": mode},
            operation="write file",
            context={"path": path},
        )

    async def write_bytes(self, path: str, content: bytes, mode: str = "0644") -> None:
        """
        Write binary content to file.

        Use this for images, PDFs, or any binary data.

        Args:
            path: File path
            content: File contents (bytes)
            mode: File permissions (default: '0644')
        """
        client = await self._get_client()
        content_b64 = base64.b64encode(content).decode("ascii")
        await client.post(
            "/files/write",
            json={"path": path, "content": content_b64, "mode": mode, "encoding": "base64"},
            operation="write binary file",
            context={"path": path},
        )

    async def read(self, path: str) -> str:
        """
        Read text file content.

        For binary files, use read_bytes() instead.

        Args:
            path: File path

        Returns:
            File contents as string
        """
        client = await self._get_client()
        response = await client.get(
            f"/files/read?path={path}", operation="read file", context={"path": path}
        )
        return response.get("content", "")

    async def read_bytes(self, path: str) -> bytes:
        """
        Read binary file content.

        Use this for images, PDFs, or any binary data.

        Args:
            path: File path

        Returns:
            File contents as bytes
        """
        client = await self._get_client()
        return await client.get_raw(
            f"/files/download?path={path}", operation="read binary file", context={"path": path}
        )

    async def list(self, path: str = "/workspace") -> List[FileInfo]:
        """
        List directory contents.

        Args:
            path: Directory path (default: '/workspace')

        Returns:
            List of FileInfo objects
        """
        client = await self._get_client()
        response = await client.get(
            f"/files/list?path={path}", operation="list files", context={"path": path}
        )

        files = []
        for item in response.get("files", []):
            files.append(
                FileInfo(
                    name=item.get("name", ""),
                    path=item.get("path", ""),
                    size=item.get("size", 0),
                    is_directory=item.get("is_directory", item.get("is_dir", False)),
                    permissions=item.get("permissions", item.get("mode", "")),
                    modified_time=item.get("modified_time", item.get("modified")),
                )
            )
        return files

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        client = await self._get_client()
        response = await client.get(
            f"/files/exists?path={path}", operation="check file exists", context={"path": path}
        )
        return response.get("exists", False)

    async def mkdir(self, path: str) -> None:
        """
        Create directory.

        Note: Directories are created with parents automatically (similar to mkdir -p).

        Args:
            path: Directory path to create
        """
        client = await self._get_client()
        await client.post(
            "/files/mkdir",
            json={"path": path},
            operation="create directory",
            context={"path": path},
        )

    async def remove(self, path: str) -> None:
        """
        Remove file or directory.

        Directories are removed recursively automatically.

        Args:
            path: File or directory path to remove
        """
        client = await self._get_client()
        await client.delete(
            "/files/remove",
            params={"path": path},
            operation="remove file",
            context={"path": path},
        )

    async def watch(
        self, path: str = "/workspace", *, timeout: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Watch filesystem for changes via WebSocket.

        Stream file system events (create, modify, delete, rename) in real-time.

        Args:
            path: Path to watch (default: /workspace)
            timeout: Connection timeout in seconds

        Yields:
            Change event dictionaries:
            - {"type": "change", "path": "...", "event": "created", "timestamp": "..."}
            - {"type": "change", "path": "...", "event": "modified", "timestamp": "..."}
            - {"type": "change", "path": "...", "event": "deleted", "timestamp": "..."}
            - {"type": "change", "path": "...", "event": "renamed", "timestamp": "..."}

        Note:
            Requires websockets library: pip install websockets

        Example:
            >>> import asyncio
            >>>
            >>> async def watch_files():
            ...     sandbox = await AsyncSandbox.create(template="code-interpreter")
            ...
            ...     # Start watching
            ...     async for event in sandbox.files.watch("/workspace"):
            ...         print(f"{event['event']}: {event['path']}")
            ...
            ...         # Stop after 10 events
            ...         if event_count >= 10:
            ...             break
            >>>
            >>> asyncio.run(watch_files())
        """
        # Lazy-load WebSocket client from sandbox if needed
        if self._sandbox is not None:
            await self._sandbox._ensure_ws_client()
            ws_client = self._sandbox._ws_client
        else:
            raise RuntimeError(
                "WebSocket client not available. "
                "File watching requires websockets library: pip install websockets"
            )

        # Connect to file watcher endpoint
        async with await ws_client.connect("/files/watch", timeout=timeout) as ws:
            # Send watch request
            await ws_client.send_message(ws, {"action": "watch", "path": path})

            # Stream change events
            async for message in ws_client.iter_messages(ws):
                yield message
