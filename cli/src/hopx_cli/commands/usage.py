"""Usage statistics commands for the Hopx CLI.

Calls /auth/usage API endpoints (api-client.ts lines 486-588).
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
    help="View usage statistics",
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


@app.command("summary")
@handle_errors
def summary(ctx: typer.Context) -> None:
    """Show usage summary with plan limits.

    Displays current usage vs plan limits including:
    - Active sandboxes
    - vCPU usage
    - Memory usage
    - Disk usage

    Examples:
        $ hopx usage summary
        $ hopx usage summary --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching usage data..."), _get_api_client(oauth_token) as client:
            # GET /auth/usage (api-client.ts lines 487-508)
            response = client.get("/auth/usage")
            response.raise_for_status()
            usage = response.json()

        # Response format: {plan: {id, name, description}, limits: {...}, current_usage: {...}}
        plan = usage.get("plan", {})
        limits = usage.get("limits", {})
        current = usage.get("current_usage", {})

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(usage, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            console.print(f"Plan: {plan.get('name', '-')}")
            console.print(
                f"Sandboxes: {current.get('active_sandboxes', 0)}/{limits.get('max_concurrent_sandboxes', '-')}"
            )
            console.print(
                f"vCPU: {current.get('total_vcpu', 0)}/{limits.get('max_total_vcpu', '-')}"
            )
            console.print(
                f"Memory: {current.get('total_memory_mb', 0)}MB/{limits.get('max_total_memory_mb', '-')}MB"
            )
            console.print(
                f"Disk: {current.get('total_disk_gb', 0)}GB/{limits.get('max_total_disk_gb', '-')}GB"
            )
        else:
            # Main usage table
            table = Table(
                title=f"Usage - {plan.get('name', 'Unknown Plan')}",
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Resource")
            table.add_column("Current", justify="right")
            table.add_column("Limit", justify="right")
            table.add_column("Usage", justify="right")

            # Calculate percentages
            def pct(current: int, limit: int) -> str:
                if limit == 0:
                    return "-"
                p = (current / limit) * 100
                if p > 80:
                    return f"[red]{p:.0f}%[/red]"
                elif p > 50:
                    return f"[yellow]{p:.0f}%[/yellow]"
                return f"[green]{p:.0f}%[/green]"

            sandboxes_cur = current.get("active_sandboxes", 0)
            sandboxes_lim = limits.get("max_concurrent_sandboxes", 0)
            table.add_row(
                "Sandboxes",
                str(sandboxes_cur),
                str(sandboxes_lim),
                pct(sandboxes_cur, sandboxes_lim),
            )

            vcpu_cur = current.get("total_vcpu", 0)
            vcpu_lim = limits.get("max_total_vcpu", 0)
            table.add_row("vCPU", str(vcpu_cur), str(vcpu_lim), pct(vcpu_cur, vcpu_lim))

            mem_cur = current.get("total_memory_mb", 0)
            mem_lim = limits.get("max_total_memory_mb", 0)
            table.add_row("Memory (MB)", str(mem_cur), str(mem_lim), pct(mem_cur, mem_lim))

            disk_cur = current.get("total_disk_gb", 0)
            disk_lim = limits.get("max_total_disk_gb", 0)
            table.add_row("Disk (GB)", str(disk_cur), str(disk_lim), pct(disk_cur, disk_lim))

            console.print(table)

            # Per-sandbox limits
            console.print()
            limits_table = Table(title="Per-Sandbox Limits", show_header=True, header_style="bold")
            limits_table.add_column("Resource")
            limits_table.add_column("Maximum", justify="right")
            limits_table.add_row("vCPU", str(limits.get("max_vcpu_per_sandbox", "-")))
            limits_table.add_row("Memory (MB)", str(limits.get("max_memory_mb_per_sandbox", "-")))
            limits_table.add_row("Disk (GB)", str(limits.get("max_disk_gb_per_sandbox", "-")))
            console.print(limits_table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("plans")
@handle_errors
def plans(ctx: typer.Context) -> None:
    """Show all available plans.

    Displays plan tiers with their limits and requirements.

    Examples:
        $ hopx usage plans
        $ hopx usage plans --output json
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner("Fetching plans..."), _get_api_client(oauth_token) as client:
            # GET /auth/plans (api-client.ts lines 511-537)
            response = client.get("/auth/plans")
            response.raise_for_status()
            data = response.json()

        plans_list = data.get("plans", [])
        total_spent = data.get("total_spent", 0)

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for plan in plans_list:
                current = " (current)" if plan.get("is_current") else ""
                console.print(f"{plan.get('name')}{current}: {plan.get('description')}")
        else:
            table = Table(title="Available Plans", show_header=True, header_style="bold cyan")
            table.add_column("Plan")
            table.add_column("Max Sandboxes", justify="right")
            table.add_column("Max vCPU", justify="right")
            table.add_column("Max Memory", justify="right")
            table.add_column("Requirement")

            for plan in plans_list:
                name = plan.get("name", "-")
                if plan.get("is_current"):
                    name = f"[green]{name} ✓[/green]"

                table.add_row(
                    name,
                    str(plan.get("max_concurrent_sandboxes", "-")),
                    str(plan.get("max_total_vcpu", "-")),
                    f"{plan.get('max_total_memory_mb', 0) // 1024}GB",
                    plan.get("upgrade_requirement", "-"),
                )
            console.print(table)

            if total_spent > 0:
                console.print(f"\n[dim]Total spent: ${total_spent / 100:.2f}[/dim]")

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
    resource: str = typer.Option(
        "sandboxes",
        "--resource",
        "-r",
        help="Resource type: sandboxes, cost, cpu, ram, disk",
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show"),
) -> None:
    """Show usage history.

    Displays historical usage data for various resources.

    Examples:
        $ hopx usage history
        $ hopx usage history --resource cost --days 30
        $ hopx usage history --resource cpu
    """
    cli_ctx: CLIContext = ctx.obj

    oauth_token = _get_oauth_token(ctx)
    if not oauth_token:
        console.print("[red]Error:[/red] OAuth authentication required")
        console.print("Use [cyan]hopx auth login[/cyan] to authenticate")
        raise typer.Exit(1)

    try:
        with Spinner(f"Fetching {resource} history..."):
            with _get_api_client(oauth_token) as client:
                if resource == "sandboxes":
                    # GET /auth/usage/history/sandboxes (api-client.ts lines 540-554)
                    response = client.get(f"/auth/usage/history/sandboxes?days={days}")
                elif resource == "cost":
                    # GET /auth/usage/history/cost (api-client.ts lines 557-570)
                    response = client.get(f"/auth/usage/history/cost?days={days}")
                elif resource in ["cpu", "ram", "disk"]:
                    # GET /auth/usage/history/resources (api-client.ts lines 573-588)
                    response = client.get(
                        f"/auth/usage/history/resources?type={resource}&days={days}"
                    )
                else:
                    console.print(f"[red]Error:[/red] Invalid resource type: {resource}")
                    console.print("Valid options: sandboxes, cost, cpu, ram, disk")
                    raise typer.Exit(2)

                response.raise_for_status()
                data = response.json()

        history_data = data.get("data", [])

        if not history_data:
            console.print(f"[dim]No {resource} history data available[/dim]")
            return

        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(json.dumps(data, indent=2))
        elif cli_ctx.output_format == OutputFormat.PLAIN:
            for entry in history_data:
                date = entry.get("date", "-")
                if resource == "sandboxes":
                    value = entry.get("active_vms", 0)
                    console.print(f"{date}: {value} sandboxes")
                elif resource == "cost":
                    value = entry.get("cost_usd", 0)
                    console.print(f"{date}: ${value:.2f}")
                else:
                    value = entry.get("total_usage", 0)
                    console.print(f"{date}: {value}")
        else:
            table = Table(
                title=f"{resource.title()} History ({days} days)",
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Date")

            if resource == "sandboxes":
                table.add_column("Active Sandboxes", justify="right")
                for entry in history_data:
                    table.add_row(entry.get("date", "-"), str(entry.get("active_vms", 0)))
            elif resource == "cost":
                table.add_column("Cost (USD)", justify="right")
                for entry in history_data:
                    table.add_row(entry.get("date", "-"), f"${entry.get('cost_usd', 0):.2f}")
            else:
                table.add_column("Usage", justify="right")
                for entry in history_data:
                    table.add_row(entry.get("date", "-"), str(entry.get("total_usage", 0)))

            console.print(table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error:[/red] API request failed: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Keep the old 'sandboxes' command as an alias for backwards compatibility
@app.command("sandboxes")
@handle_errors
def sandboxes(ctx: typer.Context) -> None:
    """Show current sandbox usage (alias for 'summary').

    Displays current usage vs plan limits.

    Examples:
        $ hopx usage sandboxes
    """
    # Delegate to summary command
    summary(ctx)
