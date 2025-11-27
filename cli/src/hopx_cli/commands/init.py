"""First-run wizard for Hopx CLI.

Guides new users through authentication, API key creation, and verifies setup.
"""

import secrets
import socket

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from hopx_cli.auth.api_keys import APIKeyManager
from hopx_cli.auth.credentials import CredentialStore
from hopx_cli.auth.oauth import browser_login, browser_login_headless
from hopx_cli.auth.token import TokenManager
from hopx_cli.core import CLIContext
from hopx_cli.output import Spinner

app = typer.Typer(
    help="First-run setup wizard",
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _get_profile(ctx: typer.Context) -> str:
    """Get profile from CLI context."""
    cli_ctx: CLIContext = ctx.obj
    return cli_ctx.config.profile if cli_ctx else "default"


def _get_machine_name() -> str:
    """Get a unique name for the API key based on machine hostname.

    Appends a random suffix to ensure uniqueness. This allows users to:
    - Re-run `hopx init` without conflicts
    - Run init on multiple machines with the same hostname
    """
    try:
        hostname = socket.gethostname()
        base_name = hostname.split(".")[0][:14]  # Shorter to leave room for suffix
    except Exception:
        base_name = "cli"

    # Append unique suffix: 6 hex characters (16M possibilities)
    suffix = secrets.token_hex(3)
    return f"{base_name}-{suffix}"


@app.callback(invoke_without_command=True)
def init(
    ctx: typer.Context,
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Headless mode: manually paste callback URL",
    ),
    skip_test: bool = typer.Option(
        False,
        "--skip-test",
        help="Skip the sandbox test step",
    ),
) -> None:
    """Set up Hopx CLI in one command.

    Interactive wizard that:
    1. Authenticates with your Hopx account
    2. Creates and stores an API key
    3. Verifies everything works by running a test

    Examples:
        # Full interactive setup
        hopx init

        # Headless mode (for servers without browsers)
        hopx init --no-browser

        # Skip the sandbox test
        hopx init --skip-test
    """
    profile = _get_profile(ctx)
    credentials = CredentialStore(profile=profile)
    cli_ctx: CLIContext = ctx.obj

    # Welcome banner
    console.print(
        Panel(
            "[bold]Welcome to Hopx![/bold]\n\n"
            "This wizard will set up your CLI in a few steps.\n"
            "You can re-run this command anytime to reconfigure.",
            title="hopx init",
            border_style="cyan",
        )
    )
    console.print()

    # Check if already configured
    try:
        existing_key = cli_ctx.config.get_api_key()
        if existing_key:
            console.print("[yellow]Note:[/yellow] You already have credentials configured.")
            if not Confirm.ask("Continue and reconfigure?", default=False):
                console.print("\nSetup cancelled. Your existing configuration is unchanged.")
                console.print("[dim]Run 'hopx auth validate' to verify your setup.[/dim]")
                raise typer.Exit(0)
            console.print()
    except ValueError:
        pass  # No existing key, continue

    # Step 1: Authentication
    console.print("[bold cyan][1/3] Authentication[/bold cyan]")
    console.print("      Opening browser for login...")
    console.print()

    try:
        if no_browser:
            token_data = browser_login_headless(provider="GoogleOAuth")
        else:
            with Spinner("Waiting for authentication...") as spinner:
                token_data = browser_login(provider="GoogleOAuth", timeout=120)
                spinner.stop()

        credentials.store_oauth_token(token_data)
        console.print("      [green]✓[/green] Logged in successfully")
        console.print()

    except TimeoutError:
        console.print("      [red]✗[/red] Authentication timed out")
        console.print("\n[dim]Try again or use 'hopx auth login' manually[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"      [red]✗[/red] Authentication failed: {e}")
        console.print("\n[dim]Try again or use 'hopx auth login' manually[/dim]")
        raise typer.Exit(1)

    # Step 2: Create API Key
    console.print("[bold cyan][2/3] API Key[/bold cyan]")
    key_name = _get_machine_name()
    console.print(f"      Creating API key '{key_name}'...")
    console.print()

    token_manager = TokenManager(credentials)
    oauth_token = token_manager.get_valid_oauth_token()

    if not oauth_token:
        console.print("      [red]✗[/red] OAuth token not available")
        raise typer.Exit(1)

    try:
        with Spinner("Creating API key...") as spinner:
            with APIKeyManager(oauth_token) as manager:
                # FIXED: Use expires_in enum (default "never"), not ISO date
                result = manager.create_key(key_name, expires_in="never")
            spinner.stop()

        # FIXED: Response uses "full_key" not "key" (types.ts line 252)
        key_value = result.get("full_key")
        if key_value:
            credentials.store_api_key(key_value)
            console.print("      [green]✓[/green] API key created and stored")
        else:
            console.print("      [red]✗[/red] Failed to create API key")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"      [red]✗[/red] Failed to create API key: {e}")
        console.print("\n[dim]Try 'hopx auth keys create --name \"my-key\"' manually[/dim]")
        raise typer.Exit(1)

    console.print()

    # Step 3: Test sandbox (optional)
    if skip_test:
        console.print("[bold cyan][3/3] Test[/bold cyan]")
        console.print("      [dim]Skipped (--skip-test)[/dim]")
    else:
        console.print("[bold cyan][3/3] Quick Test[/bold cyan]")
        console.print("      Creating test sandbox...")
        console.print()

        try:
            from hopx_ai import Sandbox

            with Spinner("Creating sandbox...") as spinner:
                sb = Sandbox.create(
                    template="code-interpreter",
                    api_key=key_value,
                    base_url=cli_ctx.config.base_url,
                )
                spinner.stop()

            console.print(f"      [green]✓[/green] Sandbox created: {sb.sandbox_id}")

            # Run test code
            with Spinner("Running test code...") as spinner:
                result = sb.run_code("print('Hello from Hopx!')")
                spinner.stop()

            if result.stdout and "Hello from Hopx!" in result.stdout:
                console.print("      [green]✓[/green] Code execution works")
            else:
                console.print("      [yellow]⚠[/yellow] Code ran but output unexpected")

            # Cleanup
            with Spinner("Cleaning up...") as spinner:
                sb.kill()
                spinner.stop()

            console.print("      [green]✓[/green] Sandbox cleaned up")

        except Exception as e:
            console.print(f"      [yellow]⚠[/yellow] Test failed: {e}")
            console.print("      [dim]This doesn't affect your setup[/dim]")

    console.print()

    # Success summary
    console.print(
        Panel(
            "[bold green]Setup complete![/bold green]\n\n"
            "[bold]Get started:[/bold]\n"
            "  hopx sandbox create    [dim]Create a sandbox[/dim]\n"
            "  hopx run 'print(1)'    [dim]Run code directly[/dim]\n"
            "  hopx template list     [dim]Browse templates[/dim]\n\n"
            "[bold]Learn more:[/bold]\n"
            "  hopx --help            [dim]See all commands[/dim]\n"
            "  https://docs.hopx.dev  [dim]Documentation[/dim]",
            title="Ready!",
            border_style="green",
        )
    )
