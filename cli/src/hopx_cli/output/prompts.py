"""Unified prompt helpers for Hopx CLI.

Provides consistent confirmation dialogs and user prompts across commands.
"""

from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


def confirm_destructive(
    message: str,
    resource_name: str,
    details: dict[str, Any] | None = None,
    default: bool = False,
) -> bool:
    """Standard confirmation for destructive operations.

    Shows a warning with resource details before confirming. Use for delete,
    revoke, kill, and other irreversible operations.

    Args:
        message: Action being performed (e.g., "Delete template")
        resource_name: Name/ID of resource being affected
        details: Optional dict of details to display
        default: Default answer (False for safety)

    Returns:
        True if user confirms, False otherwise

    Example:
        if confirm_destructive(
            "Delete template",
            "my-template",
            details={"sandboxes_using": 3, "created": "2024-01-15"}
        ):
            # proceed with deletion
    """
    console.print()
    console.print(f"[yellow]⚠ {message}[/yellow]: [bold]{resource_name}[/bold]")

    if details:
        for key, value in details.items():
            # Format key from snake_case to Title Case
            display_key = key.replace("_", " ").title()
            console.print(f"  [dim]{display_key}:[/dim] {value}")

    console.print()
    return Confirm.ask("Continue?", default=default)


def confirm_action(
    message: str,
    default: bool = True,
) -> bool:
    """Simple confirmation for non-destructive actions.

    Args:
        message: Question to ask
        default: Default answer

    Returns:
        True if user confirms, False otherwise

    Example:
        if confirm_action("Create sandbox with these settings?"):
            # proceed
    """
    return Confirm.ask(message, default=default)


def prompt_choice(
    message: str,
    choices: list[str],
    default: str | None = None,
) -> str:
    """Prompt user to select from choices.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice

    Returns:
        Selected choice

    Example:
        lang = prompt_choice("Select language", ["python", "javascript"], "python")
    """
    choices_str = "/".join(choices)
    prompt_text = f"{message} [{choices_str}]"

    while True:
        response = Prompt.ask(prompt_text, default=default)
        if response in choices:
            return response
        console.print(f"[red]Invalid choice.[/red] Options: {', '.join(choices)}")


def prompt_text(
    message: str,
    default: str | None = None,
    password: bool = False,
) -> str:
    """Prompt for text input.

    Args:
        message: Prompt message
        default: Default value
        password: Hide input (for sensitive data)

    Returns:
        User input

    Example:
        name = prompt_text("Enter sandbox name", default="my-sandbox")
    """
    if default is not None:
        return Prompt.ask(message, default=default, password=password)
    return Prompt.ask(message, password=password)


def show_resource_summary(
    title: str,
    fields: dict[str, Any],
    style: str = "cyan",
) -> None:
    """Display a summary of a resource.

    Useful for showing details after creation or before confirmation.

    Args:
        title: Summary title
        fields: Dict of field name -> value
        style: Border style color

    Example:
        show_resource_summary("Sandbox Created", {
            "ID": "sb_abc123",
            "Template": "python",
            "Status": "running"
        })
    """
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()

    for key, value in fields.items():
        table.add_row(f"{key}:", str(value))

    console.print()
    console.print(f"[{style}]{title}[/{style}]")
    console.print(table)
    console.print()
