"""Output formatting system for the Hopx CLI.

This module provides comprehensive output formatting capabilities including:
- Rich table formatting for structured data
- JSON output for machine-readable results
- Plain text output for scripting and piping
- Progress indicators for long-running operations
- Live output streaming for logs and build processes

The module respects the NO_COLOR environment variable and console width constraints.
"""

from .formatters import format_output, format_timestamp
from .json_formatter import format_json
from .plain_formatter import format_plain
from .progress import LiveOutput, ProgressBar, Spinner, StatusPanel
from .prompts import (
    confirm_action,
    confirm_destructive,
    prompt_choice,
    prompt_text,
    show_resource_summary,
)
from .tables import (
    NULL_DISPLAY,
    EnvTable,
    FileTable,
    ProcessTable,
    SandboxTable,
    TemplateTable,
    build_table,
)

__all__ = [
    # Main formatter
    "format_output",
    "format_timestamp",
    # Format-specific formatters
    "format_json",
    "format_plain",
    # Constants
    "NULL_DISPLAY",
    # Table builders
    "build_table",
    "SandboxTable",
    "TemplateTable",
    "FileTable",
    "ProcessTable",
    "EnvTable",
    # Progress indicators
    "Spinner",
    "ProgressBar",
    "StatusPanel",
    "LiveOutput",
    # Prompts
    "confirm_destructive",
    "confirm_action",
    "prompt_choice",
    "prompt_text",
    "show_resource_summary",
]
