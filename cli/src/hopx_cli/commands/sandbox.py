"""Sandbox lifecycle management commands for the Hopx CLI.

Implements all sandbox operations including creation, listing, lifecycle
management (pause/resume/kill), health checks, and utility functions.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from hopx_ai import SandboxInfo
from rich.console import Console
from rich.table import Table

from ..core import (
    CLIContext,
    OutputFormat,
    create_sandbox,
    get_sandbox,
    handle_errors,
    list_sandboxes,
)
from ..output import (
    Spinner,
    format_output,
)

app = typer.Typer(
    help="Manage cloud sandboxes",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _parse_env_vars(
    env_list: list[str] | None,
    env_file: str | None,
) -> dict[str, str]:
    """Parse environment variables from command line and file.

    Args:
        env_list: List of KEY=VALUE strings from --env flag
        env_file: Path to .env file

    Returns:
        Dictionary of environment variables

    Raises:
        typer.BadParameter: If env var format is invalid
    """
    env_vars: dict[str, str] = {}

    # Load from file first (lower priority)
    if env_file:
        env_path = Path(env_file)
        if not env_path.exists():
            raise typer.BadParameter(f"Environment file not found: {env_file}")

        with open(env_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE
                if "=" not in line:
                    raise typer.BadParameter(
                        f"Invalid env var format in {env_file}:{line_num} (expected KEY=VALUE)"
                    )

                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    # Override with command-line args (higher priority)
    if env_list:
        for env_str in env_list:
            if "=" not in env_str:
                raise typer.BadParameter(f"Invalid env var format: {env_str} (expected KEY=VALUE)")

            key, value = env_str.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def _format_time_remaining(seconds: int | None) -> str:
    """Format seconds as human-readable time.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string like "4h 32m" or "never"
    """
    if seconds is None or seconds <= 0:
        return "never"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def _format_sandbox_details(info: SandboxInfo, ctx: CLIContext) -> None:
    """Format and display detailed sandbox information.

    Args:
        info: Sandbox information
        ctx: CLI context
    """
    if ctx.output_format == OutputFormat.JSON:
        format_output(
            info.model_dump(),
            ctx.output_format,
        )
    elif ctx.output_format == OutputFormat.PLAIN:
        lines = [
            f"ID: {info.sandbox_id}",
            f"Template: {info.template_name or info.template_id or 'N/A'}",
            f"Status: {info.status}",
            f"Region: {info.region or 'N/A'}",
            f"URL: {info.public_host}",
        ]
        if info.timeout_seconds:
            lines.append(f"Timeout: {info.timeout_seconds}s")
        if info.expires_at:
            lines.append(f"Expires: {info.expires_at.isoformat()}")
        if info.created_at:
            lines.append(f"Created: {info.created_at.isoformat()}")

        console.print("\n".join(lines))
    else:
        # Rich table format
        table = Table(
            title="Sandbox Details",
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        table.add_row("ID", info.sandbox_id)
        table.add_row("Template", info.template_name or info.template_id or "[dim]N/A[/dim]")
        table.add_row("Status", _format_status_colored(info.status))
        table.add_row("Region", info.region or "[dim]N/A[/dim]")
        table.add_row("URL", info.public_host)

        if info.timeout_seconds:
            table.add_row("Timeout", f"{info.timeout_seconds}s")
        if info.expires_at:
            now = datetime.now(UTC)
            remaining = (info.expires_at - now).total_seconds()
            table.add_row("Expires", _format_time_remaining(int(remaining)))
        else:
            table.add_row("Expires", "never")

        if info.created_at:
            table.add_row("Created", info.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

        if info.resources:
            table.add_row(
                "Resources",
                f"{info.resources.vcpu} vCPU, {info.resources.memory_mb}MB RAM, {info.resources.disk_mb}MB disk",
            )

        table.add_row("Internet", "enabled" if info.internet_access else "disabled")

        console.print(table)


def _format_status_colored(status: str) -> str:
    """Format status with color coding.

    Args:
        status: Status string

    Returns:
        Formatted status with Rich color tags
    """
    status_lower = status.lower()

    if status_lower in ("running", "active", "ready"):
        return f"[green]{status}[/green]"
    elif status_lower in ("paused", "creating"):
        return f"[yellow]{status}[/yellow]"
    elif status_lower in ("stopped", "killed", "error"):
        return f"[red]{status}[/red]"
    else:
        return status


@app.command("create")
@handle_errors
def create(
    ctx: typer.Context,
    template: str = typer.Option(
        "code-interpreter",
        "--template",
        "-t",
        help="Template name or ID",
    ),
    template_id: str | None = typer.Option(
        None,
        "--template-id",
        help="Template ID (alternative to --template)",
    ),
    region: str | None = typer.Option(
        None,
        "--region",
        help="Preferred region",
    ),
    timeout: int = typer.Option(
        3600,
        "--timeout",
        "-T",
        help="Auto-kill timeout in seconds (0 = no timeout)",
    ),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable (KEY=VALUE, repeatable)",
    ),
    env_file: str | None = typer.Option(
        None,
        "--env-file",
        help="Load env vars from file",
    ),
    no_internet: bool = typer.Option(
        False,
        "--no-internet",
        help="Disable internet access",
    ),
    wait: bool = typer.Option(
        True,
        "--wait/--no-wait",
        help="Wait for sandbox to be ready",
    ),
) -> None:
    """Create a new sandbox.

    Examples:
        # Create with default template
        hopx sandbox create

        # Create with specific template and environment
        hopx sandbox create -t python -e API_KEY=secret -e DEBUG=true

        # Create with env file
        hopx sandbox create --env-file .env

        # Create without internet access
        hopx sandbox create --no-internet

        # Create with custom timeout (2 hours)
        hopx sandbox create --timeout 7200
    """
    cli_ctx: CLIContext = ctx.obj

    # Parse environment variables
    env_vars = _parse_env_vars(env, env_file)

    # Build create parameters
    create_params: dict[str, Any] = {}

    # Template selection (template_id takes precedence)
    if template_id:
        create_params["template_id"] = template_id
    else:
        create_params["template"] = template

    if region:
        create_params["region"] = region

    if timeout > 0:
        create_params["timeout"] = timeout

    if env_vars:
        create_params["env_vars"] = env_vars

    create_params["internet_access"] = not no_internet

    # Create sandbox with spinner
    with Spinner("Creating sandbox...") as spinner:
        sandbox = create_sandbox(
            cli_ctx.config,
            template=create_params.get("template"),
            template_id=create_params.get("template_id"),
            region=create_params.get("region"),
            timeout=create_params.get("timeout"),
            internet_access=create_params.get("internet_access"),
            env_vars=create_params.get("env_vars"),
        )

        if wait:
            spinner.update("Waiting for sandbox to be ready...")
            # SDK already waits for sandbox to be ready in create()

        spinner.success("Sandbox created")

    # Get full info
    info = sandbox.get_info()

    # Display result
    if not cli_ctx.quiet:
        _format_sandbox_details(info, cli_ctx)

        # Next steps suggestions (only for table output)
        if cli_ctx.output_format == OutputFormat.TABLE:
            console.print("\n[dim]Next steps:[/dim]")
            console.print(f"  hopx run 'print(1)' --sandbox {info.sandbox_id}")
            console.print(f"  hopx files list / --sandbox {info.sandbox_id}")
            console.print(f"  hopx terminal connect {info.sandbox_id}")


@app.command("list")
@handle_errors
def list_cmd(
    ctx: typer.Context,
    template: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help="Filter by template name",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status: running, paused, stopped",
    ),
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Maximum number of results",
    ),
) -> None:
    """List all sandboxes.

    Examples:
        # List all sandboxes
        hopx sandbox list

        # List only running sandboxes
        hopx sandbox list --status running

        # List sandboxes from specific template
        hopx sandbox list --template python

        # Limit results
        hopx sandbox list --limit 10
    """
    cli_ctx: CLIContext = ctx.obj

    sandboxes = list_sandboxes(cli_ctx.config, limit=limit)

    # Get info for each sandbox
    sandbox_infos = [s.get_info() for s in sandboxes]

    # Apply filters
    if template:
        sandbox_infos = [s for s in sandbox_infos if s.template_name == template]

    if status:
        sandbox_infos = [s for s in sandbox_infos if s.status.lower() == status.lower()]

    # Display results
    if not sandbox_infos:
        if not cli_ctx.quiet:
            console.print("[dim]No sandboxes found[/dim]")
        return

    format_output(
        [s.model_dump() for s in sandbox_infos],
        cli_ctx.output_format,
        table_config={"table_type": "sandbox", "title": "Sandboxes"},
    )


@app.command("info")
@handle_errors
def info(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get detailed information about a sandbox.

    Examples:
        hopx sandbox info 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    sandbox_info = sandbox.get_info()

    _format_sandbox_details(sandbox_info, cli_ctx)


@app.command("kill")
@handle_errors
def kill(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
) -> None:
    """Terminate a sandbox.

    This action is permanent and cannot be undone.

    Examples:
        # Kill with confirmation
        hopx sandbox kill 1763382095i648uu1o

        # Kill without confirmation
        hopx sandbox kill 1763382095i648uu1o --force
    """
    cli_ctx: CLIContext = ctx.obj

    # Confirm unless --force
    if not force:
        confirm = typer.confirm(f"Kill sandbox {sandbox_id}? This cannot be undone.")
        if not confirm:
            raise typer.Abort()

    with Spinner(f"Killing sandbox {sandbox_id}...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        sandbox.kill()
        spinner.success(f"Sandbox {sandbox_id} terminated")


@app.command("pause")
@handle_errors
def pause(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Pause a running sandbox.

    Paused sandboxes can be resumed later. Pausing stops resource usage
    but the sandbox state is preserved.

    Examples:
        hopx sandbox pause 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    with Spinner(f"Pausing sandbox {sandbox_id}...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        sandbox.pause()
        spinner.success(f"Sandbox {sandbox_id} paused")


@app.command("resume")
@handle_errors
def resume(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Resume a paused sandbox.

    Resumes a previously paused sandbox, restoring it to running state.

    Examples:
        hopx sandbox resume 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    with Spinner(f"Resuming sandbox {sandbox_id}...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        sandbox.resume()
        spinner.success(f"Sandbox {sandbox_id} resumed")


@app.command("timeout")
@handle_errors
def set_timeout(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    seconds: int = typer.Argument(..., help="Timeout in seconds (0 = no timeout)"),
) -> None:
    """Set auto-kill timeout for a sandbox.

    The sandbox will automatically terminate after the specified timeout.
    Set to 0 to disable auto-kill.

    Examples:
        # Set 2-hour timeout
        hopx sandbox timeout 1763382095i648uu1o 7200

        # Disable timeout
        hopx sandbox timeout 1763382095i648uu1o 0
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    sandbox.set_timeout(seconds)

    if seconds > 0:
        formatted = _format_time_remaining(seconds)
        console.print(f"[green]Timeout set to {seconds}s ({formatted})[/green]")
    else:
        console.print("[green]Timeout disabled[/green]")


