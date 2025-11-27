"""Async Sandbox class - for async/await usage."""

from typing import Optional, List, AsyncIterator, Dict, Any, Coroutine
from datetime import datetime, timedelta

from .models import SandboxInfo, Template, ExpiryInfo
from ._async_client import AsyncHTTPClient
from ._utils import remove_none_values
from ._token_cache import _token_cache, store_token_from_response, get_cached_token
from ._parsers import (
    _parse_sandbox_info_response,
    _parse_rich_outputs,
    _parse_template_response,
    _parse_template_list_response,
)
from ._sandbox_utils import (
    build_sandbox_create_payload,
    build_list_templates_params,
    build_set_timeout_payload,
)
from .errors import SandboxExpiredError, SandboxErrorMetadata, NotFoundError, TemplateNotFoundError


class _AsyncSandboxContextManager:
    """
    Wrapper to allow `async with AsyncSandbox.create(...)` syntax.

    This class makes the create() coroutine work as both:
    1. Direct await: `sandbox = await AsyncSandbox.create(...)`
    2. Context manager: `async with AsyncSandbox.create(...) as sandbox:`
    """

    def __init__(self, coro: Coroutine[Any, Any, "AsyncSandbox"]):
        self._coro = coro
        self._sandbox: Optional["AsyncSandbox"] = None

    def __await__(self):
        """Allow direct await: `sandbox = await AsyncSandbox.create(...)`."""
        return self._coro.__await__()

    async def __aenter__(self) -> "AsyncSandbox":
        """Allow context manager: `async with AsyncSandbox.create(...) as sandbox:`."""
        self._sandbox = await self._coro
        return self._sandbox

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Cleanup sandbox on context manager exit."""
        if self._sandbox:
            try:
                await self._sandbox.kill()
            except Exception:
                # Ignore cleanup errors
                pass
        return False


class AsyncSandbox:
    """
    Async Hopx Sandbox - lightweight VM management with async/await.

    For async Python applications (FastAPI, aiohttp, etc.)

    Example:
        >>> from hopx_ai import AsyncSandbox
        >>>
        >>> async with AsyncSandbox.create(template="code-interpreter") as sandbox:
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
        self._ws_client = None
        self._jwt_token = None

    # =============================================================================
    # CLASS METHODS (Static - for creating/listing sandboxes)
    # =============================================================================

    @classmethod
    def create(
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
    ) -> _AsyncSandboxContextManager:
        """
        Create a new sandbox (async).

        You can create a sandbox in two ways:
        1. From template ID (resources auto-loaded from template)
        2. Custom sandbox (specify template name + resources)

        Args:
            template: Template name for custom sandbox (e.g., "code-interpreter", "base")
            template_id: Template ID to create from (resources auto-loaded, no vcpu/memory needed)
            region: Preferred region (optional)
            timeout_seconds: Auto-kill timeout in seconds (optional, default: no timeout)
            internet_access: Enable internet access (optional, default: True)
            env_vars: Environment variables (optional)
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL

        Returns:
            Context manager that can be awaited or used with `async with`

        Examples:
            >>> # Direct await
            >>> sandbox = await AsyncSandbox.create(
            ...     template_id="282",
            ...     timeout_seconds=600,
            ...     internet_access=False
            ... )
            >>> await sandbox.kill()

            >>> # Context manager (auto-cleanup)
            >>> async with AsyncSandbox.create(template="code-interpreter") as sandbox:
            ...     result = await sandbox.run_code("print('hello')")
        """
        return _AsyncSandboxContextManager(
            cls._create_impl(
                template=template,
                template_id=template_id,
                region=region,
                timeout_seconds=timeout_seconds,
                internet_access=internet_access,
                env_vars=env_vars,
                api_key=api_key,
                base_url=base_url,
            )
        )

    @classmethod
    async def _create_impl(
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
        """Internal implementation of create() logic."""
        client = AsyncHTTPClient(api_key=api_key, base_url=base_url)

        # Build payload using shared utility
        data = build_sandbox_create_payload(
            template=template,
            template_id=template_id,
            region=region,
            timeout_seconds=timeout_seconds,
            internet_access=internet_access,
            env_vars=env_vars,
        )

        try:
            response = await client.post("/v1/sandboxes", json=data)
            sandbox_id = response["id"]
        except NotFoundError as e:
            # If template not found, provide helpful suggestions
            if template:
                # Fetch available templates for fuzzy matching
                try:
                    templates = await cls.list_templates(api_key=api_key, base_url=base_url)
                    available_names = [t.name for t in templates]
                    raise TemplateNotFoundError(
                        template_name=template,
                        available_templates=available_names,
                        code=e.code,
                        request_id=e.request_id,
                        status_code=e.status_code,
                        details=e.details,
                    ) from e
                except TemplateNotFoundError:
                    raise
                except Exception:
                    # If fetching templates fails, raise without suggestions
                    raise TemplateNotFoundError(
                        template_name=template,
                        code=e.code,
                        request_id=e.request_id,
                        status_code=e.status_code,
                        details=e.details,
                    ) from e
            else:
                # Re-raise original error if not template-related
                raise

        # Store JWT token from create response using shared utility
        store_token_from_response(sandbox_id, response)

        # Create AsyncSandbox instance
        instance = cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )

        # Set environment variables if provided
        # The API doesn't automatically set env_vars in the sandbox runtime,
        # so we need to explicitly set them via the env API
        if env_vars:
            await instance.env.update(env_vars)

        return instance

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

        params = remove_none_values(
            {
                "status": status,
                "region": region,
                "limit": limit,
            }
        )

        response = await client.get("/v1/sandboxes", params=params)
        sandboxes_data = response.get("data") or []

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

            for item in response.get("data") or []:
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

        # Build params using shared utility
        params = build_list_templates_params(category=category, language=language)

        response = await client.get("/v1/templates", params=params)

        # Parse response using shared utility
        return _parse_template_list_response(response)

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

        # Parse response using shared utility
        return _parse_template_response(response)

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
                async with session.get(
                    f"{base_url.rstrip('/')}/health", timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
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

        # Parse response using shared utility
        return _parse_sandbox_info_response(response)

    async def get_preview_url(self, port: int = 7777) -> str:
        """
        Get preview URL for accessing a service running on a specific port (async).

        Hopx automatically exposes all ports from your sandbox. Use this method
        to get the public URL for accessing a service running on any port.

        Args:
            port: Port number to access (default: 7777 for sandbox agent)

        Returns:
            Preview URL in format: https://{port}-{sandbox_id}.{region}.vms.hopx.dev/

        Raises:
            HopxError: If unable to determine preview URL from sandbox info

        Example:
            >>> # Create sandbox and run a web server
            >>> sandbox = await AsyncSandbox.create(template="code-interpreter")
            >>> await sandbox.run_code_background('''
            ... from http.server import HTTPServer, BaseHTTPRequestHandler
            ...
            ... class Handler(BaseHTTPRequestHandler):
            ...     def do_GET(self):
            ...         self.send_response(200)
            ...         self.send_header('Content-type', 'text/html')
            ...         self.end_headers()
            ...         self.wfile.write(b'<h1>Hello World!</h1>')
            ...
            ... HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
            ... ''', language="python")
            >>>
            >>> # Get preview URL for the web server
            >>> url = await sandbox.get_preview_url(8080)
            >>> print(f"Access your app at: {url}")
            >>> # Output: https://8080-sandbox123.eu-1001.vms.hopx.dev/
            >>>
            >>> # Get agent URL (default port 7777)
            >>> agent = await sandbox.get_preview_url()
            >>> print(f"Sandbox agent: {agent}")
        """
        info = await self.get_info()
        public_host = info.public_host

        # Parse public_host to extract base domain
        # Expected format: https://7777-sandbox123.eu-1001.vms.hopx.dev/
        # or: https://sandbox123.vms.hopx.dev/

        import re
        from .errors import HopxError

        # Remove protocol and trailing slash
        host = public_host.replace("https://", "").replace("http://", "").rstrip("/")

        # Pattern 1: {port}-{sandbox_id}.{region}.vms.hopx.dev
        match = re.match(r"^(?:\d+-)?([^.]+)\.(.+\.vms\.hopx\.dev)$", host)
        if match:
            sandbox_part = match.group(1)
            domain_part = match.group(2)
            return f"https://{port}-{sandbox_part}.{domain_part}/"

        # Pattern 2: {sandbox_id}.{region}.vms.hopx.dev (no port prefix)
        match = re.match(r"^([^.]+)\.(.+\.vms\.hopx\.dev)$", host)
        if match:
            sandbox_part = match.group(1)
            domain_part = match.group(2)
            return f"https://{port}-{sandbox_part}.{domain_part}/"

        # Fallback: couldn't parse, raise error
        raise HopxError(
            f"Unable to determine preview URL from public_host: {public_host}. "
            "Please ensure sandbox is running and try again."
        )

    @property
    async def agent_url(self) -> str:
        """
        Get the sandbox agent URL (port 7777) (async).

        This is a convenience property that returns the preview URL for the
        default sandbox agent running on port 7777.

        Returns:
            Agent URL (equivalent to get_preview_url(7777))

        Example:
            >>> sandbox = await AsyncSandbox.create(template="code-interpreter")
            >>> print(f"Agent URL: {await sandbox.agent_url}")
            >>> # Output: https://7777-sandbox123.eu-1001.vms.hopx.dev/
        """
        return await self.get_preview_url(7777)

    # =============================================================================
    # EXPIRY MANAGEMENT
    # =============================================================================

    async def get_time_to_expiry(self) -> Optional[int]:
        """
        Get seconds remaining until sandbox expires (async).

        Returns:
            Seconds until expiry, or None if no timeout is configured.
            Negative values indicate the sandbox has already expired.

        Example:
            >>> ttl = await sandbox.get_time_to_expiry()
            >>> if ttl is not None:
            ...     print(f"Sandbox expires in {ttl} seconds")
        """
        info = await self.get_info()
        if info.expires_at is None:
            return None

        now = datetime.now(info.expires_at.tzinfo)
        return int((info.expires_at - now).total_seconds())

    async def is_expiring_soon(self, threshold_seconds: int = 300) -> bool:
        """
        Check if sandbox expires within the given threshold (async).

        Args:
            threshold_seconds: Time threshold in seconds (default: 300 = 5 minutes)

        Returns:
            True if sandbox expires within threshold, False otherwise.

        Example:
            >>> if await sandbox.is_expiring_soon():
            ...     await sandbox.set_timeout(600)
        """
        ttl = await self.get_time_to_expiry()
        if ttl is None:
            return False
        return ttl <= threshold_seconds

    async def get_expiry_info(self, expiring_soon_threshold: int = 300) -> ExpiryInfo:
        """
        Get comprehensive expiry information (async).

        Args:
            expiring_soon_threshold: Seconds threshold for "expiring soon" (default: 300)

        Returns:
            ExpiryInfo with detailed expiry state

        Example:
            >>> expiry = await sandbox.get_expiry_info()
            >>> print(f"TTL: {expiry.time_to_expiry}s")
            >>> print(f"Expiring soon: {expiry.is_expiring_soon}")
        """
        info = await self.get_info()
        ttl = await self.get_time_to_expiry()

        has_timeout = info.expires_at is not None
        is_expired = ttl is not None and ttl < 0
        is_expiring_soon = ttl is not None and ttl <= expiring_soon_threshold and ttl >= 0

        return ExpiryInfo(
            expires_at=info.expires_at,
            time_to_expiry=ttl,
            is_expired=is_expired,
            is_expiring_soon=is_expiring_soon,
            has_timeout=has_timeout,
        )

    # =============================================================================
    # HEALTH CHECKS
    # =============================================================================

    async def is_healthy(self) -> bool:
        """
        Check if sandbox is ready for execution (async).

        Returns:
            True if sandbox is healthy and ready, False otherwise

        Example:
            >>> if await sandbox.is_healthy():
            ...     result = await sandbox.run_code("print('Hello')")
        """
        try:
            await self._ensure_agent_client()
            response = await self._agent_client.get("/health", operation="health check")
            return response.get("status") == "healthy"
        except Exception:
            return False

    async def ensure_healthy(self) -> None:
        """
        Verify sandbox is healthy and ready for execution (async).

        Raises:
            SandboxExpiredError: If sandbox has expired
            HopxError: If sandbox is not healthy

        Example:
            >>> try:
            ...     await sandbox.ensure_healthy()
            ...     result = await sandbox.run_code("print('Hello')")
            ... except SandboxExpiredError:
            ...     print("Sandbox expired")
        """
        from .errors import HopxError

        # Check expiry first
        expiry = await self.get_expiry_info()
        if expiry.is_expired:
            info = await self.get_info()
            raise SandboxExpiredError(
                message=f"Sandbox {self.sandbox_id} has expired",
                metadata=SandboxErrorMetadata(
                    sandbox_id=self.sandbox_id,
                    created_at=str(info.created_at) if info.created_at else None,
                    expires_at=str(info.expires_at) if info.expires_at else None,
                    status=info.status,
                ),
            )

        # Check agent health
        if not await self.is_healthy():
            raise HopxError(
                f"Sandbox {self.sandbox_id} is not healthy",
                code="sandbox_unhealthy",
            )

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
        # Build payload using shared utility
        payload = build_set_timeout_payload(seconds)
        await self._client.put(f"/v1/sandboxes/{self.sandbox_id}/timeout", json=payload)

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
            agent_url = info.public_host.rstrip("/")

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
                token_refresh_callback=refresh_token_callback,
            )

            # Wait for agent to be ready
            max_wait = 30
            retry_delay = 1.5

            for attempt in range(max_wait):
                try:
                    health = await self._agent_client.get("/health", operation="agent health check")
                    if health.get("status") == "healthy":
                        break
                except Exception:
                    if attempt < max_wait - 1:
                        await asyncio.sleep(retry_delay)
                        continue

    async def _ensure_ws_client(self) -> None:
        """Ensure WebSocket client is initialized and agent is ready."""
        if self._ws_client is None:
            from ._ws_client import WebSocketClient

            # First ensure agent HTTP client is ready (which waits for agent)
            await self._ensure_agent_client()

            info = await self.get_info()
            agent_url = info.public_host.rstrip("/")
            token = await self.get_token()
            self._ws_client = WebSocketClient(agent_url, token)

    async def get_agent_info(self) -> Dict[str, Any]:
        """
        Get VM agent information (async).

        Returns comprehensive information about the VM agent including version,
        OS, architecture, available endpoints, and supported features.

        Returns:
            Dict with agent information:
            - agent: Agent name
            - agent_version: Agent version
            - vm_id: VM identifier
            - os: Operating system
            - arch: Architecture
            - features: Available features

        Example:
            >>> info = await sandbox.get_agent_info()
            >>> print(f"Agent: {info['agent']} v{info['agent_version']}")
        """
        await self._ensure_agent_client()

        response = await self._agent_client.get("/info")
        return response

    async def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get real-time agent metrics (async).

        Returns:
            Dict with metrics including uptime, requests, errors

        Example:
            >>> metrics = await sandbox.get_agent_metrics()
            >>> print(f"Uptime: {metrics['uptime_seconds']}s")
        """
        await self._ensure_agent_client()

        response = await self._agent_client.get("/metrics/snapshot")
        return response

    async def list_system_processes(self) -> List[Dict[str, Any]]:
        """
        List all running system processes (async).

        Returns:
            List of process dicts with pid, name, status, etc.

        Example:
            >>> processes = await sandbox.list_system_processes()
            >>> for proc in processes:
            ...     print(f"{proc['pid']}: {proc['name']}")
        """
        await self._ensure_agent_client()

        response = await self._agent_client.get("/processes")
        return response.get("processes", [])

    async def get_jupyter_sessions(self) -> List[Dict[str, Any]]:
        """
        Get Jupyter kernel session status (async).

        Returns:
            List of active Jupyter sessions

        Example:
            >>> sessions = await sandbox.get_jupyter_sessions()
            >>> for session in sessions:
            ...     print(f"Kernel: {session.get('kernel_id')}")
        """
        await self._ensure_agent_client()

        response = await self._agent_client.get("/jupyter/sessions")
        return response.get("sessions", [])

    async def run_code(
        self,
        code: str,
        *,
        language: str = "python",
        timeout_seconds: int = 120,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
        preflight: bool = False,
    ):
        """
        Execute code with rich output capture (async).

        Args:
            code: Code to execute
            language: Language (python, javascript, bash, go)
            timeout_seconds: Execution timeout in seconds (default: 120)
            env: Optional environment variables
            working_dir: Working directory
            preflight: Run health check before execution (default: False).
                       If True, raises SandboxExpiredError if sandbox expired.

        Returns:
            ExecutionResult with stdout, stderr, rich_outputs

        Raises:
            SandboxExpiredError: If preflight=True and sandbox has expired
            HopxError: If preflight=True and sandbox is unhealthy
        """
        # Run preflight health check if requested
        if preflight:
            await self.ensure_healthy()

        await self._ensure_agent_client()

        from .models import ExecutionResult

        payload = {
            "language": language,
            "code": code,
            "workdir": working_dir,  # API expects "workdir" without underscore
            "timeout": timeout_seconds,
        }

        if env:
            payload["env"] = env

        response = await self._agent_client.post(
            "/execute",
            json=payload,
            operation="execute code",
            context={"language": language},
            timeout=timeout_seconds + 30,  # Add buffer to HTTP timeout for network latency
        )

        # Parse rich outputs using shared utility
        rich_outputs = _parse_rich_outputs(response)

        result = ExecutionResult(
            success=response.get("success", True) if response else False,
            stdout=response.get("stdout", "") if response else "",
            stderr=response.get("stderr", "") if response else "",
            exit_code=response.get("exit_code", 0) if response else 1,
            execution_time=response.get("execution_time", 0.0) if response else 0.0,
            rich_outputs=rich_outputs,
        )

        return result

    async def run_code_async(
        self,
        code: str,
        callback_url: str,
        *,
        language: str = "python",
        timeout: int = 1800,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
        callback_headers: Optional[Dict[str, str]] = None,
        callback_signature_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute code asynchronously with webhook callback.

        For long-running code (>5 minutes). Agent POSTs results to callback_url when complete.

        Args:
            code: Code to execute
            callback_url: URL to POST results to when execution completes
            language: Language (python, javascript, bash, go)
            timeout: Execution timeout in seconds (default: 1800 = 30 min)
            env: Optional environment variables
            working_dir: Working directory (default: /workspace)
            callback_headers: Custom headers to include in callback request
            callback_signature_secret: Secret to sign callback payload (HMAC-SHA256)

        Returns:
            Dict with execution_id, status, callback_url

        Example:
            >>> response = await sandbox.run_code_async(
            ...     code='import time; time.sleep(600); print("Done!")',
            ...     callback_url='https://app.com/webhooks/execution',
            ...     callback_headers={'Authorization': 'Bearer secret'},
            ...     callback_signature_secret='webhook-secret-123'
            ... )
            >>> print(f"Execution ID: {response['execution_id']}")
        """
        await self._ensure_agent_client()

        payload = {
            "code": code,
            "language": language,
            "timeout": timeout,
            "workdir": working_dir,
            "callback_url": callback_url,
        }

        if env:
            payload["env"] = env
        if callback_headers:
            payload["callback_headers"] = callback_headers
        if callback_signature_secret:
            payload["callback_signature_secret"] = callback_signature_secret

        response = await self._agent_client.post(
            "/execute/async",
            json=payload,
            operation="async execute code",
            context={"language": language},
            timeout=10,
        )

        return response

    async def list_processes(self) -> List[Dict[str, Any]]:
        """List running processes in sandbox."""
        await self._ensure_agent_client()

        response = await self._agent_client.get("/processes", operation="list processes")

        return response.get("processes", [])

    async def kill_process(self, process_id: str) -> Dict[str, Any]:
        """Kill a process by ID."""
        await self._ensure_agent_client()

        response = await self._agent_client.post(
            f"/processes/{process_id}/kill",
            operation="kill process",
            context={"process_id": process_id},
        )

        return response

    async def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get agent metrics snapshot."""
        await self._ensure_agent_client()

        response = await self._agent_client.get("/metrics", operation="get metrics")

        return response

    async def refresh_token(self) -> None:
        """
        Refresh JWT token for agent authentication.

        Note: Avoid calling this method while WebSocket connections are being established
        to prevent race conditions where a connection uses an old token. The SDK handles
        token refresh automatically before it expires.
        """
        response = await self._client.post(f"/v1/sandboxes/{self.sandbox_id}/token/refresh")

        # Store token using shared utility
        store_token_from_response(self.sandbox_id, response)

        # Update agent client's JWT token if already initialized
        if self._agent_client is not None:
            token_data = get_cached_token(self.sandbox_id)
            if token_data:
                self._agent_client.update_jwt_token(token_data.token)

        # Update WebSocket client's JWT token if already initialized
        if self._ws_client is not None:
            token_data = get_cached_token(self.sandbox_id)
            if token_data:
                self._ws_client.update_jwt_token(token_data.token)

    async def get_token(self) -> str:
        """
        Get current JWT token (for advanced use cases).
        Automatically refreshes if needed.

        Returns:
            JWT token string

        Raises:
            HopxError: If no token available
        """
        await self._ensure_valid_token()

        token_data = _token_cache.get(self.sandbox_id)
        if token_data is None:
            from .errors import HopxError

            raise HopxError("No JWT token available for sandbox")

        return token_data.token

    async def run_code_background(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 300,
        env: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute code in background and return immediately.

        Use list_processes() to check status and kill_process() to terminate.

        Args:
            code: Code to execute
            language: Language (python, javascript, bash, go)
            timeout: Execution timeout in seconds (default: 300 = 5 min)
            env: Optional environment variables
            name: Optional process name for identification

        Returns:
            Dict with process_id, execution_id, status

        Example:
            >>> result = await sandbox.run_code_background(
            ...     code='long_running_task()',
            ...     name='ml-training'
            ... )
            >>> process_id = result['process_id']
        """
        await self._ensure_agent_client()

        payload = {
            "code": code,
            "language": language,
            "timeout": timeout,
        }

        if env:
            payload["env"] = env
        if name:
            payload["name"] = name

        response = await self._agent_client.post(
            "/execute/background",
            json=payload,
            operation="background execute code",
            context={"language": language},
            timeout=10,
        )

        return response

    # =============================================================================
    # PROPERTIES - Access to specialized operations
    # =============================================================================

    @property
    def files(self):
        """Access file operations (lazy init)."""
        if not hasattr(self, "_files"):
            from ._async_files import AsyncFiles

            self._files = AsyncFiles(self)
        return self._files

    @property
    def commands(self):
        """Access command operations (lazy init)."""
        if not hasattr(self, "_commands"):
            from ._async_commands import AsyncCommands

            self._commands = AsyncCommands(self)
        return self._commands

    @property
    def env(self):
        """Access environment variable operations (lazy init)."""
        if not hasattr(self, "_env"):
            from ._async_env_vars import AsyncEnvironmentVariables

            self._env = AsyncEnvironmentVariables(self)
        return self._env

    @property
    def cache(self):
        """Access cache operations (lazy init)."""
        if not hasattr(self, "_cache"):
            from ._async_cache import AsyncCache

            self._cache = AsyncCache(self)
        return self._cache

    @property
    def terminal(self):
        """Access terminal operations (lazy init)."""
        if not hasattr(self, "_terminal"):
            from ._async_terminal import AsyncTerminal

            self._terminal = AsyncTerminal(self)
        return self._terminal

    async def run_code_stream(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute code with real-time output streaming via WebSocket.

        Stream stdout/stderr as it's generated (async generator).

        Args:
            code: Code to execute
            language: Language (python, javascript, bash, go)
            timeout: Execution timeout in seconds
            env: Optional environment variables
            working_dir: Working directory

        Yields:
            Message dictionaries:
            - {"type": "stdout", "data": "...", "timestamp": "..."}
            - {"type": "stderr", "data": "...", "timestamp": "..."}
            - {"type": "result", "exit_code": 0, "execution_time": 1.23}
            - {"type": "complete", "success": True}

        Note:
            Requires websockets library: pip install websockets

        Example:
            >>> import asyncio
            >>>
            >>> async def stream_execution():
            ...     async with AsyncSandbox.create(template="code-interpreter") as sandbox:
            ...
            ...         code = '''
            ...         import time
            ...         for i in range(5):
            ...             print(f"Step {i+1}/5")
            ...             time.sleep(1)
            ...         '''
            ...
            ...         async for message in sandbox.run_code_stream(code):
            ...             if message['type'] == 'stdout':
            ...                 print(message['data'], end='')
            ...             elif message['type'] == 'result':
            ...                 print(f"\\nExit code: {message['exit_code']}")
            >>>
            >>> asyncio.run(stream_execution())
        """
        await self._ensure_ws_client()

        # Connect to streaming endpoint
        async with await self._ws_client.connect("/execute/stream") as ws:
            # Send execution request
            request = {
                "type": "execute",
                "code": code,
                "language": language,
                "timeout": timeout,
                "workdir": working_dir,  # API expects "workdir" without underscore
            }
            if env:
                request["env"] = env

            await self._ws_client.send_message(ws, request)

            # Stream messages
            async for message in self._ws_client.iter_messages(ws):
                yield message

                # Stop on complete
                if message.get("type") == "complete":
                    break
