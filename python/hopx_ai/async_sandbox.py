"""Async Sandbox class - for async/await usage."""

from typing import Optional, List, AsyncIterator, Dict
from typing import Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from .models import SandboxInfo, Template
from ._async_client import AsyncHTTPClient

from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class TokenData:
    """JWT token data."""
    token: str
    expires_at: datetime

# Global token cache (shared between AsyncSandbox instances)
_token_cache: Dict[str, TokenData] = {}

from ._utils import remove_none_values


class AsyncSandbox:
    """
    Async Hopx Sandbox - lightweight VM management with async/await.
    
    For async Python applications (FastAPI, aiohttp, etc.)
    
    Example:
        >>> from hopx_ai import AsyncSandbox
        >>> 
        >>> async with AsyncSandbox.create(template="nodejs") as sandbox:
        ...     info = await sandbox.get_info()
        ...     print(info.public_host)
        # Automatically cleaned up!
    """
    
    def __init__(
        self,
        sandbox_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize AsyncSandbox instance.
        
        Note: Prefer using AsyncSandbox.create() or AsyncSandbox.connect() instead.
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.sandbox_id = sandbox_id
        self._client = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._agent_client = None
        self._jwt_token = None
    
    # =============================================================================
    # CLASS METHODS (Static - for creating/listing sandboxes)
    # =============================================================================
    
    @classmethod
    async def create(
        cls,
        template: Optional[str] = None,
        *,
        template_id: Optional[str] = None,
        region: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        internet_access: Optional[bool] = None,
        env_vars: Optional[Dict[str, str]] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> "AsyncSandbox":
        """
        Create a new sandbox (async).
        
        You can create a sandbox in two ways:
        1. From template ID (resources auto-loaded from template)
        2. Custom sandbox (specify template name + resources)
        
        Args:
            template: Template name for custom sandbox (e.g., "code-interpreter", "nodejs")
            template_id: Template ID to create from (resources auto-loaded, no vcpu/memory needed)
            region: Preferred region (optional)
            timeout_seconds: Auto-kill timeout in seconds (optional, default: no timeout)
            internet_access: Enable internet access (optional, default: True)
            env_vars: Environment variables (optional)
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
        
        Returns:
            AsyncSandbox instance
        
        Examples:
            >>> # Create from template ID with timeout
            >>> sandbox = await AsyncSandbox.create(
            ...     template_id="282",
            ...     timeout_seconds=600,
            ...     internet_access=False
            ... )
            
            >>> # Create custom sandbox
            >>> sandbox = await AsyncSandbox.create(
            ...     template="nodejs",
            ...     timeout_seconds=300
            ... )
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        # Validate parameters
        if template_id:
            # Create from template ID (resources from template)
            # Convert template_id to string if it's an int (API may return int from build)
            data = remove_none_values({
                "template_id": str(template_id),
                "region": region,
                "timeout_seconds": timeout_seconds,
                "internet_access": internet_access,
                "env_vars": env_vars,
            })
        elif template:
            # Create from template name (resources from template)
            data = remove_none_values({
                "template_name": template,
                "region": region,
                "timeout_seconds": timeout_seconds,
                "internet_access": internet_access,
                "env_vars": env_vars,
            })
        else:
            raise ValueError("Either 'template' or 'template_id' must be provided")
        
        response = await client.post("/v1/sandboxes", json=data)
        sandbox_id = response["id"]
        
        return cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )
    
    @classmethod
    async def connect(
        cls,
        sandbox_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> "AsyncSandbox":
        """
        Connect to an existing sandbox (async).
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
        
        Returns:
            AsyncSandbox instance
        
        Example:
            >>> sandbox = await AsyncSandbox.connect("sandbox_id")
            >>> info = await sandbox.get_info()
        """
        instance = cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )
        
        # Verify it exists
        await instance.get_info()
        
        return instance
    
    @classmethod
    async def list(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List["AsyncSandbox"]:
        """
        List all sandboxes (async).
        
        Args:
            status: Filter by status
            region: Filter by region
            limit: Maximum number of results
            api_key: API key
            base_url: API base URL
        
        Returns:
            List of AsyncSandbox instances
        
        Example:
            >>> sandboxes = await AsyncSandbox.list(status="running")
            >>> for sb in sandboxes:
            ...     info = await sb.get_info()
            ...     print(info.public_host)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        params = remove_none_values({
            "status": status,
            "region": region,
            "limit": limit,
        })
        
        response = await client.get("/v1/sandboxes", params=params)
        sandboxes_data = response.get("data", [])
        
        return [
            cls(
                sandbox_id=sb["id"],
                api_key=api_key,
                base_url=base_url,
            )
            for sb in sandboxes_data
        ]
    
    @classmethod
    async def iter(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> AsyncIterator["AsyncSandbox"]:
        """
        Lazy async iterator for sandboxes.
        
        Yields sandboxes one by one, fetching pages as needed.
        
        Args:
            status: Filter by status
            region: Filter by region
            api_key: API key
            base_url: API base URL
        
        Yields:
            AsyncSandbox instances
        
        Example:
            >>> async for sandbox in AsyncSandbox.iter(status="running"):
            ...     info = await sandbox.get_info()
            ...     print(info.public_host)
            ...     if found:
            ...         break  # Doesn't fetch remaining pages
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        limit = 100
        has_more = True
        cursor = None
        
        while has_more:
            params = {"limit": limit}
            if status:
                params["status"] = status
            if region:
                params["region"] = region
            if cursor:
                params["cursor"] = cursor
            
            response = await client.get("/v1/sandboxes", params=params)
            
            for item in response.get("data", []):
                yield cls(
                    sandbox_id=item["id"],
                    api_key=api_key,
                    base_url=base_url,
                )
            
            has_more = response.get("has_more", False)
            cursor = response.get("next_cursor")
    
    @classmethod
    async def list_templates(
        cls,
        *,
        category: Optional[str] = None,
        language: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List[Template]:
        """
        List available templates (async).
        
        Args:
            category: Filter by category
            language: Filter by language
            api_key: API key
            base_url: API base URL
        
        Returns:
            List of Template objects
        
        Example:
            >>> templates = await AsyncSandbox.list_templates()
            >>> for t in templates:
            ...     print(f"{t.name}: {t.display_name}")
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        
        params = remove_none_values({
            "category": category,
            "language": language,
        })
        
        response = await client.get("/v1/templates", params=params)
        templates_data = response.get("data", [])
        
        return [Template(**t) for t in templates_data]
    
    @classmethod
    async def get_template(
        cls,
        name: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Template:
        """
        Get template details (async).

        Args:
            name: Template name
            api_key: API key
            base_url: API base URL

        Returns:
            Template object

        Example:
            >>> template = await AsyncSandbox.get_template("nodejs")
            >>> print(template.description)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        response = await client.get(f"/v1/templates/{name}")
        return Template(**response)

    @classmethod
    async def delete_template(
        cls,
        template_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Dict[str, Any]:
        """
        Delete a custom template (async).

        Only organization-owned templates can be deleted. Public templates cannot be deleted.

        Args:
            template_id: Template ID to delete
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL

        Returns:
            Dict with deletion confirmation

        Raises:
            NotFoundError: Template not found
            ValidationError: Cannot delete public templates
            AuthenticationError: Invalid API key

        Example:
            >>> result = await AsyncSandbox.delete_template("template_123abc")
            >>> print(result)
        """
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)
        response = await client.delete(f"/v1/templates/{template_id}")
        return response

    @classmethod
    async def health_check(
        cls,
        *,
        base_url: str = "https://api.hopx.dev",
    ) -> Dict[str, Any]:
        """
        Check API health status (async).

        This endpoint does not require authentication and can be used to verify
        API availability and connectivity.

        Args:
            base_url: API base URL (default: production)

        Returns:
            Dict with health status information

        Example:
            >>> health = await AsyncSandbox.health_check()
            >>> print(health)  # {'status': 'ok', ...}
        """
        # Use a minimal async client without API key for health check
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url.rstrip('/')}/health", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            from .errors import NetworkError
            raise NetworkError(f"Health check failed: {e}")

    # =============================================================================
    # INSTANCE METHODS (for managing individual sandbox)
    # =============================================================================
    
    async def get_info(self) -> SandboxInfo:
        """
        Get current sandbox information (async).

        Returns:
            SandboxInfo with current state

        Example:
            >>> info = await sandbox.get_info()
            >>> print(f"Status: {info.status}")
            >>> print(f"Internet access: {info.internet_access}")
            >>> if info.expires_at:
            ...     print(f"Expires at: {info.expires_at}")
        """
        response = await self._client.get(f"/v1/sandboxes/{self.sandbox_id}")

        # Parse resources if present
        resources = None
        if response.get("resources"):
            from .models import Resources
            resources = Resources(
                vcpu=response["resources"]["vcpu"],
                memory_mb=response["resources"]["memory_mb"],
                disk_mb=response["resources"]["disk_mb"]
            )

        # Parse timestamps
        created_at = None
        if response.get("created_at"):
            try:
                from datetime import datetime
                created_at = datetime.fromisoformat(response["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        expires_at = None
        if response.get("expires_at"):
            try:
                from datetime import datetime
                expires_at = datetime.fromisoformat(response["expires_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return SandboxInfo(
            sandbox_id=response["id"],
            template_id=response.get("template_id"),
            template_name=response.get("template_name"),
            organization_id=response.get("organization_id", 0),
            node_id=response.get("node_id"),
            region=response.get("region"),
            status=response["status"],
            public_host=response.get("public_host") or response.get("direct_url", ""),
            direct_url=response.get("direct_url"),
            preview_url=response.get("preview_url"),
            resources=resources,
            internet_access=response.get("internet_access"),
            live_mode=response.get("live_mode"),
            timeout_seconds=response.get("timeout_seconds"),
            expires_at=expires_at,
            created_at=created_at,
            # Legacy fields for backward compatibility
            started_at=None,
            end_at=expires_at,  # Map expires_at to end_at for backward compat
        )
    
    async def stop(self) -> None:
        """Stop the sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/stop")
    
    async def start(self) -> None:
        """Start a stopped sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/start")
    
    async def pause(self) -> None:
        """Pause the sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/pause")
    
    async def resume(self) -> None:
        """Resume a paused sandbox (async)."""
        await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/resume")
    
    async def set_timeout(self, seconds: int) -> None:
        """
        Extend sandbox timeout (async).
        
        Sets a new timeout duration. The sandbox will be automatically terminated
        after the specified number of seconds from now.
        
        Args:
            seconds: New timeout duration in seconds from now (must be > 0)
        
        Example:
            >>> await sandbox.set_timeout(600)  # 10 minutes
            >>> await sandbox.set_timeout(3600)  # 1 hour
        
        Raises:
            HopxError: If the API request fails
        """
        payload = {"timeout_seconds": seconds}
        await self._client.put(
            f"/v1/sandboxes/{self.sandbox_id}/timeout",
            json=payload
        )
    
    async def kill(self) -> None:
        """
        Destroy the sandbox immediately (async).
        
        This action is irreversible.
        
        Example:
            >>> await sandbox.kill()
        """
        await self._client.delete(f"/v1/sandboxes/{self.sandbox_id}")
    
    # =============================================================================
    # ASYNC CONTEXT MANAGER (auto-cleanup)
    # =============================================================================
    
    async def __aenter__(self) -> "AsyncSandbox":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args) -> None:
        """Async context manager exit - auto cleanup."""
        try:
            await self.kill()
        except Exception:
            # Ignore errors on cleanup
            pass
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def __repr__(self) -> str:
        return f"<AsyncSandbox {self.sandbox_id}>"
    
    def __str__(self) -> str:
        return f"AsyncSandbox(id={self.sandbox_id})"


    # =============================================================================
    # AGENT OPERATIONS (Code Execution)
    # =============================================================================
    
    async def _ensure_valid_token(self) -> None:
        """Ensure JWT token is valid and refresh if needed."""
        token_data = _token_cache.get(self.sandbox_id)
        
        if token_data is None:
            # Get initial token
            await self.refresh_token()
        else:
            # Check if token expires soon (within 1 hour)
            time_until_expiry = token_data.expires_at - datetime.now(token_data.expires_at.tzinfo)
            if time_until_expiry < timedelta(hours=1):
                await self.refresh_token()
    
    async def _ensure_agent_client(self) -> None:
        """Ensure agent HTTP client is initialized."""
        if self._agent_client is None:
            from ._async_agent_client import AsyncAgentHTTPClient
            import asyncio
            
            # Get sandbox info to get agent URL
            info = await self.get_info()
            agent_url = info.public_host.rstrip('/')
            
            # Ensure JWT token is valid
            await self._ensure_valid_token()
            
            # Get JWT token for agent authentication
            jwt_token = _token_cache.get(self.sandbox_id)
            jwt_token_str = jwt_token.token if jwt_token else None
            
            # Create agent client with token refresh callback
            async def refresh_token_callback():
                """Async callback to refresh token when agent returns 401."""
                await self.refresh_token()
                token_data = _token_cache.get(self.sandbox_id)
                return token_data.token if token_data else None
            
            self._agent_client = AsyncAgentHTTPClient(
                agent_url=agent_url,
                jwt_token=jwt_token_str,
                timeout=60,
                max_retries=3,
                token_refresh_callback=refresh_token_callback
            )
            
            # Wait for agent to be ready
            max_wait = 30
            retry_delay = 1.5
            
            for attempt in range(max_wait):
                try:
                    health = await self._agent_client.get("/health", operation="agent health check")
                    if health.get("status") == "healthy":
                        break
                except Exception as e:
                    if attempt < max_wait - 1:
                        await asyncio.sleep(retry_delay)
                        continue
    
    async def run_code(
        self,
        code: str,
        *,
        language: str = "python",
        timeout_seconds: int = 60,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
    ):
        """
        Execute code with rich output capture (async).
        
        Args:
            code: Code to execute
            language: Language (python, javascript, bash, go)
            timeout_seconds: Execution timeout in seconds
            env: Optional environment variables
            working_dir: Working directory
        
        Returns:
            ExecutionResult with stdout, stderr, rich_outputs
        """
        await self._ensure_agent_client()
        
        from .models import ExecutionResult, RichOutput
        
        payload = {
            "language": language,
            "code": code,
            "working_dir": working_dir,
            "timeout": timeout_seconds
        }
        
        if env:
            payload["env"] = env
        
        response = await self._agent_client.post(
            "/execute",
            json=payload,
            operation="execute code",
            context={"language": language}
        )
        
        # Parse rich outputs from Jupyter
        # Agent returns: .png, .html, .json, .result directly in response
        rich_outputs = []
        if response and isinstance(response, dict):
            # Check for PNG (Matplotlib)
            if response.get("png"):
                rich_outputs.append(RichOutput(
                    type="image/png",
                    data={"image/png": response["png"]},
                    metadata=None,
                    timestamp=None
                ))
            
            # Check for HTML (Pandas, Plotly)
            if response.get("html"):
                rich_outputs.append(RichOutput(
                    type="text/html",
                    data={"text/html": response["html"]},
                    metadata=None,
                    timestamp=None
                ))
            
            # Check for JSON (Plotly)
            if response.get("json"):
                rich_outputs.append(RichOutput(
                    type="application/json",
                    data={"application/json": response["json"]},
                    metadata=None,
                    timestamp=None
                ))
            
            # Check for DataFrame JSON
            if response.get("dataframe"):
                rich_outputs.append(RichOutput(
                    type="application/vnd.dataframe+json",
                    data={"application/vnd.dataframe+json": response["dataframe"]},
                    metadata=None,
                    timestamp=None
                ))
        
        result = ExecutionResult(
            success=response.get("success", True) if response else False,
            stdout=response.get("stdout", "") if response else "",
            stderr=response.get("stderr", "") if response else "",
            exit_code=response.get("exit_code", 0) if response else 1,
            execution_time=response.get("execution_time", 0.0) if response else 0.0,
            rich_outputs=rich_outputs
        )
        
        return result
    
    async def run_code_async(
        self,
        code: str,
        *,
        language: str = "python",
        timeout_seconds: int = 60,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Execute code asynchronously (non-blocking, returns execution ID).
        
        Returns:
            Execution ID for tracking
        """
        await self._ensure_agent_client()
        
        payload = {
            "language": language,
            "code": code,
            "timeout": timeout_seconds,
            "async": True
        }
        
        if env:
            payload["env"] = env
        
        response = await self._agent_client.post(
            "/execute",
            json=payload,
            operation="execute code async"
        )
        
        return response.get("execution_id", "")
    
    async def list_processes(self) -> List[Dict[str, Any]]:
        """List running processes in sandbox."""
        await self._ensure_agent_client()
        
        response = await self._agent_client.get(
            "/processes",
            operation="list processes"
        )
        
        return response.get("processes", [])
    
    async def kill_process(self, process_id: str) -> Dict[str, Any]:
        """Kill a process by ID."""
        await self._ensure_agent_client()
        
        response = await self._agent_client.post(
            f"/processes/{process_id}/kill",
            operation="kill process",
            context={"process_id": process_id}
        )
        
        return response
    
    async def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get agent metrics snapshot."""
        await self._ensure_agent_client()
        
        response = await self._agent_client.get(
            "/metrics",
            operation="get metrics"
        )
        
        return response
    
    async def refresh_token(self) -> None:
        """Refresh JWT token for agent authentication."""
        response = await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/token/refresh")
        
        if "auth_token" in response and "token_expires_at" in response:
            _token_cache[self.sandbox_id] = TokenData(
                token=response["auth_token"],
                expires_at=datetime.fromisoformat(response["token_expires_at"].replace("Z", "+00:00"))
            )
            
            # Update agent client's JWT token if already initialized
            if self._agent_client is not None:
                self._agent_client.update_jwt_token(response["auth_token"])

    # =============================================================================
    # PROPERTIES - Access to specialized operations
    # =============================================================================
    
    @property
    def files(self):
        """Access file operations (lazy init)."""
        if not hasattr(self, '_files'):
            from ._async_files import AsyncFiles
            self._files = AsyncFiles(self)
        return self._files
    
    @property
    def commands(self):
        """Access command operations (lazy init)."""
        if not hasattr(self, '_commands'):
            from ._async_commands import AsyncCommands
            self._commands = AsyncCommands(self)
        return self._commands
    
    @property
    def env(self):
        """Access environment variable operations (lazy init)."""
        if not hasattr(self, '_env'):
            from ._async_env_vars import AsyncEnvironmentVariables
            self._env = AsyncEnvironmentVariables(self)
        return self._env
    
    @property
    def cache(self):
        """Access cache operations (lazy init)."""
        if not hasattr(self, '_cache'):
            from ._async_cache import AsyncCache
            self._cache = AsyncCache(self)
        return self._cache
    
    @property
    def terminal(self):
        """Access terminal operations (lazy init)."""
        if not hasattr(self, '_terminal'):
            from ._async_terminal import AsyncTerminal
            self._terminal = AsyncTerminal(self)
        return self._terminal

    async def run_code_stream(self, code: str, *, language: str = "python", timeout_seconds: int = 60):
        """
        Stream code execution output (async generator).
        
        Yields stdout/stderr as they're produced.
        """
        await self._ensure_agent_client()
        
        # For now, return regular execution result
        # TODO: Implement WebSocket streaming for async
        result = await self.run_code(code, language=language, timeout_seconds=timeout_seconds)
        yield result.stdout
