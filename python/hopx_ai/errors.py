"""HOPX.AI SDK exceptions."""

from typing import Optional, Dict, Any, List

# Import ErrorCode enum from generated models for type-safe error codes
from .models import ErrorCode

__all__ = [
    "ErrorCode",  # Re-export for convenience
    "HopxError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "ResourceLimitError",
    "AgentError",
    "FileNotFoundError",
    "FileOperationError",
    "CodeExecutionError",
    "CommandExecutionError",
    "DesktopNotAvailableError",
]


class HopxError(Exception):
    """Base exception for all HOPX.AI SDK errors."""
    
    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
        self.details = details or {}
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"(code: {self.code})")
        if self.request_id:
            parts.append(f"[request_id: {self.request_id}]")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, code={self.code!r})"


class APIError(HopxError):
    """API request failed."""
    
    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication failed (401)."""
    pass


class NotFoundError(APIError):
    """Resource not found (404)."""
    pass


class ValidationError(APIError):
    """Request validation failed (400)."""
    
    def __init__(
        self,
        message: str,
        *,
        field: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field = field


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""
    
    def __init__(
        self,
        message: str,
        *,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        msg = super().__str__()
        if self.retry_after:
            msg += f" (retry after {self.retry_after}s)"
        return msg


class ResourceLimitError(APIError):
    """Resource limit exceeded."""
    
    def __init__(
        self,
        message: str,
        *,
        limit: Optional[int] = None,
        current: Optional[int] = None,
        available: Optional[int] = None,
        upgrade_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.limit = limit
        self.current = current
        self.available = available
        self.upgrade_url = upgrade_url
    
    def __str__(self) -> str:
        msg = super().__str__()
        if self.limit and self.current:
            msg += f" (current: {self.current}/{self.limit})"
        if self.upgrade_url:
            msg += f"\nUpgrade at: {self.upgrade_url}"
        return msg


class ServerError(APIError):
    """Server error (5xx)."""
    pass


class NetworkError(HopxError):
    """Network communication failed."""
    pass


class TimeoutError(NetworkError):
    """Request timed out."""
    pass


# =============================================================================
# AGENT OPERATION ERRORS
# =============================================================================

class AgentError(HopxError):
    """Base error for agent operations."""
    pass


class FileNotFoundError(AgentError):
    """File or directory not found in sandbox."""
    
    def __init__(self, message: str = "File not found", path: Optional[str] = None, **kwargs):
        # Use provided code or default
        kwargs.setdefault('code', 'file_not_found')
        super().__init__(message, **kwargs)
        self.path = path


class FileOperationError(AgentError):
    """File operation failed."""
    
    def __init__(self, message: str = "File operation failed", operation: Optional[str] = None, **kwargs):
        # Use provided code or default
        kwargs.setdefault('code', 'file_operation_failed')
        super().__init__(message, **kwargs)
        self.operation = operation


class CodeExecutionError(AgentError):
    """Code execution failed."""
    
    def __init__(self, message: str = "Code execution failed", language: Optional[str] = None, **kwargs):
        # Use provided code or default
        kwargs.setdefault('code', 'code_execution_failed')
        super().__init__(message, **kwargs)
        self.language = language


class CommandExecutionError(AgentError):
    """Command execution failed."""
    
    def __init__(self, message: str = "Command execution failed", command: Optional[str] = None, **kwargs):
        # Use provided code or default
        kwargs.setdefault('code', 'command_execution_failed')
        super().__init__(message, **kwargs)
        self.command = command


class DesktopNotAvailableError(AgentError):
    """Desktop automation not available in this sandbox."""
    
    def __init__(
        self,
        message: str = "Desktop automation not available",
        missing_dependencies: Optional[List[str]] = None,
        **kwargs
    ):
        # Use provided code or default
        kwargs.setdefault('code', 'desktop_not_available')
        super().__init__(message, **kwargs)
        self.missing_dependencies = missing_dependencies or []
        self.docs_url = "https://docs.hopx.ai/desktop-automation"
        self.install_command = self._get_install_command()
    
    def _get_install_command(self) -> str:
        """Generate install command for missing dependencies."""
        if not self.missing_dependencies:
            # Return default desktop dependencies
            deps = [
                "xvfb",
                "tigervnc-standalone-server",
                "xdotool",
                "wmctrl",
                "xclip",
                "imagemagick",
                "ffmpeg",
                "tesseract-ocr"
            ]
            return f"apt-get update && apt-get install -y {' '.join(deps)}"
        
        return f"apt-get install -y {' '.join(self.missing_dependencies)}"
    
    def __str__(self) -> str:
        msg = super().__str__()
        if self.missing_dependencies:
            msg += f"\n\nMissing dependencies: {', '.join(self.missing_dependencies)}"
        msg += f"\n\nDocumentation: {self.docs_url}"
        if self.install_command:
            msg += f"\n\nTo enable desktop automation, add to your Dockerfile:"
            msg += f"\nRUN {self.install_command}"
        return msg

