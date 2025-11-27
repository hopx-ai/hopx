"""CLI configuration management commands.

Provides commands for managing CLI configuration including:
- Interactive setup wizard
- Configuration viewing and editing
- Profile management for multiple environments
- Secure API key handling
"""

import os
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from ..core.config import CLIConfig
from ..core.context import CLIContext

app = typer.Typer(
    help="CLI configuration management",
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def mask_api_key(api_key: str | None) -> str:
    """Mask API key for display.

    Shows only first 20 characters followed by "...".

    Args:
        api_key: API key to mask

    Returns:
        Masked API key string
    """
    if not api_key:
        return "[dim]not set[/dim]"

    if len(api_key) <= 20:
        return api_key[:4] + "..." if len(api_key) > 4 else api_key

    return api_key[:20] + "..."


def validate_config_key(key: str) -> bool:
    """Validate configuration key.

    Args:
        key: Configuration key to validate

    Returns:
        True if key is valid
    """
    valid_keys = {
        "api_key",
        "base_url",
        "default_template",
        "default_timeout",
        "output_format",
    }
    return key in valid_keys


def load_all_profiles() -> dict[str, Any]:
    """Load all profiles from config file.

    Returns:
        Dictionary with default_profile and profiles keys
    """
    config_path = CLIConfig.get_config_path()

    if not config_path.exists():
        return {"default_profile": "default", "profiles": {}}

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

            # Handle legacy format (flat profiles dict)
            if "default_profile" not in data:
                return {"default_profile": "default", "profiles": data}

            return data
    except Exception:
        return {"default_profile": "default", "profiles": {}}


def save_all_profiles(data: dict[str, Any]) -> None:
    """Save all profiles to config file.

    Args:
        data: Dictionary with default_profile and profiles keys
    """
    config_path = CLIConfig.get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False)

    # Set secure file permissions (0600)
    os.chmod(config_path, 0o600)


@app.command("init")
def init(ctx: typer.Context) -> None:
    """Interactive setup wizard for initial configuration.

    Prompts for API key, default template, and output format.
    Creates configuration file at ~/.hopx/config.yaml.
    """
    console.print("\n[bold cyan]Hopx CLI Configuration Setup[/bold cyan]\n")

    # Check if config already exists
    config_path = CLIConfig.get_config_path()
    if config_path.exists():
        console.print(f"[yellow]Configuration file already exists at:[/yellow] {config_path}")
        overwrite = typer.confirm("Do you want to overwrite it?", default=False)
        if not overwrite:
            console.print("[dim]Setup cancelled[/dim]")
            raise typer.Exit()

    # Prompt for API key
    console.print(
        "[bold]API Key[/bold]\n"
        "Get your API key from: https://hopx.ai/dashboard\n"
        "Leave empty to use HOPX_API_KEY environment variable.\n"
    )
    api_key = typer.prompt("API Key", default="", hide_input=True, show_default=False)

    if not api_key:
        api_key_from_env = os.environ.get("HOPX_API_KEY", "")
        if api_key_from_env:
            console.print(
                f"[green]✓[/green] Using API key from environment: {mask_api_key(api_key_from_env)}"
            )
            api_key = "${HOPX_API_KEY}"
        else:
            console.print(
                "[yellow]![/yellow] No API key provided. "
                "You can set it later with 'hopx config set api_key <key>'"
            )
            api_key = None

    # Prompt for default template
    console.print("\n[bold]Default Template[/bold]\nTemplate to use when creating sandboxes.\n")
    default_template = typer.prompt(
        "Default template", default="code-interpreter", show_default=True
    )

    # Prompt for output format
    console.print(
        "\n[bold]Output Format[/bold]\n"
        "Options: table (rich formatted), json (machine readable), plain (scripting)\n"
    )
    output_format = typer.prompt(
        "Output format",
        default="table",
        type=typer.Choice(["table", "json", "plain"]),
        show_default=True,
    )

    # Prompt for default timeout
    console.print("\n[bold]Default Timeout[/bold]\nTimeout in seconds for operations.\n")
    default_timeout = typer.prompt("Default timeout (seconds)", default=3600, type=int)

    # Create config
    config = CLIConfig(
        api_key=api_key,
        default_template=default_template,
        output_format=output_format,
        default_timeout=default_timeout,
        profile="default",
    )

    # Save to file
    all_data = {
        "default_profile": "default",
        "profiles": {
            "default": {
                "api_key": api_key,
                "base_url": config.base_url,
                "default_template": default_template,
                "default_timeout": default_timeout,
                "output_format": output_format,
            }
        },
    }
    save_all_profiles(all_data)

    console.print(f"\n[green]✓[/green] Configuration saved to: {config_path}")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  • Run [cyan]hopx config show[/cyan] to view your configuration")
    console.print("  • Run [cyan]hopx sandboxes list[/cyan] to list your sandboxes")
    console.print("  • Run [cyan]hopx --help[/cyan] to see all available commands\n")


