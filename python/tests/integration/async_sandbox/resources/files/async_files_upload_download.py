"""
Integration tests for AsyncSandbox Files resource upload/download operations.

Tests cover:
- Uploading files from local filesystem to async_sandbox (async)
- Downloading files from async_sandbox to local filesystem (async)
"""

import os
import pytest
import tempfile
from hopx_ai import AsyncSandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAsyncFilesUploadDownload:
    """Test async file upload and download operations."""

    @pytest.mark.asyncio
    async def test_upload_text_file(self, async_sandbox):
        """Test uploading a text file from local filesystem."""
        # Create a temporary local file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            local_path = f.name
            f.write("Hello from local file!\nThis is a test upload.")
        
        try:
            # Upload to async_sandbox
            remote_path = "/workspace/uploaded_file.txt"
            await async_sandbox.files.upload(local_path, remote_path)
            
            # Verify file was uploaded
            assert await async_sandbox.files.exists(remote_path) is True
            content = await async_sandbox.files.read(remote_path)
            assert "Hello from local file!" in content
        finally:
            # Cleanup local file
            os.unlink(local_path)

    @pytest.mark.asyncio
    async def test_download_text_file(self, async_sandbox):
        """Test downloading a text file from async_sandbox to local filesystem."""
        # Create a file in async_sandbox first
        remote_path = "/workspace/download_test.txt"
        test_content = "This file will be downloaded\nLine 2\nLine 3"
        await async_sandbox.files.write(remote_path, test_content)
        
        # Download to local filesystem
        with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.txt') as f:
            local_path = f.name
        
        try:
            await async_sandbox.files.download(remote_path, local_path)
            
            # Verify file was downloaded
            assert os.path.exists(local_path)
            with open(local_path, 'r') as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content
        finally:
            # Cleanup local file
            if os.path.exists(local_path):
                os.unlink(local_path)

