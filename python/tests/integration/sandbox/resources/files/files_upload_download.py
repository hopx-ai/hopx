"""
Integration tests for Files resource upload/download operations.

Tests cover:
- Uploading files from local filesystem to sandbox
- Downloading files from sandbox to local filesystem
"""

import os
import pytest
import tempfile
from pathlib import Path
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestFilesUploadDownload:
    """Test file upload and download operations."""

    def test_upload_text_file(self, sandbox):
        """Test uploading a text file from local filesystem."""
        # Create a temporary local file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            local_path = f.name
            f.write("Hello from local file!\nThis is a test upload.")
        
        try:
            # Upload to sandbox
            remote_path = "/workspace/uploaded_file.txt"
            sandbox.files.upload(local_path, remote_path)
            
            # Verify file was uploaded
            assert sandbox.files.exists(remote_path) is True
            content = sandbox.files.read(remote_path)
            assert "Hello from local file!" in content
        finally:
            # Cleanup local file
            os.unlink(local_path)

    def test_download_text_file(self, sandbox):
        """Test downloading a text file from sandbox to local filesystem."""
        # Create a file in sandbox first
        remote_path = "/workspace/download_test.txt"
        test_content = "This file will be downloaded\nLine 2\nLine 3"
        sandbox.files.write(remote_path, test_content)
        
        # Download to local filesystem
        with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.txt') as f:
            local_path = f.name
        
        try:
            sandbox.files.download(remote_path, local_path)
            
            # Verify file was downloaded
            assert os.path.exists(local_path)
            with open(local_path, 'r') as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content
        finally:
            # Cleanup local file
            if os.path.exists(local_path):
                os.unlink(local_path)

    def test_upload_binary_file(self, sandbox):
        """Test uploading a binary file."""
        # Create a temporary binary file
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD\xAA\xBB\xCC'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            local_path = f.name
            f.write(binary_data)
        
        try:
            # Upload to sandbox
            remote_path = "/workspace/uploaded_binary.bin"
            sandbox.files.upload(local_path, remote_path)
            
            # Verify file was uploaded
            assert sandbox.files.exists(remote_path) is True
            content = sandbox.files.read_bytes(remote_path)
            assert content == binary_data
        finally:
            # Cleanup local file
            os.unlink(local_path)

    def test_download_binary_file(self, sandbox):
        """Test downloading a binary file."""
        # Create a binary file in sandbox
        remote_path = "/workspace/download_binary.bin"
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD\xAA\xBB\xCC'
        sandbox.files.write_bytes(remote_path, binary_data)
        
        # Download to local filesystem
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            local_path = f.name
        
        try:
            sandbox.files.download(remote_path, local_path)
            
            # Verify file was downloaded
            assert os.path.exists(local_path)
            with open(local_path, 'rb') as f:
                downloaded_content = f.read()
            assert downloaded_content == binary_data
        finally:
            # Cleanup local file
            if os.path.exists(local_path):
                os.unlink(local_path)

