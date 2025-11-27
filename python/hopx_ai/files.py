"""File operations resource for Hopx Sandboxes."""

from typing import List, Optional, AsyncIterator, Dict, Any
import logging
from .models import FileInfo
from ._agent_client import AgentHTTPClient

logger = logging.getLogger(__name__)


class Files:
    """
    File operations resource.

    Provides methods for reading, writing, uploading, downloading, and managing files
    inside the sandbox.

    Features:
    - Text and binary file support
    - Automatic retry with exponential backoff
    - Connection pooling for efficiency
    - Proper error handling

    Example:
        >>> sandbox = Sandbox.create(template="code-interpreter")
        >>>
        >>> # Text files
        >>> sandbox.files.write('/workspace/hello.py', 'print("Hello, World!")')
        >>> content = sandbox.files.read('/workspace/hello.py')
        >>>
        >>> # Binary files
        >>> sandbox.files.write_bytes('/workspace/image.png', image_bytes)
        >>> data = sandbox.files.read_bytes('/workspace/image.png')
        >>>
        >>> # List files
        >>> files = sandbox.files.list('/workspace')
        >>> for f in files:
        ...     print(f"{f.name}: {f.size_kb:.2f} KB")
    """

    def __init__(self, client: AgentHTTPClient, sandbox: Optional[Any] = None):
        """
        Initialize Files resource.

        Args:
            client: Shared agent HTTP client
            sandbox: Parent sandbox instance for lazy WebSocket init
        """
        self._client = client
        self._sandbox = sandbox
        logger.debug("Files resource initialized")

    def read(self, path: str, *, timeout: Optional[int] = None) -> str:
        """
        Read text file contents.

        For binary files, use read_bytes() instead.

        Args:
            path: File path (e.g., '/workspace/data.txt')
            timeout: Request timeout in seconds (overrides default)

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
            FileOperationError: If read fails

        Example:
            >>> content = sandbox.files.read('/workspace/data.txt')
            >>> print(content)
        """
        logger.debug(f"Reading text file: {path}")

        response = self._client.get(
            "/files/read",
            params={"path": path},
            operation="read file",
            context={"path": path},
            timeout=timeout,
        )

        data = response.json()
        return data.get("content", "")

    def read_bytes(self, path: str, *, timeout: Optional[int] = None) -> bytes:
        """
        Read binary file contents.

        Use this for images, PDFs, or any binary data.

        Args:
            path: File path (e.g., '/workspace/plot.png')
            timeout: Request timeout in seconds (overrides default)

        Returns:
            File contents as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            FileOperationError: If read fails

        Example:
            >>> # Read matplotlib plot
            >>> plot_data = sandbox.files.read_bytes('/workspace/plot.png')
            >>> with open('local_plot.png', 'wb') as f:
            ...     f.write(plot_data)
        """
        logger.debug(f"Reading binary file: {path}")

        response = self._client.get(
            "/files/download",
            params={"path": path},
            operation="read binary file",
            context={"path": path},
            timeout=timeout,
        )

        content = response.content

        # Handle base64-encoded files written via write_bytes()
        # The Agent API stores base64-encoded files as text, so /files/download
        # may return the base64 string as bytes instead of decoded binary data.
        # We detect and decode base64 content to ensure round-trip compatibility.
        import base64

        try:
            # Check if content is valid base64 and decode it
            decoded = base64.b64decode(content, validate=True)
            # Verify by re-encoding: if it matches, this was base64-encoded data
            if base64.b64encode(decoded) == content:
                logger.debug(f"Decoded base64 content for {path}")
                return decoded
        except Exception:
            # Not valid base64 or decode failed, return raw content
            pass

        return content

    def write(
        self, path: str, content: str, mode: str = "0644", *, timeout: Optional[int] = None
    ) -> None:
        """
        Write text file contents.

        For binary files, use write_bytes() instead.

        Args:
            path: File path (e.g., '/workspace/output.txt')
            content: File contents to write (string)
            mode: File permissions (default: '0644')
            timeout: Request timeout in seconds (overrides default)

        Raises:
            FileOperationError: If write fails

        Example:
            >>> sandbox.files.write('/workspace/hello.py', 'print("Hello!")')
            >>>
            >>> # With custom permissions
            >>> sandbox.files.write('/workspace/script.sh', '#!/bin/bash\\necho hi', mode='0755')
        """
        logger.debug(f"Writing text file: {path} ({len(content)} chars)")

        self._client.post(
            "/files/write",
            json={"path": path, "content": content, "mode": mode},
            operation="write file",
            context={"path": path},
            timeout=timeout,
        )

    def write_bytes(
        self, path: str, content: bytes, mode: str = "0644", *, timeout: Optional[int] = None
    ) -> None:
        """
        Write binary file contents.

        Use this for images, PDFs, or any binary data.

        Args:
            path: File path (e.g., '/workspace/image.png')
            content: File contents to write (bytes)
            mode: File permissions (default: '0644')
            timeout: Request timeout in seconds (overrides default)

        Raises:
            FileOperationError: If write fails

        Example:
            >>> # Save image
            >>> with open('image.png', 'rb') as f:
            ...     image_data = f.read()
            >>> sandbox.files.write_bytes('/workspace/image.png', image_data)
        """
        logger.debug(f"Writing binary file: {path} ({len(content)} bytes)")

        # Encode bytes to base64 for JSON transport
        import base64

        content_b64 = base64.b64encode(content).decode("ascii")

        self._client.post(
            "/files/write",
            json={"path": path, "content": content_b64, "mode": mode, "encoding": "base64"},
            operation="write binary file",
            context={"path": path},
            timeout=timeout,
        )

    def list(self, path: str = "/workspace", *, timeout: Optional[int] = None) -> List[FileInfo]:
        """
        List directory contents.

        Args:
            path: Directory path (default: '/workspace')
            timeout: Request timeout in seconds (overrides default)

        Returns:
            List of FileInfo objects

        Raises:
            FileNotFoundError: If directory doesn't exist
            FileOperationError: If list fails

        Example:
            >>> files = sandbox.files.list('/workspace')
            >>> for f in files:
            ...     if f.is_file:
            ...         print(f"📄 {f.name}: {f.size_kb:.2f} KB")
            ...     else:
            ...         print(f"📁 {f.name}/")
        """
        logger.debug(f"Listing directory: {path}")

        response = self._client.get(
            "/files/list",
            params={"path": path},
            operation="list directory",
            context={"path": path},
            timeout=timeout,
        )

        data = response.json()

        files = []
        for item in data.get("files", []):
            files.append(
                FileInfo(
                    name=item.get("name", ""),
                    path=item.get("path", ""),
                    size=item.get("size", 0),
                    is_directory=item.get(
                        "is_directory", item.get("is_dir", False)
                    ),  # Support both
                    permissions=item.get("permissions", item.get("mode", "")),  # Support both
                    modified_time=item.get("modified_time", item.get("modified")),  # Support both
                )
            )

        return files

    def upload(self, local_path: str, remote_path: str, *, timeout: Optional[int] = None) -> None:
        """
        Upload file from local filesystem to sandbox.

        Args:
            local_path: Path to local file
            remote_path: Destination path in sandbox
            timeout: Request timeout in seconds (overrides default, recommended: 60+)

        Raises:
            FileNotFoundError: If local file doesn't exist
            FileOperationError: If upload fails

        Example:
            >>> # Upload local file to sandbox
            >>> sandbox.files.upload('./data.csv', '/workspace/data.csv')
            >>>
            >>> # Upload with custom timeout for large file
            >>> sandbox.files.upload('./large.zip', '/workspace/large.zip', timeout=120)
        """
        logger.debug(f"Uploading file: {local_path} -> {remote_path}")

        with open(local_path, "rb") as f:
            self._client.post(
                "/files/upload",
                files={"file": f},
                data={"path": remote_path},
                operation="upload file",
                context={"path": remote_path},
                timeout=timeout or 60,  # Default 60s for uploads
            )

    def download(self, remote_path: str, local_path: str, *, timeout: Optional[int] = None) -> None:
        """
        Download file from sandbox to local filesystem.

        Args:
            remote_path: Path in sandbox
            local_path: Destination path on local filesystem
            timeout: Request timeout in seconds (overrides default, recommended: 60+)

        Raises:
            FileNotFoundError: If file doesn't exist in sandbox
            FileOperationError: If download fails

        Example:
            >>> # Download file from sandbox
            >>> sandbox.files.download('/workspace/result.csv', './result.csv')
            >>>
            >>> # Download plot
            >>> sandbox.files.download('/workspace/plot.png', './plot.png')
        """
        logger.debug(f"Downloading file: {remote_path} -> {local_path}")

        response = self._client.get(
            "/files/download",
            params={"path": remote_path},
            operation="download file",
            context={"path": remote_path},
            timeout=timeout or 60,  # Default 60s for downloads
        )

        content = response.content

        # Handle base64-encoded files written via write_bytes()
        # The Agent API stores base64-encoded files as text, so /files/download
        # may return the base64 string as bytes instead of decoded binary data.
        # We detect and decode base64 content to ensure round-trip compatibility.
        import base64

        try:
            # Check if content is valid base64 and decode it
            decoded = base64.b64decode(content, validate=True)
            # Verify by re-encoding: if it matches, this was base64-encoded data
            if base64.b64encode(decoded) == content:
                logger.debug(f"Decoded base64 content for {remote_path}")
                content = decoded
        except Exception:
            # Not valid base64 or decode failed, use raw content
            pass

        with open(local_path, "wb") as f:
            f.write(content)

    def exists(self, path: str, *, timeout: Optional[int] = None) -> bool:
        """
        Check if file or directory exists.

        Args:
            path: File or directory path
            timeout: Request timeout in seconds (overrides default)

        Returns:
            True if exists, False otherwise

        Example:
            >>> if sandbox.files.exists('/workspace/data.csv'):
            ...     print("File exists!")
            ... else:
            ...     print("File not found")
        """
        logger.debug(f"Checking if exists: {path}")

        try:
            response = self._client.get(
                "/files/exists",
                params={"path": path},
                operation="check file exists",
                context={"path": path},
                timeout=timeout or 10,
            )
            data = response.json()
            return data.get("exists", False)
        except Exception:
            return False

    def remove(self, path: str, *, timeout: Optional[int] = None) -> None:
        """
        Delete file or directory.

        Args:
            path: Path to file or directory to delete
            timeout: Request timeout in seconds (overrides default)

        Raises:
            FileNotFoundError: If file doesn't exist
            FileOperationError: If delete fails

        Example:
            >>> # Remove file
            >>> sandbox.files.remove('/workspace/temp.txt')
            >>>
            >>> # Remove directory (recursive)
            >>> sandbox.files.remove('/workspace/old_data')
        """
        logger.debug(f"Removing: {path}")

        self._client.delete(
            "/files/remove",
            params={"path": path},
            operation="remove file",
            context={"path": path},
            timeout=timeout,
        )

    def mkdir(self, path: str, *, timeout: Optional[int] = None) -> None:
        """
        Create directory.

        Args:
            path: Directory path to create
            timeout: Request timeout in seconds (overrides default)

        Raises:
            FileOperationError: If mkdir fails

        Example:
            >>> # Create directory
            >>> sandbox.files.mkdir('/workspace/data')
            >>>
            >>> # Create nested directories
            >>> sandbox.files.mkdir('/workspace/project/src')
        """
        logger.debug(f"Creating directory: {path}")

        self._client.post(
            "/files/mkdir",
            json={"path": path},
            operation="create directory",
            context={"path": path},
            timeout=timeout,
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
            ...     sandbox = Sandbox.create(template="code-interpreter")
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
            self._sandbox._ensure_ws_client()
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

    def __repr__(self) -> str:
        return f"<Files client={self._client}>"
