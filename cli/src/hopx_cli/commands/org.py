"""Organization management commands for the Hopx CLI.

Calls /auth/organization API endpoints (api-client.ts lines 614-654).
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
    help="Manage organization settings",
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
    """Show organization information.

    Retrieves organization details from the /auth/organization API.
    Shows: ID, name, slug, plan, and creation date.

    Examples:
        $ hopx org info
        $ hopx org info --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching organization..."), _get_api_client(oauth_token) as client:
            # GET /auth/organization (api-client.ts lines 616-622)
            response = client.get("/auth/organization")
            response.raise_for_status()
            org = response.json()

        # Response format: {id, name, slug, plan_id, created_at}
        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(org, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            console.print(f"ID: {org.get('id')}")
            console.print(f"Name: {org.get('name')}")
            console.print(f"Slug: {org.get('slug')}")
            console.print(f"Plan: {org.get('plan_id')}")
        else:
            table = Table(title="Organization", show_header=False)
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            table.add_row("ID", str(org.get("id", "-")))
            table.add_row("Name", org.get("name", "-"))
            table.add_row("Slug", org.get("slug", "-"))
            table.add_row("Plan", org.get("plan_id", "-"))
            table.add_row("Created", org.get("created_at", "-"))
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
    name: str = typer.Option(..., "--name", "-n", help="New organization name"),
) -> None:
    """Update organization name.

    Requires OAuth authentication.

    Examples:
        $ hopx org update --name "My Company"
    """
    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Updating organization name to '{name}'..."):
            with _get_api_client(oauth_token) as client:
                # PUT /auth/organization (api-client.ts lines 625-629)
                response = client.put("/auth/organization", json={"name": name})
                response.raise_for_status()
                result = response.json()

        if result.get("success"):
            console.print(f"[green]✓[/green] Organization name updated to '{name}'")
        else:
            console.print(f"[red]Error:[/red] {result.get('message', 'Update failed')}")
            raise typer.Exit(1)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
@handle_errors
def list_orgs(ctx: typer.Context) -> None:
    """List all organizations you belong to.

    Shows all organizations where you are a member.

    Examples:
        $ hopx org list
        $ hopx org list --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching organizations..."), _get_api_client(oauth_token) as client:
            # GET /auth/user/organizations (api-client.ts lines 633-642)
            response = client.get("/auth/user/organizations")
            response.raise_for_status()
            result = response.json()

        orgs = result.get("data", [])

        if not orgs:
            console.print("[dim]No organizations found[/dim]")
            return

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(orgs, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for org in orgs:
                console.print(f"{org.get('id')}: {org.get('name')} ({org.get('role')})")
        else:
            table = Table(title="Your Organizations", show_header=True, header_style="bold cyan")
            table.add_column("ID", style="cyan")
            table.add_column("Name")
            table.add_column("Role")
            for org in orgs:
                table.add_row(
                    str(org.get("id", "-")),
                    org.get("name", "-"),
                    org.get("role", "-"),
                )
            console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("switch")
@handle_errors
def switch(
    ctx: typer.Context,
    org_id: int = typer.Argument(..., help="Organization ID to switch to"),
) -> None:
    """Switch to a different organization.

    Changes your active organization context.

    Examples:
        $ hopx org switch 123
    """
    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Switching to organization {org_id}..."):
            with _get_api_client(oauth_token) as client:
                # POST /auth/organization/switch (api-client.ts lines 646-653)
                response = client.post(
                    "/auth/organization/switch",
                    json={"organization_id": org_id},
                )
                response.raise_for_status()
                result = response.json()

        if result.get("success"):
            console.print(f"[green]✓[/green] Switched to organization {org_id}")
            console.print("[dim]Note: You may need to re-login for changes to take effect[/dim]")
        else:
            console.print(f"[red]Error:[/red] {result.get('message', 'Switch failed')}")
            raise typer.Exit(1)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Error:[/red] Organization {org_id} not found")
        else:
            console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
