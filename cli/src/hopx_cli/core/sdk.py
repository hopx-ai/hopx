"""SDK client initialization and caching.

Provides functions to work with the Hopx SDK for CLI commands.
Implements connection caching for sandbox instances.
"""

from hopx_ai import AsyncSandbox, Sandbox

from .config import CLIConfig

# Global cache for sandbox instances by ID
_sandbox_cache: dict[str, Sandbox] = {}
_async_sandbox_cache: dict[str, AsyncSandbox] = {}


def list_sandboxes(
    config: CLIConfig,
    *,
    status: str | None = None,
    region: str | None = None,
    limit: int = 100,
) -> list[Sandbox]:
    """List all sandboxes.

    Args:
        config: CLI configuration
        status: Filter by status
        region: Filter by region
        limit: Maximum number of results

    Returns:
        List of Sandbox objects

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()
    result = Sandbox.list(
        status=status,
        region=region,
        limit=limit,
        api_key=api_key,
        base_url=config.base_url,
    )
    return list(result) if result else []


def create_sandbox(
    config: CLIConfig,
    *,
    template: str | None = None,
    template_id: str | None = None,
    region: str | None = None,
    timeout: int | None = None,
    internet_access: bool | None = None,
    env_vars: dict[str, str] | None = None,
) -> Sandbox:
    """Create a new sandbox.

    Args:
        config: CLI configuration
        template: Template name
        template_id: Template ID (takes precedence over template)
        region: Preferred region
        timeout: Auto-kill timeout in seconds
        internet_access: Enable internet access
        env_vars: Environment variables

    Returns:
        Created Sandbox instance

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()
    return Sandbox.create(
        template=template,
        template_id=template_id,
        region=region,
        timeout_seconds=timeout,
        internet_access=internet_access,
        env_vars=env_vars,
        api_key=api_key,
        base_url=config.base_url,
    )


def get_sandbox(
    config: CLIConfig,
    sandbox_id: str,
    *,
    use_cache: bool = True,
) -> Sandbox:
    """Get or create a sync Sandbox instance for an existing sandbox.

    Creates a new Sandbox instance or returns a cached instance if one exists
    for the given sandbox ID.

    Args:
        config: CLI configuration
        sandbox_id: Sandbox ID to connect to
        use_cache: Whether to use cached instance

    Returns:
        Sandbox instance

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()

    # Check cache if enabled
    if use_cache:
        cache_key = f"{api_key}:{sandbox_id}"
        if cache_key in _sandbox_cache:
            return _sandbox_cache[cache_key]

    # Create new instance
    sandbox = Sandbox.connect(
        sandbox_id=sandbox_id,
        api_key=api_key,
        base_url=config.base_url,
    )

    # Cache the instance
    if use_cache:
        cache_key = f"{api_key}:{sandbox_id}"
        _sandbox_cache[cache_key] = sandbox

    return sandbox


async def list_sandboxes_async(
    config: CLIConfig,
    *,
    status: str | None = None,
    region: str | None = None,
    limit: int = 100,
) -> list[AsyncSandbox]:
    """List all sandboxes asynchronously.

    Args:
        config: CLI configuration
        status: Filter by status
        region: Filter by region
        limit: Maximum number of results

    Returns:
        List of AsyncSandbox objects

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()
    result = await AsyncSandbox.list(
        status=status,
        region=region,
        limit=limit,
        api_key=api_key,
        base_url=config.base_url,
    )
    return list(result) if result else []


async def create_sandbox_async(
    config: CLIConfig,
    *,
    template: str | None = None,
    template_id: str | None = None,
    region: str | None = None,
    timeout: int | None = None,
    internet_access: bool | None = None,
    env_vars: dict[str, str] | None = None,
) -> AsyncSandbox:
    """Create a new sandbox asynchronously.

    Args:
        config: CLI configuration
        template: Template name
        template_id: Template ID (takes precedence over template)
        region: Preferred region
        timeout: Auto-kill timeout in seconds
        internet_access: Enable internet access
        env_vars: Environment variables

    Returns:
        Created AsyncSandbox instance

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()
    return await AsyncSandbox.create(
        template=template,
        template_id=template_id,
        region=region,
        timeout_seconds=timeout,
        internet_access=internet_access,
        env_vars=env_vars,
        api_key=api_key,
        base_url=config.base_url,
    )


async def get_sandbox_async(
    config: CLIConfig,
    sandbox_id: str,
    *,
    use_cache: bool = True,
) -> AsyncSandbox:
    """Get or create an async Sandbox instance for an existing sandbox.

    Creates a new AsyncSandbox instance or returns a cached instance if one
    exists for the given sandbox ID.

    Args:
        config: CLI configuration
        sandbox_id: Sandbox ID to connect to
        use_cache: Whether to use cached instance

    Returns:
        AsyncSandbox instance

    Raises:
        ValueError: If API key is not configured
    """
    api_key = config.get_api_key()

    # Check cache if enabled
    if use_cache:
        cache_key = f"{api_key}:{sandbox_id}"
        if cache_key in _async_sandbox_cache:
            return _async_sandbox_cache[cache_key]

    # Create new instance
    sandbox = await AsyncSandbox.connect(
        sandbox_id=sandbox_id,
        api_key=api_key,
        base_url=config.base_url,
    )

    # Cache the instance
    if use_cache:
        cache_key = f"{api_key}:{sandbox_id}"
        _async_sandbox_cache[cache_key] = sandbox

    return sandbox


def clear_sandbox_cache(sandbox_id: str | None = None) -> None:
    """Clear cached sandbox instances.

    Args:
        sandbox_id: Specific sandbox ID to clear (clears all if not provided)
    """
    if sandbox_id:
        # Clear specific sandbox from both caches
        keys_to_remove = [key for key in _sandbox_cache if key.endswith(f":{sandbox_id}")]
        for key in keys_to_remove:
            del _sandbox_cache[key]

        async_keys_to_remove = [
            key for key in _async_sandbox_cache if key.endswith(f":{sandbox_id}")
        ]
        for key in async_keys_to_remove:
            del _async_sandbox_cache[key]
    else:
        # Clear all caches
        _sandbox_cache.clear()
        _async_sandbox_cache.clear()


def get_cached_sandbox_ids() -> list[str]:
    """Get list of cached sandbox IDs.

    Returns:
        List of sandbox IDs currently in cache
    """
    sandbox_ids = set()
    for key in _sandbox_cache:
        if ":" in key:
            sandbox_ids.add(key.split(":", 1)[1])
    for key in _async_sandbox_cache:
        if ":" in key:
            sandbox_ids.add(key.split(":", 1)[1])
    return sorted(sandbox_ids)
