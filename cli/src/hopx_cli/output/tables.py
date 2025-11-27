"""Rich table builders for structured data.

Provides specialized table formatters for different data types including
sandboxes, templates, files, processes, and environment variables.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from rich import box
from rich.table import Table

# Consistent display for null/empty values across all tables
NULL_DISPLAY = "[dim]—[/dim]"  # Em dash, dimmed


def build_table(
    data: Any,
    columns: list[dict[str, Any]],
    title: str | None = None,
) -> Table:
    """Build a generic Rich table from data.

    Args:
        data: Data to display (list of dicts, models, or single item)
        columns: Column definitions with keys:
            - name: Column header
            - field: Field name to extract
            - align: Text alignment (left, center, right)
            - style: Rich style string
        title: Optional table title

    Returns:
        Configured Rich table instance

    Examples:
        >>> columns = [
        ...     {"name": "ID", "field": "id", "align": "left"},
        ...     {"name": "Status", "field": "status", "align": "center", "style": "bold"},
        ... ]
        >>> table = build_table(data, columns, title="Items")
    """
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold cyan")

    # Add columns
    for col in columns:
        table.add_column(
            col["name"],
            justify=col.get("align", "left"),
            style=col.get("style"),
            no_wrap=col.get("no_wrap", False),
        )

    # Normalize data to list
    items = data if isinstance(data, list) else [data]

    # Add rows
    for item in items:
        row_values: list[str] = []
        for col in columns:
            field = col["field"]
            value = _extract_value(item, field)
            formatted = _format_value(value, col.get("formatter"))
            row_values.append(formatted)

        table.add_row(*row_values)

    return table


class SandboxTable:
    """Table builder for sandbox data."""

    @staticmethod
    def build(data: Any, title: str | None = None) -> Table:
        """Build table for sandbox list or info.

        Args:
            data: Sandbox data (SandboxInfo or list)
            title: Optional table title

        Returns:
            Configured Rich table
        """
        columns = [
            {"name": "ID", "field": "sandbox_id", "align": "left", "style": "cyan"},
            {"name": "Template", "field": "template_name", "align": "left"},
            {"name": "Status", "field": "status", "align": "center", "formatter": "status"},
            {"name": "Region", "field": "region", "align": "center"},
            {"name": "Created", "field": "created_at", "align": "right", "formatter": "time_ago"},
            {"name": "Expires", "field": "expires_at", "align": "right", "formatter": "time_ago"},
        ]

        return build_table(data, columns, title=title or "Sandboxes")


class TemplateTable:
    """Table builder for template data."""

    @staticmethod
    def build(data: Any, title: str | None = None) -> Table:
        """Build table for template list or info.

        Args:
            data: Template data (Template or list)
            title: Optional table title

        Returns:
            Configured Rich table
        """
        columns = [
            {"name": "Name", "field": "name", "align": "left", "style": "cyan"},
            {"name": "Display Name", "field": "display_name", "align": "left"},
            {"name": "Status", "field": "status", "align": "center", "formatter": "status"},
            {"name": "Language", "field": "language", "align": "center"},
            {"name": "Category", "field": "category", "align": "left"},
            {"name": "Public", "field": "is_public", "align": "center", "formatter": "bool"},
        ]

        return build_table(data, columns, title=title or "Templates")


class FileTable:
    """Table builder for file listings."""

    @staticmethod
    def build(data: Any, title: str | None = None) -> Table:
        """Build table for file list.

        Args:
            data: File data (list of FileInfo or dicts)
            title: Optional table title

        Returns:
            Configured Rich table
        """
        columns = [
            {"name": "Name", "field": "name", "align": "left", "style": "cyan"},
            {"name": "Type", "field": "type", "align": "center", "formatter": "file_type"},
            {"name": "Size", "field": "size", "align": "right", "formatter": "size"},
            {"name": "Modified", "field": "modified_at", "align": "right", "formatter": "time_ago"},
            {"name": "Permissions", "field": "mode", "align": "center"},
        ]

        return build_table(data, columns, title=title or "Files")


class ProcessTable:
    """Table builder for process listings."""

    @staticmethod
    def build(data: Any, title: str | None = None) -> Table:
        """Build table for process list.

        Args:
            data: Process data (list of dicts)
            title: Optional table title

        Returns:
            Configured Rich table
        """
        columns = [
            {"name": "PID", "field": "pid", "align": "right", "style": "cyan"},
            {"name": "Command", "field": "command", "align": "left"},
            {"name": "Status", "field": "status", "align": "center", "formatter": "status"},
            {"name": "CPU %", "field": "cpu_percent", "align": "right"},
            {"name": "Memory %", "field": "memory_percent", "align": "right"},
            {"name": "Started", "field": "started_at", "align": "right", "formatter": "time_ago"},
        ]

        return build_table(data, columns, title=title or "Processes")


class EnvTable:
    """Table builder for environment variables."""

    @staticmethod
    def build(data: Any, title: str | None = None) -> Table:
        """Build table for environment variables.

        Args:
            data: Environment variable dict
            title: Optional table title

        Returns:
            Configured Rich table
        """
        # Convert dict to list of {name, value} dicts
        if isinstance(data, dict):
            items = [{"name": k, "value": v} for k, v in data.items()]
        else:
            items = data

        columns = [
            {"name": "Variable", "field": "name", "align": "left", "style": "cyan bold"},
            {"name": "Value", "field": "value", "align": "left"},
        ]

        return build_table(items, columns, title=title or "Environment Variables")


def _extract_value(obj: Any, field: str) -> Any:
    """Extract field value from object.

    Args:
        obj: Object (model, dict, or other)
        field: Field name

    Returns:
        Field value
    """
    if isinstance(obj, BaseModel):
        return getattr(obj, field, None)
    elif isinstance(obj, dict):
        return obj.get(field)
    else:
        return getattr(obj, field, None)


def _format_value(value: Any, formatter: str | None = None) -> str:
    """Format value according to formatter type.

    Args:
        value: Value to format
        formatter: Formatter name (status, time_ago, size, bool, file_type)

    Returns:
        Formatted string
    """
    # Handle None
    if value is None:
        return NULL_DISPLAY

    # Apply formatter
    if formatter == "status":
        return _format_status(value)
    elif formatter == "time_ago":
        return _format_time_ago(value)
    elif formatter == "size":
        return _format_size(value)
    elif formatter == "bool":
        return _format_bool(value)
    elif formatter == "file_type":
        return _format_file_type(value)
    else:
        return str(value)


def _format_status(status: str) -> str:
    """Format status with color coding.

    Args:
        status: Status string

    Returns:
        Formatted status with color
    """
    status_lower = status.lower() if isinstance(status, str) else ""

    if status_lower in ("running", "active", "ready", "success"):
        return f"[green]{status}[/green]"
    elif status_lower in ("paused", "pending", "building", "publishing"):
        return f"[yellow]{status}[/yellow]"
    elif status_lower in ("error", "failed", "stopped", "killed"):
        return f"[red]{status}[/red]"
    else:
        return str(status)


def _format_time_ago(dt: Any) -> str:
    """Format datetime as relative time ago.

    Args:
        dt: Datetime object or ISO string

    Returns:
        Human-readable time ago string (e.g., "2h 15m ago")
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

    # Calculate time difference
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
        return f"{int(seconds)}s {suffix}"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m {suffix}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        if minutes > 0:
            return f"{hours}h {minutes}m {suffix}"
        return f"{hours}h {suffix}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        if hours > 0:
            return f"{days}d {hours}h {suffix}"
        return f"{days}d {suffix}"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w {suffix}"


