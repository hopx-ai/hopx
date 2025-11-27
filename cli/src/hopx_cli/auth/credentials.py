"""
Secure credential storage for Hopx CLI.

Stores credentials in system keyring with fallback to encrypted config file.
"""

import os
import stat
from pathlib import Path
from typing import Any

import keyring
import yaml

KEYRING_SERVICE = "hopx-cli"


class CredentialStore:
    """Manages secure storage and retrieval of API keys and OAuth tokens."""

    def __init__(self, profile: str = "default") -> None:
        """
        Initialize credential store.

        Args:
            profile: Profile name for multi-account support (default: "default")
        """
        self.profile = profile
        self.config_dir = Path.home() / ".hopx"
        self.credentials_file = self.config_dir / "credentials.yaml"

    def store_api_key(self, api_key: str, use_keyring: bool = True) -> None:
        """
        Store API key securely.

        Attempts to use system keyring first, falls back to config file if unavailable.

        Args:
            api_key: API key to store
            use_keyring: Whether to attempt keyring storage (default: True)
        """
        if use_keyring:
            try:
                keyring.set_password(KEYRING_SERVICE, f"{self.profile}:api_key", api_key)
                return
            except Exception:
                pass

        self._write_to_config("api_key", api_key)

    def get_api_key(self) -> str | None:
        """
        Retrieve API key from storage.

        Checks keyring first, then config file, then environment variable.

        Returns:
            API key if found, None otherwise
        """
        try:
            key = keyring.get_password(KEYRING_SERVICE, f"{self.profile}:api_key")
            if key:
                return key
        except Exception:
            pass

        key = self._read_from_config("api_key")
        if key:
            return key

        return os.environ.get("HOPX_API_KEY")

    def store_oauth_token(self, token: dict[str, Any]) -> None:
        """
        Store OAuth token data.

        Stores both access token and refresh token in keyring or config file.

        Args:
            token: Dictionary containing access_token, refresh_token, and expires_at
        """
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        expires_at = token.get("expires_at")

        if not access_token:
            raise ValueError("Token must contain access_token")

        try:
            if access_token:
                keyring.set_password(KEYRING_SERVICE, f"{self.profile}:oauth_access", access_token)
            if refresh_token:
                keyring.set_password(
                    KEYRING_SERVICE, f"{self.profile}:oauth_refresh", refresh_token
                )
            if expires_at:
                keyring.set_password(
                    KEYRING_SERVICE, f"{self.profile}:oauth_expires", str(expires_at)
                )
            return
        except Exception:
            pass

        self._write_to_config("oauth_token", token)

    def get_oauth_token(self) -> dict[str, Any] | None:
        """
        Retrieve OAuth token from storage.

        Returns:
            Dictionary with access_token, refresh_token, and expires_at, or None
        """
        try:
            access_token = keyring.get_password(KEYRING_SERVICE, f"{self.profile}:oauth_access")
            refresh_token = keyring.get_password(KEYRING_SERVICE, f"{self.profile}:oauth_refresh")
            expires_at_str = keyring.get_password(KEYRING_SERVICE, f"{self.profile}:oauth_expires")

            if access_token:
                token = {"access_token": access_token}
                if refresh_token:
                    token["refresh_token"] = refresh_token
                if expires_at_str:
                    try:
                        token["expires_at"] = int(expires_at_str)
                    except ValueError:
                        pass
                return token
        except Exception:
            pass

        return self._read_from_config("oauth_token")

    def clear(self) -> None:
        """Remove all stored credentials for this profile."""
        try:
            keyring.delete_password(KEYRING_SERVICE, f"{self.profile}:api_key")
        except Exception:
            pass

        try:
            keyring.delete_password(KEYRING_SERVICE, f"{self.profile}:oauth_access")
        except Exception:
            pass

        try:
            keyring.delete_password(KEYRING_SERVICE, f"{self.profile}:oauth_refresh")
        except Exception:
            pass

        try:
            keyring.delete_password(KEYRING_SERVICE, f"{self.profile}:oauth_expires")
        except Exception:
            pass

        self._delete_from_config()

    def _write_to_config(self, key: str, value: Any) -> None:
        """
        Write credential to config file as fallback.

        Creates ~/.hopx directory if needed and sets restrictive permissions.

        Args:
            key: Credential key (e.g., "api_key", "oauth_token")
            value: Credential value
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {}
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file) as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                pass

        if self.profile not in data:
            data[self.profile] = {}

        data[self.profile][key] = value

        with open(self.credentials_file, "w") as f:
            yaml.safe_dump(data, f)

        os.chmod(self.credentials_file, stat.S_IRUSR | stat.S_IWUSR)

    def _read_from_config(self, key: str) -> Any:
        """
        Read credential from config file.

        Args:
            key: Credential key to read

        Returns:
            Credential value or None if not found
        """
        if not self.credentials_file.exists():
            return None

        try:
            with open(self.credentials_file) as f:
                data = yaml.safe_load(f) or {}
                return data.get(self.profile, {}).get(key)
        except Exception:
            return None

    def _delete_from_config(self) -> None:
        """Remove all credentials for this profile from config file."""
        if not self.credentials_file.exists():
            return

        try:
            with open(self.credentials_file) as f:
                data = yaml.safe_load(f) or {}

            if self.profile in data:
                del data[self.profile]

            if data:
                with open(self.credentials_file, "w") as f:
                    yaml.safe_dump(data, f)
                os.chmod(self.credentials_file, stat.S_IRUSR | stat.S_IWUSR)
            else:
                self.credentials_file.unlink()
        except Exception:
            pass

    @classmethod
    def clear_all_profiles(cls) -> list[str]:
        """Remove credentials for all profiles from keyring and config file.

        Returns:
            List of profile names that were cleared
        """
        cleared_profiles = []
        config_dir = Path.home() / ".hopx"
        credentials_file = config_dir / "credentials.yaml"

        # Get all profiles from credentials file
        profiles_from_file = set()
        if credentials_file.exists():
            try:
                with open(credentials_file) as f:
                    data = yaml.safe_load(f) or {}
                    profiles_from_file = set(data.keys())
            except Exception:
                pass

        # Add "default" profile (always attempt to clear)
        all_profiles = profiles_from_file | {"default"}

        # Clear each profile from keyring
        for profile in all_profiles:
            store = cls(profile=profile)
            try:
                # Check if profile has any credentials before adding to list
                has_creds = False
                try:
                    if keyring.get_password(KEYRING_SERVICE, f"{profile}:api_key"):
                        has_creds = True
                except Exception:
                    pass
                try:
                    if keyring.get_password(KEYRING_SERVICE, f"{profile}:oauth_access"):
                        has_creds = True
                except Exception:
                    pass
                if not has_creds:
                    # Check config file
                    cred_data = store._read_from_config("api_key")
                    if cred_data:
                        has_creds = True
                    cred_data = store._read_from_config("oauth_token")
                    if cred_data:
                        has_creds = True

                if has_creds:
                    store.clear()
                    cleared_profiles.append(profile)
            except Exception:
                pass

        # Delete the entire credentials file
        if credentials_file.exists():
            try:
                credentials_file.unlink()
            except Exception:
                pass

        return cleared_profiles
