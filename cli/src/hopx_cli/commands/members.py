"""Organization members commands for the Hopx CLI.

Calls /auth/members endpoints (api-client.ts lines 876-911).
"""

import json

import httpx
import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from ..auth.credentials import CredentialStore
from ..auth.token import TokenManager
from ..core import CLIContext, OutputFormat, handle_errors
from ..output import Spinner

app = typer.Typer(
    help="Manage organization members",
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


@app.command("list")
@handle_errors
def list_members(ctx: typer.Context) -> None:
    """List organization members.

    Shows all members in your organization with their roles and status.

    Examples:
        $ hopx members list
        $ hopx members list --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching members..."), _get_api_client(oauth_token) as client:
            # GET /auth/members (api-client.ts lines 877-891)
            response = client.get("/auth/members")
            response.raise_for_status()
            result = response.json()

        members = result.get("data", [])

        if not members:
            console.print("[dim]No members found[/dim]")
            return

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(members, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for member in members:
                email = member.get("email", "-")
                role = member.get("role", "-")
                status = member.get("status", "-")
                console.print(f"{email} ({role}) - {status}")
        else:
            table = Table(title="Organization Members", show_header=True, header_style="bold cyan")
            table.add_column("Email")
            table.add_column("Name")
            table.add_column("Role")
            table.add_column("Status")

            for member in members:
                name = (
                    f"{member.get('first_name', '')} {member.get('last_name', '')}".strip() or "-"
                )
                status = member.get("status", "-")
                if status == "active":
                    status = f"[green]{status}[/green]"
                elif status == "pending":
                    status = f"[yellow]{status}[/yellow]"

                table.add_row(
                    member.get("email", "-"),
                    name,
                    member.get("role", "-"),
                    status,
                )
            console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("invite")
@handle_errors
def invite(
    ctx: typer.Context,
    email: str = typer.Argument(..., help="Email address to invite"),
) -> None:
    """Invite a new member to your organization.

    Sends an invitation email to the specified address.

    Examples:
        $ hopx members invite user@example.com
    """
    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Sending invitation to {email}..."):
            with _get_api_client(oauth_token) as client:
                # POST /auth/members/invite (api-client.ts lines 894-901)
                response = client.post("/auth/members/invite", json={"email": email})
                response.raise_for_status()
                result = response.json()

        if result.get("success"):
            console.print(f"[green]✓[/green] Invitation sent to {email}")
        else:
            console.print(f"[red]Error:[/red] {result.get('message', 'Invitation failed')}")
            raise typer.Exit(1)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            console.print(
                f"[yellow]Warning:[/yellow] {email} is already a member or has a pending invitation"
            )
        else:
            console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("remove")
@handle_errors
def remove(
    ctx: typer.Context,
    membership_id: str = typer.Argument(..., help="Membership ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove a member from your organization.

    Removes the specified member by their membership ID.
    Use 'hopx members list --output json' to find membership IDs.

    Examples:
        $ hopx members remove mem_abc123
        $ hopx members remove mem_abc123 --force
    """
    if not force and not Confirm.ask(f"Remove member [cyan]{membership_id}[/cyan]?", default=False):
        console.print("Cancelled")
        raise typer.Exit(0)

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Removing member {membership_id}..."):
            with _get_api_client(oauth_token) as client:
                # DELETE /auth/members/{membershipId} (api-client.ts lines 904-910)
                response = client.delete(f"/auth/members/{membership_id}")
                response.raise_for_status()
                result = response.json()

        if result.get("success"):
            console.print("[green]✓[/green] Member removed successfully")
        else:
            console.print(f"[red]Error:[/red] {result.get('message', 'Removal failed')}")
            raise typer.Exit(1)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Error:[/red] Member {membership_id} not found")
        else:
            console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
