"""
Integration tests for Sandbox creation operations.

Tests cover:
- Creating sandbox from template name
- Creating sandbox with environment variables
- Creating sandbox with timeout
- Creating sandbox without internet access
- Error handling for invalid templates
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import NotFoundError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


class TestSandboxCreation:
    """Test sandbox creation operations."""

    def test_create_from_template_name(self, api_key):
        """Test creating sandbox from template name."""
        sandbox = None
        try:
            sandbox = Sandbox.create(
                template=TEST_TEMPLATE,
                api_key=api_key,
                base_url=BASE_URL,
            )
            assert sandbox.sandbox_id is not None
            assert isinstance(sandbox.sandbox_id, str)
            assert len(sandbox.sandbox_id) > 0

            # Verify sandbox exists
            info = sandbox.get_info()
            assert info.status in ("running", "creating")
            assert info.public_host is not None
        finally:
            if sandbox:
                try:
                    sandbox.kill()
                except Exception:
                    pass

    def test_create_with_env_vars(self, api_key):
        """Test creating sandbox with environment variables."""
        sandbox = None
        try:
            env_vars = {
                "TEST_VAR": "test_value",
                "ANOTHER_VAR": "another_value",
            }
            sandbox = Sandbox.create(
                template=TEST_TEMPLATE,
                api_key=api_key,
                base_url=BASE_URL,
                env_vars=env_vars,
            )

            # Verify env vars are set
            env = sandbox.env.get_all()
            assert env.get("TEST_VAR") == "test_value"
            assert env.get("ANOTHER_VAR") == "another_value"
        finally:
            if sandbox:
                try:
                    sandbox.kill()
                except Exception:
                    pass

    def test_create_with_timeout(self, api_key):
        """Test creating sandbox with timeout."""
        sandbox = None
        try:
            timeout_seconds = 300  # 5 minutes
            sandbox = Sandbox.create(
                template=TEST_TEMPLATE,
                api_key=api_key,
                base_url=BASE_URL,
                timeout_seconds=timeout_seconds,
            )

            info = sandbox.get_info()
            assert info.timeout_seconds == timeout_seconds
        finally:
            if sandbox:
                try:
                    sandbox.kill()
                except Exception:
                    pass

    def test_create_without_internet(self, api_key):
        """Test creating sandbox without internet access."""
        sandbox = None
        try:
            sandbox = Sandbox.create(
                template=TEST_TEMPLATE,
                api_key=api_key,
                base_url=BASE_URL,
                internet_access=False,
            )

            info = sandbox.get_info()
            assert info.internet_access is False
        finally:
            if sandbox:
                try:
                    sandbox.kill()
                except Exception:
                    pass

    def test_create_invalid_template(self, api_key):
        """Test creating sandbox with invalid template raises error."""
        with pytest.raises(NotFoundError):
            Sandbox.create(
                template="nonexistent-template-12345",
                api_key=api_key,
                base_url=BASE_URL,
            )

