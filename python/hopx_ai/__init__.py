"""
Hopx Python SDK

Official Python client for Hopx Sandboxes.

Sync Example:
    >>> from hopx_ai import Sandbox
    >>> 
    >>> # Create sandbox
    >>> sandbox = Sandbox.create(template="code-interpreter")
    >>> print(sandbox.get_info().public_host)
    >>> 
    >>> # Cleanup
    >>> sandbox.kill()

Async Example:
    >>> from hopx_ai import AsyncSandbox
    >>> 
    >>> async with AsyncSandbox.create(template="nodejs") as sandbox:
    ...     info = await sandbox.get_info()
    ...     print(f"Running at: {info.public_host}")
    # Automatically killed when exiting context
"""

from .sandbox import Sandbox
from .async_sandbox import AsyncSandbox
from .models import (
    SandboxInfo,
    Template as SandboxTemplate,
    TemplateResources,
    ExecutionResult,
    CommandResult,
    FileInfo,
    RichOutput,
    # Desktop models
    VNCInfo,
    WindowInfo,
    RecordingInfo,
    DisplayInfo,
)
from .errors import (
    HopxError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ResourceLimitError,
    ValidationError,
    ServerError,
    NetworkError,
    TimeoutError,
    # Agent operation errors
    AgentError,
    FileNotFoundError,
    FileOperationError,
    CodeExecutionError,
    CommandExecutionError,
    DesktopNotAvailableError,
)
# Template Building
from .template import (
    Template,
    create_template,
    wait_for_port,
    wait_for_url,
    wait_for_file,
    wait_for_process,
    wait_for_command,
)

__version__ = "0.2.2"
__all__ = [
    "Sandbox",
    "AsyncSandbox",
    "SandboxInfo",
    "SandboxTemplate",
    "TemplateResources",
    "ExecutionResult",
    "CommandResult",
    "FileInfo",
    "RichOutput",
    # Desktop models
    "VNCInfo",
    "WindowInfo",
    "RecordingInfo",
    "DisplayInfo",
    # Errors
    "HopxError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ResourceLimitError",
    "ValidationError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    # Agent operation errors
    "AgentError",
    "FileNotFoundError",
    "FileOperationError",
    "CodeExecutionError",
    "CommandExecutionError",
    "DesktopNotAvailableError",
    # Template Building
    "Template",
    "create_template",
    "wait_for_port",
    "wait_for_url",
    "wait_for_file",
    "wait_for_process",
    "wait_for_command",
]

