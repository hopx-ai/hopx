"""Core utilities for the Hopx CLI.

This module provides core functionality for the CLI including:
- Configuration management via CLIConfig
- CLI context state via CLIContext
- Error handling and mapping from SDK errors
- Async operation helpers
- SDK client initialization and caching
"""

from .async_helpers import gather_with_concurrency, run_async, run_with_timeout
from .config import CLIConfig
from .context import CLIContext, OutputFormat
from .errors import (
    AuthenticationError,
    CLIError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    handle_errors,
)
from .sdk import (
    clear_sandbox_cache,
    create_sandbox,
    create_sandbox_async,
    get_cached_sandbox_ids,
    get_sandbox,
    get_sandbox_async,
    list_sandboxes,
    list_sandboxes_async,
)
from .version import (
    VersionInfo,
    check_pypi_version,
    compare_versions,
    detect_install_method,
    get_install_method_display,
    get_update_command,
)

__all__ = [
    # Config
    "CLIConfig",
    # Context
    "CLIContext",
    "OutputFormat",
    # Errors
    "CLIError",
    "AuthenticationError",
    "NotFoundError",
    "TimeoutError",
    "NetworkError",
    "RateLimitError",
    "ValidationError",
    "handle_errors",
    # Async helpers
    "run_async",
    "run_with_timeout",
    "gather_with_concurrency",
    # SDK
    "list_sandboxes",
    "list_sandboxes_async",
    "create_sandbox",
    "create_sandbox_async",
    "get_sandbox",
    "get_sandbox_async",
    "clear_sandbox_cache",
    "get_cached_sandbox_ids",
    # Version utilities
    "VersionInfo",
    "check_pypi_version",
    "compare_versions",
    "detect_install_method",
    "get_install_method_display",
    "get_update_command",
]