def _format_size(size: Any) -> str:
    """Format file size in human-readable format.

    Args:
        size: Size in bytes

    Returns:
        Human-readable size string (e.g., "1.2 MB")
    """
    if size is None:
        return NULL_DISPLAY

    try:
        bytes_val = int(size)
    except (ValueError, TypeError):
        return str(size)

    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        kb = bytes_val / 1024
        return f"{kb:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        mb = bytes_val / (1024 * 1024)
        return f"{mb:.1f} MB"
    else:
        gb = bytes_val / (1024 * 1024 * 1024)
        return f"{gb:.2f} GB"


def _format_bool(value: Any) -> str:
    """Format boolean value.

    Args:
        value: Boolean value

    Returns:
        Formatted boolean string
    """
    if value is None:
        return NULL_DISPLAY

    if value is True or (isinstance(value, str) and value.lower() == "true"):
        return "[green]Yes[/green]"
    elif value is False or (isinstance(value, str) and value.lower() == "false"):
        return "[dim]No[/dim]"
    else:
        return str(value)


def _format_file_type(file_type: str) -> str:
    """Format file type with icon.

    Args:
        file_type: File type string

    Returns:
        Formatted file type
    """
    if file_type is None:
        return NULL_DISPLAY

    type_lower = file_type.lower() if isinstance(file_type, str) else ""

    if type_lower in ("directory", "dir", "folder"):
        return "[blue]DIR[/blue]"
    elif type_lower in ("file", "regular"):
        return "[white]FILE[/white]"
    elif type_lower in ("symlink", "link"):
        return "[cyan]LINK[/cyan]"
    else:
        return str(file_type)
