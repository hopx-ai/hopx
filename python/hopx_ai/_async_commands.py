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
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace"
    ) -> ExecutionResult:
        """Run shell command."""
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
