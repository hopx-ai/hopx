"""
Integration tests for Files resource binary operations.

Tests cover:
- Reading binary files (read_bytes)
- Writing binary files (write_bytes)
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestFilesBinaryOperations:
    """Test binary file operations."""

    def test_read_bytes(self, sandbox):
        """Test reading binary file contents."""
        # Create a binary file first using code execution
        sandbox.run_code(
            """
with open('/workspace/test.bin', 'wb') as f:
    f.write(b'\\x00\\x01\\x02\\x03\\xFF\\xFE\\xFD')
"""
        )

        # Read binary file
        content = sandbox.files.read_bytes("/workspace/test.bin")
        assert isinstance(content, bytes)
        assert content == b'\x00\x01\x02\x03\xFF\xFE\xFD'

    def test_write_bytes(self, sandbox):
        """Test writing binary file contents."""
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD\xAA\xBB\xCC'
        path = "/workspace/test_write.bin"

        sandbox.files.write_bytes(path, binary_data)
        
        # Verify by reading back
        read_content = sandbox.files.read_bytes(path)
        assert read_content == binary_data

    def test_write_bytes_png_image(self, sandbox):
        """Test writing PNG image file."""
        # Create a minimal valid PNG file (1x1 pixel)
        # PNG signature + minimal IHDR chunk
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR'  # IHDR chunk header
            b'\x00\x00\x00\x01'  # Width: 1
            b'\x00\x00\x00\x01'  # Height: 1
            b'\x08\x02\x00\x00\x00'  # Bit depth, color type, etc.
            b'\x90wS\xde'  # CRC
            b'\x00\x00\x00\nIDAT'  # IDAT chunk header
            b'x\x9cc\x00\x00\x00\x02\x00\x01'  # Compressed data
            b'\xcd\xb3V\xd7'  # CRC
            b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND
        )

        path = "/workspace/test_image.png"
        sandbox.files.write_bytes(path, png_data)
        
        # Verify it's a valid PNG by checking signature
        read_content = sandbox.files.read_bytes(path)
        assert read_content[:8] == b'\x89PNG\r\n\x1a\n'