@app.command("show")
def show(ctx: typer.Context) -> None:
    """Display current configuration.

    Shows all configuration settings with masked API key.
    Displays active profile and config file path.
    """
    # Get CLI context
    cli_ctx: CLIContext = ctx.obj

    # Load all profiles data
    all_data = load_all_profiles()
    active_profile = all_data.get("default_profile", "default")
    config = cli_ctx.config

    # Build configuration table
    table = Table(title="Hopx CLI Configuration", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="white")

    # Add rows
    table.add_row("Profile", f"[bold]{active_profile}[/bold]")
    table.add_row("API Key", mask_api_key(config.api_key))
    table.add_row("Base URL", config.base_url)
    table.add_row("Default Template", config.default_template)
    table.add_row("Default Timeout", f"{config.default_timeout}s")
    table.add_row("Output Format", config.output_format)

    console.print(table)

    # Show config file path
    config_path = CLIConfig.get_config_path()
    console.print(f"\n[dim]Config file:[/dim] {config_path}")

    # Show if using environment variables
    if os.environ.get("HOPX_API_KEY"):
        console.print("[dim]Using HOPX_API_KEY from environment[/dim]")


@app.command("set")
def set_config(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value.

    Valid keys: api_key, base_url, default_template, default_timeout, output_format

    Examples:
        hopx config set api_key hopx_live_...
        hopx config set default_template python
        hopx config set output_format json
    """
    # Validate key
    if not validate_config_key(key):
        console.print(f"[red]✗[/red] Invalid configuration key: {key}")
        console.print(
            "\n[bold]Valid keys:[/bold]\n"
            "  • api_key\n"
            "  • base_url\n"
            "  • default_template\n"
            "  • default_timeout\n"
            "  • output_format\n"
        )
        raise typer.Exit(1)

    # Validate output_format value
    if key == "output_format" and value not in ["table", "json", "plain"]:
        console.print(f"[red]✗[/red] Invalid output format: {value}")
        console.print("[bold]Valid formats:[/bold] table, json, plain")
        raise typer.Exit(1)

    # Validate default_timeout value
    if key == "default_timeout":
        try:
            timeout_val = int(value)
            if timeout_val < 1:
                raise ValueError()
        except ValueError:
            console.print(f"[red]✗[/red] Invalid timeout value: {value}")
            console.print("Timeout must be a positive integer (seconds)")
            raise typer.Exit(1)

    # Load all profiles
    all_data = load_all_profiles()
    active_profile = all_data.get("default_profile", "default")

    # Update profile
    if "profiles" not in all_data:
        all_data["profiles"] = {}

    if active_profile not in all_data["profiles"]:
        all_data["profiles"][active_profile] = {}

    all_data["profiles"][active_profile][key] = value

    # Save
    save_all_profiles(all_data)

    # Show result
    display_value = mask_api_key(value) if key == "api_key" else value
    console.print(f"[green]✓[/green] Set {key} = {display_value}")


@app.command("get")
def get_config(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Configuration key"),
    reveal: bool = typer.Option(False, "--reveal", help="Show full API key without masking"),
) -> None:
    """Get a configuration value.

    API key is masked by default. Use --reveal to show full value.

    Examples:
        hopx config get api_key
        hopx config get api_key --reveal
        hopx config get default_template
    """
    # Validate key
    if not validate_config_key(key):
        console.print(f"[red]✗[/red] Invalid configuration key: {key}")
        raise typer.Exit(1)

    # Get CLI context
    cli_ctx: CLIContext = ctx.obj
    config = cli_ctx.config

    # Get value
    value = getattr(config, key, None)

    if value is None:
        console.print(f"[yellow]![/yellow] {key} is not set")
        raise typer.Exit(1)

    # Display value
    if key == "api_key" and not reveal:
        console.print(mask_api_key(value))
    else:
        console.print(value)


@app.command("path")
def config_path(ctx: typer.Context) -> None:
    """Show configuration file path.

    Displays the path to the configuration file.
    """
    config_path = CLIConfig.get_config_path()
    console.print(config_path)


# Profile management subgroup
profiles_app = typer.Typer(help="Manage configuration profiles")
app.add_typer(profiles_app, name="profiles")


@profiles_app.command("list")
def profiles_list(ctx: typer.Context) -> None:
    """List available configuration profiles.

    Shows all profiles with active profile highlighted.
    """
    all_data = load_all_profiles()
    active_profile = all_data.get("default_profile", "default")
    profiles = all_data.get("profiles", {})

    if not profiles:
        console.print("[dim]No profiles found[/dim]")
        console.print("\n[bold]Create a profile:[/bold]")
        console.print("  hopx config profiles create <name>")
        return

    # Build table
    table = Table(title="Configuration Profiles", show_header=True, header_style="bold cyan")
    table.add_column("Profile", style="cyan")
    table.add_column("Active", justify="center")
    table.add_column("API Key", style="white")
    table.add_column("Template", style="white")

    for profile_name, profile_data in profiles.items():
        is_active = "✓" if profile_name == active_profile else ""
        api_key_display = mask_api_key(profile_data.get("api_key"))
        template = profile_data.get("default_template", "code-interpreter")

        style = "bold green" if profile_name == active_profile else None
        table.add_row(profile_name, is_active, api_key_display, template, style=style)

    console.print(table)
    console.print(f"\n[dim]Active profile:[/dim] [bold]{active_profile}[/bold]")


@profiles_app.command("use")
def profiles_use(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Profile name to activate"),
) -> None:
    """Switch to a different profile.

    Makes the specified profile the active default profile.

    Examples:
        hopx config profiles use production
        hopx config profiles use staging
    """
    all_data = load_all_profiles()
    profiles = all_data.get("profiles", {})

    # Check if profile exists
    if name not in profiles:
        console.print(f"[red]✗[/red] Profile not found: {name}")
        console.print("\n[bold]Available profiles:[/bold]")
        for profile_name in profiles:
            console.print(f"  • {profile_name}")
        raise typer.Exit(1)

    # Set as default
    all_data["default_profile"] = name
    save_all_profiles(all_data)

    console.print(f"[green]✓[/green] Switched to profile: [bold]{name}[/bold]")


@profiles_app.command("create")
def profiles_create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="New profile name"),
) -> None:
    """Create a new configuration profile.

    Creates a new profile by copying settings from the active profile.

    Examples:
        hopx config profiles create production
        hopx config profiles create staging
    """
    all_data = load_all_profiles()
    profiles = all_data.get("profiles", {})

    # Check if profile already exists
    if name in profiles:
        console.print(f"[yellow]![/yellow] Profile already exists: {name}")
        raise typer.Exit(1)

    # Get current profile as template
    current_profile = all_data.get("default_profile", "default")
    template_config = profiles.get(current_profile, {})

    # Create new profile (copy from current)
    new_profile = {
        "api_key": None,  # Don't copy API key
        "base_url": template_config.get("base_url", "https://api.hopx.dev"),
        "default_template": template_config.get("default_template", "code-interpreter"),
        "default_timeout": template_config.get("default_timeout", 3600),
        "output_format": template_config.get("output_format", "table"),
    }

    profiles[name] = new_profile
    all_data["profiles"] = profiles
    save_all_profiles(all_data)

    console.print(f"[green]✓[/green] Created profile: [bold]{name}[/bold]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  • Set API key: [cyan]hopx config profiles use {name}[/cyan]")
    console.print("  • Then run: [cyan]hopx config set api_key <your-key>[/cyan]")


@profiles_app.command("delete")
def profiles_delete(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Profile name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """Delete a configuration profile.

    Removes the specified profile. Cannot delete the active profile.

    Examples:
        hopx config profiles delete staging
        hopx config profiles delete old-profile --force
    """
    all_data = load_all_profiles()
    active_profile = all_data.get("default_profile", "default")
    profiles = all_data.get("profiles", {})

    # Check if profile exists
    if name not in profiles:
        console.print(f"[red]✗[/red] Profile not found: {name}")
        raise typer.Exit(1)

    # Cannot delete active profile
    if name == active_profile:
        console.print(f"[red]✗[/red] Cannot delete active profile: {name}")
        console.print("\n[bold]Switch to another profile first:[/bold]")
        console.print("  hopx config profiles use <other-profile>")
        raise typer.Exit(1)

    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Delete profile '{name}'?", default=False)
        if not confirm:
            console.print("[dim]Deletion cancelled[/dim]")
            raise typer.Exit()

    # Delete profile
    del profiles[name]
    all_data["profiles"] = profiles
    save_all_profiles(all_data)

    console.print(f"[green]✓[/green] Deleted profile: [bold]{name}[/bold]")
