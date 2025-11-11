"""Command execution resource for Hopx Sandboxes."""

from typing import Optional, Dict
import logging
from .models import CommandResult
from ._agent_client import AgentHTTPClient

logger = logging.getLogger(__name__)


class Commands:
    """
    Command execution resource.
    
    Provides methods for running shell commands inside the sandbox.
    
    Features:
    - Automatic retry with exponential backoff
    - Connection pooling for efficiency  
    - Proper error handling
    - Configurable timeouts
    
    Example:
        >>> sandbox = Sandbox.create(template="code-interpreter")
        >>> 
        >>> # Run simple command
        >>> result = sandbox.commands.run('ls -la /workspace')
        >>> print(result.stdout)
        >>> 
        >>> # Check success
        >>> if result.success:
        ...     print("Command succeeded!")
        ... else:
        ...     print(f"Failed: {result.stderr}")
    """
    
    def __init__(self, client: AgentHTTPClient):
        """
        Initialize Commands resource.
        
        Args:
            client: Shared agent HTTP client
        """
        self._client = client
        logger.debug("Commands resource initialized")
    
    def run(
        self,
        command: str,
        *,
        timeout: int = 30,
        background: bool = False,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
    ) -> CommandResult:
        """
        Run shell command.
        
        Args:
            command: Shell command to run
            timeout: Command timeout in seconds (default: 30)
            background: Run in background (returns immediately)
            env: Optional environment variables for this command only.
                 Priority: Request env > Global env > Agent env
            working_dir: Working directory for command (default: /workspace)
        
        Returns:
            CommandResult with stdout, stderr, exit_code
        
        Raises:
            CommandExecutionError: If command execution fails
            TimeoutError: If command times out
        
        Example:
            >>> # Simple command
            >>> result = sandbox.commands.run('ls -la')
            >>> print(result.stdout)
            >>> print(f"Exit code: {result.exit_code}")
            >>> 
            >>> # With environment variables
            >>> result = sandbox.commands.run(
            ...     'echo $API_KEY',
            ...     env={"API_KEY": "sk-test-123"}
            ... )
            >>> 
            >>> # With custom timeout
            >>> result = sandbox.commands.run('npm install', timeout=300)
            >>> 
            >>> # Check success
            >>> if result.success:
            ...     print("Success!")
            ... else:
            ...     print(f"Failed with exit code {result.exit_code}")
            ...     print(f"Error: {result.stderr}")
        """
        if background:
            return self._run_background(command, env=env, working_dir=working_dir)
        
        logger.debug(f"Running command: {command[:50]}...")
        
        # Build request payload
        payload = {
            "command": command,
            "timeout": timeout,
            "working_dir": working_dir
        }
        
        # Add optional environment variables
        if env:
            payload["env"] = env
        
        response = self._client.post(
            "/commands/run",
            json=payload,
            operation="run command",
            context={"command": command},
            timeout=timeout + 5  # Add buffer to HTTP timeout
        )
        
        data = response.json()
        
        return CommandResult(
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            exit_code=data.get("exit_code", 0),
            execution_time=data.get("execution_time", 0.0)
        )
    
    def _run_background(
        self,
        command: str,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace"
    ) -> CommandResult:
        """
        Run command in background.
        
        Args:
            command: Shell command to run
            env: Optional environment variables
            working_dir: Working directory
        
        Returns:
            CommandResult with process info
        """
        logger.debug(f"Running command in background: {command[:50]}...")
        
        # Build request payload
        payload = {"command": command, "working_dir": working_dir}
        
        # Add optional environment variables
        if env:
            payload["env"] = env
        
        response = self._client.post(
            "/commands/background",
            json=payload,
            operation="run background command",
            context={"command": command},
            timeout=10
        )
        
        data = response.json()
        
        # Return a CommandResult indicating background execution
        return CommandResult(
            stdout=f"Background process started: {data.get('process_id', 'unknown')}",
            stderr="",
            exit_code=0,
            execution_time=0.0
        )
    
    def __repr__(self) -> str:
        return f"<Commands client={self._client}>"
