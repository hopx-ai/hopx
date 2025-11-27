"""Cache management resource for Hopx Sandboxes."""

from typing import Dict, Any, Optional
import logging
from ._agent_client import AgentHTTPClient

logger = logging.getLogger(__name__)


class Cache:
    """
    Cache management resource.

    Provides methods for managing execution result cache.

    Features:
    - Get cache statistics
    - Clear cache

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

    def __init__(self, client: AgentHTTPClient):
        """
        Initialize Cache resource.

        Args:
            client: Shared agent HTTP client
        """
        self._client = client
        logger.debug("Cache resource initialized")

    def stats(self, *, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Get cache statistics.

        Args:
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)

        Example:
            >>> stats = sandbox.cache.stats()
            >>> print(f"Cache hits: {stats['hits']}")
            >>> print(f"Cache misses: {stats['misses']}")
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
            >>> print(f"Cache size: {stats['size']} MB")
            >>> print(f"Entry count: {stats['count']}")
        """
        logger.debug("Getting cache statistics")

        response = self._client.get("/cache/stats", operation="get cache stats", timeout=timeout)

        return response.json()

    def clear(self, *, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Clear the execution result cache.

        Args:
            timeout: Request timeout in seconds (overrides default)

        Returns:
            Dictionary with confirmation message

        Example:
            >>> result = sandbox.cache.clear()
            >>> print(result['message'])  # "Cache cleared successfully"
            >>> print(f"Entries removed: {result.get('entries_removed', 0)}")
        """
        logger.debug("Clearing cache")

        response = self._client.post("/cache/clear", operation="clear cache", timeout=timeout)

        return response.json()

    def __repr__(self) -> str:
        return f"<Cache client={self._client}>"
