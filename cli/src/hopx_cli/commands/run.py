"""Code execution commands for the Hopx CLI.

Provides the `hopx run` command for executing code in sandboxes with support for
multiple languages, input sources, background execution, and streaming output.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import typer
from hopx_ai import CommandResult, ExecutionResult, HopxError, Sandbox
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ..core import CLIContext

app = typer.Typer(
    help="Execute code in sandboxes",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()
console_stderr = Console(stderr=True)

# Language to file extension mapping
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".mjs"],
    "bash": [".sh", ".bash"],
    "go": [".go"],
}

# File extension to language mapping
EXTENSION_TO_LANGUAGE = {ext: lang for lang, exts in LANGUAGE_EXTENSIONS.items() for ext in exts}


def get_sandbox_client(ctx: typer.Context, sandbox_id: str) -> Sandbox:
    """Get a Sandbox client instance with API key from context."""
    cli_ctx: CLIContext = ctx.obj
    api_key = cli_ctx.config.api_key
    return Sandbox.connect(sandbox_id=sandbox_id, api_key=api_key)


def detect_language_from_file(file_path: Path) -> str:
    """Detect language from file extension.

    Args:
        file_path: Path to code file

    Returns:
        Language name (defaults to python if unknown)
    """
    suffix = file_path.suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(suffix, "python")


def parse_env_vars(env_list: list[str] | None) -> dict[str, str]:
    """Parse environment variable list.

    Args:
        env_list: List of KEY=VALUE strings

    Returns:
        Dictionary of environment variables

    Raises:
        typer.BadParameter: If env var format is invalid
    """
    if not env_list:
        return {}

    env_vars = {}
    for env_str in env_list:
        if "=" not in env_str:
            raise typer.BadParameter(f"Invalid env var format: {env_str} (use KEY=VALUE)")
        key, value = env_str.split("=", 1)
        env_vars[key] = value
    return env_vars


def truncate_output(text: str, max_lines: int = 1000) -> tuple[str, bool]:
    """Truncate output if too large.

    Args:
        text: Output text
        max_lines: Maximum number of lines

    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    if not text:
        return text, False

    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text, False

    truncated = "\n".join(lines[:max_lines])
    return truncated, True


def format_execution_result(
    result: ExecutionResult,
    output_format: str,
    language: str,
    verbose: bool = False,
    full_output: bool = False,
) -> None:
    """Format and display execution result.

    Args:
        result: Execution result from SDK
        output_format: Output format (table, json, plain)
        language: Programming language
        verbose: Show verbose output
        full_output: Show full output without truncation
    """
    if output_format == "json":
        # JSON output - machine readable
        data = {
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "exit_code": result.exit_code or 0,
            "success": result.success,
            "execution_time": result.execution_time,
            "result": result.result,
            "rich_outputs": [
                {"type": ro.type, "data_length": len(ro.data) if ro.data else 0}
                for ro in (result.rich_outputs or [])
            ],
        }
        console.print(json.dumps(data, indent=2))

    elif output_format == "plain":
        # Plain text - for scripting/piping
        if result.stdout:
            console.print(result.stdout, highlight=False, end="")
        if result.stderr:
            console.print(result.stderr, file=sys.stderr, highlight=False, end="")

    else:  # table
        # Rich formatted output
        if result.stdout:
            if full_output:
                stdout_text = result.stdout
                was_truncated = False
            else:
                stdout_text, was_truncated = truncate_output(result.stdout)

            if language in ["python", "javascript", "bash"]:
                syntax = Syntax(stdout_text, language, theme="monokai", line_numbers=False)
                console.print(Panel(syntax, title="[bold green]Output[/bold green]"))
            else:
                console.print(Panel(stdout_text, title="[bold green]Output[/bold green]"))

            if was_truncated:
                console.print(
                    "[dim]... output truncated (>1000 lines). Use --full to see all.[/dim]"
                )

        if result.stderr:
            if full_output:
                stderr_text = result.stderr
                was_truncated = False
            else:
                stderr_text, was_truncated = truncate_output(result.stderr)

            console.print(
                Panel(stderr_text, title="[bold red]Error Output[/bold red]", border_style="red")
            )
            if was_truncated:
                console.print(
                    "[dim]... error output truncated (>1000 lines). Use --full to see all.[/dim]"
                )

        if result.result and result.result != result.stdout:
            console.print(
                Panel(result.result, title="[bold blue]Result[/bold blue]", border_style="blue")
            )

        # Show rich outputs
        if result.rich_outputs:
            console.print(f"\n[bold cyan]Rich Outputs:[/bold cyan] {len(result.rich_outputs)}")
            for i, output in enumerate(result.rich_outputs):
                console.print(
                    f"  {i + 1}. {output.type} ({len(output.data) if output.data else 0} bytes)"
                )

        # Show execution info if verbose
        if verbose:
            info = Table.grid(padding=(0, 2))
            info.add_row(
                "[dim]Exit Code:[/dim]",
                f"[{'green' if result.success else 'red'}]{result.exit_code or 0}[/]",
            )
            info.add_row(
                "[dim]Execution Time:[/dim]",
                f"{result.execution_time or 0:.3f}s",
            )
            info.add_row(
                "[dim]Success:[/dim]",
                f"[{'green' if result.success else 'red'}]{result.success}[/]",
            )
            console.print(info)