@app.command("health")
@handle_errors
def health(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    wait: bool = typer.Option(
        False,
        "--wait",
        help="Wait until healthy (with timeout)",
    ),
    wait_timeout: int = typer.Option(
        60,
        "--wait-timeout",
        help="Max seconds to wait for health",
    ),
) -> None:
    """Check sandbox health status.

    Examples:
        # Check health once
        hopx sandbox health 1763382095i648uu1o

        # Wait until healthy (up to 60 seconds)
        hopx sandbox health 1763382095i648uu1o --wait

        # Wait with custom timeout
        hopx sandbox health 1763382095i648uu1o --wait --wait-timeout 120
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    if wait:
        with Spinner(f"Waiting for sandbox {sandbox_id} to be healthy...") as spinner:
            sandbox.ensure_healthy(timeout=wait_timeout)
            spinner.success(f"Sandbox {sandbox_id} is healthy")
    else:
        is_healthy = sandbox.is_healthy()

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print({"healthy": is_healthy})
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            console.print("healthy" if is_healthy else "unhealthy")
        else:
            if is_healthy:
                console.print(f"[green]Sandbox {sandbox_id} is healthy[/green]")
            else:
                console.print(f"[red]Sandbox {sandbox_id} is unhealthy[/red]")
                raise typer.Exit(code=1)


@app.command("expiry")
@handle_errors
def expiry(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get sandbox expiration information.

    Shows when the sandbox will expire and how much time remains.

    Examples:
        hopx sandbox expiry 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    expiry_info = sandbox.get_expiry_info()

    if cli_ctx.output_format == OutputFormat.JSON:
        format_output(
            expiry_info.model_dump(),
            cli_ctx.output_format,
        )
    elif cli_ctx.output_format == OutputFormat.PLAIN:
        if not expiry_info.has_timeout:
            console.print("never")
        elif expiry_info.is_expired:
            console.print("expired")
        else:
            console.print(_format_time_remaining(expiry_info.time_to_expiry))
    else:
        # Rich format
        if not expiry_info.has_timeout:
            console.print(f"[dim]Sandbox {sandbox_id} has no timeout configured[/dim]")
            return

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        if expiry_info.is_expired:
            table.add_row("Status", "[red]EXPIRED[/red]")
        elif expiry_info.is_expiring_soon:
            table.add_row("Status", "[yellow]Expiring soon[/yellow]")
        else:
            table.add_row("Status", "[green]Active[/green]")

        if expiry_info.expires_at:
            table.add_row("Expires At", expiry_info.expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

        if expiry_info.time_to_expiry:
            table.add_row(
                "Time Remaining",
                _format_time_remaining(expiry_info.time_to_expiry),
            )

        console.print(table)


@app.command("url")
@handle_errors
def url(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    port: int = typer.Argument(7777, help="Port number"),
) -> None:
    """Get preview URL for a sandbox port.

    Hopx automatically exposes all sandbox ports via public URLs.
    Default port is 7777 (agent API).

    Examples:
        # Get agent URL (port 7777)
        hopx sandbox url 1763382095i648uu1o

        # Get URL for custom port
        hopx sandbox url 1763382095i648uu1o 8080
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    preview_url = sandbox.get_preview_url(port)

    if cli_ctx.output_format == OutputFormat.JSON:
        console.print({"url": preview_url, "port": port})
    else:
        console.print(preview_url)


