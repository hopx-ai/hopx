"""Billing commands for the Hopx CLI.

Calls /auth/billing/* endpoints (api-client.ts lines 658-852).
Note: Only read-only operations are exposed in CLI. Payment operations
should be done through the web console for security.
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
    help="View billing information",
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


@app.command("balance")
@handle_errors
def balance(ctx: typer.Context) -> None:
    """Show your credit balance.

    Displays your current credit balance in USD.

    Examples:
        $ hopx billing balance
        $ hopx billing balance --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching balance..."), _get_api_client(oauth_token) as client:
            # GET /auth/billing/credit/balance (api-client.ts lines 660-665)
            response = client.get("/auth/billing/credit/balance")
            response.raise_for_status()
            data = response.json()

        # Response: {balance_cents, balance_usd, currency}
        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            console.print(data.get("balance_usd", "$0.00"))
        else:
            balance_usd = data.get("balance_usd", "$0.00")
            balance_cents = data.get("balance_cents", 0)

            # Color based on balance
            if balance_cents < 100:  # Less than $1
                balance_display = f"[red]{balance_usd}[/red]"
            elif balance_cents < 1000:  # Less than $10
                balance_display = f"[yellow]{balance_usd}[/yellow]"
            else:
                balance_display = f"[green]{balance_usd}[/green]"

            console.print(f"\n  Credit Balance: {balance_display}\n")

            if balance_cents < 500:
                console.print("[dim]Tip: Add credits at https://console.hopx.dev/billing[/dim]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("history")
@handle_errors
def history(
    ctx: typer.Context,
    limit: int = typer.Option(20, "--limit", "-l", help="Number of transactions to show"),
) -> None:
    """Show billing transaction history.

    Displays recent billing transactions including credits and charges.

    Examples:
        $ hopx billing history
        $ hopx billing history --limit 50
        $ hopx billing history --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching billing history..."), _get_api_client(oauth_token) as client:
            # GET /auth/billing/history (api-client.ts lines 803-829)
            response = client.get(f"/auth/billing/history?limit={limit}")
            response.raise_for_status()
            data = response.json()

        transactions = data.get("transactions", [])

        if not transactions:
            console.print("[dim]No billing history found[/dim]")
            return

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for tx in transactions:
                date = tx.get("created_at", "-")[:10]
                amount = tx.get("amount_display", "-")
                desc = tx.get("description", "-")
                console.print(f"{date}: {amount} - {desc}")
        else:
            table = Table(title="Billing History", show_header=True, header_style="bold cyan")
            table.add_column("Date")
            table.add_column("Amount", justify="right")
            table.add_column("Type")
            table.add_column("Description")

            for tx in transactions:
                date = tx.get("created_at", "-")[:10]
                amount = tx.get("amount_display", "-")
                tx_type = tx.get("type", "-")
                desc = tx.get("description", "-")

                # Color based on debit/credit
                if tx.get("is_debit"):
                    amount = f"[red]{amount}[/red]"
                else:
                    amount = f"[green]+{amount}[/green]"

                table.add_row(date, amount, tx_type, desc[:40])

            console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("invoices")
@handle_errors
def invoices(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", "-l", help="Number of invoices to show"),
) -> None:
    """Show invoices.

    Displays your Stripe invoices with links to view/download.

    Examples:
        $ hopx billing invoices
        $ hopx billing invoices --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching invoices..."), _get_api_client(oauth_token) as client:
            # GET /auth/billing/invoices (api-client.ts lines 833-851)
            response = client.get(f"/auth/billing/invoices?limit={limit}")
            response.raise_for_status()
            data = response.json()

        invoices_list = data.get("invoices", [])

        if not invoices_list:
            console.print("[dim]No invoices found[/dim]")
            return

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for inv in invoices_list:
                number = inv.get("number", "-")
                amount = inv.get("amount_due", 0) / 100
                status = inv.get("status", "-")
                console.print(f"{number}: ${amount:.2f} ({status})")
        else:
            table = Table(title="Invoices", show_header=True, header_style="bold cyan")
            table.add_column("Number")
            table.add_column("Amount", justify="right")
            table.add_column("Status")
            table.add_column("PDF")

            for inv in invoices_list:
                number = inv.get("number", "-")
                amount = f"${inv.get('amount_due', 0) / 100:.2f}"
                status = inv.get("status", "-")
                pdf_url = inv.get("pdf_url", "")

                if status == "paid":
                    status = f"[green]{status}[/green]"
                elif status == "open":
                    status = f"[yellow]{status}[/yellow]"

                table.add_row(
                    number,
                    amount,
                    status,
                    "[link]View[/link]" if pdf_url else "-",
                )

            console.print(table)
            console.print("\n[dim]Tip: Use --output json to get full invoice URLs[/dim]")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("auto-recharge")
@handle_errors
def auto_recharge(ctx: typer.Context) -> None:
    """Show auto-recharge settings.

    Displays your current auto-recharge configuration.
    To modify settings, use the web console.

    Examples:
        $ hopx billing auto-recharge
        $ hopx billing auto-recharge --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching auto-recharge settings..."):
            with _get_api_client(oauth_token) as client:
                # GET /auth/billing/auto-recharge (api-client.ts lines 745-753)
                response = client.get("/auth/billing/auto-recharge")
                response.raise_for_status()
                data = response.json()

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            enabled = "Enabled" if data.get("enabled") else "Disabled"
            console.print(f"Auto-recharge: {enabled}")
            if data.get("enabled"):
                threshold = data.get("threshold_cents", 0) / 100
                recharge_to = data.get("recharge_to_cents", 0) / 100
                console.print(f"Threshold: ${threshold:.2f}")
                console.print(f"Recharge to: ${recharge_to:.2f}")
        else:
            table = Table(title="Auto-Recharge Settings", show_header=False)
            table.add_column("Setting", style="cyan")
            table.add_column("Value")

            enabled = data.get("enabled", False)
            table.add_row("Status", "[green]Enabled[/green]" if enabled else "[dim]Disabled[/dim]")

            if enabled:
                threshold = data.get("threshold_cents")
                if threshold:
                    table.add_row("Threshold", f"${threshold / 100:.2f}")

                recharge_to = data.get("recharge_to_cents")
                if recharge_to:
                    table.add_row("Recharge To", f"${recharge_to / 100:.2f}")

                monthly_limit = data.get("monthly_limit_cents")
                if monthly_limit:
                    table.add_row("Monthly Limit", f"${monthly_limit / 100:.2f}")

                current_month = data.get("current_month_recharged_cents", 0)
                table.add_row("This Month", f"${current_month / 100:.2f}")

            console.print(table)

            if not enabled:
                console.print(
                    "\n[dim]Enable auto-recharge at https://console.hopx.dev/billing[/dim]"
                )

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
