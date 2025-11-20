"""
Integration tests for EnvironmentVariables resource.

Tests cover:
- Getting all environment variables
- Setting all environment variables
- Updating specific environment variables
- Deleting environment variables
- Getting single environment variable
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def sandbox(api_key):
    """Create a sandbox for testing and clean up after."""
    sandbox = Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    )
    yield sandbox
    try:
        sandbox.kill()
    except Exception:
        pass


class TestEnvironmentVariables:
    """Test environment variable operations."""

    def test_get_all_env_vars(self, sandbox):
        """Test getting all environment variables."""
        env_vars = sandbox.env.get_all()

        assert isinstance(env_vars, dict)
        # Should have at least some system env vars
        assert len(env_vars) > 0

    def test_set_all_env_vars(self, sandbox):
        """Test setting all environment variables."""
        new_vars = {
            "VAR1": "value1",
            "VAR2": "value2",
        }

        result = sandbox.env.set_all(new_vars)

        assert isinstance(result, dict)
        assert result.get("VAR1") == "value1"
        assert result.get("VAR2") == "value2"

    def test_update_env_vars(self, sandbox):
        """Test updating specific environment variables."""
        # Set initial vars
        sandbox.env.set_all({"VAR1": "initial", "VAR2": "initial2"})

        # Update one var
        sandbox.env.update({"VAR1": "updated"})

        # Verify update
        env_vars = sandbox.env.get_all()
        assert env_vars.get("VAR1") == "updated"
        assert env_vars.get("VAR2") == "initial2"  # Should be preserved

    def test_delete_env_var(self, sandbox):
        """Test deleting an environment variable."""
        # Set a var
        sandbox.env.set("TEST_DELETE", "value")

        # Verify it exists
        assert sandbox.env.get("TEST_DELETE") == "value"

        # Delete it
        sandbox.env.delete("TEST_DELETE")

        # Verify it's gone
        assert sandbox.env.get("TEST_DELETE") is None

    def test_get_single_env_var(self, sandbox):
        """Test getting a single environment variable."""
        sandbox.env.set("TEST_GET", "test_value")

        value = sandbox.env.get("TEST_GET")
        assert value == "test_value"

        # Test with default
        value = sandbox.env.get("NONEXISTENT", default="default_value")
        assert value == "default_value"

