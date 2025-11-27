"""CLI configuration management using Pydantic Settings.

Configuration is loaded from:
1. Environment variables (HOPX_*)
2. Config file (~/.hopx/config.yaml)
3. Default values

Environment variables take precedence over config file values.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLIConfig(BaseSettings):
    """Configuration for the Hopx CLI.

    Configuration is loaded from environment variables and config file.
    Environment variables are prefixed with HOPX_ (e.g., HOPX_API_KEY).

    Attributes:
        api_key: API key for Hopx authentication
        base_url: Base URL for the Hopx API
        default_template: Default template name for sandbox creation
        default_timeout: Default timeout in seconds for sandbox operations
        output_format: Default output format (table, json, plain)
        profile: Configuration profile name
    """

    model_config = SettingsConfigDict(
        env_prefix="HOPX_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str | None = Field(
        default=None,
        description="API key for authentication",
    )
    base_url: str = Field(
        default="https://api.hopx.dev",
        description="Base URL for the Hopx API",
    )
    default_template: str = Field(
        default="code-interpreter",
        description="Default template for sandbox creation",
    )
    default_timeout: int = Field(
        default=3600,
        description="Default timeout in seconds for operations",
        ge=1,
    )
    output_format: str = Field(
        default="table",
        description="Default output format (table, json, plain)",
    )
    profile: str = Field(
        default="default",
        description="Configuration profile name",
    )

    @classmethod
    def load(cls, profile: str = "default") -> "CLIConfig":
        """Load configuration from file and environment variables.

        Args:
            profile: Profile name to load from config file

        Returns:
            Loaded configuration instance

        Note:
            Environment variables take precedence over file values.
            If config file does not exist, uses defaults and env vars.
        """
        config_path = cls.get_config_path()
        file_config: dict[str, Any] = {}

        # Load from file if exists
        if config_path.exists():
            try:
                with open(config_path) as f:
                    all_profiles = yaml.safe_load(f) or {}
                    file_config = all_profiles.get(profile, {})
            except Exception:
                # Silently ignore file load errors, use env vars and defaults
                pass

        # Merge file config with environment variables
        # Pydantic Settings will automatically load env vars with HOPX_ prefix
        config = cls(**file_config)
        config.profile = profile
        return config

    @classmethod
    def get_config_path(cls) -> Path:
        """Get path to config file.

        Returns:
            Path to ~/.hopx/config.yaml
        """
        return Path.home() / ".hopx" / "config.yaml"

    def save(self) -> None:
        """Save current configuration to file.

        Saves the configuration to the profile specified in self.profile.
        Creates the config directory if it does not exist.
        """
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing profiles
        all_profiles: dict[str, Any] = {}
        if config_path.exists():
            try:
                with open(config_path) as f:
                    all_profiles = yaml.safe_load(f) or {}
            except Exception:
                pass

        # Update profile with current config
        all_profiles[self.profile] = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "default_template": self.default_template,
            "default_timeout": self.default_timeout,
            "output_format": self.output_format,
        }

        # Write back to file
        with open(config_path, "w") as f:
            yaml.safe_dump(all_profiles, f, default_flow_style=False)

    def get_api_key(self) -> str:
        """Get API key from environment, config file, or credential store.

        Priority order:
        1. HOPX_API_KEY environment variable (highest)
        2. --api-key command-line flag (via constructor)
        3. Config file (~/.hopx/config.yaml)
        4. Credential store (keyring) - where 'hopx auth keys create' stores keys

        Returns:
            API key string

        Raises:
            ValueError: If API key is not configured anywhere
        """
        # Check env var, flag, or config file (already loaded by pydantic)
        if self.api_key:
            return self.api_key

        # Try credential store (keyring) where 'hopx auth keys create' stores keys
        try:
            from hopx_cli.auth.credentials import CredentialStore

            creds = CredentialStore(profile=self.profile)
            stored_key = creds.get_api_key()
            if stored_key:
                return stored_key
        except Exception:
            pass  # Keyring not available or no key stored

        # No API key found - provide helpful guidance
        raise ValueError(
            "API key not configured.\n\n"
            "Options:\n"
            "  1. Set HOPX_API_KEY environment variable (for CI/CD)\n"
            "  2. Run: hopx auth login && hopx auth keys create\n"
            "  3. Get key from: https://console.hopx.dev/api-keys\n\n"
            "For more info: hopx auth --help"
        )
