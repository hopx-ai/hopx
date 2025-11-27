"""Self-update command for the Hopx CLI."""

from __future__ import annotations

import subprocess

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hopx_cli.core import run_async
from hopx_cli.core.version import (
    INSTALL_GIT,
    INSTALL_PIP_SYSTEM,
    INSTALL_UNKNOWN,
    check_pypi_version,
    detect_install_method,
    get_install_method_display,
    get_update_command,
)

app = typer.Typer(
    help="Update Hopx CLI to the latest version",
    invoke_without_command=True,
)
console = Console()


@app.callback(invoke_without_command=True)
@run_async
async def self_update(
    ctx: typer.Context,
    check: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Check for updates without installing",
    ),
    version: str | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Update to specific version (e.g., 0.2.0)",
    ),
    pre: bool = typer.Option(
        False,
        "--pre",
        help="Include pre-release versions",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force update even if already on latest",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be done without executing",
    ),
) -> None:
    """Update Hopx CLI to the latest version.

    This command checks PyPI for the latest version and updates the CLI
    using the same method it was originally installed with (pip, pipx, or uv).

    Examples:

        hopx self-update              # Update to latest

        hopx self-update --check      # Check without updating

        hopx self-update --version 0.2.0  # Install specific version

        hopx self-update --pre        # Include pre-releases
    """
    # Check for updates
    console.print("\n[bold]Checking for updates...[/bold]")

    try:
        version_info = await check_pypi_version(
            include_prerelease=pre,
            timeout=15.0,
        )
    except httpx.TimeoutException:
        console.print("[red]Error:[/red] Request timed out")
        console.print("[dim]Check your network connection and try again[/dim]")
        raise typer.Exit(5)
    except httpx.HTTPError as e:
        console.print(f"[red]Error:[/red] Failed to check for updates: {e}")
        raise typer.Exit(6)

    # If specific version requested, check if it's valid
    target_version = version or version_info.latest
    if version:
        console.print(f"[dim]Target version: {version}[/dim]")

    # Display version info
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Current version", version_info.current)
    table.add_row("Latest version", version_info.latest)

    if version_info.is_prerelease:
        table.add_row("Note", "[yellow]Latest is a pre-release[/yellow]")

    console.print(table)
    console.print()

    # Check if update needed
    needs_update = version_info.update_available or force or (version is not None)

    if not needs_update:
        console.print("[green]Hopx CLI is up to date[/green]")
        raise typer.Exit(0)

    # If only checking, exit here
    if check:
        if version_info.update_available:
            console.print(
                Panel(
                    f"[yellow]Update available:[/yellow] {version_info.current} → {version_info.latest}\n\n"
                    f"Run [cyan]hopx self-update[/cyan] to update",
                    title="Update Available",
                    border_style="yellow",
                )
            )
            raise typer.Exit(2)  # Exit code 2 = update available
        raise typer.Exit(0)

    # Detect installation method
    install_method = detect_install_method()
    method_display = get_install_method_display(install_method)

    console.print(f"[dim]Installation method: {method_display}[/dim]")

    # Handle unknown installation method
    if install_method == INSTALL_UNKNOWN:
        console.print(
            Panel(
                "[yellow]Could not detect installation method.[/yellow]\n\n"
                "Manual update options:\n"
                "  [cyan]pip install --upgrade hopx-cli[/cyan]\n"
                "  [cyan]pipx upgrade hopx-cli[/cyan]\n"
                "  [cyan]uv tool upgrade hopx-cli[/cyan]",
                title="Manual Update Required",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    # Get update command
    update_cmd = get_update_command(install_method, version)
    cmd_display = " ".join(update_cmd)

    # Dry run - show what would happen
    if dry_run:
        console.print(
            Panel(
                f"[bold]Dry Run[/bold] - No changes will be made\n\n"
                f"Current version: {version_info.current}\n"
                f"Target version: {target_version}\n"
                f"Install method: {method_display}\n\n"
                f"Would run:\n  [cyan]{cmd_display}[/cyan]",
                title="Update Preview",
                border_style="blue",
            )
        )
        raise typer.Exit(0)

    # Warn about system-wide installs
    if install_method == INSTALL_PIP_SYSTEM:
        console.print(
            "[yellow]Warning:[/yellow] System-wide installation detected. You may need sudo."
        )
        if not force and not typer.confirm("Continue with update?", default=True):
            raise typer.Exit(0)

    # Warn about git installs
    if install_method == INSTALL_GIT:
        console.print(
            "[yellow]Warning:[/yellow] Development installation detected. "
            "This will update from the main branch."
        )

    # Execute update
    console.print(f"\n[bold]Updating to {target_version}...[/bold]")
    console.print(f"[dim]Running: {cmd_display}[/dim]\n")

    try:
        result = subprocess.run(
            update_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            console.print("[red]Update failed[/red]")
            if result.stderr:
                console.print(f"[dim]{result.stderr}[/dim]")
            raise typer.Exit(1)

    except subprocess.TimeoutExpired:
        console.print("[red]Error:[/red] Update timed out")
        raise typer.Exit(5)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] Command not found: {e}")
        raise typer.Exit(1)

    # Verify update
    console.print()
    try:
        # Check new version by running hopx --version
        verify_result = subprocess.run(
            ["hopx", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        new_version = verify_result.stdout.strip() if verify_result.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        new_version = "unknown"

    console.print(
        Panel(
            f"[green]Successfully updated to {target_version}[/green]\n\n"
            f"New version: {new_version}\n\n"
            "[dim]Run [cyan]hopx --help[/cyan] to see available commands[/dim]",
            title="Update Complete",
            border_style="green",
        )
    )
