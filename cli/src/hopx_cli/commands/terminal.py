"""Terminal operations for interactive sandbox sessions.

Provides WebSocket-based terminal access to sandboxes with PTY support.
"""

import asyncio
import sys
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ..core import CLIContext, OutputFormat, get_sandbox, handle_errors
from ..output import Spinner, format_output

app = typer.Typer(
    help="Interactive terminal sessions",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


@app.command("info")
@handle_errors
def info(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get terminal connection information.

    Shows WebSocket URL and connection details for the sandbox terminal.

    Examples:
        hopx terminal info 1763382095i648uu1o
        hopx term info 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    sandbox_info = sandbox.get_info()

    # Convert HTTPS to WSS
    agent_url = sandbox_info.public_host.rstrip("/")
    ws_url = agent_url.replace("https://", "wss://").replace("http://", "ws://")
    terminal_url = f"{ws_url}/terminal"

    if cli_ctx.output_format == OutputFormat.JSON:
        format_output(
            {
                "sandbox_id": sandbox_id,
                "agent_url": agent_url,
                "ws_url": ws_url,
                "terminal_url": terminal_url,
                "status": sandbox_info.status,
            },
            cli_ctx.output_format,
        )
    elif cli_ctx.output_format == OutputFormat.PLAIN:
        console.print(terminal_url)
    else:
        # Rich table format
        table = Table(
            title=f"Terminal Connection - {sandbox_id}",
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        table.add_row("Sandbox ID", sandbox_id)
        table.add_row("Status", _format_status(sandbox_info.status))
        table.add_row("Agent URL", agent_url)
        table.add_row("WebSocket URL", ws_url)
        table.add_row("Terminal URL", terminal_url)

        console.print(table)
        console.print("\n[dim]Use 'hopx terminal connect' for interactive session[/dim]")


@app.command("url")
@handle_errors
def url(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get terminal WebSocket URL.

    Returns the WebSocket URL for connecting to the sandbox terminal.

    Examples:
        hopx terminal url 1763382095i648uu1o
        hopx term url 1763382095i648uu1o
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    sandbox_info = sandbox.get_info()

    # Convert HTTPS to WSS
    agent_url = sandbox_info.public_host.rstrip("/")
    ws_url = agent_url.replace("https://", "wss://").replace("http://", "ws://")
    terminal_url = f"{ws_url}/terminal"

    if cli_ctx.output_format == OutputFormat.JSON:
        format_output(
            {
                "url": terminal_url,
                "sandbox_id": sandbox_id,
            },
            cli_ctx.output_format,
        )
    else:
        console.print(terminal_url)


@app.command("connect")
@handle_errors
def connect(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    command: str | None = typer.Option(
        None,
        "--command",
        "-c",
        help="Command to execute (default: interactive shell)",
    ),
    timeout: int = typer.Option(
        30,
        "--timeout",
        help="Connection timeout in seconds",
    ),
) -> None:
    """Connect to interactive terminal session.

    Opens a WebSocket connection to the sandbox terminal for interactive
    command execution. The terminal supports full PTY with real-time I/O.

    Note: This is a basic implementation. For full terminal features like
    resize support, use the Python SDK directly with asyncio.

    Examples:
        # Interactive shell
        hopx terminal connect 1763382095i648uu1o

        # Execute command and return
        hopx terminal connect 1763382095i648uu1o --command "ls -la"

        # With custom timeout
        hopx terminal connect 1763382095i648uu1o --timeout 60
    """
    cli_ctx: CLIContext = ctx.obj

    # Check if websockets is available
    import importlib.util

    if importlib.util.find_spec("websockets") is None:
        console.print(
            "[red]Error:[/red] websockets library required for terminal features\n"
            "[yellow]Install with:[/yellow] pip install websockets"
        )
        raise typer.Exit(code=1)

    # Run async connect
    try:
        asyncio.run(
            _async_connect(
                cli_ctx=cli_ctx,
                sandbox_id=sandbox_id,
                command=command,
                timeout=timeout,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Terminal session interrupted[/yellow]")
        raise typer.Exit(code=0)


async def _async_connect(
    cli_ctx: CLIContext,
    sandbox_id: str,
    command: str | None,
    timeout: int,
) -> None:
    """Async implementation of terminal connect.

    Args:
        cli_ctx: CLI context
        sandbox_id: Sandbox ID
        command: Optional command to execute
        timeout: Connection timeout
    """

    import websockets
    from hopx_ai import AsyncSandbox

    # Create async sandbox instance
    with Spinner(f"Connecting to sandbox {sandbox_id}...") as spinner:
        sandbox = AsyncSandbox(
            sandbox_id=sandbox_id,
            api_key=cli_ctx.config.api_key,
            base_url=cli_ctx.config.base_url,
        )

        # Get JWT token for authentication
        token = await sandbox.get_token()

        # Get sandbox info for WebSocket URL
        info = await sandbox.get_info()
        agent_url = info.public_host.rstrip("/")
        ws_url = agent_url.replace("https://", "wss://").replace("http://", "ws://")
        terminal_url = f"{ws_url}/terminal"

        spinner.success(f"Connected to {sandbox_id}")

    # Connect to WebSocket
    console.print("[dim]Opening terminal session...[/dim]")

    try:
        async with websockets.connect(
            terminal_url,
            additional_headers={"Authorization": f"Bearer {token}"},
            open_timeout=timeout,
        ) as ws:
            console.print("[green]Terminal connected[/green]")

            if command:
                # Execute command and wait for output
                await _execute_command(ws, command)
            else:
                # Interactive mode
                await _interactive_session(ws)

    except websockets.exceptions.ConnectionClosed:
        # Normal termination when shell exits
        pass
    except websockets.exceptions.WebSocketException as e:
        # Ignore "no close frame" errors - these happen when shell exits
        error_str = str(e).lower()
        if "close frame" not in error_str and "connection closed" not in error_str:
            console.print(f"[red]WebSocket error:[/red] {e}")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Connection failed:[/red] {e}")
        raise typer.Exit(code=1)


async def _execute_command(ws: Any, command: str) -> None:
    """Execute a single command and display output.

    Args:
        ws: WebSocket connection
        command: Command to execute
    """
    import json

    # Send command followed by exit to close the shell
    await ws.send(json.dumps({"type": "input", "data": f"{command}\n"}))

    # Give the command time to start executing
    await asyncio.sleep(0.1)

    # Send exit to close the shell after command completes
    await ws.send(json.dumps({"type": "input", "data": "exit\n"}))

    # Read output until exit or timeout (max 30 seconds)
    try:
        message_count = 0
        max_messages = 1000  # Safety limit

        # Read messages with timeout
        async def read_messages() -> None:
            nonlocal message_count
            async for message in ws:
                message_count += 1
                if message_count > max_messages:
                    console.print("\n[yellow]Message limit reached[/yellow]")
                    return

                if isinstance(message, bytes):
                    message = message.decode("utf-8")

                if not message or not message.strip():
                    continue

                try:
                    data = json.loads(message)

                    if data.get("type") == "output":
                        # Print output directly
                        output = data.get("data", "")
                        # Filter out terminal control sequences if needed
                        console.print(output, end="")
                    elif data.get("type") == "exit":
                        exit_code = data.get("code", 0)
                        if exit_code != 0:
                            console.print(f"\n[yellow]Exit code: {exit_code}[/yellow]")
                        return
                except json.JSONDecodeError:
                    continue

        await asyncio.wait_for(read_messages(), timeout=30)

    except TimeoutError:
        console.print("\n[yellow]Command timed out[/yellow]")


async def _interactive_session(ws: Any) -> None:
    """Run interactive terminal session.

    This is a basic implementation that reads from stdin and forwards
    to the WebSocket. For full PTY features (raw mode, signal handling),
    use the Python SDK directly.

    Args:
        ws: WebSocket connection
    """
    import json

    console.print("[dim]Interactive mode (press Ctrl+C to exit)[/dim]")
    console.print("[dim]Type 'exit' or press Ctrl+D to close session[/dim]\n")

    # Create tasks for reading input and output
    async def read_stdin() -> None:
        """Read from stdin and send to WebSocket."""
        loop = asyncio.get_event_loop()
        while True:
            # Read line from stdin (blocking, run in executor)
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:  # EOF (Ctrl+D)
                    break
                await ws.send(json.dumps({"type": "input", "data": line}))
            except Exception:
                break

    async def read_output() -> None:
        """Read from WebSocket and write to stdout."""
        try:
            async for message in ws:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")

                if not message or not message.strip():
                    continue

                try:
                    data = json.loads(message)

                    if data.get("type") == "output":
                        console.print(data.get("data", ""), end="")
                    elif data.get("type") == "exit":
                        exit_code = data.get("code", 0)
                        console.print(f"\n[yellow]Process exited with code {exit_code}[/yellow]")
                        break
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass

    # Run both tasks concurrently
    try:
        await asyncio.gather(
            read_stdin(),
            read_output(),
            return_exceptions=True,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Session terminated[/yellow]")


def _format_status(status: str) -> str:
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
