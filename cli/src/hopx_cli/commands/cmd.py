"""Shell command execution commands for the Hopx CLI.

Implements command execution operations in sandboxes including synchronous,
background, and long-running commands with proper output streaming and error handling.
"""

import typer
from hopx_ai import CommandResult
from rich.console import Console
from rich.panel import Panel

from ..core import (
    CLIContext,
    OutputFormat,
    get_sandbox,
    handle_errors,
)
from ..output import (
    Spinner,
    format_output,
)

app = typer.Typer(
    help="Run shell commands in sandboxes",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _parse_env_vars(env_list: list[str] | None) -> dict[str, str]:
    """Parse environment variables from command line.

    Args:
        env_list: List of KEY=VALUE strings from --env flag

    Returns:
        Dictionary of environment variables

    Raises:
        typer.BadParameter: If env var format is invalid
    """
    env_vars: dict[str, str] = {}

    if env_list:
        for env_str in env_list:
            if "=" not in env_str:
                raise typer.BadParameter(f"Invalid env var format: {env_str} (expected KEY=VALUE)")

            key, value = env_str.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def _format_command_result(
    result: CommandResult,
    ctx: CLIContext,
    command: str,
) -> None:
    """Format and display command result.

    Args:
        result: Command execution result
        ctx: CLI context
        command: The command that was executed
    """
    # Determine success based on exit code
    is_success = result.exit_code == 0

    if ctx.output_format == OutputFormat.JSON:
        format_output(
            {
                "command": command,
                "success": is_success,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
            },
            ctx.output_format,
        )
    elif ctx.output_format == OutputFormat.PLAIN:
        # Plain format - just output stdout and stderr
        if result.stdout:
            console.print(result.stdout, end="")
        if result.stderr:
            console.print(result.stderr, end="", style="red")
    else:
        # Rich table format with panels
        if result.stdout:
            console.print(
                Panel(
                    result.stdout,
                    title="[cyan]Standard Output[/cyan]",
                    border_style="cyan",
                )
            )

        if result.stderr:
            console.print(
                Panel(
                    result.stderr,
                    title="[red]Standard Error[/red]",
                    border_style="red",
                )
            )

        # Show execution summary
        status_color = "green" if is_success else "red"
        status_text = "SUCCESS" if is_success else "FAILED"

        summary_lines = [
            f"[bold {status_color}]Status:[/bold {status_color}] {status_text}",
            f"[bold]Exit Code:[/bold] {result.exit_code}",
            f"[bold]Execution Time:[/bold] {result.execution_time:.2f}s",
        ]

        console.print("\n" + "\n".join(summary_lines))


@app.command("run")
@handle_errors
def run(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    command: str = typer.Argument(..., help="Shell command to execute"),
    timeout: int = typer.Option(
        120,
        "--timeout",
        "-t",
        help="Command timeout in seconds",
    ),
    workdir: str = typer.Option(
        "/workspace",
        "--workdir",
        "-w",
        help="Working directory for command execution",
    ),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable (KEY=VALUE, repeatable)",
    ),
    background: bool = typer.Option(
        False,
        "--background",
        "-b",
        help="Run command in background (returns immediately)",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress execution details (show output only)",
    ),
) -> None:
    """Run a shell command in a sandbox.

    The command is executed in a bash shell with proper error handling.
    Use --background to start long-running processes.

    Examples:
        # Run simple command
        hopx cmd run 1763382095i648uu1o "ls -la /workspace"

        # Run with timeout
        hopx cmd run 1763382095i648uu1o "npm install" --timeout 300

        # Run with environment variables
        hopx cmd run 1763382095i648uu1o "echo $API_KEY" -e API_KEY=secret

        # Run in background
        hopx cmd run 1763382095i648uu1o "python train.py" --background --timeout 3600

        # Run with custom working directory
        hopx cmd run 1763382095i648uu1o "ls" --workdir /tmp

        # Multiple environment variables
        hopx cmd run 1763382095i648uu1o "./app" -e PORT=8080 -e DEBUG=true
    """
    cli_ctx: CLIContext = ctx.obj

    # Parse environment variables
    env_vars = _parse_env_vars(env)

    # Get sandbox
    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    # Execute command with spinner (unless quiet or plain output)
    show_spinner = not quiet and cli_ctx.output_format != OutputFormat.PLAIN

    if show_spinner:
        spinner_text = f"Running command in sandbox {sandbox_id}..."
        if background:
            spinner_text = f"Starting background command in sandbox {sandbox_id}..."

        with Spinner(spinner_text) as spinner:
            result = sandbox.commands.run(
                command,
                timeout=timeout,
                background=background,
                env=env_vars if env_vars else None,
                working_dir=workdir,
            )

            if background:
                spinner.success("Background command started")
            else:
                is_success = result.exit_code == 0
                if is_success:
                    spinner.success("Command completed successfully")
                else:
                    spinner.error(f"Command failed with exit code {result.exit_code}")
    else:
        result = sandbox.commands.run(
            command,
            timeout=timeout,
            background=background,
            env=env_vars if env_vars else None,
            working_dir=workdir,
        )

    # Determine success
    is_success = result.exit_code == 0

    # Format output (skip if quiet and success)
    if not (quiet and is_success):
        _format_command_result(result, cli_ctx, command)

    # Exit with error code if command failed
    if not is_success and not background:
        raise typer.Exit(code=result.exit_code)


@app.command("exec")
@handle_errors
def exec_cmd(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    command: list[str] = typer.Argument(..., help="Command and arguments"),
    timeout: int = typer.Option(
        120,
        "--timeout",
        "-t",
        help="Command timeout in seconds",
    ),
    workdir: str = typer.Option(
        "/workspace",
        "--workdir",
        "-w",
        help="Working directory for command execution",
    ),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable (KEY=VALUE, repeatable)",
    ),
) -> None:
    """Execute a command with proper argument handling.

    This is similar to 'run' but handles command arguments more explicitly,
    similar to docker exec. Arguments are passed as separate values.

    Examples:
        # Execute with explicit arguments
        hopx cmd exec 1763382095i648uu1o ls -la /workspace

        # With environment variables
        hopx cmd exec 1763382095i648uu1o python script.py -e DEBUG=true

        # With custom working directory
        hopx cmd exec 1763382095i648uu1o cat data.txt --workdir /tmp
    """
    cli_ctx: CLIContext = ctx.obj

    # Join command and arguments into a single command string
    full_command = " ".join(command)

    # Parse environment variables
    env_vars = _parse_env_vars(env)

    # Get sandbox
    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    # Execute command
    show_spinner = cli_ctx.output_format != OutputFormat.PLAIN

    if show_spinner:
        with Spinner(f"Executing command in sandbox {sandbox_id}...") as spinner:
            result = sandbox.commands.run(
                full_command,
                timeout=timeout,
                env=env_vars if env_vars else None,
                working_dir=workdir,
            )

            is_success = result.exit_code == 0
            if is_success:
                spinner.success("Command completed successfully")
            else:
                spinner.error(f"Command failed with exit code {result.exit_code}")
    else:
        result = sandbox.commands.run(
            full_command,
            timeout=timeout,
            env=env_vars if env_vars else None,
            working_dir=workdir,
        )

    # Format output
    _format_command_result(result, cli_ctx, full_command)

    # Exit with error code if command failed
    is_success = result.exit_code == 0
    if not is_success:
        raise typer.Exit(code=result.exit_code)
