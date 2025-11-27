"""File operations commands for the Hopx CLI.

Implements all file operations including read, write, upload, download,
list, delete, and info commands for managing files within sandboxes.
"""

import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table

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
    help="File operations on sandboxes",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string like "1.23 KB" or "456 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def _format_file_info(file_info: dict[str, Any], ctx: CLIContext) -> None:
    """Format and display file information.

    Args:
        file_info: File information dictionary
        ctx: CLI context
    """
    # Convert modified_time to string if it's a datetime object
    modified_time = file_info.get("modified_time")
    if modified_time is not None:
        if hasattr(modified_time, "isoformat"):
            modified_time_str = modified_time.isoformat()
        else:
            modified_time_str = str(modified_time)
    else:
        modified_time_str = None

    if ctx.output_format == OutputFormat.JSON:
        # For JSON, convert datetime to ISO string
        output_info = dict(file_info)
        if modified_time_str:
            output_info["modified_time"] = modified_time_str
        format_output(output_info, ctx.output_format)
    elif ctx.output_format == OutputFormat.PLAIN:
        lines = [
            f"Name: {file_info.get('name', 'N/A')}",
            f"Path: {file_info.get('path', 'N/A')}",
            f"Size: {_format_file_size(file_info.get('size', 0))}",
            f"Type: {'directory' if file_info.get('is_directory') else 'file'}",
            f"Permissions: {file_info.get('permissions', 'N/A')}",
        ]
        if modified_time_str:
            lines.append(f"Modified: {modified_time_str}")
        console.print("\n".join(lines))
    else:
        # Rich table format
        table = Table(
            title="File Info",
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        table.add_row("Name", file_info.get("name", "[dim]N/A[/dim]"))
        table.add_row("Path", file_info.get("path", "[dim]N/A[/dim]"))
        table.add_row("Size", _format_file_size(file_info.get("size", 0)))
        table.add_row("Type", "📁 Directory" if file_info.get("is_directory") else "📄 File")
        table.add_row("Permissions", file_info.get("permissions", "[dim]N/A[/dim]"))

        if modified_time_str:
            table.add_row("Modified", modified_time_str)

        console.print(table)


@app.command("read")
@handle_errors
def read(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    path: str = typer.Argument(..., help="File path to read"),
) -> None:
    """Read file contents from sandbox.

    Examples:
        # Read a text file
        hopx files read 1763382095i648uu1o /workspace/data.txt

        # Read and pipe to local file
        hopx files read 1763382095i648uu1o /app/config.json > config.json
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    content = sandbox.files.read(path)

    # Always output content directly (ignore output format for file content)
    console.print(content, end="")


@app.command("write")
@handle_errors
def write(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    path: str = typer.Argument(..., help="File path to write"),
    data: str | None = typer.Option(
        None,
        "--data",
        "-d",
        help="Data to write (use '-' to read from stdin)",
    ),
) -> None:
    """Write file contents to sandbox.

    Examples:
        # Write inline data
        hopx files write 1763382095i648uu1o /workspace/hello.txt --data "Hello, World!"

        # Read from stdin
        echo "Hello" | hopx files write 1763382095i648uu1o /workspace/hello.txt --data -

        # Pipe file content
        cat local.txt | hopx files write 1763382095i648uu1o /workspace/remote.txt --data -
    """
    cli_ctx: CLIContext = ctx.obj

    # Read content from stdin or data parameter
    if data == "-" or data is None:
        if not sys.stdin.isatty():
            # Read from stdin
            content = sys.stdin.read()
        elif data is None:
            console.print("[red]Error: Must provide --data or pipe content via stdin[/red]")
            raise typer.Exit(code=1)
        else:
            console.print("[red]Error: No data provided via stdin[/red]")
            raise typer.Exit(code=1)
    else:
        content = data

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    with Spinner(f"Writing file {path}...") as spinner:
        sandbox.files.write(path, content)
        spinner.success(f"File written: {path}")


@app.command("list")
@handle_errors
def list_files(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    path: str = typer.Argument("/workspace", help="Directory path to list"),
) -> None:
    """List files in sandbox directory.

    Examples:
        # List workspace directory
        hopx files list 1763382095i648uu1o

        # List specific directory
        hopx files list 1763382095i648uu1o /app/data

        # List root
        hopx files list 1763382095i648uu1o /
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    files = sandbox.files.list(path)

    if not files:
        if not cli_ctx.quiet:
            console.print(f"[dim]No files found in {path}[/dim]")
        return

    # Convert FileInfo objects to dicts for formatting
    files_data = []
    for f in files:
        files_data.append(
            {
                "name": f.name,
                "path": f.path,
                "size": f.size,
                "size_kb": f.size_kb,
                "is_directory": f.is_directory,
                "is_dir": f.is_directory,
                "is_file": f.is_file,
                "permissions": f.permissions,
                "modified_time": f.modified_time,
            }
        )

    format_output(
        files_data,
        cli_ctx.output_format,
        table_config={"table_type": "file", "title": f"Files in {path}"},
    )


@app.command("delete")
@handle_errors
def delete(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    path: str = typer.Argument(..., help="File or directory path to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
) -> None:
    """Delete file or directory from sandbox.

    Examples:
        # Delete with confirmation
        hopx files delete 1763382095i648uu1o /workspace/temp.txt

        # Delete without confirmation
        hopx files delete 1763382095i648uu1o /workspace/old_data --force

        # Delete directory (recursive)
        hopx files delete 1763382095i648uu1o /workspace/cache -f
    """
    cli_ctx: CLIContext = ctx.obj

    # Confirm unless --force
    if not force:
        confirm = typer.confirm(f"Delete {path}? This cannot be undone.")
        if not confirm:
            raise typer.Abort()

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    with Spinner(f"Deleting {path}...") as spinner:
        sandbox.files.remove(path)
        spinner.success(f"Deleted: {path}")


@app.command("upload")
@handle_errors
def upload(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    local_path: str = typer.Argument(..., help="Local file path"),
    remote_path: str = typer.Argument(..., help="Destination path in sandbox"),
) -> None:
    """Upload local file to sandbox.

    Examples:
        # Upload file
        hopx files upload 1763382095i648uu1o ./data.csv /workspace/data.csv

        # Upload to different name
        hopx files upload 1763382095i648uu1o ./local.txt /workspace/remote.txt

        # Upload binary file
        hopx files upload 1763382095i648uu1o ./image.png /workspace/assets/image.png
    """
    cli_ctx: CLIContext = ctx.obj

    local_file = Path(local_path)
    if not local_file.exists():
        console.print(f"[red]Error: Local file not found: {local_path}[/red]")
        raise typer.Exit(code=1)

    if not local_file.is_file():
        console.print(f"[red]Error: Path is not a file: {local_path}[/red]")
        raise typer.Exit(code=1)

    file_size = local_file.stat().st_size
    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    # Show progress for larger files
    if file_size > 1024 * 1024:  # > 1MB
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Uploading {local_file.name}...", total=file_size)
            sandbox.files.upload(local_path, remote_path, timeout=120)
            progress.update(task, completed=file_size)
    else:
        with Spinner(f"Uploading {local_file.name}...") as spinner:
            sandbox.files.upload(local_path, remote_path)
            spinner.success(f"Uploaded: {local_path} → {remote_path}")


@app.command("download")
@handle_errors
def download(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    remote_path: str = typer.Argument(..., help="File path in sandbox"),
    local_path: str = typer.Argument(..., help="Local destination path"),
) -> None:
    """Download file from sandbox to local filesystem.

    Examples:
        # Download file
        hopx files download 1763382095i648uu1o /workspace/result.csv ./result.csv

        # Download to current directory
        hopx files download 1763382095i648uu1o /workspace/plot.png ./plot.png

        # Download binary file
        hopx files download 1763382095i648uu1o /workspace/output.pdf ./output.pdf
    """
    cli_ctx: CLIContext = ctx.obj

    local_file = Path(local_path)
    if local_file.exists() and local_file.is_dir():
        console.print(f"[red]Error: Local path is a directory: {local_path}[/red]")
        raise typer.Exit(code=1)

    # Create parent directory if it doesn't exist
    local_file.parent.mkdir(parents=True, exist_ok=True)

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    with Spinner(f"Downloading {Path(remote_path).name}...") as spinner:
        sandbox.files.download(remote_path, local_path, timeout=120)
        downloaded_size = local_file.stat().st_size
        spinner.success(
            f"Downloaded: {remote_path} → {local_path} ({_format_file_size(downloaded_size)})"
        )


@app.command("info")
@handle_errors
def info(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    path: str = typer.Argument(..., help="File or directory path"),
) -> None:
    """Get file or directory information.

    Examples:
        # Get file info
        hopx files info 1763382095i648uu1o /workspace/data.txt

        # Get directory info
        hopx files info 1763382095i648uu1o /workspace/
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

    # Check if file exists first
    exists = sandbox.files.exists(path)
    if not exists:
        console.print(f"[red]Error: File not found: {path}[/red]")
        raise typer.Exit(code=1)

    # Get parent directory and filename
    path_obj = Path(path)
    parent_dir = str(path_obj.parent)
    filename = path_obj.name

    # List parent directory to get file info
    files = sandbox.files.list(parent_dir)
    file_info = None

    for f in files:
        if f.name == filename:
            file_info = {
                "name": f.name,
                "path": f.path,
                "size": f.size,
                "is_directory": f.is_directory,
                "permissions": f.permissions,
                "modified_time": f.modified_time,
            }
            break

    if not file_info:
        console.print(f"[yellow]Warning: File exists but metadata not available: {path}[/yellow]")
        raise typer.Exit(code=1)

    _format_file_info(file_info, cli_ctx)
