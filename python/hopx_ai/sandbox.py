"""Main Sandbox class"""

from typing import Optional, List, Iterator, Dict, Any
from datetime import datetime, timedelta
import logging

# Public API models (enhanced with generated models + convenience)
from .models import (
    SandboxInfo,
    Template,
    ExecutionResult,  # ExecuteResponse + convenience methods
    RichOutput,
    MetricsSnapshot,
    Language,
)

from ._client import HTTPClient
from ._agent_client import AgentHTTPClient
from ._utils import remove_none_values
from .files import Files
from .commands import Commands
from .desktop import Desktop
from .env_vars import EnvironmentVariables
from .cache import Cache
from ._ws_client import WebSocketClient
from .terminal import Terminal

# Shared utilities (reduce code duplication with AsyncSandbox)
from ._token_cache import (
    TokenData,
    _token_cache,
    store_token_from_response,
    get_cached_token,
)
from ._parsers import (
    _parse_sandbox_info_response,
    _parse_rich_outputs,
    _parse_template_response,
    _parse_template_list_response,
)
from ._sandbox_utils import (
    build_sandbox_create_payload,
    build_list_sandboxes_params,
    build_list_templates_params,
    build_set_timeout_payload,
)

logger = logging.getLogger(__name__)


class Sandbox:
    """
    Hopx Sandbox - lightweight VM management.
    
    Create and manage sandboxes (microVMs) with a simple, intuitive API.
    
    Example:
        >>> from hopx_ai import Sandbox
        >>> 
        >>> # Create sandbox
        >>> sandbox = Sandbox.create(template="code-interpreter")
        >>> print(sandbox.get_info().public_host)
        >>> 
        >>> # Use and cleanup
        >>> sandbox.kill()
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
        Initialize Sandbox instance.
        
        Note: Prefer using Sandbox.create() or Sandbox.connect() instead of direct instantiation.
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.sandbox_id = sandbox_id
        self._client = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._agent_client: Optional[AgentHTTPClient] = None
        self._ws_client: Optional[WebSocketClient] = None
        self._files: Optional[Files] = None
        self._commands: Optional[Commands] = None
        self._desktop: Optional[Desktop] = None
        self._env: Optional[EnvironmentVariables] = None
        self._cache: Optional[Cache] = None
        self._terminal: Optional[Terminal] = None
    
    @property
    def files(self) -> Files:
        """
        File operations resource.
        
        Lazy initialization - gets agent URL on first access.
        
        Returns:
            Files resource instance
        
        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> content = sandbox.files.read('/workspace/data.txt')
        """
        if self._files is None:
            self._ensure_agent_client()
            # WS client is lazy-loaded in Files.watch() - not needed for basic operations
            self._files = Files(self._agent_client, self)
        return self._files
    
    @property
    def commands(self) -> Commands:
        """
        Command execution resource.
        
        Lazy initialization - gets agent URL on first access.
        
        Returns:
            Commands resource instance
        
        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> result = sandbox.commands.run('npm install')
        """
        if self._commands is None:
            self._ensure_agent_client()
            self._commands = Commands(self._agent_client)
        return self._commands
    
    @property
    def desktop(self) -> Desktop:
        """
        Desktop automation resource.
        
        Lazy initialization - checks desktop availability on first access.
        
        Provides methods for:
        - VNC server management
        - Mouse and keyboard control
        - Screenshot capture
        - Screen recording
        - Window management
        - Display configuration
        
        Returns:
            Desktop resource instance
        
        Raises:
            DesktopNotAvailableError: If template doesn't support desktop automation
        
        Example:
            >>> sandbox = Sandbox.create(template="desktop")
            >>> 
            >>> # Start VNC
            >>> vnc_info = sandbox.desktop.start_vnc()
            >>> print(f"VNC at: {vnc_info.url}")
            >>> 
            >>> # Mouse control
            >>> sandbox.desktop.click(100, 100)
            >>> sandbox.desktop.type("Hello World")
            >>> 
            >>> # Screenshot
            >>> img = sandbox.desktop.screenshot()
            >>> with open('screen.png', 'wb') as f:
            ...     f.write(img)
            >>> 
            >>> # If desktop not available:
            >>> try:
            ...     sandbox.desktop.click(100, 100)
            ... except DesktopNotAvailableError as e:
            ...     print(e.message)
            ...     print(e.install_command)
        """
        if self._desktop is None:
            self._ensure_agent_client()
            self._desktop = Desktop(self._agent_client)
        return self._desktop
    
    @property
    def env(self) -> EnvironmentVariables:
        """
        Environment variables resource.
        
        Lazy initialization - gets agent URL on first access.
        
        Provides methods for:
        - Get all environment variables
        - Set/replace all environment variables
        - Update specific environment variables (merge)
        - Delete environment variables
        
        Returns:
            EnvironmentVariables resource instance
        
        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> 
            >>> # Get all environment variables
            >>> env = sandbox.env.get_all()
            >>> print(env.get("PATH"))
            >>> 
            >>> # Set a single variable
            >>> sandbox.env.set("API_KEY", "sk-prod-xyz")
            >>> 
            >>> # Update multiple variables (merge)
            >>> sandbox.env.update({
            ...     "NODE_ENV": "production",
            ...     "DEBUG": "false"
            ... })
            >>> 
            >>> # Get a specific variable
            >>> api_key = sandbox.env.get("API_KEY")
            >>> 
            >>> # Delete a variable
            >>> sandbox.env.delete("DEBUG")
        """
        if self._env is None:
            self._ensure_agent_client()
            self._env = EnvironmentVariables(self._agent_client)
        return self._env
    
    @property
    def cache(self) -> Cache:
        """
        Cache management resource.
        
        Lazy initialization - gets agent URL on first access.
        
        Provides methods for:
        - Get cache statistics
        - Clear cache
        
        Returns:
            Cache resource instance
        
        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> 
            >>> # Get cache stats
            >>> stats = sandbox.cache.stats()
            >>> print(f"Cache hits: {stats['hits']}")
            >>> print(f"Cache size: {stats['size']} MB")
            >>> 
            >>> # Clear cache
            >>> sandbox.cache.clear()
        """
        if self._cache is None:
            self._ensure_agent_client()
            self._cache = Cache(self._agent_client)
        return self._cache
    
    @property
    def terminal(self) -> Terminal:
        """
        Interactive terminal resource via WebSocket.
        
        Lazy initialization - gets agent URL and WebSocket client on first access.
        
        Provides methods for:
        - Connect to interactive terminal
        - Send input to terminal
        - Resize terminal
        - Receive output stream
        
        Returns:
            Terminal resource instance
        
        Note:
            Requires websockets library: pip install websockets
        
        Example:
            >>> import asyncio
            >>> 
            >>> async def run_terminal():
            ...     sandbox = Sandbox.create(template="code-interpreter")
            ...     
            ...     # Connect to terminal
            ...     async with await sandbox.terminal.connect() as ws:
            ...         # Send command
            ...         await sandbox.terminal.send_input(ws, "ls -la\\n")
            ...         
            ...         # Receive output
            ...         async for message in sandbox.terminal.iter_output(ws):
            ...             if message['type'] == 'output':
            ...                 print(message['data'], end='')
            ...             elif message['type'] == 'exit':
            ...                 break
            >>> 
            >>> asyncio.run(run_terminal())
        """
        if self._terminal is None:
            self._ensure_ws_client()
            self._terminal = Terminal(self._ws_client)
        return self._terminal
    
    def _ensure_agent_client(self) -> None:
        """Ensure agent HTTP client is initialized."""
        if self._agent_client is None:
            info = self.get_info()
            agent_url = info.public_host.rstrip('/')
            
            # Ensure JWT token is valid
            self._ensure_valid_token()
            
            # Get JWT token for agent authentication
            jwt_token = _token_cache.get(self.sandbox_id)
            jwt_token_str = jwt_token.token if jwt_token else None
            
            # Create agent client with token refresh callback
            def refresh_token_callback():
                """Callback to refresh token when agent returns 401."""
                self.refresh_token()
                token_data = _token_cache.get(self.sandbox_id)
                return token_data.token if token_data else None
            
            self._agent_client = AgentHTTPClient(
                agent_url=agent_url,
                jwt_token=jwt_token_str,
                timeout=60,  # Default 60s for agent operations
                max_retries=3,
                token_refresh_callback=refresh_token_callback
            )
            logger.debug(f"Agent client initialized: {agent_url}")
            
            # Wait for agent to be ready on first access
            # Agent might need a moment after sandbox creation
            import time
            max_wait = 30  # seconds (increased for reliability)
            retry_delay = 1.5  # seconds between retries
            
            for attempt in range(max_wait):
                try:
                    # Quick health check with short timeout
                    health = self._agent_client.get("/health", operation="agent health check", timeout=5)
                    if health.json().get("status") == "healthy":
                        logger.debug(f"Agent ready after {attempt * retry_delay:.1f}s")
                        break
                except Exception as e:
                    if attempt < max_wait - 1:
                        time.sleep(retry_delay)
                        continue
                    # Don't log warning - agent will usually work anyway
                    logger.debug(f"Agent health check timeout after {max_wait * retry_delay:.1f}s: {e}")
    
    def _ensure_ws_client(self) -> None:
        """Ensure WebSocket client is initialized and agent is ready."""
        if self._ws_client is None:
            # First ensure agent HTTP client is ready (which waits for agent)
            self._ensure_agent_client()
            
            info = self.get_info()
            agent_url = info.public_host.rstrip('/')
            token = self.get_token()
            self._ws_client = WebSocketClient(agent_url, token)
            logger.debug(f"WebSocket client initialized: {agent_url}")
    
    def refresh_token(self) -> None:
        """
        Refresh JWT token for agent authentication.
        Called automatically when token is about to expire (<1 hour left).
        """
        response = self._client.post(f"/v1/sandboxes/{self.sandbox_id}/token/refresh")

        # Store token using shared utility function
        store_token_from_response(self.sandbox_id, response)

        # Update agent client's JWT token if already initialized
        if self._agent_client is not None and "auth_token" in response:
            self._agent_client.update_jwt_token(response["auth_token"])
        if self._ws_client is not None and "auth_token" in response:
            self._ws_client.update_jwt_token(response["auth_token"])
    
    def _ensure_valid_token(self) -> None:
        """
        Ensure JWT token is valid (not expired or expiring soon).
        Auto-refreshes if less than 1 hour remaining.
        """
        token_data = _token_cache.get(self.sandbox_id)
        
        if token_data is None:
            # No token yet, try to refresh
            try:
                self.refresh_token()
            except Exception:
                # Token might not be available yet (e.g., old sandbox)
                pass
            return
        
        # Check if token expires soon (< 1 hour)
        now = datetime.now(token_data.expires_at.tzinfo)
        hours_left = (token_data.expires_at - now).total_seconds() / 3600
        
        if hours_left < 1:
            # Refresh token
            self.refresh_token()
    
    def get_token(self) -> str:
        """
        Get current JWT token (for advanced use cases).
        Automatically refreshes if needed.
        
        Returns:
            JWT token string
        
        Raises:
            HopxError: If no token available
        """
        self._ensure_valid_token()
        
        token_data = _token_cache.get(self.sandbox_id)
        if token_data is None:
            from .errors import HopxError
            raise HopxError('No JWT token available for sandbox')
        
        return token_data.token
    
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
    ) -> "Sandbox":
        """
        Create a new sandbox from a template.
        
        Resources (vcpu, memory, disk) are ALWAYS loaded from the template.
        You cannot specify custom resources - create a template first with desired resources.
        
        Args:
            template: Template name (e.g., "my-python-template")
            template_id: Template ID (alternative to template name)
            region: Preferred region (optional, auto-selected if not specified)
            timeout_seconds: Auto-kill timeout in seconds (optional, default: no timeout)
            internet_access: Enable internet access (optional, default: True)
            env_vars: Environment variables to set in the sandbox (optional)
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL (default: production)
        
        Returns:
            Sandbox instance
        
        Raises:
            ValidationError: Invalid parameters
            ResourceLimitError: Insufficient resources
            APIError: API request failed
        
        Examples:
            >>> # Create from template ID with timeout
            >>> sandbox = Sandbox.create(
            ...     template_id="291",
            ...     timeout_seconds=300,
            ...     internet_access=True
            ... )
            >>> print(sandbox.get_info().public_host)
            
            >>> # Create from template name without internet
            >>> sandbox = Sandbox.create(
            ...     template="my-python-template",
            ...     env_vars={"DEBUG": "true"},
            ...     internet_access=False
            ... )
        """
        # Create HTTP client
        client = HTTPClient(api_key=api_key, base_url=base_url)

        # Build request payload using shared utility
        data = build_sandbox_create_payload(
            template=template,
            template_id=template_id,
            region=region,
            timeout_seconds=timeout_seconds,
            internet_access=internet_access,
            env_vars=env_vars,
        )

        # Create sandbox via API
        response = client.post("/v1/sandboxes", json=data)
        sandbox_id = response["id"]

        # Store JWT token from create response using shared utility
        store_token_from_response(sandbox_id, response)

        # Create Sandbox instance
        instance = cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )

        # Set environment variables if provided
        # The API doesn't automatically set env_vars in the sandbox runtime,
        # so we need to explicitly set them via the env API
        if env_vars:
            logger.debug(f"Setting {len(env_vars)} environment variables in sandbox")
            instance.env.update(env_vars)

        return instance
    
    @classmethod
    def debug(
        cls,
        agent_url: str,
        jwt_token: str,
        sandbox_id: str = "debug",
    ) -> "Sandbox":
        """
        Connect directly to agent for debugging (bypass public API).
        
        Useful for testing SDK against a specific agent without creating a sandbox.
        
        Args:
            agent_url: Agent URL (e.g., "https://7777-xxx.vms.hopx.dev" or "wss://...")
            jwt_token: JWT token for agent authentication
            sandbox_id: Sandbox ID (default: "debug")
        
        Returns:
            Sandbox instance connected directly to agent
        
        Example:
            >>> sandbox = Sandbox.debug(
            ...     agent_url="https://7777-xxx.vms.hopx.dev",
            ...     jwt_token="eyJhbGciOi..."
            ... )
            >>> result = sandbox.run_code("print('Hello')")
        """
        from datetime import datetime, timedelta
        
        # Remove wss:// prefix if present (use https://)
        if agent_url.startswith("wss://"):
            agent_url = "https://" + agent_url[6:]
        elif agent_url.startswith("ws://"):
            agent_url = "http://" + agent_url[5:]
        
        # Create sandbox instance (no API key needed)
        sandbox = cls(
            sandbox_id=sandbox_id,
            api_key="debug",
            base_url="https://api.hopx.dev",
        )
        
        # Store JWT token in cache
        _token_cache[sandbox_id] = TokenData(
            token=jwt_token,
            expires_at=datetime.now() + timedelta(hours=24),  # Long expiry for debug
        )
        
        # Initialize agent client directly
        from ._agent_client import AgentHTTPClient
        
        def token_refresh_callback():
            # For debug mode, token refresh is not supported
            return None
        
        sandbox._agent_client = AgentHTTPClient(
            agent_url,
            jwt_token=jwt_token,
            token_refresh_callback=token_refresh_callback,
        )
        
        return sandbox
    
    @classmethod
    def connect(
        cls,
        sandbox_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> "Sandbox":
        """
        Connect to an existing sandbox.
        
        NEW JWT Behavior:
        - If VM is paused → resumes it and refreshes JWT token
        - If VM is stopped → raises error (cannot connect to stopped VM)
        - If VM is running/active → refreshes JWT token
        - Stores JWT token for agent authentication
        
        Args:
            sandbox_id: Sandbox ID
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
        
        Returns:
            Sandbox instance
        
        Raises:
            NotFoundError: Sandbox not found
            HopxError: If sandbox is stopped or in invalid state
        
        Example:
            >>> sandbox = Sandbox.connect("1761048129dsaqav4n")
            >>> info = sandbox.get_info()
            >>> print(info.status)
        """
        # Create instance
        instance = cls(
            sandbox_id=sandbox_id,
            api_key=api_key,
            base_url=base_url,
        )
        
        # Get current VM status
        info = instance.get_info()
        
        # Handle different VM states
        if info.status == "stopped":
            from .errors import HopxError
            raise HopxError(
                f"Cannot connect to stopped sandbox {sandbox_id}. "
                "Please create a new sandbox."
            )
        
        if info.status == "paused":
            # Resume paused VM
            instance.resume()
        
        if info.status not in ("running", "paused"):
            from .errors import HopxError
            raise HopxError(
                f"Cannot connect to sandbox {sandbox_id} with status '{info.status}'. "
                "Expected 'running' or 'paused'."
            )
        
        # Refresh JWT token for agent authentication
        instance.refresh_token()
        
        return instance
    
    @classmethod
    def iter(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Iterator["Sandbox"]:
        """
        Lazy iterator for sandboxes.
        
        Yields sandboxes one by one, fetching pages as needed.
        Doesn't load all sandboxes into memory at once.
        
        Args:
            status: Filter by status (running, stopped, paused, creating)
            region: Filter by region
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
        
        Yields:
            Sandbox instances
        
        Example:
            >>> # Lazy loading - fetches pages as needed
            >>> for sandbox in Sandbox.iter(status="running"):
            ...     print(f"{sandbox.sandbox_id}")
            ...     if found:
            ...         break  # Doesn't fetch remaining pages!
        """
        client = HTTPClient(api_key=api_key, base_url=base_url)
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
            
            logger.debug(f"Fetching sandboxes page (cursor: {cursor})")
            response = client.get("/v1/sandboxes", params=params)
            
            for item in response.get("data", []):
                yield cls(
                    sandbox_id=item["id"],
                    api_key=api_key,
                    base_url=base_url,
                )
            
            has_more = response.get("has_more", False)
            cursor = response.get("next_cursor")
            
            if has_more:
                logger.debug(f"More results available, next cursor: {cursor}")
    
    @classmethod
    def list(
        cls,
        *,
        status: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List["Sandbox"]:
        """
        List all sandboxes (loads all into memory).
        
        For lazy loading (better memory usage), use Sandbox.iter() instead.
        
        Args:
            status: Filter by status (running, stopped, paused, creating)
            region: Filter by region
            limit: Maximum number of results (default: 100)
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL
        
        Returns:
            List of Sandbox instances (all loaded into memory)
        
        Example:
            >>> # List all running sandboxes (loads all into memory)
            >>> sandboxes = Sandbox.list(status="running")
            >>> for sb in sandboxes:
            ...     print(f"{sb.sandbox_id}")
            
            >>> # For better memory usage, use iter():
            >>> for sb in Sandbox.iter(status="running"):
            ...     print(f"{sb.sandbox_id}")
        """
        client = HTTPClient(api_key=api_key, base_url=base_url)
        
        params = remove_none_values({
            "status": status,
            "region": region,
            "limit": limit,
        })
        
        response = client.get("/v1/sandboxes", params=params)
        sandboxes_data = response.get("data", [])
        
        # Create Sandbox instances
        return [
            cls(
                sandbox_id=sb["id"],
                api_key=api_key,
                base_url=base_url,
            )
            for sb in sandboxes_data
        ]
    
    @classmethod
    def list_templates(
        cls,
        *,
        category: Optional[str] = None,
        language: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> List[Template]:
        """
        List available templates.

        Args:
            category: Filter by category (development, infrastructure, operating-system)
            language: Filter by language (python, nodejs, etc.)
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL

        Returns:
            List of Template objects

        Example:
            >>> templates = Sandbox.list_templates()
            >>> for t in templates:
            ...     print(f"{t.name}: {t.display_name}")

            >>> # Filter by category
            >>> dev_templates = Sandbox.list_templates(category="development")
        """
        client = HTTPClient(api_key=api_key, base_url=base_url)

        # Build query params using shared utility
        params = build_list_templates_params(category=category, language=language)

        response = client.get("/v1/templates", params=params)

        # Parse response using shared utility
        return _parse_template_list_response(response)
    
    @classmethod
    def get_template(
        cls,
        name: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Template:
        """
        Get template details.

        Args:
            name: Template name
            api_key: API key (or use HOPX_API_KEY env var)
            base_url: API base URL

        Returns:
            Template object

        Raises:
            NotFoundError: Template not found

        Example:
            >>> template = Sandbox.get_template("code-interpreter")
            >>> print(template.description)
            >>> print(f"Default: {template.default_resources.vcpu} vCPU")
        """
        client = HTTPClient(api_key=api_key, base_url=base_url)
        response = client.get(f"/v1/templates/{name}")

        # Parse response using shared utility
        return _parse_template_response(response)

    @classmethod
    def delete_template(
        cls,
        template_id: str,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
    ) -> Dict[str, Any]:
        """
        Delete a custom template.

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
            >>> # Delete a custom template by ID
            >>> result = Sandbox.delete_template("template_123abc")
            >>> print(result)
        """
        client = HTTPClient(api_key=api_key, base_url=base_url)
        response = client.delete(f"/v1/templates/{template_id}")
        return response

    @classmethod
    def health_check(
        cls,
        *,
        base_url: str = "https://api.hopx.dev",
    ) -> Dict[str, Any]:
        """
        Check API health status.

        This endpoint does not require authentication and can be used to verify
        API availability and connectivity.

        Args:
            base_url: API base URL (default: production)

        Returns:
            Dict with health status information

        Example:
            >>> health = Sandbox.health_check()
            >>> print(health)  # {'status': 'ok', ...}

            >>> # Check custom/staging API
            >>> health = Sandbox.health_check(base_url="https://staging-api.hopx.dev")
        """
        # Use a minimal client without API key for health check
        import httpx
        try:
            response = httpx.get(f"{base_url.rstrip('/')}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            from .errors import NetworkError
            raise NetworkError(f"Health check failed: {e}")

    # =============================================================================
    # INSTANCE METHODS (for managing individual sandbox)
    # =============================================================================
    
    def get_info(self) -> SandboxInfo:
        """
        Get current sandbox information.

        Returns:
            SandboxInfo with current state

        Raises:
            NotFoundError: Sandbox not found

        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> info = sandbox.get_info()
            >>> print(f"Status: {info.status}")
            >>> print(f"URL: {info.public_host}")
            >>> print(f"Internet access: {info.internet_access}")
            >>> if info.expires_at:
            ...     print(f"Expires at: {info.expires_at}")
        """
        response = self._client.get(f"/v1/sandboxes/{self.sandbox_id}")

        # Parse response using shared utility function
        return _parse_sandbox_info_response(response)

    def get_preview_url(self, port: int = 7777) -> str:
        """
        Get preview URL for accessing a service running on a specific port.

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
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> sandbox.run_code_background('''
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
            >>> url = sandbox.get_preview_url(8080)
            >>> print(f"Access your app at: {url}")
            >>> # Output: https://8080-sandbox123.eu-1001.vms.hopx.dev/
            >>>
            >>> # Get agent URL (default port 7777)
            >>> agent = sandbox.get_preview_url()
            >>> print(f"Sandbox agent: {agent}")
        """
        info = self.get_info()
        public_host = info.public_host

        # Parse public_host to extract base domain
        # Expected format: https://7777-sandbox123.eu-1001.vms.hopx.dev/
        # or: https://sandbox123.vms.hopx.dev/

        import re
        from .errors import HopxError

        # Remove protocol and trailing slash
        host = public_host.replace('https://', '').replace('http://', '').rstrip('/')

        # Pattern 1: {port}-{sandbox_id}.{region}.vms.hopx.dev
        match = re.match(r'^(?:\d+-)?([^.]+)\.(.+\.vms\.hopx\.dev)$', host)
        if match:
            sandbox_part = match.group(1)
            domain_part = match.group(2)
            return f"https://{port}-{sandbox_part}.{domain_part}/"

        # Pattern 2: {sandbox_id}.{region}.vms.hopx.dev (no port prefix)
        match = re.match(r'^([^.]+)\.(.+\.vms\.hopx\.dev)$', host)
        if match:
            sandbox_part = match.group(1)
            domain_part = match.group(2)
            return f"https://{port}-{sandbox_part}.{domain_part}/"

        # Fallback: couldn't parse, return best guess
        logger.warning(f"Could not parse public_host format: {public_host}")
        raise HopxError(
            f"Unable to determine preview URL from public_host: {public_host}. "
            "Please ensure sandbox is running and try again."
        )

    @property
    def agent_url(self) -> str:
        """
        Get the sandbox agent URL (port 7777).

        This is a convenience property that returns the preview URL for the
        default sandbox agent running on port 7777.

        Returns:
            Agent URL (equivalent to get_preview_url(7777))

        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> print(f"Agent URL: {sandbox.agent_url}")
            >>> # Output: https://7777-sandbox123.eu-1001.vms.hopx.dev/
        """
        return self.get_preview_url(7777)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get VM agent information.

        Returns comprehensive information about the VM agent including version,
        OS, architecture, available endpoints, and supported features.

        Returns:
            Dict with agent information:
            - agent: Agent name (e.g., "hopx-vm-agent-desktop")
            - agent_version: Agent version (e.g., "3.2.8")
            - vm_id: VM identifier
            - os: Operating system
            - arch: Architecture (e.g., "amd64", "arm64")
            - go_version: Go version used to build agent
            - vm_ip: VM IP address
            - vm_port: VM port
            - start_time: Agent start timestamp
            - uptime: Uptime in seconds
            - endpoints: Map of available endpoints
            - features: Available features dict

        Example:
            >>> info = sandbox.get_agent_info()
            >>> print(f"Agent: {info['agent']} v{info['agent_version']}")
            >>> print(f"OS: {info['os']} ({info['arch']})")
            >>> print(f"Uptime: {info['uptime']}s")
            >>> print(f"Features: {list(info['features'].keys())}")

        Note:
            Requires Agent v3.1.0+. GET /info endpoint.
        """
        self._ensure_agent_client()

        logger.debug("Getting agent info")

        response = self._agent_client.get(
            "/info",
            operation="get agent info"
        )

        return response.json()

    def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get real-time agent metrics.

        Returns agent performance and health metrics including uptime,
        request counts, error counts, and performance statistics.

        Returns:
            Dict with metrics including:
            - uptime_seconds: Agent uptime
            - total_requests: Total requests count
            - total_errors: Total errors count
            - requests_total: Per-endpoint request counts
            - avg_duration_ms: Average request duration by endpoint

        Example:
            >>> metrics = sandbox.get_agent_metrics()
            >>> print(f"Uptime: {metrics['uptime_seconds']}s")
            >>> print(f"Total requests: {metrics.get('total_requests', 0)}")
            >>> print(f"Errors: {metrics.get('total_errors', 0)}")

        Note:
            Requires Agent v3.1.0+. GET /metrics/snapshot endpoint.
        """
        self._ensure_agent_client()

        logger.debug("Getting agent metrics")

        response = self._agent_client.get(
            "/metrics/snapshot",
            operation="get agent metrics"
        )

        return response.json()

    def list_system_processes(self) -> List[Dict[str, Any]]:
        """
        List all running system processes in the sandbox.

        Returns a list of all processes running in the VM, not just background
        code executions. Useful for debugging and monitoring system state.

        Returns:
            List of dicts with process information:
            - pid: Process ID
            - name: Process name
            - status: Process status
            - cpu_percent: CPU usage percentage
            - memory_mb: Memory usage in MB
            - command: Full command line

        Example:
            >>> processes = sandbox.list_system_processes()
            >>> for proc in processes:
            ...     print(f"{proc['pid']}: {proc['name']} (CPU: {proc.get('cpu_percent', 0)}%)")

        Note:
            Requires Agent v3.2.0+. GET /processes endpoint.
        """
        self._ensure_agent_client()

        logger.debug("Listing system processes")

        response = self._agent_client.get(
            "/processes",
            operation="list system processes"
        )

        return response.json().get("processes", [])

    def get_jupyter_sessions(self) -> List[Dict[str, Any]]:
        """
        Get Jupyter kernel session status.

        Returns information about active Jupyter kernel sessions, useful for
        debugging kernel state and managing long-running Python executions.

        Returns:
            List of active Jupyter sessions with:
            - kernel_id: Kernel identifier
            - execution_state: idle, busy, starting
            - connections: Number of connections
            - last_activity: Last activity timestamp

        Example:
            >>> sessions = sandbox.get_jupyter_sessions()
            >>> for session in sessions:
            ...     print(f"Kernel {session['kernel_id']}: {session['execution_state']}")

        Note:
            Requires Agent v3.2.0+ with Jupyter support. GET /jupyter/sessions endpoint.
        """
        self._ensure_agent_client()

        logger.debug("Getting Jupyter sessions")

        response = self._agent_client.get(
            "/jupyter/sessions",
            operation="get jupyter sessions"
        )

        return response.json().get("sessions", [])

    def run_code(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
    ) -> ExecutionResult:
        """
        Execute code with rich output capture (plots, DataFrames, etc.).
        
        This method automatically captures visual outputs like matplotlib plots,
        pandas DataFrames, and plotly charts.
        
        Args:
            code: Code to execute
            language: Language (python, javascript, bash, go)
            timeout: Execution timeout in seconds (default: 60)
            env: Optional environment variables for this execution only.
                 Priority: Request env > Global env > Agent env
            working_dir: Working directory for execution (default: /workspace)
        
        Returns:
            ExecutionResult with stdout, stderr, rich_outputs
        
        Raises:
            CodeExecutionError: If execution fails
            TimeoutError: If execution times out
        
        Example:
            >>> # Simple code execution
            >>> result = sandbox.run_code('print("Hello, World!")')
            >>> print(result.stdout)  # "Hello, World!\n"
            >>> 
            >>> # With environment variables
            >>> result = sandbox.run_code(
            ...     'import os; print(os.environ["API_KEY"])',
            ...     env={"API_KEY": "sk-test-123", "DEBUG": "true"}
            ... )
            >>> 
            >>> # Execute with matplotlib plot
            >>> code = '''
            ... import matplotlib.pyplot as plt
            ... plt.plot([1, 2, 3, 4])
            ... plt.savefig('/workspace/plot.png')
            ... '''
            >>> result = sandbox.run_code(code)
            >>> print(f"Generated {result.rich_count} outputs")
            >>> 
            >>> # Check for errors
            >>> result = sandbox.run_code('print(undefined_var)')
            >>> if not result.success:
            ...     print(f"Error: {result.stderr}")
            >>> 
            >>> # With custom timeout for long-running code
            >>> result = sandbox.run_code(long_code, timeout=300)
        """
        self._ensure_agent_client()
        
        logger.debug(f"Executing {language} code ({len(code)} chars)")
        
        # Build request payload
        payload = {
            "language": language,
            "code": code,
            "working_dir": working_dir,
            "timeout": timeout
        }
        
        # Add optional environment variables
        if env:
            payload["env"] = env
        
        # Use /execute endpoint for code execution
        response = self._agent_client.post(
            "/execute",
            json=payload,
            operation="execute code",
            context={"language": language},
            timeout=timeout + 5  # Add buffer to HTTP timeout
        )
        
        data = response.json() if response.content else {}

        # Parse rich outputs using shared utility function
        rich_outputs = _parse_rich_outputs(data)

        # Create result
        result = ExecutionResult(
            success=data.get("success", True) if data else False,
            stdout=data.get("stdout", "") if data else "",
            stderr=data.get("stderr", "") if data else "",
            exit_code=data.get("exit_code", 0) if data else 1,
            execution_time=data.get("execution_time", 0.0) if data else 0.0,
            rich_outputs=rich_outputs
        )
        
        return result
    
    def run_code_async(
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
        
        For long-running code (>5 minutes). Agent will POST results to callback_url when complete.
        
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
            >>> # Start async execution
            >>> response = sandbox.run_code_async(
            ...     code='import time; time.sleep(600); print("Done!")',
            ...     callback_url='https://app.com/webhooks/ml/training',
            ...     callback_headers={'Authorization': 'Bearer secret'},
            ...     callback_signature_secret='webhook-secret-123'
            ... )
            >>> print(f"Execution ID: {response['execution_id']}")
            >>> 
            >>> # Agent will POST to callback_url when done:
            >>> # POST https://app.com/webhooks/ml/training
            >>> # X-HOPX-Signature: sha256=...
            >>> # X-HOPX-Timestamp: 1698765432
            >>> # Authorization: Bearer secret
            >>> # {
            >>> #   "execution_id": "abc123",
            >>> #   "status": "completed",
            >>> #   "stdout": "Done!",
            >>> #   "stderr": "",
            >>> #   "exit_code": 0,
            >>> #   "execution_time": 600.123
            >>> # }
        """
        self._ensure_agent_client()
        
        logger.debug(f"Starting async {language} execution ({len(code)} chars)")
        
        # Build request payload
        payload = {
            "code": code,
            "language": language,
            "timeout": timeout,
            "working_dir": working_dir,
            "callback_url": callback_url,
        }
        
        if env:
            payload["env"] = env
        if callback_headers:
            payload["callback_headers"] = callback_headers
        if callback_signature_secret:
            payload["callback_signature_secret"] = callback_signature_secret
        
        response = self._agent_client.post(
            "/execute/async",
            json=payload,
            operation="async execute code",
            context={"language": language},
            timeout=10  # Quick response
        )
        
        return response.json()
    
    def run_code_background(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 300,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace",
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
            working_dir: Working directory (default: /workspace)
            name: Optional process name for identification
        
        Returns:
            Dict with process_id, execution_id, status
        
        Example:
            >>> # Start background execution
            >>> result = sandbox.run_code_background(
            ...     code='long_running_task()',
            ...     name='ml-training',
            ...     env={"GPU": "enabled"}
            ... )
            >>> process_id = result['process_id']
            >>> 
            >>> # Check status
            >>> processes = sandbox.list_processes()
            >>> for p in processes:
            ...     if p['process_id'] == process_id:
            ...         print(f"Status: {p['status']}")
            >>> 
            >>> # Kill if needed
            >>> sandbox.kill_process(process_id)
        """
        self._ensure_agent_client()
        
        logger.debug(f"Starting background {language} execution ({len(code)} chars)")
        
        # Build request payload
        payload = {
            "code": code,
            "language": language,
            "timeout": timeout,
            "working_dir": working_dir,
        }
        
        if env:
            payload["env"] = env
        if name:
            payload["name"] = name
        
        response = self._agent_client.post(
            "/execute/background",
            json=payload,
            operation="background execute code",
            context={"language": language},
            timeout=10  # Quick response
        )
        
        return response.json()
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """
        List all background execution processes.
        
        Returns:
            List of process dictionaries with status
        
        Example:
            >>> processes = sandbox.list_processes()
            >>> for p in processes:
            ...     print(f"{p['name']}: {p['status']} (PID: {p['process_id']})")
        """
        self._ensure_agent_client()
        
        response = self._agent_client.get(
            "/execute/processes",
            operation="list processes"
        )
        
        data = response.json()
        return data.get("processes", [])
    
    def kill_process(self, process_id: str) -> Dict[str, Any]:
        """
        Kill a background execution process.
        
        Args:
            process_id: Process ID to kill
        
        Returns:
            Dict with confirmation message
        
        Example:
            >>> sandbox.kill_process("proc_abc123")
        """
        self._ensure_agent_client()
        
        response = self._agent_client.post(
            f"/execute/kill/{process_id}",
            operation="kill process",
            context={"process_id": process_id}
        )
        
        return response.json()
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """
        Get current system metrics snapshot.
        
        Returns:
            Dict with system metrics (CPU, memory, disk), process metrics, cache stats
        
        Example:
            >>> metrics = sandbox.get_metrics_snapshot()
            >>> print(f"CPU: {metrics['system']['cpu']['usage_percent']}%")
            >>> print(f"Memory: {metrics['system']['memory']['usage_percent']}%")
            >>> print(f"Processes: {metrics['process']['count']}")
            >>> print(f"Cache size: {metrics['cache']['size']}")
        """
        self._ensure_agent_client()
        
        response = self._agent_client.get(
            "/metrics/snapshot",
            operation="get metrics snapshot"
        )
        
        return response.json()
    
    async def run_code_stream(
        self,
        code: str,
        *,
        language: str = "python",
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
        working_dir: str = "/workspace"
    ):
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
            ...     sandbox = Sandbox.create(template="code-interpreter")
            ...     
            ...     code = '''
            ...     import time
            ...     for i in range(5):
            ...         print(f"Step {i+1}/5")
            ...         time.sleep(1)
            ...     '''
            ...     
            ...     async for message in sandbox.run_code_stream(code):
            ...         if message['type'] == 'stdout':
            ...             print(message['data'], end='')
            ...         elif message['type'] == 'result':
            ...             print(f"\\nExit code: {message['exit_code']}")
            >>> 
            >>> asyncio.run(stream_execution())
        """
        self._ensure_ws_client()
        
        # Connect to streaming endpoint
        async with await self._ws_client.connect("/execute/stream") as ws:
            # Send execution request
            request = {
                "type": "execute",
                "code": code,
                "language": language,
                "timeout": timeout,
                "working_dir": working_dir
            }
            if env:
                request["env"] = env
            
            await self._ws_client.send_message(ws, request)
            
            # Stream messages
            async for message in self._ws_client.iter_messages(ws):
                yield message
                
                # Stop on complete
                if message.get('type') == 'complete':
                    break
    
    def set_timeout(self, seconds: int) -> None:
        """
        Extend sandbox timeout.

        Sets a new timeout duration. The sandbox will be automatically terminated
        after the specified number of seconds from now.

        Args:
            seconds: New timeout duration in seconds from now (must be > 0)

        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter", timeout_seconds=300)
            >>> # Extend to 10 minutes from now
            >>> sandbox.set_timeout(600)
            >>>
            >>> # Extend to 1 hour
            >>> sandbox.set_timeout(3600)

        Raises:
            HopxError: If the API request fails

        Note:
            This feature may not be available in all plans.
        """
        logger.debug(f"Setting timeout to {seconds}s for sandbox {self.sandbox_id}")

        # Build payload using shared utility
        payload = build_set_timeout_payload(seconds)

        self._client.put(
            f"/v1/sandboxes/{self.sandbox_id}/timeout",
            json=payload
        )

        logger.info(f"Timeout updated to {seconds}s")

    def pause(self) -> None:
        """
        Pause the sandbox.
        
        A paused sandbox can be resumed with resume().
        
        Example:
            >>> sandbox.pause()
            >>> # ... do something else ...
            >>> sandbox.resume()
        """
        self._client.post(f"/v1/sandboxes/{self.sandbox_id}/pause")
    
    def resume(self) -> None:
        """
        Resume a paused sandbox.
        
        Example:
            >>> sandbox.resume()
        """
        self._client.post(f"/v1/sandboxes/{self.sandbox_id}/resume")
    
    def kill(self) -> None:
        """
        Destroy the sandbox immediately.
        
        This action is irreversible. All data in the sandbox will be lost.
        
        Example:
            >>> sandbox = Sandbox.create(template="code-interpreter")
            >>> # ... use sandbox ...
            >>> sandbox.kill()  # Clean up
        """
        self._client.delete(f"/v1/sandboxes/{self.sandbox_id}")
    
    # =============================================================================
    # CONTEXT MANAGER (auto-cleanup)
    # =============================================================================
    
    def __enter__(self) -> "Sandbox":
        """Context manager entry."""
        return self
    
    def __exit__(self, *args) -> None:
        """Context manager exit - auto cleanup."""
        try:
            self.kill()
        except Exception:
            # Ignore errors on cleanup
            pass
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def __repr__(self) -> str:
        return f"<Sandbox {self.sandbox_id}>"
    
    def __str__(self) -> str:
        try:
            info = self.get_info()
            return f"Sandbox(id={self.sandbox_id}, status={info.status}, url={info.public_host})"
        except Exception:
            return f"Sandbox(id={self.sandbox_id})"

