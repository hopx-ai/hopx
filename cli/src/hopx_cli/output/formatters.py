"""Main output formatter dispatcher.

Routes data to appropriate formatter based on output format selection.
Handles format detection and delegation to specialized formatters.
"""

from datetime import datetime
from typing import Any

from rich.console import Console

from ..core.context import OutputFormat
from .json_formatter import format_json
from .plain_formatter import format_plain
from .tables import (
    NULL_DISPLAY,
    EnvTable,
    FileTable,
    ProcessTable,
    SandboxTable,
    TemplateTable,
    build_table,
)


def format_timestamp(dt: datetime | str | None, include_relative: bool = True) -> str:
    """Format timestamp with ISO 8601 and optional relative time.

    Args:
        dt: Datetime object, ISO string, or None
        include_relative: Include relative time like "2h ago"

    Returns:
        Formatted timestamp string

    Examples:
        >>> format_timestamp(datetime.now())
        "2024-01-15T10:30:00 (just now)"
        >>> format_timestamp("2024-01-15T10:30:00Z", include_relative=False)
        "2024-01-15T10:30:00"
    """
    if dt is None:
        return NULL_DISPLAY

    # Parse datetime if string
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return str(dt)

    if not isinstance(dt, datetime):
        return str(dt)

    # ISO format
    iso_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    if not include_relative:
        return iso_str

    # Calculate relative time
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    # Future time
    if diff.total_seconds() < 0:
        diff = dt - now
        suffix = "from now"
    else:
        suffix = "ago"

    seconds = abs(diff.total_seconds())

    # Format based on magnitude
    if seconds < 60:
        relative = f"{int(seconds)}s {suffix}"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        relative = f"{minutes}m {suffix}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        relative = f"{hours}h {suffix}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        relative = f"{days}d {suffix}"
    else:
        weeks = int(seconds / 604800)
        relative = f"{weeks}w {suffix}"

    return f"{iso_str} ({relative})"


def format_output(
    data: Any,
    format: OutputFormat,
    table_config: dict[str, Any] | None = None,
    console: Console | None = None,
) -> None:
    """Format and print data according to output format.

    Dispatches to appropriate formatter based on format selection.
    Handles JSON, table, and plain text output formats.

    Args:
        data: Data to format and output
        format: Output format (TABLE, JSON, or PLAIN)
        table_config: Configuration for table formatting including:
            - title: Table title
            - columns: Column definitions
            - table_type: Type hint for table builder (sandbox, template, etc.)
        console: Rich console instance. Creates new if not provided.

    Examples:
        >>> format_output(sandboxes, OutputFormat.TABLE, {"table_type": "sandbox"})
        >>> format_output({"id": "123"}, OutputFormat.JSON)
        >>> format_output(["id1", "id2"], OutputFormat.PLAIN)
    """
    if console is None:
        console = Console()

    if format == OutputFormat.JSON:
        # JSON format - machine readable
        json_str = format_json(data)
        console.print(json_str)

    elif format == OutputFormat.PLAIN:
        # Plain text format - for scripting
        plain_str = format_plain(data)
        console.print(plain_str, highlight=False)

    elif format == OutputFormat.TABLE:
        # Table format - rich formatted output
        _format_table(data, table_config or {}, console)

    else:
        # Fallback to JSON for unknown formats
        json_str = format_json(data)
        console.print(json_str)


def _format_table(
    data: Any,
    config: dict[str, Any],
    console: Console,
) -> None:
    """Format data as a Rich table.

    Args:
        data: Data to format
        config: Table configuration
        console: Rich console instance
    """
    table_type = config.get("table_type")
    title = config.get("title")
    columns = config.get("columns")

    # Handle empty data
    if not data:
        if isinstance(data, list):
            console.print(f"[dim]No {table_type or 'items'} found[/dim]")
        else:
            console.print("[dim]No data[/dim]")
        return

    # Use specialized table builders if type is specified
    if table_type == "sandbox":
        table = SandboxTable.build(data, title=title)
        console.print(table)

    elif table_type == "template":
        table = TemplateTable.build(data, title=title)
        console.print(table)

    elif table_type == "file":
        table = FileTable.build(data, title=title)
        console.print(table)

    elif table_type == "process":
        table = ProcessTable.build(data, title=title)
        console.print(table)

    elif table_type == "env":
        table = EnvTable.build(data, title=title)
        console.print(table)

    else:
        # Generic table builder
        if columns:
            table = build_table(data, columns=columns, title=title)
            console.print(table)
        else:
            # No columns specified - output as JSON
            json_str = format_json(data)
            console.print(json_str)
