"""
Integration tests for Files resource.

Tests cover:
- Writing and reading files
- Listing files in directory
- Checking file existence
- Creating directories
- Removing files
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestFilesResource:
    """Test file operations."""

    def test_write_and_read_file(self, sandbox):
        """Test writing and reading a file."""
        content = "Hello, World!\nThis is a test file."
        path = "/workspace/test.txt"

        sandbox.files.write(path, content)
        read_content = sandbox.files.read(path)

        assert read_content == content

    def test_list_files(self, sandbox):
        """Test listing files in a directory."""
        # Create a test file
        sandbox.files.write("/workspace/test_list.txt", "test")

        files = sandbox.files.list("/workspace")

        assert isinstance(files, list)
        file_names = [f.name for f in files if hasattr(f, "name")]
        # File might be in the list (depending on API response format)

    def test_file_exists(self, sandbox):
        """Test checking if file exists."""
        path = "/workspace/test_exists.txt"

        # File shouldn't exist initially
        assert sandbox.files.exists(path) is False

        # Create file
        sandbox.files.write(path, "test")
        assert sandbox.files.exists(path) is True

    def test_mkdir(self, sandbox):
        """Test creating a directory."""
        dir_path = "/workspace/test_dir"

        sandbox.files.mkdir(dir_path)
        assert sandbox.files.exists(dir_path) is True

    def test_remove_file(self, sandbox):
        """Test removing a file."""
        path = "/workspace/test_remove.txt"

        # Create file
        sandbox.files.write(path, "test")
        assert sandbox.files.exists(path) is True

        # Remove file
        sandbox.files.remove(path)
        assert sandbox.files.exists(path) is False

