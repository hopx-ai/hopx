"""Environment variables resource for Hopx Sandboxes."""

from typing import Dict, Optional
import logging
from ._agent_client import AgentHTTPClient

logger = logging.getLogger(__name__)


class EnvironmentVariables:
    """
    Environment variables resource.

    Provides methods for managing environment variables inside the sandbox at runtime.

    Features:
    - Get all environment variables
    - Set/replace all environment variables
    - Update specific environment variables (merge)
    - Delete individual environment variables

    Example:
        >>> sandbox = Sandbox.create(template="code-interpreter")
        >>>
        >>> # Get all environment variables
        >>> env = sandbox.env.get_all()
        >>> print(env)
        >>>
        >>> # Set multiple variables (replaces all)
        >>> sandbox.env.set_all({
        ...     "API_KEY": "sk-prod-xyz",
        ...     "DATABASE_URL": "postgres://localhost/db"
        ... })
        >>>
        >>> # Update specific variables (merge)
        >>> sandbox.env.update({
        ...     "NODE_ENV": "production",
        ...     "DEBUG": "false"
        ... })
        >>>
        >>> # Delete a variable
        >>> sandbox.env.delete("DEBUG")
    """

    def __init__(self, client: AgentHTTPClient):
        """
        Initialize EnvironmentVariables resource.

        Args:
            client: Shared agent HTTP client
        """
        self._client = client
        logger.debug("EnvironmentVariables resource initialized")

    def get_all(self, *, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Get all environment variables.

        Args:
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Dictionary of environment variables

        Example:
            >>> env = sandbox.env.get_all()
            >>> print(env.get("PATH"))
            >>> print(env.get("HOME"))
        """
        logger.debug("Getting all environment variables")

        response = self._client.get("/env", operation="get environment variables", timeout=timeout)

        # response is httpx.Response, need to parse JSON
        try:
            data = response.json()
            return data.get("env_vars", {})
        except Exception:
            # If response is empty or not JSON, return empty dict
            return {}

    def set_all(self, env_vars: Dict[str, str], *, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Set/replace all environment variables.

        This replaces ALL existing environment variables with the provided ones.
        Use update() if you want to merge instead.

        Args:
            env_vars: Dictionary of environment variables to set
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Updated dictionary of all environment variables

        Example:
            >>> sandbox.env.set_all({
            ...     "API_KEY": "sk-prod-xyz",
            ...     "DATABASE_URL": "postgres://localhost/db",
            ...     "NODE_ENV": "production"
            ... })
        """
        logger.debug(f"Setting {len(env_vars)} environment variables (replace all)")

        response = self._client.put(
            "/env",
            json={"env_vars": env_vars},
            operation="set environment variables",
            timeout=timeout,
        )

        # Agent returns 204 No Content (empty response) on success
        if response.status_code == 204 or not response.content:
            return env_vars  # Return what we set

        data = response.json()
        return data.get("env_vars", {})

    def update(self, env_vars: Dict[str, str], *, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Update specific environment variables (merge).

        This merges the provided variables with existing ones.
        Existing variables not specified are preserved.

        Args:
            env_vars: Dictionary of environment variables to update/add
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Updated dictionary of all environment variables

        Example:
            >>> # Add/update specific variables
            >>> sandbox.env.update({
            ...     "NODE_ENV": "production",
            ...     "DEBUG": "false"
            ... })
            >>>
            >>> # Existing variables like PATH, HOME, etc. are preserved
        """
        logger.debug(f"Updating {len(env_vars)} environment variables (merge)")

        response = self._client.patch(
            "/env",
            json={"env_vars": env_vars, "merge": True},  # ✅ FIXED: add merge flag
            operation="update environment variables",
            timeout=timeout,
        )

        # Agent returns 204 No Content on success
        if response.status_code == 204 or not response.content:
            # Get current env vars to return updated state
            return self.get_all()

        data = response.json()
        return data.get("env_vars", {})

    def delete(self, key: str, *, timeout: Optional[int] = None) -> None:
        """
        Delete a specific environment variable.

        Note: Agent's DELETE /env clears ALL custom variables.
        We work around this by re-setting all vars except the one to delete.

        Args:
            key: Environment variable name to delete
            timeout: Request timeout in seconds (overrides default)

        Example:
            >>> sandbox.env.delete("DEBUG")
            >>> sandbox.env.delete("TEMP_TOKEN")
        """
        logger.debug(f"Deleting environment variable: {key}")

        # Get all current env vars
        current_vars = self.get_all()

        # Remove the specified variable
        if key in current_vars:
            del current_vars[key]
            # Re-set all env vars without the deleted one
            self.set_all(current_vars)
            logger.debug(f"Environment variable {key} deleted")
        else:
            logger.debug(f"Environment variable {key} not found (already deleted)")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific environment variable value.

        Convenience method that fetches all variables and returns the requested one.

        Args:
            key: Environment variable name
            default: Default value if variable doesn't exist

        Returns:
            Variable value or default

        Example:
            >>> api_key = sandbox.env.get("API_KEY")
            >>> db_url = sandbox.env.get("DATABASE_URL", "postgres://localhost/db")
        """
        env_vars = self.get_all()
        return env_vars.get(key, default)

    def set(self, key: str, value: str, *, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Set a single environment variable.

        Convenience method that updates just one variable (merge).

        Args:
            key: Environment variable name
            value: Environment variable value
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Updated dictionary of all environment variables

        Example:
            >>> sandbox.env.set("API_KEY", "sk-prod-xyz")
            >>> sandbox.env.set("NODE_ENV", "production")
        """
        return self.update({key: value}, timeout=timeout)

    def __repr__(self) -> str:
        return f"<EnvironmentVariables client={self._client}>"
