"""System and health commands for the Hopx CLI."""

import json
from typing import Any

import typer
from hopx_ai import HopxError, Sandbox
from rich.console import Console
from rich.table import Table

from ..core import CLIContext

app = typer.Typer(
    help="System and health commands",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def format_output(ctx: typer.Context, data: Any, title: str = "") -> None:
    """Format and display output based on the global output format."""
    cli_ctx: CLIContext = ctx.obj
    output_format = cli_ctx.output_format.value if cli_ctx else "table"
    no_color = cli_ctx.no_color if cli_ctx else False

    if no_color:
        console.no_color = True

    if output_format == "json":
        typer.echo(json.dumps(data, indent=2))
    elif output_format == "plain":
        if isinstance(data, dict):
            for key, value in data.items():
                typer.echo(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                typer.echo(item)
        else:
            typer.echo(str(data))
    else:  # table
        if isinstance(data, dict):
            table = Table(title=title or "System Information", show_header=True)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            for key, value in data.items():
                table.add_row(str(key), str(value))
            console.print(table)
        elif isinstance(data, list):
            for item in data:
                console.print(item)
        else:
            console.print(data)


def get_sandbox_client(ctx: typer.Context, sandbox_id: str) -> Sandbox:
    """Get a Sandbox client instance with API key from context."""
    cli_ctx: CLIContext = ctx.obj
    api_key = cli_ctx.config.api_key if cli_ctx else None
    return Sandbox.connect(sandbox_id=sandbox_id, api_key=api_key)


@app.command("health")
def health(ctx: typer.Context) -> None:
    """Check Hopx API health status."""
    try:
        result = Sandbox.health_check()

        status_data = {
            "status": result.get("status", "unknown"),
            "message": result.get("message", ""),
        }

        format_output(ctx, status_data, "API Health Status")

        if result.get("status") != "healthy":
            raise typer.Exit(code=1)

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("metrics")
def metrics(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get system metrics snapshot for a sandbox."""
    try:
        sandbox = get_sandbox_client(ctx, sandbox_id)
        metrics_data = sandbox.get_metrics_snapshot()

        format_output(ctx, metrics_data, f"Metrics for Sandbox {sandbox_id}")

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("agent-info")
def agent_info(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get agent information for a sandbox."""
    try:
        sandbox = get_sandbox_client(ctx, sandbox_id)
        info_data = sandbox.get_agent_info()

        format_output(ctx, info_data, f"Agent Info for Sandbox {sandbox_id}")

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("processes")
def processes(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """List system processes in a sandbox."""
    try:
        sandbox = get_sandbox_client(ctx, sandbox_id)
        process_list = sandbox.list_processes()

        cli_ctx: CLIContext = ctx.obj
        output_format = cli_ctx.output_format.value if cli_ctx else "table"

        if output_format == "json":
            typer.echo(json.dumps(process_list, indent=2))
        elif output_format == "plain":
            for proc in process_list:
                typer.echo(f"PID: {proc.get('pid')} | Command: {proc.get('command', 'N/A')}")
        else:  # table
            table = Table(title=f"Processes in Sandbox {sandbox_id}", show_header=True)
            table.add_column("PID", style="cyan")
            table.add_column("Command", style="green")
            table.add_column("Status", style="yellow")

            for proc in process_list:
                table.add_row(
                    str(proc.get("pid", "")),
                    str(proc.get("command", "N/A")),
                    str(proc.get("status", "N/A")),
                )

            console.print(table)

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("jupyter")
def jupyter(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get Jupyter sessions in a sandbox."""
    try:
        sandbox = get_sandbox_client(ctx, sandbox_id)
        jupyter_data = sandbox.get_jupyter_sessions()

        format_output(ctx, jupyter_data, f"Jupyter Sessions in Sandbox {sandbox_id}")

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("snapshot")
def snapshot(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
) -> None:
    """Get metrics snapshot for a sandbox (alias for metrics command)."""
    try:
        sandbox = get_sandbox_client(ctx, sandbox_id)
        snapshot_data = sandbox.get_metrics_snapshot()

        format_output(ctx, snapshot_data, f"Metrics Snapshot for Sandbox {sandbox_id}")

    except HopxError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)
