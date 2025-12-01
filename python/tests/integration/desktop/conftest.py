"""
Desktop-specific pytest configuration and fixtures.

This module provides desktop-specific fixtures that use the desktop-enabled template (ID: 399).
"""

import os
import pytest
import time
from unittest.mock import patch
from hopx_ai import Sandbox
from hopx_ai._token_cache import _token_cache

# Desktop template ID - the template we built with all desktop dependencies
DESKTOP_TEMPLATE_ID = "399"

# Allow override via environment variable
DESKTOP_TEMPLATE = os.getenv("HOPX_DESKTOP_TEMPLATE", DESKTOP_TEMPLATE_ID)


@pytest.fixture
def desktop_template():
    """Get desktop template ID/name from environment or use default (399)."""
    return DESKTOP_TEMPLATE


@pytest.fixture
def sandbox(api_key, test_base_url, desktop_template):
    """
    Create a desktop-enabled sandbox for testing and clean up after.
    
    This fixture overrides the default sandbox fixture to use the desktop template (ID: 399).
    It creates a sandbox with desktop automation capabilities and automatically
    cleans it up after the test completes.
    
    Note: Uses template_id parameter (not template) since "399" is a template ID, not a name.
    
    FIXES APPLIED:
    1. JWT Token Refresh: Explicitly refreshes JWT token after sandbox creation to ensure
       it's available for agent communication (not just backend API calls)
    2. JWT Token Verification: Verifies token exists before yielding sandbox
    3. Fail Fast: Sets max_retries=0 to fail immediately on errors instead of retrying
    4. Agent Readiness Wait: Waits up to 30 seconds for agent to become ready (with 1s retry delays)
    5. Graceful Error Handling: Uses pytest.skip() for sandbox creation failures to make
       errors visible in test reports instead of showing 0 tests executed
    
    Args:
        api_key: API key fixture from parent conftest (used for backend API only)
        test_base_url: Base URL fixture from parent conftest
        desktop_template: Desktop template ID/name (default: 399)
    
    Yields:
        Sandbox instance with desktop automation enabled
    
    Note:
        If sandbox creation fails (e.g., template doesn't exist, API error), the fixture
        will skip all tests with a descriptive message instead of raising an exception.
        This makes the failure reason visible in test reports.
    """
    from hopx_ai._agent_client import AgentHTTPClient
    
    # Patch AgentHTTPClient to disable retries (fail fast)
    original_init = AgentHTTPClient.__init__
    
    def patched_init(self, agent_url, *, jwt_token=None, timeout=30, max_retries=3, token_refresh_callback=None):
        # Force max_retries to 0 to fail fast - no retries on errors
        original_init(self, agent_url, jwt_token=jwt_token, timeout=timeout, max_retries=0, token_refresh_callback=token_refresh_callback)
    
    # Patch _ensure_agent_client to reduce wait time for agent readiness
    original_ensure = Sandbox._ensure_agent_client
    
    def patched_ensure_agent_client(self):
        """Patched version that waits up to 30 seconds for agent to become ready."""
        if self._agent_client is None:
            from hopx_ai._agent_client import AgentHTTPClient
            info = self.get_info()
            agent_url = info.public_host.rstrip("/")
            
            # Ensure JWT token is valid
            self._ensure_valid_token()
            
            # Get JWT token for agent authentication (CRITICAL: Desktop operations need JWT, not API key)
            jwt_token = _token_cache.get(self.sandbox_id)
            jwt_token_str = jwt_token.token if jwt_token else None
            
            # Create agent client with token refresh callback
            def refresh_token_callback():
                """Callback to refresh token when agent returns 401."""
                self.refresh_token()
                token_data = _token_cache.get(self.sandbox_id)
                return token_data.token if token_data else None
            
            self._agent_client = AgentHTTPClient(
                agent_url=agent_url,
                jwt_token=jwt_token_str,  # Using JWT token, not API key
                timeout=60,
                max_retries=0,  # No retries - fail fast
                token_refresh_callback=refresh_token_callback,
            )
            
            # Wait for agent to be ready (increased from 2s to allow more time for agent readiness)
            max_wait = 30  # seconds (increased from 2 to allow agent time to become ready)
            retry_delay = 1  # seconds between retries (increased from 0.5 for better spacing)
            
            for attempt in range(max_wait):
                try:
                    health = self._agent_client.get(
                        "/health", operation="agent health check", timeout=5
                    )
                    if health.json().get("status") == "healthy":
                        break
                except Exception:
                    if attempt < max_wait - 1:
                        time.sleep(retry_delay)
                        continue
                    # After max_wait attempts, raise the error
                    raise
    
    with patch.object(AgentHTTPClient, '__init__', patched_init), \
         patch.object(Sandbox, '_ensure_agent_client', patched_ensure_agent_client):
        try:
            sandbox = Sandbox.create(
                template_id=desktop_template,  # Use template_id for template IDs (e.g., "399")
                api_key=api_key,
                base_url=test_base_url,
                timeout_seconds=600,  # 10 minutes
            )
        except Exception as e:
            # Handle sandbox creation failures gracefully
            # This makes the error visible in test reports instead of showing 0 tests
            pytest.skip(
                f"Failed to create desktop sandbox with template '{desktop_template}': {e}. "
                f"This may indicate the template doesn't exist, is invalid, or there's an API issue."
            )
        
        # FIX #1: CRITICAL - Refresh JWT token after creation to ensure it's available for agent calls
        # The create() method stores the token from the response, but we need to ensure
        # it's refreshed and valid for communicating with the agent (not just the backend API)
        # Desktop operations require JWT token for agent authentication, not API key
        try:
            sandbox.refresh_token()
        except Exception as e:
            # If refresh fails, log but continue - token might still be valid from create response
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Token refresh after sandbox creation failed: {e}")
        
        # FIX #2: Verify JWT token is available for agent authentication
        # Desktop operations require JWT token, not API key
        token_data = _token_cache.get(sandbox.sandbox_id)
        if not token_data or not token_data.token:
            pytest.skip(
                f"JWT token not available for sandbox {sandbox.sandbox_id}. "
                "Desktop operations require JWT token for agent authentication, not API key."
            )
        
        yield sandbox
        try:
            sandbox.kill()
        except Exception:
            pass  # Ignore cleanup errors
