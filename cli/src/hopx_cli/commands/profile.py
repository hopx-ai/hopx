"""User profile commands for the Hopx CLI.

Calls /auth/me and /auth/profile endpoints (api-client.ts lines 592-610).
"""

import json

import httpx
import typer
from rich.console import Console
from rich.table import Table

from ..auth.credentials import CredentialStore
from ..auth.token import TokenManager
from ..core import CLIContext, OutputFormat, handle_errors
from ..output import Spinner

app = typer.Typer(
    help="Manage user profile",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _get_oauth_token(ctx: typer.Context) -> str | None:
    """Get valid OAuth token from context."""
    cli_ctx: CLIContext = ctx.obj
    profile = cli_ctx.config.profile if cli_ctx else "default"
    credentials = CredentialStore(profile=profile)
    token_manager = TokenManager(credentials)
    return token_manager.get_valid_oauth_token()


def _get_api_client(oauth_token: str, base_url: str = "https://api.hopx.dev") -> httpx.Client:
    """Create authenticated HTTP client."""
    return httpx.Client(
        base_url=base_url,
        headers={"Authorization": f"Bearer {oauth_token}"},
        timeout=30.0,
    )


@app.command("info")
@handle_errors
def info(ctx: typer.Context) -> None:
    """Show your profile information.

    Displays your user ID, email, name, role, and organization.

    Examples:
        $ hopx profile info
        $ hopx profile info --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching profile..."), _get_api_client(oauth_token) as client:
            # GET /auth/me (api-client.ts lines 593-602)
            response = client.get("/auth/me")
            response.raise_for_status()
            profile = response.json()

        # Response format: {user_id, email, first_name, last_name, avatar_url, organization_id, role}
        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(profile, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            console.print(f"User ID: {profile.get('user_id')}")
            console.print(f"Email: {profile.get('email')}")
            console.print(f"Name: {profile.get('first_name', '')} {profile.get('last_name', '')}")
            console.print(f"Role: {profile.get('role')}")
            console.print(f"Organization ID: {profile.get('organization_id')}")
        else:
            table = Table(title="Profile", show_header=False)
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            table.add_row("User ID", profile.get("user_id", "-"))
            table.add_row("Email", profile.get("email", "-"))
            table.add_row("First Name", profile.get("first_name", "-"))
            table.add_row("Last Name", profile.get("last_name", "-"))
            table.add_row("Role", profile.get("role", "-"))
            table.add_row("Organization ID", str(profile.get("organization_id", "-")))
            console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("update")
@handle_errors
def update(
    ctx: typer.Context,
    first_name: str | None = typer.Option(None, "--first-name", "-f", help="First name"),
    last_name: str | None = typer.Option(None, "--last-name", "-l", help="Last name"),
) -> None:
    """Update your profile.

    Updates your first and/or last name.

    Examples:
        $ hopx profile update --first-name "John"
        $ hopx profile update --first-name "John" --last-name "Doe"
    """
    if not first_name and not last_name:
        console.print("[red]Error:[/red] At least one of --first-name or --last-name is required")
        raise typer.Exit(2)

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    # Build update payload
    payload = {}
    if first_name:
        payload["first_name"] = first_name
    if last_name:
        payload["last_name"] = last_name

    try:
        with Spinner("Updating profile..."), _get_api_client(oauth_token) as client:
            # PUT /auth/profile (api-client.ts lines 605-609)
            response = client.put("/auth/profile", json=payload)
            response.raise_for_status()
            result = response.json()

        if result.get("success"):
            console.print("[green]✓[/green] Profile updated successfully")
            if first_name:
                console.print(f"  First name: {first_name}")
            if last_name:
                console.print(f"  Last name: {last_name}")
        else:
            console.print(f"[red]Error:[/red] {result.get('message', 'Update failed')}")
            raise typer.Exit(1)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
