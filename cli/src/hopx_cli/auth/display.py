"""Authentication display utilities for beautiful terminal output."""

from typing import Any

import pyperclip  # type: ignore[import-untyped]
import qrcode  # type: ignore[import-untyped]
from rich.console import Console

console = Console()


def show_auth_url(
    url: str,
    title: str = "Authenticate",
    show_qr: bool = True,
    auto_copy: bool = True,
) -> None:
    """Display authentication URL with QR code and clipboard support.

    Args:
        url: The authentication URL to display
        title: Header title for the display
        show_qr: Whether to show QR code
        auto_copy: Whether to auto-copy URL to clipboard
    """
    if title:
        console.print()
        console.print(f"[bold cyan]{title}[/bold cyan]")

    console.print()
    console.print("Open this URL to authenticate:")
    console.print()
    console.print(f"  [link={url}]{url}[/link]", highlight=False)

    # Auto-copy to clipboard
    if auto_copy:
        try:
            pyperclip.copy(url)
            console.print()
            console.print("  [dim](copied to clipboard)[/dim]")
        except Exception:
            pass  # Clipboard not available (headless server)

    # QR code
    if show_qr:
        console.print()
        _print_qr_code(url)


def _print_qr_code(url: str) -> None:
    """Print ASCII QR code to terminal.

    Args:
        url: The URL to encode in the QR code
    """
    import io

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Generate ASCII output
        f = io.StringIO()
        qr.print_ascii(out=f, invert=True)
        qr_text = f.getvalue()

        # Print with indentation
        for line in qr_text.strip().split("\n"):
            console.print(f"  {line}")
    except Exception:
        pass  # QR generation failed, skip silently


def show_headless_instructions() -> None:
    """Show instructions for headless callback URL flow."""
    console.print()
    console.print("[dim]After login, your browser shows 'connection refused'.[/dim]")
    console.print("[dim]Copy the URL from your browser's address bar and paste below.[/dim]")
    console.print()


def prompt_callback_url() -> str:
    """Prompt user for callback URL with styled input.

    Returns:
        The callback URL entered by the user

    Raises:
        RuntimeError: If authentication is cancelled
    """
    try:
        return console.input("[bold]URL:[/bold] ").strip()
    except (KeyboardInterrupt, EOFError):
        console.print()
        raise RuntimeError("Authentication cancelled") from None


def show_success(message: str = "Login successful!") -> None:
    """Show success message.

    Args:
        message: Success message to display
    """
    console.print()
    console.print(f"[bold green]✓[/bold green] {message}")


def show_error(message: str) -> None:
    """Show error message.

    Args:
        message: Error message to display
    """
    console.print()
    console.print(f"[bold red]✗[/bold red] {message}")


def show_progress(message: str) -> Any:
    """Return a spinner context manager for progress indication.

    Args:
        message: Progress message to display

    Returns:
        Spinner context manager
    """
    from hopx_cli.output import Spinner

    return Spinner(message)
