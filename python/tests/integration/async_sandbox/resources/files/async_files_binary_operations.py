"""
Integration tests for AsyncSandbox Files resource binary operations.

Tests cover:
- Reading binary files (async)
- Writing binary files (async)
"""

import os
import pytest
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncFilesBinaryOperations:
    """Test async binary file operations."""

    @pytest.mark.asyncio
    async def test_read_bytes(self, async_sandbox):
        """Test reading binary file contents."""
        # Create a binary file first using code execution
        await async_sandbox.run_code(
            """
with open('/workspace/test.bin', 'wb') as f:
    f.write(b'\\x00\\x01\\x02\\x03\\xFF\\xFE\\xFD')
"""
        )

        # Read binary file
        content = await async_sandbox.files.read_bytes("/workspace/test.bin")
        assert isinstance(content, bytes)
        assert content == b'\x00\x01\x02\x03\xFF\xFE\xFD'

    @pytest.mark.asyncio
    async def test_write_bytes(self, async_sandbox):
        """Test writing binary file contents."""
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD\xAA\xBB\xCC'
        path = "/workspace/test_write.bin"

        await async_sandbox.files.write_bytes(path, binary_data)
        
        # Verify by reading back
        read_content = await async_sandbox.files.read_bytes(path)
        assert read_content == binary_data

