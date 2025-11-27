"""Environment variable management commands for the Hopx CLI.

Implements all environment variable operations for sandboxes including
listing, getting, setting, deleting, and loading from files.
"""

import re
from pathlib import Path

import typer
from rich.console import Console

from ..core import CLIContext, OutputFormat, get_sandbox, handle_errors
from ..output import Spinner, format_output

app = typer.Typer(
    help="Manage sandbox environment variables",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _mask_sensitive_value(key: str, value: str) -> str:
    """Mask sensitive environment variable values.

    Args:
        key: Environment variable name
        value: Environment variable value

    Returns:
        Original value if not sensitive, masked value otherwise
    """
    # Keywords that indicate sensitive data
    sensitive_keywords = [
        "key",
        "secret",
        "token",
        "password",
        "passwd",
        "credential",
        "auth",
        "private",
        "api_key",
        "access_key",
    ]

    key_lower = key.lower()

    # Check if any sensitive keyword is in the key name
    for keyword in sensitive_keywords:
        if keyword in key_lower:
            # Mask all but first 3 and last 3 characters
            if len(value) > 10:
                return f"{value[:3]}...{value[-3:]}"
            elif len(value) > 6:
                return f"{value[:2]}...{value[-2:]}"
            else:
                return "***MASKED***"

    return value


def _parse_env_vars(env_list: list[str] | None, env_file: str | None) -> dict[str, str]:
    """Parse environment variables from command line and file.

    Args:
        env_list: List of KEY=VALUE strings from --env flag
        env_file: Path to .env file

    Returns:
        Dictionary of environment variables

    Raises:
        typer.BadParameter: If env var format is invalid
    """
    env_vars: dict[str, str] = {}

    # Load from file first (lower priority)
    if env_file:
        env_path = Path(env_file)
        if not env_path.exists():
            raise typer.BadParameter(f"Environment file not found: {env_file}")

        with open(env_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE (handle values with = in them)
                if "=" not in line:
                    raise typer.BadParameter(
                        f"Invalid env var format in {env_file}:{line_num} (expected KEY=VALUE)"
                    )

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                env_vars[key] = value

    # Override with command-line args (higher priority)
    if env_list:
        for env_str in env_list:
            if "=" not in env_str:
                raise typer.BadParameter(f"Invalid env var format: {env_str} (expected KEY=VALUE)")

            key, value = env_str.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


@app.command("list")
@handle_errors
def list_cmd(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    mask: bool = typer.Option(
        True,
        "--mask/--no-mask",
        help="Mask sensitive values (passwords, keys)",
    ),
    filter_pattern: str | None = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter by variable name pattern (regex)",
    ),
) -> None:
    """List all environment variables in a sandbox.

    Examples:
        # List all env vars
        hopx env list 1763382095i648uu1o

        # List without masking sensitive values
        hopx env list 1763382095i648uu1o --no-mask

        # Filter by pattern
        hopx env list 1763382095i648uu1o --filter "^PATH|^HOME"
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    env_vars = sandbox.env.get_all()

    # Apply filter if provided
    if filter_pattern:
        try:
            pattern = re.compile(filter_pattern)
            env_vars = {k: v for k, v in env_vars.items() if pattern.search(k)}
        except re.error as e:
            raise typer.BadParameter(f"Invalid regex pattern: {e}")

    if not env_vars:
        if not cli_ctx.quiet:
            console.print("[dim]No environment variables found[/dim]")
        return

    # Mask sensitive values if requested
    if mask:
        env_vars = {k: _mask_sensitive_value(k, v) for k, v in env_vars.items()}

    # Sort by key name
    env_vars = dict(sorted(env_vars.items()))

    # Output
    format_output(
        env_vars,
        cli_ctx.output_format,
        table_config={"table_type": "env", "title": "Environment Variables"},
    )


@app.command("get")
@handle_errors
def get(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    key: str = typer.Argument(..., help="Environment variable name"),
    default: str | None = typer.Option(
        None,
        "--default",
        "-d",
        help="Default value if variable not found",
    ),
    mask: bool = typer.Option(
        True,
        "--mask/--no-mask",
        help="Mask sensitive values",
    ),
) -> None:
    """Get a specific environment variable.

    Examples:
        # Get variable
        hopx env get 1763382095i648uu1o API_KEY

        # Get with default
        hopx env get 1763382095i648uu1o DEBUG --default "false"

        # Get without masking
        hopx env get 1763382095i648uu1o API_KEY --no-mask
    """
    cli_ctx: CLIContext = ctx.obj

    sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
    value = sandbox.env.get(key, default)

    if value is None:
        if not cli_ctx.quiet:
            console.print(f"[yellow]Variable '{key}' not found[/yellow]")
        raise typer.Exit(code=1)

    # Mask if requested
    if mask:
        value = _mask_sensitive_value(key, value)

    # Output
    if cli_ctx.output_format == OutputFormat.JSON:
        format_output({key: value}, cli_ctx.output_format)
    elif cli_ctx.output_format == OutputFormat.PLAIN:
        console.print(value)
    else:
        # Rich table
        format_output(
            {key: value},
            cli_ctx.output_format,
            table_config={"table_type": "env", "title": f"Variable: {key}"},
        )


@app.command("set")
@handle_errors
def set_cmd(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    key: str | None = typer.Argument(None, help="Environment variable name"),
    value: str | None = typer.Argument(None, help="Environment variable value"),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variable (KEY=VALUE, repeatable)",
    ),
    env_file: str | None = typer.Option(
        None,
        "--env-file",
        help="Load env vars from file",
    ),
) -> None:
    """Set environment variable(s) in a sandbox.

    You can set a single variable or multiple variables at once.

    Examples:
        # Set single variable
        hopx env set 1763382095i648uu1o API_KEY "sk-prod-xyz"

        # Set multiple variables
        hopx env set 1763382095i648uu1o -e API_KEY=secret -e DEBUG=true

        # Load from file
        hopx env set 1763382095i648uu1o --env-file .env

        # Combine methods
        hopx env set 1763382095i648uu1o --env-file .env -e DEBUG=true
    """
    cli_ctx: CLIContext = ctx.obj

    # Validate arguments
    if key and value:
        # Single key-value pair
        env_vars = {key: value}
    elif env or env_file:
        # Multiple vars from --env or --env-file
        env_vars = _parse_env_vars(env, env_file)
        if not env_vars:
            raise typer.BadParameter("No environment variables provided")
    else:
        raise typer.BadParameter(
            "Provide either KEY VALUE arguments or use --env/-e or --env-file flags"
        )

    # Set variables
    with Spinner(f"Setting {len(env_vars)} variable(s)...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        sandbox.env.update(env_vars)
        spinner.success(f"Set {len(env_vars)} variable(s)")

    if not cli_ctx.quiet:
        # Show what was set (masked)
        masked_vars = {k: _mask_sensitive_value(k, v) for k, v in env_vars.items()}
        console.print("\n[green]Variables set:[/green]")
        for k, v in masked_vars.items():
            console.print(f"  {k}={v}")


@app.command("delete")
@handle_errors
def delete(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    key: str = typer.Argument(..., help="Environment variable name"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
) -> None:
    """Delete an environment variable.

    Examples:
        # Delete with confirmation
        hopx env delete 1763382095i648uu1o DEBUG

        # Delete without confirmation
        hopx env delete 1763382095i648uu1o DEBUG --force
    """
    cli_ctx: CLIContext = ctx.obj

    # Confirm unless --force
    if not force:
        confirm = typer.confirm(f"Delete environment variable '{key}'?")
        if not confirm:
            raise typer.Abort()

    with Spinner(f"Deleting variable '{key}'...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)
        sandbox.env.delete(key)
        spinner.success(f"Variable '{key}' deleted")


@app.command("load")
@handle_errors
def load(
    ctx: typer.Context,
    sandbox_id: str = typer.Argument(..., help="Sandbox ID"),
    file: str = typer.Option(
        ...,
        "--file",
        "-f",
        help="Path to .env file",
    ),
    replace: bool = typer.Option(
        False,
        "--replace",
        help="Replace all existing variables (default: merge)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip confirmation for --replace",
    ),
) -> None:
    """Load environment variables from a file.

    By default, merges with existing variables. Use --replace to replace all.

    File format:
        # Comments are ignored
        KEY1=value1
        KEY2="value with spaces"
        KEY3='single quotes'

    Examples:
        # Merge with existing variables
        hopx env load 1763382095i648uu1o --file .env

        # Replace all variables (will prompt for confirmation)
        hopx env load 1763382095i648uu1o --file .env --replace

        # Replace without confirmation
        hopx env load 1763382095i648uu1o --file .env --replace --force
    """
    cli_ctx: CLIContext = ctx.obj

    # Parse env file
    env_vars = _parse_env_vars(None, file)

    if not env_vars:
        if not cli_ctx.quiet:
            console.print("[yellow]No variables found in file[/yellow]")
        return

    # Confirm for --replace unless --force
    if replace and not force:
        console.print(
            "[yellow]Warning:[/yellow] --replace will remove all existing environment "
            "variables and replace them with the contents of the file."
        )
        confirm = typer.confirm("Continue?")
        if not confirm:
            raise typer.Abort()

    # Load variables
    action = "Replacing" if replace else "Loading"
    with Spinner(f"{action} {len(env_vars)} variable(s)...") as spinner:
        sandbox = get_sandbox(cli_ctx.config, sandbox_id=sandbox_id)

        if replace:
            sandbox.env.set_all(env_vars)
        else:
            sandbox.env.update(env_vars)

        spinner.success(f"Loaded {len(env_vars)} variable(s)")

    if not cli_ctx.quiet:
        # Show what was loaded (masked)
        masked_vars = {k: _mask_sensitive_value(k, v) for k, v in env_vars.items()}
        console.print(f"\n[green]Variables loaded from {file}:[/green]")
        for k, v in masked_vars.items():
            console.print(f"  {k}={v}")
