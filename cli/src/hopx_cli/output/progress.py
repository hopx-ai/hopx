"""Progress indicators and live output for long-running operations.

Provides Rich-based progress indicators including spinners, progress bars,
status panels, and live output streaming for logs and build processes.
"""

import os
import threading
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.spinner import Spinner as RichSpinner
from rich.text import Text


class Spinner:
    """Context manager for displaying a spinner during operations.

    Displays an animated spinner with a message while operation executes.
    Thread-safe and respects NO_COLOR environment variable.

    Examples:
        >>> with Spinner("Creating sandbox...") as spin:
        ...     sandbox = Sandbox.create(...)
        ...     spin.success(f"Created: {sandbox.sandbox_id}")

        >>> with Spinner("Building template...") as spin:
        ...     result = Template.build(...)
        ...     spin.update("Activating template...")
        ...     time.sleep(5)
        ...     spin.success("Template ready!")
    """

    def __init__(
        self,
        message: str,
        spinner_name: str = "dots",
        console: Console | None = None,
    ) -> None:
        """Initialize spinner.

        Args:
            message: Message to display next to spinner
            spinner_name: Rich spinner name (dots, line, bouncingBar, etc.)
            console: Rich console instance. Creates new if not provided.
        """
        self.message = message
        self.spinner_name = spinner_name
        self.console = console or Console()
        self._live: Live | None = None
        self._spinner: RichSpinner | None = None
        self._lock = threading.Lock()

    def __enter__(self) -> "Spinner":
        """Start the spinner."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the spinner."""
        if exc_type is None:
            self.success(self.message)
        else:
            self.error(f"Failed: {exc_val}")

    def start(self) -> None:
        """Start displaying the spinner."""
        with self._lock:
            if self._live is not None:
                return

            # Respect NO_COLOR
            if os.environ.get("NO_COLOR"):
                self.console.print(f"... {self.message}")
                return

            self._spinner = RichSpinner(self.spinner_name, text=self.message)
            self._live = Live(
                self._spinner,
                console=self.console,
                refresh_per_second=10,
                transient=True,
            )
            self._live.start()

    def stop(self) -> None:
        """Stop displaying the spinner."""
        with self._lock:
            if self._live:
                self._live.stop()
                self._live = None
                self._spinner = None

    def update(self, message: str) -> None:
        """Update spinner message.

        Args:
            message: New message to display
        """
        with self._lock:
            self.message = message
            if self._spinner:
                self._spinner.update(text=message)

    def success(self, message: str | None = None) -> None:
        """Stop spinner and show success message.

        Args:
            message: Success message. Uses current message if not provided.
        """
        self.stop()
        msg = message or self.message
        self.console.print(f"[green]✓[/green] {msg}")

    def error(self, message: str | None = None) -> None:
        """Stop spinner and show error message.

        Args:
            message: Error message. Uses current message if not provided.
        """
        self.stop()
        msg = message or self.message
        self.console.print(f"[red]✗[/red] {msg}")

    def warn(self, message: str | None = None) -> None:
        """Stop spinner and show warning message.

        Args:
            message: Warning message. Uses current message if not provided.
        """
        self.stop()
        msg = message or self.message
        self.console.print(f"[yellow]![/yellow] {msg}")


