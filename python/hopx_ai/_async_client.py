"""Async HTTP client with retry logic."""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from .errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ResourceLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """Async HTTP client with automatic retries and error handling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.hopx.dev",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        # API key priority: param > env var > error
        self.api_key = api_key or os.environ.get("HOPX_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key parameter or set HOPX_API_KEY environment variable.\n"
                "Get your API key at: https://hopx.ai"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Force IPv4 to avoid IPv6 timeout issues (270s delay)
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._default_headers(),
            transport=httpx.AsyncHTTPTransport(
                local_address="0.0.0.0", retries=0  # Force IPv4  # We handle retries ourselves
            ),
        )

    def _default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "hopx-python/0.1.0",
        }

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False

        # Retry on server errors and rate limits
        return status_code in (429, 500, 502, 503, 504)

    def _get_retry_delay(self, attempt: int, retry_after: Optional[int] = None) -> float:
        """Calculate retry delay with exponential backoff."""
        if retry_after:
            return float(retry_after)

        # Exponential backoff: 1s, 2s, 4s, 8s...
        return min(2**attempt, 60)

    def _handle_error(self, response: httpx.Response) -> None:
        """Convert HTTP errors to appropriate exceptions."""
        try:
            error_data = response.json().get("error", {})
            message = error_data.get("message", response.text)
            code = error_data.get("code")
            request_id = error_data.get("request_id")
            details = error_data.get("details", {})
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
            code = None
            request_id = response.headers.get("X-Request-ID")
            details = {}

        kwargs = {
            "code": code,
            "request_id": request_id,
            "details": details,
            "status_code": response.status_code,
        }

        if response.status_code == 401:
            raise AuthenticationError(message, **kwargs)
        elif response.status_code == 404:
            raise NotFoundError(message, **kwargs)
        elif response.status_code == 400:
            raise ValidationError(message, **kwargs)
        elif response.status_code == 429:
            retry_after = details.get("retry_after_seconds")
            raise RateLimitError(message, retry_after=retry_after, **kwargs)
        elif response.status_code == 403 and "limit" in message.lower():
            raise ResourceLimitError(
                message,
                limit=details.get("limit"),
                current=details.get("current"),
                available=details.get("available"),
                upgrade_url=details.get("upgrade_url"),
                **kwargs,
            )
        elif response.status_code >= 500:
            raise ServerError(message, **kwargs)
        else:
            raise APIError(message, **kwargs)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request with automatic retries.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API endpoint path (without base URL)
            params: Query parameters
            json: JSON request body

        Returns:
            Response JSON data

        Raises:
            HopxError: On API errors
            NetworkError: On network errors
            TimeoutError: On timeout
        """
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Debug logging
        logger.debug(f"{method} {url}")
        if json:
            logger.debug(f"Request body: {json}")
        if params:
            logger.debug(f"Query params: {params}")

        for attempt in range(self.max_retries + 1):
            try:
                import time

                start_time = time.time()

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                )

                elapsed = time.time() - start_time
                logger.debug(f"Response: {response.status_code} ({elapsed:.3f}s)")

                # Success
                if response.status_code < 400:
                    result = response.json()
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Response body: {result}")
                    return result

                # Should we retry?
                if self._should_retry(response.status_code, attempt):
                    retry_after = None
                    if response.status_code == 429:
                        try:
                            retry_after = (
                                response.json()
                                .get("error", {})
                                .get("details", {})
                                .get("retry_after_seconds")
                            )
                        except Exception:
                            pass

                    delay = self._get_retry_delay(attempt, retry_after)
                    logger.debug(f"Retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                    continue

                # Error - no retry
                self._handle_error(response)

            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    delay = self._get_retry_delay(attempt)
                    logger.debug(f"Timeout, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    continue
                raise TimeoutError(f"Request timed out after {self.timeout}s") from e

            except httpx.NetworkError as e:
                if attempt < self.max_retries:
                    delay = self._get_retry_delay(attempt)
                    logger.debug(f"Network error, retrying in {delay}s")
                    await asyncio.sleep(delay)
                    continue
                raise NetworkError(f"Network error: {e}") from e

        raise ServerError("Max retries exceeded")

    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """POST request."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> Dict[str, Any]:
        """PUT request."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """DELETE request."""
        return await self.request("DELETE", path, **kwargs)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