def format_command_result(
    result: CommandResult,
    output_format: str,
    verbose: bool = False,
) -> None:
    """Format and display command result.

    Args:
        result: Command result from SDK
        output_format: Output format (table, json, plain)
        verbose: Show verbose output
    """
    if output_format == "json":
        data = {
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "exit_code": result.exit_code or 0,
            "success": result.success,
            "execution_time": result.execution_time,
            "pid": result.pid,
        }
        console.print(json.dumps(data, indent=2))

    elif output_format == "plain":
        if result.stdout:
            console.print(result.stdout, highlight=False, end="")
        if result.stderr:
            console.print(result.stderr, file=sys.stderr, highlight=False, end="")

    else:  # table
        if result.stdout:
            stdout_text, was_truncated = truncate_output(result.stdout)
            console.print(Panel(stdout_text, title="[bold green]Output[/bold green]"))
            if was_truncated:
                console.print("[dim]... output truncated (>1000 lines)[/dim]")

        if result.stderr:
            stderr_text, was_truncated = truncate_output(result.stderr)
            console.print(
                Panel(stderr_text, title="[bold red]Error Output[/bold red]", border_style="red")
            )
            if was_truncated:
                console.print("[dim]... error output truncated (>1000 lines)[/dim]")

        if verbose:
            info = Table.grid(padding=(0, 2))
            info.add_row(
                "[dim]Exit Code:[/dim]",
                f"[{'green' if result.is_success else 'red'}]{result.exit_code or 0}[/]",
            )
            info.add_row(
                "[dim]Execution Time:[/dim]",
                f"{result.execution_time or 0:.3f}s",
            )
            if result.pid:
                info.add_row("[dim]PID:[/dim]", str(result.pid))
            console.print(info)


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    code: str | None = typer.Argument(
        None,
        help="Code to execute (use '-' to read from stdin)",
    ),
    file: Path | None = typer.Option(
        None,
        "--file",
        "-f",
        help="File containing code to execute",
    ),
    sandbox: str | None = typer.Option(
        None,
        "--sandbox",
        "-s",
        help="Sandbox ID (creates temporary if omitted)",
    ),
    template: str = typer.Option(
        "code-interpreter",
        "--template",
        "-t",
        help="Template for temporary sandbox",
    ),
    language: str | None = typer.Option(
        None,
        "--language",
        "-l",
        help="Language: python, javascript, bash, go",
    ),
    timeout: int = typer.Option(
        120,
        "--timeout",
        "-T",
        help="Execution timeout in seconds",
    ),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable (KEY=VALUE, repeatable)",
    ),
    workdir: str = typer.Option(
        "/workspace",
        "--workdir",
        "-w",
        help="Working directory",
    ),
    preflight: bool = typer.Option(
        False,
        "--preflight",
        help="Run health check before execution",
    ),
    background: bool = typer.Option(
        False,
        "--background",
        "-b",
        help="Run in background, return process ID",
    ),
    keep: bool = typer.Option(
        False,
        "--keep",
        help="Don't kill temporary sandbox after execution",
    ),
    full: bool = typer.Option(
        False,
        "--full",
        "--no-pager",
        help="Show full output without truncation",
    ),
) -> None:
    """
    Execute code in a sandbox.

    Examples:
      hopx run "print('Hello')"
      hopx run -f script.py
      echo "print(1+1)" | hopx run -
      hopx run -s abc123 "console.log('hi')" -l javascript
    """
    # If subcommand invoked, skip main execution
    if ctx.invoked_subcommand is not None:
        return

    try:
        # Get context settings
        cli_ctx: CLIContext = ctx.obj
        output_format = cli_ctx.output_format.value
        verbose = cli_ctx.verbose
        quiet = cli_ctx.quiet

        # Determine code source
        code_content = None
        detected_language = language or "python"

        if code == "-":
            # Read from stdin
            code_content = sys.stdin.read()
            if not code_content.strip():
                raise typer.BadParameter("No code provided via stdin")

        elif file:
            # Read from file
            if not file.exists():
                raise typer.BadParameter(f"File not found: {file}")

            code_content = file.read_text()

            # Auto-detect language from extension if not specified
            if not language:
                detected_language = detect_language_from_file(file)

        elif code is not None:
            # Code provided as argument
            code_content = code

        else:
            # No code source provided
            raise typer.BadParameter("Provide code, --file, or '-' for stdin")

        # Parse environment variables
        env_vars = parse_env_vars(env)

        # Get or create sandbox
        created_temp = False
        sb = None

        if sandbox:
            # Connect to existing sandbox
            if not quiet:
                console_stderr.print(f"[dim]Connecting to sandbox {sandbox}...[/dim]")
            sb = get_sandbox_client(ctx, sandbox)
        else:
            # Create temporary sandbox
            if not quiet:
                console_stderr.print(
                    f"[dim]Creating temporary sandbox (template: {template})...[/dim]"
                )

            api_key = cli_ctx.config.api_key
            sb = Sandbox.create(template=template, api_key=api_key, env_vars=env_vars)
            created_temp = True

            if not quiet:
                console_stderr.print(f"[dim]Created sandbox: {sb.sandbox_id}[/dim]")

        try:
            # Set additional env vars if provided and using existing sandbox
            if sandbox and env_vars:
                sb.env.update(env_vars)

            # Run preflight check
            if preflight:
                if not quiet:
                    console_stderr.print("[dim]Running preflight check...[/dim]")
                health = sb.get_health()
                if health.get("status") != "healthy":
                    console_stderr.print("[yellow]Warning:[/yellow] Sandbox health check failed")

            # Execute code
            if background:
                # Background execution via commands API
                if not quiet:
                    console_stderr.print("[dim]Starting background process...[/dim]")

                # Wrap code execution as background command
                if detected_language == "python":
                    cmd = f"python -c {code_content!r}"
                elif detected_language == "javascript":
                    cmd = f"node -e {code_content!r}"
                elif detected_language == "bash":
                    cmd = code_content
                else:
                    cmd = code_content

                result = sb.commands.run(
                    cmd,
                    working_dir=workdir,
                    background=True,
                    timeout=timeout,
                )

                if output_format == "json":
                    console.print(
                        json.dumps(
                            {
                                "message": "Background process started",
                                "stdout": result.stdout,
                                "pid": result.pid,
                            },
                            indent=2,
                        )
                    )
                elif output_format == "plain":
                    console.print(result.stdout or "Background process started")
                else:
                    console.print(
                        Panel(
                            result.stdout or "Background process started",
                            title="[bold green]Background Process[/bold green]",
                        )
                    )
                    console.print(
                        f"\n[dim]Use 'hopx run ps -s {sb.sandbox_id}' to check status[/dim]"
                    )

            else:
                # Regular synchronous execution
                result = sb.run_code(
                    code_content,
                    language=detected_language,
                    timeout=timeout,
                )

                format_execution_result(result, output_format, detected_language, verbose, full)

                # Set exit code based on execution result
                if result.exit_code is not None and result.exit_code != 0:
                    raise typer.Exit(code=result.exit_code)

        finally:
            # Clean up temporary sandbox
            if created_temp and not keep:
                if not quiet:
                    console_stderr.print(
                        f"[dim]Cleaning up temporary sandbox {sb.sandbox_id}...[/dim]"
                    )
                sb.kill()

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Exit(code=130)


