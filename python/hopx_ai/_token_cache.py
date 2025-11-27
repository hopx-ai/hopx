"""
Shared JWT token cache for Hopx SDK.

This module provides a global token cache shared between Sandbox and AsyncSandbox.
Token caching reduces unnecessary API calls and improves performance.

The cache is thread-safe for basic operations (dict get/set) and can be safely
used from both sync and async contexts.

Architecture Note:
    Previously, Sandbox and AsyncSandbox each had their own separate token caches,
    which meant tokens couldn't be shared between sync and async instances of the
    same sandbox. This module centralizes token management.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenData:
    """
    JWT token storage with expiration tracking.

    Attributes:
        token: JWT token string
        expires_at: Token expiration datetime (timezone-aware)

    Example:
        >>> from datetime import datetime, timedelta, timezone
        >>> expires = datetime.now(timezone.utc) + timedelta(hours=24)
        >>> token_data = TokenData(token="eyJhbG...", expires_at=expires)
        >>> token_data.token[:10]
        'eyJhbG...'
    """

    token: str
    expires_at: datetime


# Global token cache (shared between Sandbox and AsyncSandbox)
# Maps sandbox_id -> TokenData
_token_cache: Dict[str, TokenData] = {}


def store_token_from_response(sandbox_id: str, response: Dict[str, Any]) -> None:
    """
    Store JWT token from API response in global cache.

    Extracts auth_token and token_expires_at from API response and
    stores in global cache for future use.

    Args:
        sandbox_id: Sandbox ID (cache key)
        response: API response dict containing auth_token and token_expires_at

    Example:
        >>> response = {
        ...     "id": "sandbox_123",
        ...     "auth_token": "eyJhbG...",
        ...     "token_expires_at": "2025-01-16T10:30:00Z"
        ... }
        >>> store_token_from_response("sandbox_123", response)
        >>> get_cached_token("sandbox_123") is not None
        True
    """
    if "auth_token" in response and "token_expires_at" in response:
        _token_cache[sandbox_id] = TokenData(
            token=response["auth_token"],
            expires_at=datetime.fromisoformat(response["token_expires_at"].replace("Z", "+00:00")),
        )


def get_cached_token(sandbox_id: str) -> Optional[TokenData]:
    """
    Get cached JWT token for a sandbox.

    Args:
        sandbox_id: Sandbox ID (cache key)

    Returns:
        TokenData if token exists in cache, None otherwise

    Example:
        >>> token_data = get_cached_token("sandbox_123")
        >>> if token_data:
        ...     print(f"Token expires at: {token_data.expires_at}")
    """
    return _token_cache.get(sandbox_id)


def clear_cached_token(sandbox_id: str) -> None:
    """
    Remove token from cache.

    Useful when a sandbox is deleted or token is known to be invalid.

    Args:
        sandbox_id: Sandbox ID (cache key)

    Example:
        >>> clear_cached_token("sandbox_123")
        >>> get_cached_token("sandbox_123") is None
        True
    """
    _token_cache.pop(sandbox_id, None)


def clear_all_tokens() -> None:
    """
    Clear entire token cache.

    Useful for testing or when switching API environments.

    Example:
        >>> clear_all_tokens()
        >>> len(_token_cache)
        0
    """
    _token_cache.clear()


def get_cache_size() -> int:
    """
    Get number of tokens currently cached.

    Returns:
        Number of cached tokens

    Example:
        >>> get_cache_size()
        5
    """
    return len(_token_cache)
