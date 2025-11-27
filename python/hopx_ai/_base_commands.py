"""Base class for command execution with shared logic between sync and async implementations."""

from abc import ABC
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class _CommandsBase(ABC):
    """
    Base class for command execution.

    Contains pure functions (no I/O) for:
    - Building request payloads
    - Parsing responses
    - Input validation

    Subclasses (Commands, AsyncCommands) handle actual HTTP I/O.
    """

    def _build_run_payload(
        self, command: str, timeout: int, working_dir: str, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build payload for /commands/run endpoint.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds
            working_dir: Working directory path
            env: Optional environment variables

        Returns:
            Request payload dict ready for JSON serialization
        """
        # Wrap command in bash for proper shell execution
        payload = {
            "command": "bash",
            "args": ["-c", command],
            "timeout": timeout,
            "workdir": working_dir,  # API expects "workdir" without underscore
        }

        if env:
            payload["env"] = env

        return payload

    def _build_background_payload(
        self, command: str, timeout: int, working_dir: str, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Build payload for /commands/background endpoint.

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds
            working_dir: Working directory path
            env: Optional environment variables

        Returns:
            Request payload dict ready for JSON serialization
        """
        # Same format as regular run - wrap in bash
        payload = {
            "command": "bash",
            "args": ["-c", command],
            "timeout": timeout,
            "workdir": working_dir,  # API expects "workdir" without underscore
        }

        if env:
            payload["env"] = env

        return payload

    def _log_command_start(self, command: str, background: bool = False) -> None:
        """Log command execution start."""
        prefix = "background" if background else "regular"
        logger.debug(f"Running {prefix} command: {command[:50]}...")
