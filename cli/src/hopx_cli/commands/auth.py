"""Authentication commands for Hopx CLI.

Handles OAuth login, API key management, and authentication status.
"""

import re
import time
from datetime import UTC, datetime

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from hopx_cli.auth.api_keys import APIKeyManager
from hopx_cli.auth.credentials import CredentialStore
from hopx_cli.auth.oauth import browser_login, browser_login_headless, refresh_oauth_token
from hopx_cli.auth.token import TokenManager
from hopx_cli.core import CLIContext
from hopx_cli.output import Spinner

app = typer.Typer(
    help="Authentication management",
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _get_profile(ctx: typer.Context) -> str:
    """Get profile from CLI context."""
    cli_ctx: CLIContext = ctx.obj
    return cli_ctx.config.profile if cli_ctx else "default"


# API key validation regex: hopx_live_{12 chars}.{base64url}
API_KEY_PATTERN = re.compile(r"^hopx_live_[A-Za-z0-9]{12}\.[A-Za-z0-9_-]+$")


@app.command("login")
def login(
    ctx: typer.Context,
    provider: str = typer.Option(
        "GoogleOAuth",
        "--provider",
        help="OAuth provider: GoogleOAuth, GitHubOAuth",
    ),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Headless mode: manually paste callback URL (for servers without browsers)",
    ),
) -> None:
    """Authenticate with Hopx via browser OAuth.

    Opens browser for OAuth login. After login, you can generate API keys
    with 'hopx auth keys create' for sandbox operations.

    For CI/CD, set the HOPX_API_KEY environment variable instead.

    Examples:
        # OAuth login with Google (default)
        hopx auth login

        # OAuth login with GitHub
        hopx auth login --provider GitHubOAuth

        # Headless mode (for servers/containers without browsers)
        hopx auth login --no-browser

        # After login, create an API key
        hopx auth keys create --name "my-key"
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)

    try:
        if no_browser:
            # Headless flow: display handled in browser_login_headless()
            token_data = browser_login_headless(provider=provider)
        else:
            # Browser flow
            console.print()
            console.print("[bold cyan]OAuth Login[/bold cyan]")

            with Spinner("Waiting for authentication...") as spinner:
                token_data = browser_login(provider=provider, timeout=120)
                spinner.stop()

        # Store OAuth token
        credentials.store_oauth_token(token_data)

        console.print("\n[green]✓[/green] OAuth login successful!")
        console.print(f"Profile: [cyan]{profile}[/cyan]")

        # Show expiry
        expires_at = token_data.get("expires_at")
        if expires_at:
            expires_dt = datetime.fromtimestamp(expires_at, tz=UTC)
            expires_str = expires_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            console.print(f"Token expires: [dim]{expires_str}[/dim]")

        # Next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print('  1. Create an API key: [cyan]hopx auth keys create --name "my-key"[/cyan]')
        console.print("  2. The key will be stored automatically")
        console.print("  3. Then run: [cyan]hopx sandbox list[/cyan]")
        console.print(
            "\n[dim]Why? OAuth proves your identity. API keys authorize sandbox operations.[/dim]"
        )

    except TimeoutError:
        console.print("\n[red]Error:[/red] Authentication timed out")
        console.print("\nPlease try again or use the web console:")
        console.print("  [cyan]https://console.hopx.dev[/cyan]")
        raise typer.Exit(1) from None
    except ValueError as e:
        # Invalid provider or other validation error
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1) from None
    except RuntimeError as e:
        error_msg = str(e).lower()
        console.print(f"\n[red]Error:[/red] Authentication failed: {e}")

        # Provide helpful guidance based on error type
        if "client" in error_msg or "invalid" in error_msg or "redirect" in error_msg:
            console.print("\n[yellow]This may be a configuration issue.[/yellow]")

        console.print("\nPlease try again or use the web console:")
        console.print("  [cyan]https://console.hopx.dev[/cyan]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"\n[red]Error:[/red] Authentication failed: {e}")
        console.print("\nPlease try again or use the web console:")
        console.print("  [cyan]https://console.hopx.dev[/cyan]")
        raise typer.Exit(1) from None


@app.command("logout")
def logout(
    ctx: typer.Context,
    all_profiles: bool = typer.Option(
        False,
        "--all",
        help="Clear credentials for all profiles",
    ),
) -> None:
    """Clear stored credentials.

    By default, clears credentials for the current profile only.
    Use --all to clear all profiles.

    Examples:
        # Logout current profile
        hopx auth logout

        # Logout all profiles
        hopx auth logout --all
    """
    profile = _get_profile(ctx)

    if all_profiles:
        if not Confirm.ask(
            "[yellow]Warning:[/yellow] Clear credentials for all profiles?",
            default=False,
        ):
            console.print("Cancelled")
            raise typer.Exit(0)

        cleared = CredentialStore.clear_all_profiles()
        if cleared:
            console.print(
                f"[green]✓[/green] Cleared credentials for {len(cleared)} profile(s): {', '.join(cleared)}"
            )
        else:
            console.print("[dim]No credentials found to clear[/dim]")
    else:
        if not Confirm.ask(
            f"Clear credentials for profile [cyan]{profile}[/cyan]?",
            default=False,
        ):
            console.print("Cancelled")
            raise typer.Exit(0)

        credentials = CredentialStore(profile=profile)
        credentials.clear()
        console.print(f"[green]✓[/green] Cleared credentials for profile [cyan]{profile}[/cyan]")


@app.command("status")
def status(ctx: typer.Context) -> None:
    """Show current authentication status.

    Displays whether you are authenticated, the authentication method,
    masked credentials, and expiry information.

    Examples:
        hopx auth status
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)

    auth_status = token_manager.get_auth_status()

    if not auth_status["is_authenticated"]:
        console.print(
            Panel(
                "[yellow]Not authenticated[/yellow]\n\n"
                "Use [cyan]hopx auth login[/cyan] to authenticate",
                title="Authentication Status",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    # Build status panel content
    lines = []
    lines.append(f"[bold]Profile:[/bold]     {profile}")

    method = auth_status["auth_method"]
    if method == "both":
        lines.append("[bold]Method:[/bold]      API Key + OAuth")
    elif method == "api_key":
        lines.append("[bold]Method:[/bold]      API Key")
    elif method == "oauth":
        lines.append("[bold]Method:[/bold]      OAuth")

    # Show API key if present
    if auth_status["api_key_preview"]:
        key_parts = auth_status["api_key_preview"].split(".")
        if len(key_parts) == 2:
            key_id = key_parts[0].replace("hopx_live_", "")
            lines.append(f"[bold]Key ID:[/bold]      {key_id}")
            lines.append(f"[bold]Key:[/bold]         {auth_status['api_key_preview']}")

    # Show OAuth expiry if present
    if auth_status["oauth_expires_at"]:
        expires_at = auth_status["oauth_expires_at"]
        expires_dt = datetime.fromtimestamp(expires_at, tz=UTC)
        now = datetime.now(UTC)

        if expires_dt > now:
            time_left = expires_dt - now
            hours = int(time_left.total_seconds() / 3600)
            minutes = int((time_left.total_seconds() % 3600) / 60)

            expires_str = expires_dt.strftime("%Y-%m-%d %H:%M UTC")
            lines.append(f"[bold]Expires:[/bold]     {expires_str}")
            lines.append(f"[bold]Time left:[/bold]   {hours}h {minutes}m")
        else:
            lines.append("[bold]Expires:[/bold]     [red]Expired[/red]")

    lines.append("\n[bold]Status:[/bold]      [green]Authenticated[/green]")

    content = "\n".join(lines)
    console.print(
        Panel(
            content,
            title="Authentication Status",
            border_style="green",
        )
    )


@app.command("refresh")
def refresh(ctx: typer.Context) -> None:
    """Refresh OAuth tokens.

    Only works for OAuth authentication. API keys do not expire.

    Examples:
        hopx auth refresh
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)

    token_data = credentials.get_oauth_token()
    if not token_data:
        console.print("[red]Error:[/red] No OAuth token found")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        console.print("[red]Error:[/red] No refresh token available")
        console.print("Please re-authenticate with [cyan]hopx auth login[/cyan]")
        raise typer.Exit(1)

    try:
        with Spinner("Refreshing token..."):
            new_token = refresh_oauth_token(refresh_token)

        # Preserve refresh token
        new_token["refresh_token"] = refresh_token
        credentials.store_oauth_token(new_token)

        console.print("[green]✓[/green] Token refreshed successfully")

        # Show new expiry
        expires_at = new_token.get("expires_at")
        if expires_at:
            expires_dt = datetime.fromtimestamp(expires_at, tz=UTC)
            expires_str = expires_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            console.print(f"New expiry: [cyan]{expires_str}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] Token refresh failed: {e}")
        console.print("Please re-authenticate with [cyan]hopx auth login[/cyan]")
        raise typer.Exit(1) from None


@app.command("validate")
def validate(ctx: typer.Context) -> None:
    """Validate complete authentication setup and test API access.

    Checks:
    - OAuth token status (for key management commands)
    - API key availability (for sandbox operations)
    - API connectivity (makes test request)

    This command helps diagnose authentication issues and confirms
    your setup is ready for sandbox operations.

    Examples:
        hopx auth validate
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    cli_ctx: CLIContext = ctx.obj

    console.print(f"[bold]Validating authentication for profile:[/bold] [cyan]{profile}[/cyan]\n")

    issues: list[str] = []

    # Check OAuth token
    oauth_token = credentials.get_oauth_token()
    if oauth_token:
        expires_at = oauth_token.get("expires_at")
        if expires_at and expires_at < time.time():
            console.print("[yellow]⚠[/yellow] OAuth token: Expired")
            console.print("  [dim]Fix: hopx auth refresh[/dim]")
            issues.append("oauth_expired")
        else:
            console.print("[green]✓[/green] OAuth token: Valid")
            if expires_at:
                expires_dt = datetime.fromtimestamp(expires_at, tz=UTC)
                console.print(f"  [dim]Expires: {expires_dt.strftime('%Y-%m-%d %H:%M UTC')}[/dim]")
    else:
        console.print("[yellow]○[/yellow] OAuth token: Not present")
        console.print("  [dim]Needed for: hopx auth keys * commands[/dim]")

    # Check API key
    api_key = None
    try:
        api_key = cli_ctx.config.get_api_key()
        masked = api_key[:16] + "..." if len(api_key) > 16 else "***"
        console.print(f"[green]✓[/green] API key: {masked}")
    except ValueError:
        console.print("[red]✗[/red] API key: Not configured")
        issues.append("no_api_key")

    # Test API connectivity
    if api_key:
        try:
            from hopx_ai import Sandbox

            with Spinner("Testing API connectivity...") as spinner:
                Sandbox.list(api_key=api_key, base_url=cli_ctx.config.base_url, limit=1)
                spinner.stop()
            console.print("[green]✓[/green] API connectivity: Working")
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "authentication" in error_str.lower():
                console.print("[red]✗[/red] API connectivity: Invalid API key")
                issues.append("invalid_api_key")
            else:
                console.print("[red]✗[/red] API connectivity: Failed")
                console.print(f"  [dim]{e}[/dim]")
                issues.append("api_failed")

    # Summary
    console.print("")
    if not issues:
        console.print("[green]All checks passed![/green] You're ready to use Hopx CLI.")
        console.print("\n[dim]Try: hopx sandbox list[/dim]")
    else:
        console.print("[yellow]Setup incomplete.[/yellow] To fix:")
        if "no_api_key" in issues:
            console.print("  [cyan]hopx auth login && hopx auth keys create[/cyan]")
        if "invalid_api_key" in issues:
            console.print("  [cyan]hopx auth keys create[/cyan] (create a new key)")
        if "oauth_expired" in issues:
            console.print("  [cyan]hopx auth refresh[/cyan]")
        if "api_failed" in issues:
            console.print("  Check your network connection and try again")
        raise typer.Exit(1)


# API Key management subgroup
keys_app = typer.Typer(
    help="Manage API keys (requires OAuth login)",
    context_settings={"allow_interspersed_args": True},
)
app.add_typer(keys_app, name="keys")


@keys_app.command("list")
def keys_list(ctx: typer.Context) -> None:
    """List all API keys for your organization.

    Requires OAuth authentication. Shows key ID, name, creation date,
    expiration, and last used timestamp.

    Examples:
        hopx auth keys list
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)

    oauth_token = token_manager.get_valid_oauth_token()
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching API keys..."), APIKeyManager(oauth_token) as manager:
            keys = manager.list_keys()

        if not keys:
            console.print("[dim]No API keys found[/dim]")
            console.print('\nCreate one with: [cyan]hopx auth keys create --name "My Key"[/cyan]')
            return

        # Build table
        table = Table(title="API Keys", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Prefix")
        table.add_column("Created", justify="right")
        table.add_column("Expires", justify="right")
        table.add_column("Last Used", justify="right")

        for key in keys:
            key_id = key.get("id", "-")
            name = key.get("name", "-")
            prefix = key.get("prefix", "-")

            # Format dates
            created_at = key.get("created_at")
            created_str = _format_datetime(created_at) if created_at else "-"

            expires_at = key.get("expires_at")
            expires_str = _format_datetime(expires_at) if expires_at else "[green]Never[/green]"

            last_used_at = key.get("last_used_at")
            last_used_str = _format_datetime(last_used_at) if last_used_at else "[dim]Never[/dim]"

            table.add_row(key_id, name, prefix, created_str, expires_str, last_used_str)

        console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


# Valid expiration options - must match API schema exactly
# From types.ts line 245: expires_in: "1month" | "3months" | "6months" | "1year" | "never"
EXPIRES_OPTIONS = ["1month", "3months", "6months", "1year", "never"]


@keys_app.command("create")
def keys_create(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Key name"),
    expires_in: str = typer.Option(
        "never",
        "--expires",
        "-e",
        help="Expiration: 1month, 3months, 6months, 1year, or never",
    ),
    copy: bool = typer.Option(
        False,
        "--copy",
        help="Copy key to clipboard",
    ),
    no_store: bool = typer.Option(
        False,
        "--no-store",
        help="Don't store key as current credentials (by default, keys are auto-stored)",
    ),
) -> None:
    """Create a new API key.

    Requires OAuth authentication. The key is automatically stored as your
    current credentials for sandbox operations. Use --no-store to disable.

    The full key value is only shown once - save it if you need it elsewhere.

    Examples:
        # Create key (auto-stored for immediate use)
        hopx auth keys create --name "Production Server"

        # Create key that expires in 1 year
        hopx auth keys create --name "CI/CD" --expires 1year

        # Create and copy to clipboard
        hopx auth keys create --name "Dev" --copy

        # Create without storing (for use elsewhere)
        hopx auth keys create --name "External" --no-store
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)

    oauth_token = token_manager.get_valid_oauth_token()
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    # Validate expires_in (must match API enum exactly)
    if expires_in not in EXPIRES_OPTIONS:
        console.print(f"[red]Error:[/red] Invalid expiration: {expires_in}")
        console.print(f"Valid options: {', '.join(EXPIRES_OPTIONS)}")
        raise typer.Exit(2)

    try:
        with Spinner(f"Creating API key '{name}'..."), APIKeyManager(oauth_token) as manager:
            result = manager.create_key(name, expires_in=expires_in)

        # FIXED: Parse response correctly (from types.ts lines 248-253)
        # Response: {"success": true, "api_key": {...}, "full_key": "hopx_live_xxx.secret"}
        key_value = result.get("full_key")  # FIXED: was result.get("key")
        api_key = result.get("api_key", {})
        key_id = api_key.get("id")  # FIXED: was result.get("id")
        expires_at = api_key.get("expires_at")  # FIXED: was result.get("expires_at")

        # Extract key ID from key value
        if key_value and key_value.startswith("hopx_live_"):
            parts = key_value.split(".")
            display_id = parts[0].replace("hopx_live_", "") if len(parts) == 2 else key_id
        else:
            display_id = key_id

        # Format expiry
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            expires_display = expires_dt.strftime("%Y-%m-%d")
        else:
            expires_display = "Never"

        # Build panel content
        lines = []
        lines.append(f"[bold]Name:[/bold]     {name}")
        lines.append(f"[bold]Key ID:[/bold]   {display_id}")
        lines.append(f"[bold]Expires:[/bold]  {expires_display}")
        lines.append("")
        lines.append("[yellow]Warning:[/yellow] Copy this key now - you won't see it again!")
        lines.append("")
        lines.append(f"[cyan]{key_value}[/cyan]")

        # Copy to clipboard if requested
        if copy:
            try:
                import pyperclip

                pyperclip.copy(key_value)
                lines.append("")
                lines.append("[green]✓ Copied to clipboard[/green]")
            except ImportError:
                lines.append("")
                lines.append(
                    "[yellow]Install pyperclip to enable clipboard: pip install pyperclip[/yellow]"
                )
            except Exception as e:
                lines.append("")
                lines.append(f"[yellow]Failed to copy to clipboard: {e}[/yellow]")

        content = "\n".join(lines)
        console.print(Panel(content, title="API Key Created", border_style="green"))

        # Auto-store as current credentials by default
        if not no_store:
            credentials.store_api_key(key_value)
            console.print(
                f"\n[green]✓[/green] Stored as current credentials for profile [cyan]{profile}[/cyan]"
            )
            console.print("[dim]You can now run sandbox commands: hopx sandbox list[/dim]")
        else:
            console.print(
                "\n[yellow]Note:[/yellow] Key not stored locally. "
                "Set HOPX_API_KEY environment variable to use this key."
            )

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@keys_app.command("revoke")
def keys_revoke(
    ctx: typer.Context,
    key_id: str = typer.Argument(..., help="Key ID to revoke"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Revoke an API key.

    Requires OAuth authentication. This action cannot be undone.

    Examples:
        # Revoke with confirmation
        hopx auth keys revoke NXAXAV4sU3Ii

        # Revoke without confirmation
        hopx auth keys revoke NXAXAV4sU3Ii --force
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)

    oauth_token = token_manager.get_valid_oauth_token()
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    if not force and not Confirm.ask(
        f"[yellow]Revoke API key[/yellow] [cyan]{key_id}[/cyan]?",
        default=False,
    ):
        console.print("Cancelled")
        raise typer.Exit(0)

    try:
        with Spinner(f"Revoking key {key_id}..."), APIKeyManager(oauth_token) as manager:
            manager.revoke_key(key_id)

        console.print(f"[green]✓[/green] Revoked API key [cyan]{key_id}[/cyan]")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Error:[/red] API key [cyan]{key_id}[/cyan] not found")
        else:
            console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@keys_app.command("info")
def keys_info(
    ctx: typer.Context,
    key_id: str = typer.Argument(..., help="Key ID to inspect"),
) -> None:
    """Get details about an API key.

    Requires OAuth authentication. Shows key metadata but not the full key value.

    Examples:
        hopx auth keys info NXAXAV4sU3Ii
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)

    oauth_token = token_manager.get_valid_oauth_token()
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Fetching key {key_id}..."), APIKeyManager(oauth_token) as manager:
            key = manager.get_key(key_id)

        # Build panel content
        lines = []
        lines.append(f"[bold]ID:[/bold]         {key.get('id', '-')}")
        lines.append(f"[bold]Name:[/bold]       {key.get('name', '-')}")
        lines.append(f"[bold]Prefix:[/bold]     {key.get('prefix', '-')}")

        created_at = key.get("created_at")
        if created_at:
            lines.append(f"[bold]Created:[/bold]    {_format_datetime(created_at)}")

        expires_at = key.get("expires_at")
        if expires_at:
            expires_str = _format_datetime(expires_at)
            expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            now = datetime.now(UTC)
            if expires_dt < now:
                expires_str += " [red](expired)[/red]"
            lines.append(f"[bold]Expires:[/bold]    {expires_str}")
        else:
            lines.append("[bold]Expires:[/bold]    [green]Never[/green]")

        last_used_at = key.get("last_used_at")
        if last_used_at:
            lines.append(f"[bold]Last Used:[/bold]  {_format_datetime(last_used_at)}")
        else:
            lines.append("[bold]Last Used:[/bold]  [dim]Never[/dim]")

        content = "\n".join(lines)
        console.print(Panel(content, title=f"API Key: {key_id}", border_style="cyan"))

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Error:[/red] API key [cyan]{key_id}[/cyan] not found")
        else:
            console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


def _format_datetime(dt_str: str) -> str:
    """Format ISO datetime string for display.

    Args:
        dt_str: ISO format datetime string

    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return dt_str
