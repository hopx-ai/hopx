"""Async environment variables for sandboxes."""

from typing import Dict, Optional
import logging
from ._async_agent_client import AsyncAgentHTTPClient

logger = logging.getLogger(__name__)


class AsyncEnvironmentVariables:
    """
    Async environment variable operations.

    Provides methods for managing environment variables inside the sandbox at runtime.

    Features:
    - Get all environment variables
    - Set/replace all environment variables
    - Update specific environment variables (merge)
    - Delete individual environment variables
    """

    def __init__(self, sandbox):
        """Initialize with sandbox reference."""
        self._sandbox = sandbox
        logger.debug("AsyncEnvironmentVariables initialized")

    async def _get_client(self) -> AsyncAgentHTTPClient:
        """Get agent client from sandbox."""
        await self._sandbox._ensure_agent_client()
        return self._sandbox._agent_client

    async def get_all(self, *, timeout: Optional[int] = None) -> Dict[str, str]:
        """
        Get all environment variables.

        Args:
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Dictionary of environment variables
        """
        logger.debug("Getting all environment variables")

        client = await self._get_client()
        response = await client.get("/env", operation="get environment variables")

        return response.get("env_vars", {})

    async def set_all(
        self, env_vars: Dict[str, str], *, timeout: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Set/replace all environment variables.

        This replaces ALL existing environment variables with the provided ones.
        Use update() if you want to merge instead.

        Args:
            env_vars: Dictionary of environment variables to set
            timeout: Request timeout in seconds

        Returns:
            Updated dictionary of all environment variables
        """
        logger.debug(f"Setting {len(env_vars)} environment variables (replace all)")

        client = await self._get_client()
        response = await client.put(
            "/env", json={"env_vars": env_vars}, operation="set environment variables"
        )

        return response.get("env_vars", env_vars)

    async def update(
        self, env_vars: Dict[str, str], *, timeout: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Update specific environment variables (merge).

        This merges the provided variables with existing ones.
        Existing variables not specified are preserved.

        Args:
            env_vars: Dictionary of environment variables to update/add
            timeout: Request timeout in seconds

        Returns:
            Updated dictionary of all environment variables
        """
        logger.debug(f"Updating {len(env_vars)} environment variables (merge)")

        client = await self._get_client()
        response = await client.patch(
            "/env",
            json={"env_vars": env_vars, "merge": True},  # ✅ FIXED: add merge flag
            operation="update environment variables",
        )

        # Agent returns 204 No Content - get updated vars
        if not response or not response.get("env_vars"):
            return await self.get_all()

        return response.get("env_vars", {})

    async def delete(self, name: str, *, timeout: Optional[int] = None) -> None:
        """
        Delete a specific environment variable.

        Note: Agent's DELETE /env clears ALL custom variables.
        We work around this by re-setting all vars except the one to delete.

        Args:
            name: Variable name to delete
            timeout: Request timeout in seconds
        """
        logger.debug(f"Deleting environment variable: {name}")

        # Get all current env vars
        current_vars = await self.get_all()

        # Remove the specified variable
        if name in current_vars:
            del current_vars[name]
            # Re-set all env vars without the deleted one
            await self.set_all(current_vars)
            logger.debug(f"Environment variable {name} deleted")
        else:
            logger.debug(f"Environment variable {name} not found (already deleted)")

    # Convenience methods (aliases)

    async def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a single environment variable value.

        Args:
            name: Variable name
            default: Default value if variable not found

        Returns:
            Variable value or default
        """
        all_vars = await self.get_all()
        return all_vars.get(name, default)

    async def set(self, name: str, value: str) -> None:
        """Set a single environment variable (convenience method)."""
        await self.update({name: value})
