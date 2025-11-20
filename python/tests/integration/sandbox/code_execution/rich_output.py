"""
Integration tests for rich output capture.

Tests cover:
- Capturing standard output
- Capturing standard error
- Rich outputs property
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


class TestRichOutput:
    """Test rich output capture."""

    def test_capture_stdout(self, sandbox):
        """Test capturing standard output."""
        result = sandbox.run_code(
            """
print('Line 1')
print('Line 2')
print('Line 3')
            """
        )

        assert result.success is True
        assert "Line 1" in result.stdout
        assert "Line 2" in result.stdout
        assert "Line 3" in result.stdout

    def test_capture_stderr(self, sandbox):
        """Test capturing standard error."""
        result = sandbox.run_code(
            """
import sys
sys.stderr.write('Error message')
            """
        )

        assert result.success is True
        assert "Error message" in result.stderr

    def test_rich_outputs_property(self, sandbox):
        """Test rich_outputs property exists."""
        result = sandbox.run_code("print('test')")

        # Rich outputs may or may not be present depending on code
        assert hasattr(result, "rich_outputs")
        assert isinstance(result.rich_outputs, list) or result.rich_outputs is None

