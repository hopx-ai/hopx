"""Async command execution for sandboxes."""

from typing import Optional, Dict, Any
import logging
from ._async_agent_client import AsyncAgentHTTPClient
from .models import ExecutionResult

logger = logging.getLogger(__name__)


class AsyncCommands:
    """Async command execution for sandboxes."""
    
    def __init__(self, sandbox):
        """Initialize with sandbox reference."""
        self._sandbox = sandbox
        logger.debug("AsyncCommands initialized")
    
    async def _get_client(self) -> AsyncAgentHTTPClient:
        """Get agent client from sandbox."""
        await self._sandbox._ensure_agent_client()
        return self._sandbox._agent_client
    
    async def run(
        self,
        command: str,
        *,
        timeout_seconds: int = 60,
        background: bool = False,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace"
    ) -> ExecutionResult:
        """
        Run shell command.

        Args:
            command: Shell command to run
            timeout_seconds: Command timeout in seconds (default: 60)
            background: Run in background (returns immediately)
            env: Optional environment variables for this command only
            working_dir: Working directory for command (default: /workspace)

        Returns:
            ExecutionResult with stdout, stderr, exit_code
        """
        if background:
            return await self._run_background(command, timeout=timeout_seconds, env=env, working_dir=working_dir)

        client = await self._get_client()

        payload = {
            "command": command,
            "timeout": timeout_seconds,
            "working_dir": working_dir
        }

        if env:
            payload["env"] = env

        response = await client.post(
            "/commands/run",
            json=payload,
            operation="run command",
            context={"command": command}
        )

        return ExecutionResult(
            success=response.get("success", True),
            stdout=response.get("stdout", ""),
            stderr=response.get("stderr", ""),
            exit_code=response.get("exit_code", 0),
            execution_time=response.get("execution_time", 0.0),
            rich_outputs=[]
        )

    async def _run_background(
        self,
        command: str,
        timeout: int = 30,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace"
    ) -> ExecutionResult:
        """
        Run command in background.

        Args:
            command: Shell command to run
            timeout: Command timeout in seconds (default: 30)
            env: Optional environment variables
            working_dir: Working directory

        Returns:
            ExecutionResult with process info
        """
        logger.debug(f"Running command in background: {command[:50]}...")

        client = await self._get_client()

        # Build request payload - wrap command in bash for proper shell execution
        payload = {
            "command": "bash",
            "args": ["-c", command],
            "timeout": timeout,
            "working_dir": working_dir
        }

        # Add optional environment variables
        if env:
            payload["env"] = env

        response = await client.post(
            "/commands/background",
            json=payload,
            operation="run background command",
            context={"command": command}
        )

        # Return an ExecutionResult indicating background execution
        process_id = response.get('process_id', 'unknown')
        return ExecutionResult(
            success=True,
            stdout=f"Background process started: {process_id}",
            stderr="",
            exit_code=0,
            execution_time=0.0,
            rich_outputs=[]
        )
