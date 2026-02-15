"""
Integration tests for AsyncSandbox Files resource.

Tests cover:
- Writing and reading files (async)
- Listing files (async)
- File existence checks (async)
- Creating directories (async)
- Removing files (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncFilesResource:
    """Test async file operations."""

    @pytest.mark.asyncio
    async def test_write_and_read_file(self, async_sandbox):
        """Test writing and reading a file."""
        content = "Hello, World!\nThis is a test file."
        path = "/workspace/test.txt"

        await async_sandbox.files.write(path, content)
        read_content = await async_sandbox.files.read(path)

        assert read_content == content

    @pytest.mark.asyncio
    async def test_list_files(self, async_sandbox):
        """Test listing files in a directory."""
        # Create a test file
        await async_sandbox.files.write("/workspace/test_list.txt", "test")

        files = await async_sandbox.files.list("/workspace")

        assert isinstance(files, list)

    @pytest.mark.asyncio
    async def test_file_exists(self, async_sandbox):
        """Test checking if file exists."""
        path = "/workspace/test_exists.txt"

        # File shouldn't exist initially
        assert await async_sandbox.files.exists(path) is False

        # Create file
        await async_sandbox.files.write(path, "test")
        assert await async_sandbox.files.exists(path) is True

    @pytest.mark.asyncio
    async def test_mkdir(self, async_sandbox):
        """Test creating a directory."""
        dir_path = "/workspace/test_dir"

        await async_sandbox.files.mkdir(dir_path)
        assert await async_sandbox.files.exists(dir_path) is True

    @pytest.mark.asyncio
    async def test_remove_file(self, async_sandbox):
        """Test removing a file."""
        path = "/workspace/test_remove.txt"

        # Create file
        await async_sandbox.files.write(path, "test")
        assert await async_sandbox.files.exists(path) is True

        # Remove file
        await async_sandbox.files.remove(path)
        assert await async_sandbox.files.exists(path) is False

