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
        assert process_id is not None, "Process ID should be returned"

        # Wait a moment for process to start and appear in the list
        # Retry a few times since processes might not appear immediately
        processes = []
        for attempt in range(5):
            time.sleep(0.5)
            processes = sandbox.list_processes()
            assert isinstance(processes, list), "list_processes() should return a list"
            
            # Check if our process appears in the list
            process_ids = [
                p.get("process_id") or p.get("id") or p.get("execution_id")
                for p in processes
            ]
            if process_id in process_ids:
                break
        
        # Verify the process we started is in the list
        assert process_id in process_ids, \
            f"Process {process_id} should appear in the process list. Found processes: {process_ids}"

    def test_kill_process(self, sandbox):
        """Test killing a background process."""
        # Start a long-running background process
        response = sandbox.run_code_background(
            "import time; time.sleep(300); print('Done')",
            timeout=600,
        )
        process_id = response.get("process_id") or response.get("execution_id")
        assert process_id is not None, "Process ID should be returned"

        time.sleep(1)  # Wait a moment for process to start

        # Get process status before killing
        processes_before = sandbox.list_processes()
        process_before = None
        for p in processes_before:
            pid = p.get("process_id") or p.get("id") or p.get("execution_id")
            if pid == process_id:
                process_before = p
                break
        
        # Get initial status if process is in the list
        initial_status = None
        if process_before:
            initial_status = process_before.get("status")
            # Process should be running before we kill it
            assert initial_status in ["running", "pending", None], \
                f"Process should be running/pending before kill, got status: {initial_status}"

        # Kill the process
        result = sandbox.kill_process(process_id)
        assert isinstance(result, dict), "kill_process() should return a dict"
        
        # Wait and retry checking process status - it should change to killed/terminated
        # or the process should be removed from the list
        killed_statuses = ["killed", "terminated", "stopped", "exited"]
        process_killed = False
        
        for attempt in range(10):  # Retry up to 10 times (5 seconds total)
            time.sleep(0.5)
            processes_after = sandbox.list_processes()
            
            # Check if process is still in the list
            process_after = None
            for p in processes_after:
                pid = p.get("process_id") or p.get("id") or p.get("execution_id")
                if pid == process_id:
                    process_after = p
                    break
            
            if process_after is None:
                # Process removed from list - kill was successful
                process_killed = True
                break
            
            # Check if status changed to a killed/terminated state
            current_status = process_after.get("status")
            if current_status in killed_statuses:
                process_killed = True
                break
        
        # Verify the process was killed (either removed or status changed)
        assert process_killed, \
            f"Process {process_id} should be killed (removed from list or status changed to killed/terminated). " \
            f"Final status: {process_after.get('status') if process_after else 'removed'}"