@app.command("ps")
def ps(
    ctx: typer.Context,
    sandbox: str | None = typer.Option(
        None,
        "--sandbox",
        "-s",
        help="Sandbox ID (required)",
    ),
) -> None:
    """List background processes in a sandbox."""
    try:
        if not sandbox:
            raise typer.BadParameter("Sandbox ID required (use --sandbox)")

        # Get context settings
        cli_ctx: CLIContext = ctx.obj
        output_format = cli_ctx.output_format.value
        quiet = cli_ctx.quiet

        if not quiet:
            console_stderr.print(f"[dim]Fetching processes for sandbox {sandbox}...[/dim]")

        sb = get_sandbox_client(ctx, sandbox)
        processes = sb.list_processes()

        if output_format == "json":
            console.print(json.dumps(processes, indent=2))

        elif output_format == "plain":
            for proc in processes:
                pid = proc.get("pid", "N/A")
                cmd = proc.get("command", "N/A")
                status = proc.get("status", "N/A")
                console.print(f"{pid}\t{cmd}\t{status}")

        else:  # table
            if not processes:
                console.print("[dim]No processes found[/dim]")
                return

            table = Table(title=f"Processes in Sandbox {sandbox}", show_header=True)
            table.add_column("Process ID", style="cyan", no_wrap=True)
            table.add_column("Command", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Started", style="dim")

            for proc in processes:
                # Parse process info
                pid = str(proc.get("pid", "N/A"))
                cmd = str(proc.get("command", "N/A"))
                status = str(proc.get("status", "unknown"))

                # Truncate long commands
                if len(cmd) > 50:
                    cmd = cmd[:47] + "..."

                # Format timestamp if available
                started = proc.get("started_at", "")
                if started:
                    try:
                        dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                        now = datetime.now(dt.tzinfo)
                        delta = now - dt

                        if delta.total_seconds() < 60:
                            started_str = f"{int(delta.total_seconds())}s ago"
                        elif delta.total_seconds() < 3600:
                            started_str = f"{int(delta.total_seconds() / 60)}m ago"
                        else:
                            started_str = f"{int(delta.total_seconds() / 3600)}h ago"
                    except Exception:
                        started_str = started
                else:
                    started_str = "N/A"

                table.add_row(pid, cmd, status, started_str)

            console.print(table)

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("kill")
def kill_process(
    ctx: typer.Context,
    process_id: str = typer.Argument(..., help="Process ID to kill"),
    sandbox: str | None = typer.Option(
        None,
        "--sandbox",
        "-s",
        help="Sandbox ID (required)",
    ),
) -> None:
    """Kill a background process in a sandbox."""
    try:
        if not sandbox:
            raise typer.BadParameter("Sandbox ID required (use --sandbox)")

        # Get context settings
        cli_ctx: CLIContext = ctx.obj
        output_format = cli_ctx.output_format.value
        quiet = cli_ctx.quiet

        if not quiet:
            console_stderr.print(f"[dim]Killing process {process_id} in sandbox {sandbox}...[/dim]")

        sb = get_sandbox_client(ctx, sandbox)

        # Kill the process
        # Note: SDK may not have a direct kill_process method, so we use commands
        result = sb.commands.run(f"kill {process_id}", timeout=10)

        if output_format == "json":
            console.print(
                json.dumps(
                    {
                        "process_id": process_id,
                        "sandbox": sandbox,
                        "killed": result.is_success,
                        "message": result.stdout or result.stderr,
                    },
                    indent=2,
                )
            )

        elif output_format == "plain":
            if result.is_success:
                console.print(f"Process {process_id} killed")
            else:
                console.print(f"Failed to kill process {process_id}")

        else:  # table
            if result.is_success:
                console.print(f"[green]✓[/green] Process {process_id} killed")
            else:
                console.print(f"[red]✗[/red] Failed to kill process {process_id}")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)
