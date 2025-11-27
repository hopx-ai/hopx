"""
Token management for Hopx CLI.

Handles token validation, refresh, and authentication status.
"""

import os
import time
from typing import Any

from hopx_cli.auth.credentials import CredentialStore
from hopx_cli.auth.oauth import refresh_oauth_token


class TokenManager:
    """Manages authentication tokens and validates credentials."""

    def __init__(self, credentials: CredentialStore) -> None:
        """
        Initialize token manager.

        Args:
            credentials: Credential store instance
        """
        self.credentials = credentials

    def get_valid_api_key(self) -> str | None:
        """
        Get API key from storage or environment.

        Checks environment variable first, then credential store.

        Returns:
            Valid API key or None if not found
        """
        env_key = os.environ.get("HOPX_API_KEY")
        if env_key:
            return env_key

        return self.credentials.get_api_key()

    def get_valid_oauth_token(self) -> str | None:
        """
        Get valid OAuth token, refreshing if expired.

        Checks stored OAuth token and refreshes if within 5 minutes of expiry.

        Returns:
            Valid access token or None if not authenticated
        """
        token_data = self.credentials.get_oauth_token()
        if not token_data:
            return None

        access_token = token_data.get("access_token")
        expires_at = token_data.get("expires_at")
        refresh_token = token_data.get("refresh_token")

        if not access_token or not isinstance(access_token, str):
            return None

        # Type narrowing: access_token is now str
        validated_token: str = access_token

        current_time = int(time.time())

        if expires_at and isinstance(expires_at, int) and expires_at - current_time < 300:
            if not refresh_token or not isinstance(refresh_token, str):
                return None

            try:
                new_token = refresh_oauth_token(refresh_token)
                new_token["refresh_token"] = refresh_token
                self.credentials.store_oauth_token(new_token)
                new_access: str = str(new_token["access_token"])
                return new_access
            except Exception:
                return None

        return validated_token

    def is_authenticated(self) -> bool:
        """
        Check if user has valid credentials.

        Returns:
            True if API key or valid OAuth token exists, False otherwise
        """
        return self.get_valid_api_key() is not None or self.get_valid_oauth_token() is not None

    def get_auth_status(self) -> dict[str, Any]:
        """
        Return detailed authentication status for display.

        Returns:
            Dictionary with auth_method, has_api_key, has_oauth, is_authenticated
        """
        api_key = self.get_valid_api_key()
        oauth_token = self.get_valid_oauth_token()

        auth_method = None
        if api_key and oauth_token:
            auth_method = "both"
        elif api_key:
            auth_method = "api_key"
        elif oauth_token:
            auth_method = "oauth"

        api_key_preview = None
        if api_key:
            if api_key.startswith("hopx_live_"):
                parts = api_key.split(".")
                if len(parts) == 2:
                    key_id = parts[0].replace("hopx_live_", "")
                    api_key_preview = f"hopx_live_{key_id}.{'*' * 10}"
                else:
                    api_key_preview = f"{api_key[:15]}...{'*' * 10}"
            else:
                api_key_preview = f"{api_key[:15]}...{'*' * 10}"

        token_data = self.credentials.get_oauth_token()
        oauth_expires_at = None
        if token_data:
            oauth_expires_at = token_data.get("expires_at")

        return {
            "auth_method": auth_method,
            "has_api_key": api_key is not None,
            "has_oauth": oauth_token is not None,
            "is_authenticated": auth_method is not None,
            "api_key_preview": api_key_preview,
            "oauth_expires_at": oauth_expires_at,
        }

    def get_preferred_token(self) -> str | None:
        """
        Get preferred authentication token.

        Prefers OAuth token over API key for better security and user experience.

        Returns:
            OAuth access token if available, otherwise API key, or None
        """
        oauth_token = self.get_valid_oauth_token()
        if oauth_token:
            return oauth_token

        return self.get_valid_api_key()