class ProgressBar:
    """Context manager for displaying a progress bar during operations.

    Displays a progress bar with percentage, elapsed time, and optional
    task description. Useful for file uploads, downloads, and batch operations.

    Examples:
        >>> with ProgressBar("Uploading files", total=100) as progress:
        ...     for i in range(100):
        ...         # Do work
        ...         progress.advance(1)

        >>> with ProgressBar("Processing") as progress:
        ...     task = progress.add_task("Download", total=1000)
        ...     for chunk in chunks:
        ...         progress.update(task, advance=len(chunk))
    """

    def __init__(
        self,
        description: str | None = None,
        total: float | None = None,
        console: Console | None = None,
    ) -> None:
        """Initialize progress bar.

        Args:
            description: Task description
            total: Total number of units. Creates indeterminate bar if None.
            console: Rich console instance. Creates new if not provided.
        """
        self.console = console or Console()
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self._main_task: TaskID | None = None
        self._description = description or "Processing"
        self._total = total

    def __enter__(self) -> "ProgressBar":
        """Start the progress bar."""
        self._progress.start()
        if self._total is not None:
            self._main_task = self.add_task(self._description, total=self._total)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the progress bar."""
        self._progress.stop()

    def add_task(self, description: str, total: float | None = None) -> TaskID:
        """Add a new task to the progress bar.

        Args:
            description: Task description
            total: Total units for task

        Returns:
            Task ID for updating progress
        """
        return self._progress.add_task(description, total=total)

    def update(self, task_id: TaskID, advance: float | None = None, **kwargs: Any) -> None:
        """Update task progress.

        Args:
            task_id: Task ID to update
            advance: Amount to advance progress
            **kwargs: Additional task parameters
        """
        self._progress.update(task_id, advance=advance, **kwargs)

    def advance(self, advance: float = 1.0) -> None:
        """Advance the main task progress.

        Args:
            advance: Amount to advance
        """
        if self._main_task is not None:
            self._progress.update(self._main_task, advance=advance)


class StatusPanel:
    """Display a status panel with key-value pairs.

    Shows operation status and details in a formatted panel.
    Useful for displaying build status, operation results, etc.

    Examples:
        >>> panel = StatusPanel("Build Status")
        >>> panel.add("Template", "my-app")
        >>> panel.add("Status", "Building", style="yellow")
        >>> panel.add("Progress", "45%")
        >>> panel.display()
    """

    def __init__(self, title: str, console: Console | None = None) -> None:
        """Initialize status panel.

        Args:
            title: Panel title
            console: Rich console instance. Creates new if not provided.
        """
        self.title = title
        self.console = console or Console()
        self._items: list[tuple[str, str, str | None]] = []

    def add(self, key: str, value: str, style: str | None = None) -> None:
        """Add a key-value pair to the panel.

        Args:
            key: Item key/label
            value: Item value
            style: Optional Rich style for the value
        """
        self._items.append((key, value, style))

    def display(self) -> None:
        """Display the panel."""
        if not self._items:
            return

        # Build panel content
        lines: list[str] = []
        max_key_len = max(len(key) for key, _, _ in self._items)

        for key, value, style in self._items:
            padded_key = key.ljust(max_key_len)
            if style:
                lines.append(f"[bold]{padded_key}:[/bold] [{style}]{value}[/{style}]")
            else:
                lines.append(f"[bold]{padded_key}:[/bold] {value}")

        content = "\n".join(lines)
        panel = Panel(content, title=self.title, border_style="cyan")
        self.console.print(panel)


class LiveOutput:
    """Context manager for live streaming output.

    Displays live updating output for logs, build processes, and other
    streaming data. Automatically scrolls and handles multi-line content.

    Examples:
        >>> with LiveOutput(title="Build Logs") as live:
        ...     for log in build_logs:
        ...         live.append(log.get("message", ""))

        >>> with LiveOutput() as live:
        ...     live.append("Starting process...")
        ...     live.append("Step 1 complete")
        ...     live.append("Step 2 complete")
    """

    def __init__(
        self,
        title: str | None = None,
        max_lines: int = 50,
        console: Console | None = None,
    ) -> None:
        """Initialize live output.

        Args:
            title: Optional title for output
            max_lines: Maximum lines to keep in buffer
            console: Rich console instance. Creates new if not provided.
        """
        self.title = title
        self.max_lines = max_lines
        self.console = console or Console()
        self._lines: list[str] = []
        self._live: Live | None = None
        self._lock = threading.Lock()

    def __enter__(self) -> "LiveOutput":
        """Start live output."""
        with self._lock:
            self._live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=4,
            )
            self._live.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop live output."""
        with self._lock:
            if self._live:
                self._live.stop()
                self._live = None

    def append(self, line: str) -> None:
        """Append a line to the output.

        Args:
            line: Line to append
        """
        with self._lock:
            self._lines.append(line)

            # Trim to max lines
            if len(self._lines) > self.max_lines:
                self._lines = self._lines[-self.max_lines :]

            # Update display
            if self._live:
                self._live.update(self._render())

    def clear(self) -> None:
        """Clear all output lines."""
        with self._lock:
            self._lines.clear()
            if self._live:
                self._live.update(self._render())

    def _render(self) -> Panel | Text:
        """Render current output.

        Returns:
            Rendered output as Panel or Text
        """
        content = "\n".join(self._lines) if self._lines else "[dim]No output yet[/dim]"

        if self.title:
            return Panel(content, title=self.title, border_style="cyan")
        else:
            return Text(content)
