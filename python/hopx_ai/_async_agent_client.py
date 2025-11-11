"""Async HTTP client for agent operations with retry logic."""

import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from .errors import (
    FileNotFoundError,
    FileOperationError,
    CodeExecutionError,
    CommandExecutionError,
    DesktopNotAvailableError,
    AgentError,
    NetworkError,
    TimeoutError as HopxTimeoutError,
)

logger = logging.getLogger(__name__)


class AsyncAgentHTTPClient:
    """
    Async HTTP client for agent operations with retry logic and error handling.
    
    Features:
    - Connection pooling (reuses TCP connections)
    - Automatic retries with exponential backoff
    - Proper error wrapping to HOPX exceptions
    - Configurable timeouts
    """
    
    def __init__(
        self,
        agent_url: str,
        *,
        jwt_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        token_refresh_callback: Optional[callable] = None,
    ):
        """
        Initialize async agent HTTP client.
        
        Args:
            agent_url: Agent base URL (e.g., https://7777-{id}.domain)
            jwt_token: JWT token for agent authentication
            timeout: Default timeout in seconds
            max_retries: Maximum retry attempts
            token_refresh_callback: Async callback to refresh token on 401
        """
        self._agent_url = agent_url.rstrip('/')
        self._jwt_token = jwt_token
        self._timeout = timeout
        self._max_retries = max_retries
        self._token_refresh_callback = token_refresh_callback
        
        # Build headers
        headers = {}
        if self._jwt_token:
            headers['Authorization'] = f'Bearer {self._jwt_token}'
        
        # Create reusable async HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            headers=headers,
            transport=httpx.AsyncHTTPTransport(
                local_address="0.0.0.0",  # Force IPv4
            )
        )
        
        logger.debug(f"Async agent client initialized: {self._agent_url}")
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    def update_jwt_token(self, token: str) -> None:
        """Update JWT token for agent authentication."""
        self._jwt_token = token
        self._client.headers['Authorization'] = f'Bearer {token}'
    
    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried."""
        return status_code in {429, 500, 502, 503, 504}
    
    def _get_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff."""
        return min(2 ** attempt, 10)  # Max 10 seconds
    
    def _wrap_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentError:
        """Wrap httpx errors into HOPX exceptions."""
        context = context or {}
        
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            
            try:
                error_data = error.response.json()
                error_code = error_data.get('code', '').upper()
                error_message = error_data.get('message', str(error))
            except:
                error_code = None
                error_message = str(error)
            
            # Map error codes to specific exceptions
            if error_code == 'FILE_NOT_FOUND':
                return FileNotFoundError(
                    error_message,
                    path=context.get('path'),
                    code='file_not_found'
                )
            elif error_code in ('PATH_NOT_ALLOWED', 'PERMISSION_DENIED'):
                return FileOperationError(
                    error_message,
                    path=context.get('path'),
                    operation=operation,
                    code='file_operation_failed'
                )
            elif error_code in ('EXECUTION_FAILED', 'EXECUTION_TIMEOUT', 'INVALID_TOKEN'):
                return CodeExecutionError(
                    error_message,
                    exit_code=error_data.get('exit_code'),
                    code='execution_failed'
                )
            elif error_code == 'COMMAND_FAILED':
                return CommandExecutionError(
                    error_message,
                    exit_code=error_data.get('exit_code'),
                    command=context.get('command'),
                    code='command_failed'
                )
            elif error_code == 'DESKTOP_NOT_AVAILABLE':
                return DesktopNotAvailableError(
                    error_message,
                    missing_dependencies=error_data.get('missing_dependencies', []),
                    code='desktop_not_available'
                )
        
        elif isinstance(error, httpx.TimeoutException):
            return HopxTimeoutError(f"{operation} timed out after {self._timeout}s")
        elif isinstance(error, httpx.NetworkError):
            return NetworkError(f"{operation} failed: {error}")
        
        return AgentError(f"{operation} failed: {error}")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        operation: str = "request",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = f"{self._agent_url}{endpoint}"
        
        for attempt in range(self._max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                
                # Handle empty responses (204 No Content)
                if response.status_code == 204 or not response.content:
                    return {}
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    return response.json()
                return {"content": response.content}
                
            except httpx.HTTPStatusError as e:
                # Handle 401 Unauthorized - try to refresh token
                if e.response.status_code == 401 and self._token_refresh_callback and attempt == 0:
                    logger.info(f"{operation} got 401 Unauthorized, attempting token refresh...")
                    try:
                        # Call async refresh callback to get new token
                        new_token = await self._token_refresh_callback()
                        if new_token:
                            # Update token and retry request
                            self.update_jwt_token(new_token)
                            logger.info(f"{operation} token refreshed, retrying request...")
                            continue
                    except Exception as refresh_error:
                        logger.error(f"Token refresh failed: {refresh_error}")
                        # Fall through to raise original error
                
                if not self._should_retry(e.response.status_code) or attempt == self._max_retries - 1:
                    raise self._wrap_error(e, operation, context)
                
                await asyncio.sleep(self._get_retry_delay(attempt))
                
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                if attempt == self._max_retries - 1:
                    raise self._wrap_error(e, operation, context)
                
                await asyncio.sleep(self._get_retry_delay(attempt))
        
        raise AgentError(f"{operation} failed after {self._max_retries} retries")
    
    async def get(self, endpoint: str, operation: str = "GET request", context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self._request("GET", endpoint, operation=operation, context=context, **kwargs)
    
    async def post(self, endpoint: str, operation: str = "POST request", context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self._request("POST", endpoint, operation=operation, context=context, **kwargs)
    
    async def put(self, endpoint: str, operation: str = "PUT request", context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._request("PUT", endpoint, operation=operation, context=context, **kwargs)
    
    async def delete(self, endpoint: str, operation: str = "DELETE request", context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint, operation=operation, context=context, **kwargs)
    
    async def patch(self, endpoint: str, operation: str = "PATCH request", context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PATCH request."""
        return await self._request("PATCH", endpoint, operation=operation, context=context, **kwargs)