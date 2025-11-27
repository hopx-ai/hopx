"""CLI-specific error handling and SDK error mapping.

Maps SDK errors to CLI errors with exit codes and provides user-friendly
error messages with helpful suggestions.

Exit Codes
----------
The CLI uses standardized exit codes for scripting and automation:

    0   Success - Command completed successfully
    1   General error - Unspecified error occurred
    2   Validation error - Invalid input or arguments
    3   Authentication error - API key invalid or missing
    4   Not found - Resource (sandbox/template) not found
    5   Timeout - Operation exceeded time limit
    6   Network error - Connection or request failed
    7   Rate limit - API rate limit exceeded
    130 Interrupted - User pressed Ctrl+C (SIGINT)

Example usage in scripts::

    hopx sandbox create --template python
    if [ $? -eq 3 ]; then
        echo "Authentication failed - check your API key"
    elif [ $? -eq 4 ]; then
        echo "Template not found - list available templates"
    fi
"""

import sys
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import hopx_ai.errors as sdk_errors
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console(stderr=True)

# Type variable for decorated function return type
F = TypeVar("F", bound=Callable[..., Any])


class CLIError(Exception):
    """Base exception for CLI errors.

    Attributes:
        message: Error message
        exit_code: Process exit code
        suggestion: Optional suggestion to fix the error
        request_id: Optional request ID from API
    """

    exit_code: int = 1

    def __init__(
        self,
        message: str,
        *,
        suggestion: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.request_id = request_id


class AuthenticationError(CLIError):
    """Authentication failed (exit code 3).

    Raised when API key is invalid or missing.
    """

    exit_code = 3


class NotFoundError(CLIError):
    """Resource not found (exit code 4).

    Raised when a sandbox, template, or other resource is not found.
    """

    exit_code = 4


class TimeoutError(CLIError):
    """Operation timed out (exit code 5).

    Raised when an operation exceeds the timeout limit.
    """

    exit_code = 5


class NetworkError(CLIError):
    """Network communication failed (exit code 6).

    Raised when network requests fail.
    """

    exit_code = 6


class RateLimitError(CLIError):
    """Rate limit exceeded (exit code 7).

    Raised when API rate limits are exceeded.
    """

    exit_code = 7


class ValidationError(CLIError):
    """Request validation failed (exit code 2).

    Raised when input validation fails.
    """

    exit_code = 2


def map_sdk_error(error: sdk_errors.HopxError) -> CLIError:
    """Map SDK error to CLI error with exit code and suggestion.

    Args:
        error: SDK error to map

    Returns:
        Corresponding CLI error
    """
    message = str(error)
    request_id = error.request_id

    # Map SDK errors to CLI errors
    match error:
        case sdk_errors.AuthenticationError() | sdk_errors.TokenExpiredError():
            return AuthenticationError(
                message,
                suggestion=(
                    "Authentication failed. Check your setup:\n"
                    "  1. Validate: hopx auth validate\n"
                    "  2. Re-login: hopx auth login && hopx auth keys create\n"
                    "  3. Or set: HOPX_API_KEY environment variable"
                ),
                request_id=request_id,
            )
        case sdk_errors.NotFoundError() | sdk_errors.TemplateNotFoundError():
            suggestion = "List available resources with the appropriate list command"
            if isinstance(error, sdk_errors.TemplateNotFoundError):
                if error.suggested_template:
                    suggestion = f"Did you mean '{error.suggested_template}'? List templates with 'hopx template list'"
                elif error.available_templates:
                    templates = ", ".join(error.available_templates[:3])
                    suggestion = (
                        f"Available templates: {templates}. List all with 'hopx template list'"
                    )
            return NotFoundError(
                message,
                suggestion=suggestion,
                request_id=request_id,
            )
        case sdk_errors.TimeoutError():
            return TimeoutError(
                message,
                suggestion="Increase timeout with --timeout flag or check network connectivity",
                request_id=request_id,
            )
        case sdk_errors.NetworkError():
            return NetworkError(
                message,
                suggestion="Check network connectivity and try again",
                request_id=request_id,
            )
        case sdk_errors.RateLimitError():
            retry_msg = ""
            if hasattr(error, "retry_after") and error.retry_after:
                retry_msg = f" Retry after {error.retry_after} seconds."
            return RateLimitError(
                message,
                suggestion=f"Rate limit exceeded.{retry_msg} Consider upgrading your plan.",
                request_id=request_id,
            )
        case sdk_errors.ValidationError():
            field_msg = ""
            if hasattr(error, "field") and error.field:
                field_msg = f" (field: {error.field})"
            return ValidationError(
                f"{message}{field_msg}",
                suggestion="Check command arguments and try again",
                request_id=request_id,
            )
        case sdk_errors.ResourceLimitError():
            upgrade_msg = ""
            if hasattr(error, "upgrade_url") and error.upgrade_url:
                upgrade_msg = f" Upgrade at: {error.upgrade_url}"
            return CLIError(
                message,
                suggestion=f"Resource limit exceeded.{upgrade_msg}",
                request_id=request_id,
            )
        case sdk_errors.TemplateBuildError():
            logs_msg = ""
            if hasattr(error, "logs_url") and error.logs_url:
                logs_msg = f" View logs: {error.logs_url}"
            return CLIError(
                message,
                suggestion=f"Template build failed.{logs_msg} Check Dockerfile syntax and dependencies.",
                request_id=request_id,
            )
        case sdk_errors.SandboxExpiredError():
            return CLIError(
                message,
                suggestion="Sandbox has expired. Create a new sandbox with 'hopx sandbox create'",
                request_id=request_id,
            )
        case sdk_errors.DesktopNotAvailableError():
            deps = ""
            if hasattr(error, "install_command") and error.install_command:
                deps = f" Install with: {error.install_command}"
            return CLIError(
                message,
                suggestion=f"Desktop automation not available.{deps}",
                request_id=request_id,
            )
        case _:
            # Generic error mapping
            return CLIError(
                message,
                suggestion="Check command arguments and API status",
                request_id=request_id,
            )


def display_error(error: CLIError, verbose: bool = False) -> None:
    """Display error message with Rich formatting.

    Args:
        error: CLI error to display
        verbose: Show additional error details
    """
    # Build error text
    error_text = Text()
    error_text.append("Error: ", style="bold red")
    error_text.append(error.message)

    # Add request ID if available
    if error.request_id:
        error_text.append("\n\nRequest ID: ", style="dim")
        error_text.append(error.request_id, style="dim cyan")

    # Add suggestion if available
    if error.suggestion:
        error_text.append("\n\nTo fix: ", style="bold yellow")
        error_text.append(error.suggestion, style="yellow")

    # Create panel with error
    panel = Panel(
        error_text,
        title="[bold red]Error[/bold red]",
        border_style="red",
        padding=(1, 2),
    )

    console.print(panel)

    # Show verbose details if requested
    if verbose and hasattr(error, "__cause__") and error.__cause__:
        console.print("\n[dim]Details:[/dim]")
        console.print(f"[dim]{error.__cause__}[/dim]")


def handle_errors(func: F) -> F:
    """Decorator to handle errors in CLI commands.

    Catches SDK errors and maps them to CLI errors with user-friendly
    messages and appropriate exit codes. Also handles keyboard interrupts
    and unexpected errors.

    Args:
        func: Function to decorate

    Returns:
        Decorated function

    Example:
        @handle_errors
        def my_command():
            sandbox = Sandbox.create(template="python")
            # If this fails, error is automatically caught and displayed
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(130)  # Standard exit code for SIGINT
        except CLIError as e:
            # Already a CLI error, just display and exit
            verbose = kwargs.get("verbose", False)
            display_error(e, verbose=verbose)
            sys.exit(e.exit_code)
        except sdk_errors.HopxError as e:
            # Map SDK error to CLI error
            cli_error = map_sdk_error(e)
            verbose = kwargs.get("verbose", False)
            display_error(cli_error, verbose=verbose)
            sys.exit(cli_error.exit_code)
        except Exception as e:
            # Unexpected error
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            verbose = kwargs.get("verbose", False)
            if verbose:
                import traceback

                console.print("\n[dim]Traceback:[/dim]")
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            sys.exit(1)

    return wrapper  # type: ignore
