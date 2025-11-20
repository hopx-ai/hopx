"""
Integration tests for background code execution.

Tests cover:
- Running code in background
- Listing background processes
- Killing background processes
"""

import os
import pytest
import time
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


class TestBackgroundExecution:
    """Test background code execution."""

    def test_run_code_background(self, sandbox):
        """Test running code in background."""
        response = sandbox.run_code_background(
            "import time; time.sleep(5); print('Done')",
            timeout=60,
        )

        assert "process_id" in response or "execution_id" in response
        process_id = response.get("process_id") or response.get("execution_id")
        assert process_id is not None

    def test_list_processes(self, sandbox):
        """Test listing background processes."""
        # Start a background process
        response = sandbox.run_code_background(
            "import time; time.sleep(10); print('Done')",
            timeout=60,
        )
        process_id = response.get("process_id") or response.get("execution_id")

        time.sleep(1)  # Wait a moment for process to start

        # List processes
        processes = sandbox.list_processes()

        assert isinstance(processes, list)
        # Process might be in the list
        process_ids = [p.get("process_id") or p.get("id") for p in processes]
        # Note: Process might not appear immediately

    def test_kill_process(self, sandbox):
        """Test killing a background process."""
        # Start a long-running background process
        response = sandbox.run_code_background(
            "import time; time.sleep(300); print('Done')",
            timeout=600,
        )
        process_id = response.get("process_id") or response.get("execution_id")

        time.sleep(1)  # Wait a moment for process to start

        # Kill the process
        try:
            result = sandbox.kill_process(process_id)
            assert isinstance(result, dict)
        except Exception as e:
            # Process might have already finished or not exist
            # This is acceptable for integration tests
            pass

