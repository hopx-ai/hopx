"""Main Typer application and command routing for Hopx CLI."""

import typer

from hopx_cli import __version__
from hopx_cli.core import CLIConfig, CLIContext, OutputFormat


def version_callback(value: bool) -> None:
    """Callback to handle --version flag."""
    if value:
        typer.echo(f"hopx {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="hopx",
    help="Hopx CLI - Manage cloud sandboxes from the command line",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
    epilog="""
[bold]Aliases:[/bold]
  sb    [dim]→[/dim] sandbox     [dim]Manage sandboxes[/dim]
  tpl   [dim]→[/dim] template    [dim]Manage templates[/dim]
  f     [dim]→[/dim] files       [dim]File operations[/dim]
  term  [dim]→[/dim] terminal    [dim]Interactive terminals[/dim]

[bold]Quick Start:[/bold]
  hopx auth login        [dim]Authenticate with browser[/dim]
  hopx auth keys create  [dim]Create and store API key[/dim]
  hopx sandbox create    [dim]Create a new sandbox[/dim]
  hopx run "print(1)"    [dim]Run code in sandbox[/dim]

[dim]Docs: https://docs.hopx.dev | Support: support@hopx.ai[/dim]
""",
)


@app.callback()
def main(
    ctx: typer.Context,
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="HOPX_API_KEY",
        help="API key (overrides HOPX_API_KEY env var)",
    ),
    profile: str = typer.Option(
        "default",
        "--profile",
        envvar="HOPX_PROFILE",
        help="Configuration profile to use",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format",
        case_sensitive=False,
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Increase output verbosity",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        envvar="NO_COLOR",
        help="Disable colored output",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
        is_eager=True,
        callback=version_callback,
    ),
) -> None:
    """
    Global options for all commands.

    These options are available to all subcommands via the context object.
    """
    # Load configuration (will read from .env and config file)
    config = CLIConfig()

    # Override API key if provided via flag
    if api_key:
        config = CLIConfig(api_key=api_key, profile=profile)

    # Create CLI context with proper object
    cli_ctx = CLIContext(
        config=config,
        output_format=output,
        verbose=verbose,
        quiet=quiet,
        no_color=no_color,
    )

    # Store context for subcommands
    ctx.obj = cli_ctx


# Import command groups
from hopx_cli.commands import (
    auth,
    billing,
    cmd,
    env,
    files,
    init,
    members,
    org,
    profile,
    run,
    sandbox,
    self_update,
    system,
    template,
    terminal,
    usage,
)
from hopx_cli.commands import config as config_cmd

# Register subcommands with primary names
app.add_typer(init.app, name="init", help="First-run setup wizard")
app.add_typer(system.app, name="system", help="System and health commands")
app.add_typer(run.app, name="run", help="Execute code in sandboxes")
app.add_typer(auth.app, name="auth", help="Authentication management")
app.add_typer(sandbox.app, name="sandbox", help="Manage sandboxes")
app.add_typer(sandbox.app, name="sb", hidden=True)  # Alias
app.add_typer(template.app, name="template", help="Manage templates")
app.add_typer(template.app, name="tpl", hidden=True)  # Alias
app.add_typer(config_cmd.app, name="config", help="Configuration management")
app.add_typer(files.app, name="files", help="File operations")
app.add_typer(files.app, name="f", hidden=True)  # Alias
app.add_typer(cmd.app, name="cmd", help="Run shell commands in sandboxes")
app.add_typer(env.app, name="env", help="Manage environment variables")
app.add_typer(terminal.app, name="terminal", help="Interactive terminal sessions")
app.add_typer(terminal.app, name="term", hidden=True)  # Alias
app.add_typer(org.app, name="org", help="Manage organization settings")
app.add_typer(usage.app, name="usage", help="View usage statistics")
app.add_typer(profile.app, name="profile", help="Manage user profile")
app.add_typer(members.app, name="members", help="Manage organization members")
app.add_typer(billing.app, name="billing", help="View billing information")
app.add_typer(self_update.app, name="self-update", help="Update CLI to latest version")