@app.command("connect")
@handle_errors
def connect(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Connect to an existing sandbox and show info.

    Establishes a connection to an existing sandbox and displays
    its current state and connection details.

    Examples:
        hopx sandbox connect 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    with Spinner(f"Connecting to sandbox {sandbox_id}...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        info = sandbox.get_info()
        spinner.success("Connected")

    if not cli_ctx.quiet:
        _format_sandbox_details(info, cli_ctx)


@app.command("token")
@handle_errors
def token(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        help="Force token refresh",
    ),
    reveal: bool = typer.Option(
        False,
        "--reveal",
        help="Show full token (use with caution)",
    ),
) -> None:
    """Get JWT token for sandbox agent API.

    This is primarily for debugging. The SDK handles token management
    automatically for most use cases.

    Examples:
        # Get current token (partial)
        hopx sandbox token 1763382095i648uu1o

        # Refresh and show token
        hopx sandbox token 1763382095i648uu1o --refresh

        # Show full token
        hopx sandbox token 1763382095i648uu1o --reveal
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    if refresh:
        with Spinner("Refreshing token..."):
            token_data = sandbox.refresh_token()
    else:
        token_data = sandbox.get_token()

    jwt_token = token_data.get("token", "")
    expires_at = token_data.get("expires_at")

    if cli_ctx.output_format == OutputFormat.JSON:
        output = {
            "token": jwt_token if reveal else jwt_token[:20] + "..." + jwt_token[-20:],
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        console.print(output)
    elif cli_ctx.output_format == OutputFormat.PLAIN:
        if reveal:
            console.print(jwt_token)
        else:
            console.print(jwt_token[:20] + "..." + jwt_token[-20:])
    else:
        # Rich format
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        if reveal:
            table.add_row("Token", jwt_token)
        else:
            table.add_row("Token", jwt_token[:20] + "..." + jwt_token[-20:])

        if expires_at:
            table.add_row("Expires", expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

            now = datetime.now(UTC)
            remaining = (expires_at - now).total_seconds()
            if remaining > 0:
                table.add_row("Valid For", _format_time_remaining(int(remaining)))
            else:
                table.add_row("Status", "[red]EXPIRED[/red]")

        console.print(table)

        if not reveal:
            console.print("\n[dim]Use --reveal to show full token[/dim]")
