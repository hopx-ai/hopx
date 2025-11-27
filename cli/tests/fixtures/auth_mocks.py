"""Factory classes for creating authentication mocks.

These factories provide reusable mock objects for keyring, credential storage,
and OAuth flows.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch


class KeyringMock:
    """Mock keyring backend for testing credential storage."""

    def __init__(self) -> None:
        """Initialize empty keyring storage."""
        self._storage: dict[str, dict[str, str]] = {}

    def get_password(self, service: str, key: str) -> str | None:
        """Get password from mock storage.

        Args:
            service: Service name
            key: Key identifier

        Returns:
            Stored password or None
        """
        return self._storage.get(service, {}).get(key)

    def set_password(self, service: str, key: str, password: str) -> None:
        """Store password in mock storage.

        Args:
            service: Service name
            key: Key identifier
            password: Password to store
        """
        if service not in self._storage:
            self._storage[service] = {}
        self._storage[service][key] = password

    def delete_password(self, service: str, key: str) -> None:
        """Delete password from mock storage.

        Args:
            service: Service name
            key: Key identifier
        """
        if service in self._storage and key in self._storage[service]:
            del self._storage[service][key]

    def clear(self) -> None:
        """Clear all stored passwords."""
        self._storage.clear()

    @classmethod
    @contextmanager
    def patch_keyring(cls) -> Generator[KeyringMock, None, None]:
        """Context manager to patch keyring with mock.

        Yields:
            KeyringMock instance for assertions
        """
        mock = cls()
        with patch("hopx_cli.auth.credentials.keyring", mock):
            yield mock

    @classmethod
    @contextmanager
    def patch_unavailable(cls) -> Generator[MagicMock, None, None]:
        """Context manager to patch keyring as unavailable.

        Yields:
            MagicMock that raises exceptions
        """
        with patch("hopx_cli.auth.credentials.keyring") as mock:
            mock.get_password.side_effect = Exception("Keyring backend not available")
            mock.set_password.side_effect = Exception("Keyring backend not available")
            mock.delete_password.side_effect = Exception("Keyring backend not available")
            yield mock


class CredentialStoreMock:
    """Mock CredentialStore for testing."""

    def __init__(
        self,
        api_key: str | None = None,
        oauth_token: dict[str, Any] | None = None,
        profile: str = "default",
    ) -> None:
        """Initialize mock credential store.

        Args:
            api_key: Pre-stored API key
            oauth_token: Pre-stored OAuth token
            profile: Profile name
        """
        self.profile = profile
        self._api_key = api_key
        self._oauth_token = oauth_token

    def store_api_key(self, api_key: str, use_keyring: bool = True) -> None:
        """Store API key."""
        self._api_key = api_key

    def get_api_key(self) -> str | None:
        """Get stored API key."""
        return self._api_key

    def store_oauth_token(self, token: dict[str, Any]) -> None:
        """Store OAuth token."""
        self._oauth_token = token

    def get_oauth_token(self) -> dict[str, Any] | None:
        """Get stored OAuth token."""
        return self._oauth_token

    def clear(self) -> None:
        """Clear all credentials."""
        self._api_key = None
        self._oauth_token = None

    @classmethod
    def create_with_api_key(
        cls, api_key: str = "hopx_live_test.secret", profile: str = "default"
    ) -> CredentialStoreMock:
        """Create mock with pre-stored API key.

        Args:
            api_key: API key to store
            profile: Profile name

        Returns:
            CredentialStoreMock instance
        """
        return cls(api_key=api_key, profile=profile)

    @classmethod
    def create_with_oauth(
        cls,
        access_token: str = "oauth_access_token",
        refresh_token: str | None = "oauth_refresh_token",
        expires_at: int | None = None,
        profile: str = "default",
    ) -> CredentialStoreMock:
        """Create mock with pre-stored OAuth token.

        Args:
            access_token: Access token
            refresh_token: Refresh token
            expires_at: Token expiration timestamp
            profile: Profile name

        Returns:
            CredentialStoreMock instance
        """
        token: dict[str, Any] = {"access_token": access_token}
        if refresh_token:
            token["refresh_token"] = refresh_token
        if expires_at:
            token["expires_at"] = expires_at
        return cls(oauth_token=token, profile=profile)


class OAuthFlowMock:
    """Mock OAuth flow for testing browser-based authentication."""

    def __init__(
        self,
        success: bool = True,
        access_token: str = "mock_access_token",
        refresh_token: str = "mock_refresh_token",
        expires_in: int = 3600,
    ) -> None:
        """Initialize OAuth flow mock.

        Args:
            success: Whether the flow should succeed
            access_token: Access token to return
            refresh_token: Refresh token to return
            expires_in: Token expiration in seconds
        """
        self.success = success
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self._browser_opened = False
        self._callback_received = False

    def start_flow(self) -> dict[str, Any] | None:
        """Simulate starting OAuth flow.

        Returns:
            Token data if successful, None otherwise
        """
        if not self.success:
            return None

        self._browser_opened = True
        self._callback_received = True

        import time

        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": int(time.time()) + self.expires_in,
        }

    @classmethod
    @contextmanager
    def patch_oauth(
        cls, success: bool = True, **kwargs: Any
    ) -> Generator[OAuthFlowMock, None, None]:
        """Context manager to patch OAuth module.

        Args:
            success: Whether flow should succeed
            **kwargs: Additional OAuth flow parameters

        Yields:
            OAuthFlowMock instance
        """
        mock = cls(success=success, **kwargs)

        with patch("hopx_cli.auth.oauth.start_oauth_flow") as mock_start:
            if success:
                mock_start.return_value = mock.start_flow()
            else:
                mock_start.return_value = None
            yield mock


class APIKeyManagerMock:
    """Mock API key manager for testing key operations."""

    def __init__(self) -> None:
        """Initialize with empty key list."""
        self._keys: list[dict[str, Any]] = []
        self._next_id = 1

    def list_keys(self) -> list[dict[str, Any]]:
        """List all API keys."""
        return self._keys

    def create_key(
        self,
        name: str = "test-key",
        expires_in: str | None = None,
    ) -> dict[str, Any]:
        """Create a new API key.

        Args:
            name: Key name
            expires_in: Expiration period

        Returns:
            Created key data
        """
        key_id = f"key_{self._next_id:03d}"
        self._next_id += 1

        key = {
            "id": key_id,
            "name": name,
            "key": f"hopx_live_{key_id}.secret",
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": None,
        }
        self._keys.append(key)
        return key

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key.

        Args:
            key_id: Key identifier

        Returns:
            True if key was revoked
        """
        for i, key in enumerate(self._keys):
            if key["id"] == key_id:
                del self._keys[i]
                return True
        return False

    @classmethod
    @contextmanager
    def patch_manager(cls) -> Generator[APIKeyManagerMock, None, None]:
        """Context manager to patch APIKeyManager.

        Yields:
            APIKeyManagerMock instance
        """
        mock = cls()
        with patch("hopx_cli.auth.api_keys.APIKeyManager") as MockClass:
            instance = MagicMock()
            instance.list_keys.side_effect = mock.list_keys
            instance.create_key.side_effect = mock.create_key
            instance.revoke_key.side_effect = mock.revoke_key
            instance.__enter__ = MagicMock(return_value=instance)
            instance.__exit__ = MagicMock(return_value=False)
            MockClass.return_value = instance
            yield mock
