"""Auth module specific fixtures."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

# Note: Keyring fixtures are already in root conftest.py
# This file can add auth-specific fixtures as needed


@pytest.fixture
def mock_oauth_flow() -> Generator[MagicMock, None, None]:
    """Mock OAuth flow functions."""
    with patch("hopx_cli.auth.oauth.start_oauth_flow") as mock:
        mock.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_at": 1700000000,
        }
        yield mock


@pytest.fixture
def mock_oauth_flow_failure() -> Generator[MagicMock, None, None]:
    """Mock OAuth flow that fails."""
    with patch("hopx_cli.auth.oauth.start_oauth_flow") as mock:
        mock.return_value = None
        yield mock
