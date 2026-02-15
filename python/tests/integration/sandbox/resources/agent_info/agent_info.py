"""
Integration tests for Agent info and metrics.

Tests cover:
- Getting agent information
- Getting agent system metrics
- Getting system metrics snapshot
- Listing system processes
- Getting Jupyter sessions
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


class TestAgentInfo:
    """Test agent information and metrics."""

    def test_get_agent_info(self, sandbox):
        """Test getting agent information."""
        info = sandbox.get_agent_info()

        assert isinstance(info, dict)
        # Agent info should contain version or capabilities

    def test_get_agent_metrics(self, sandbox):
        """Test getting agent system metrics."""
        metrics = sandbox.get_agent_metrics()

        assert isinstance(metrics, dict)
        # Metrics might contain CPU, memory, etc.

    def test_get_metrics_snapshot(self, sandbox):
        """Test getting system metrics snapshot."""
        snapshot = sandbox.get_metrics_snapshot()

        assert isinstance(snapshot, dict)
        # Snapshot might contain system metrics, process metrics, cache stats

    def test_list_system_processes(self, sandbox):
        """Test listing system processes."""
        processes = sandbox.list_system_processes()

        assert isinstance(processes, list)
        # Should have at least some system processes

    def test_get_jupyter_sessions(self, sandbox):
        """Test getting Jupyter sessions."""
        sessions = sandbox.get_jupyter_sessions()

        assert isinstance(sessions, list)
        # Sessions list might be empty if no Jupyter is running

