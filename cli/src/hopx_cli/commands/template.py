"""Template management commands for the Hopx CLI.

Implements all template operations including listing, getting details,
building custom templates, and deletion.
"""

from pathlib import Path
from typing import Any

import typer
from hopx_ai import Sandbox
from hopx_ai import Template as TemplateModel
from hopx_ai.template.builder import BuildResult
from rich.console import Console
from rich.table import Table

from ..core import (
    CLIContext,
    OutputFormat,
    handle_errors,
)
from ..output import (
    Spinner,
    format_output,
)

app = typer.Typer(
    help="Manage templates",
    no_args_is_help=True,
    context_settings={"allow_interspersed_args": True},
)
console = Console()


def _format_template_table(templates: list[TemplateModel], title: str = "Templates") -> Table:
    """Format templates as a rich table.

    Args:
        templates: List of template objects
        title: Table title

    Returns:
        Rich Table object
    """
    table = Table(title=title, show_header=True)

    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="white")
    table.add_column("Category", style="yellow")
    table.add_column("Language", style="green")
    table.add_column("Public", style="magenta")
    table.add_column("Resources", style="blue")

    for t in templates:
        resources = ""
        if t.default_resources:
            parts = []
            if t.default_resources.vcpu:
                parts.append(f"{t.default_resources.vcpu}vCPU")
            if t.default_resources.memory_mb:
                parts.append(f"{t.default_resources.memory_mb}MB")
            if t.default_resources.disk_gb:
                parts.append(f"{t.default_resources.disk_gb}GB")
            resources = ", ".join(parts)

        public_str = "Yes" if t.is_public else "No"

        table.add_row(
            t.name,
            t.display_name,
            t.category or "[dim]N/A[/dim]",
            t.language or "[dim]N/A[/dim]",
            public_str,
            resources or "[dim]N/A[/dim]",
        )

    return table


def _format_template_details(template: TemplateModel, ctx: CLIContext) -> None:
    """Format and display detailed template information.

    Args:
        template: Template object
        ctx: CLI context
    """
    if ctx.output_format == OutputFormat.JSON:
        format_output(
            template.model_dump(),
            ctx.output_format,
        )
    elif ctx.output_format == OutputFormat.PLAIN:
        lines = [
            f"ID: {template.id}",
            f"Name: {template.name}",
            f"Display Name: {template.display_name}",
            f"Category: {template.category or 'N/A'}",
            f"Language: {template.language or 'N/A'}",
            f"Public: {'Yes' if template.is_public else 'No'}",
            f"Active: {'Yes' if template.is_active else 'No'}",
        ]

        if template.description:
            lines.append(f"Description: {template.description}")

        if template.default_resources:
            res = template.default_resources
            lines.append(
                f"Default Resources: {res.vcpu or 'N/A'} vCPU, "
                f"{res.memory_mb or 'N/A'}MB RAM, "
                f"{res.disk_gb or 'N/A'}GB disk"
            )

        if template.features:
            lines.append(f"Features: {', '.join(template.features)}")

        if template.tags:
            lines.append(f"Tags: {', '.join(template.tags)}")

        if template.docs_url:
            lines.append(f"Docs: {template.docs_url}")

        console.print("\n".join(lines))
    else:
        # Rich table format
        table = Table(
            title="Template Details",
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        table.add_column("Property", style="cyan bold")
        table.add_column("Value")

        table.add_row("ID", template.id)
        table.add_row("Name", template.name)
        table.add_row("Display Name", template.display_name)
        table.add_row("Category", template.category or "[dim]N/A[/dim]")
        table.add_row("Language", template.language or "[dim]N/A[/dim]")
        table.add_row("Public", "Yes" if template.is_public else "No")
        table.add_row("Active", "Yes" if template.is_active else "No")

        if template.description:
            table.add_row("Description", template.description)

        if template.default_resources:
            res = template.default_resources
            table.add_row(
                "Default Resources",
                f"{res.vcpu or 'N/A'} vCPU, {res.memory_mb or 'N/A'}MB RAM, {res.disk_gb or 'N/A'}GB disk",
            )

        if template.min_resources:
            res = template.min_resources
            table.add_row(
                "Min Resources",
                f"{res.vcpu or 'N/A'} vCPU, {res.memory_mb or 'N/A'}MB RAM, {res.disk_gb or 'N/A'}GB disk",
            )

        if template.max_resources:
            res = template.max_resources
            table.add_row(
                "Max Resources",
                f"{res.vcpu or 'N/A'} vCPU, {res.memory_mb or 'N/A'}MB RAM, {res.disk_gb or 'N/A'}GB disk",
            )

        if template.features:
            table.add_row("Features", ", ".join(template.features))

        if template.tags:
            table.add_row("Tags", ", ".join(template.tags))

        if template.popularity_score is not None:
            table.add_row("Popularity", str(template.popularity_score))

        if template.docs_url:
            table.add_row("Docs", template.docs_url)

        if template.icon:
            table.add_row("Icon", template.icon)

        console.print(table)


@app.command("list")
@handle_errors
def list_cmd(
    ctx: typer.Context,
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by category: development, infrastructure, operating-system",
    ),
    language: str | None = typer.Option(
        None,
        "--language",
        "-l",
        help="Filter by language: python, nodejs, etc.",
    ),
    public: bool = typer.Option(
        False,
        "--public",
        help="Show only public templates",
    ),
) -> None:
    """List available templates.

    Examples:
        # List all templates
        hopx template list

        # List development templates
        hopx template list --category development

        # List Python templates
        hopx template list --language python

        # List only public templates
        hopx template list --public
    """
    cli_ctx: CLIContext = ctx.obj

    templates = Sandbox.list_templates(
        category=category,
        language=language,
        api_key=cli_ctx.config.api_key,
        base_url=cli_ctx.config.base_url,
    )

    # Apply public filter (SDK doesn't provide this filter)
    if public:
        templates = [t for t in templates if t.is_public]

    # Display results
    if not templates:
        if not cli_ctx.quiet:
            console.print("[dim]No templates found[/dim]")
        return

    if cli_ctx.output_format == OutputFormat.JSON:
        format_output(
            [t.model_dump() for t in templates],
            cli_ctx.output_format,
        )
    elif cli_ctx.output_format == OutputFormat.PLAIN:
        for t in templates:
            console.print(f"{t.name}: {t.display_name}")
    else:
        table = _format_template_table(templates)
        console.print(table)


@app.command("info")
@handle_errors
def info(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Template name or ID"),
) -> None:
    """Get detailed information about a template.

    Examples:
        hopx template info code-interpreter
        hopx template info python
    """
    cli_ctx: CLIContext = ctx.obj

    template = Sandbox.get_template(
        name=name,
        api_key=cli_ctx.config.api_key,
        base_url=cli_ctx.config.base_url,
    )

    _format_template_details(template, cli_ctx)


@app.command("delete")
@handle_errors
def delete(
    ctx: typer.Context,
    template_id: str = typer.Argument(..., help="Template ID to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
) -> None:
    """Delete a custom template.

    Only organization-owned templates can be deleted.
    Public templates cannot be deleted.

    This action is permanent and cannot be undone.

    Examples:
        # Delete with confirmation
        hopx template delete template_abc123

        # Delete without confirmation
        hopx template delete template_abc123 --force
    """
    cli_ctx: CLIContext = ctx.obj

    # Confirm unless --force
    if not force:
        confirm = typer.confirm(f"Delete template {template_id}? This cannot be undone.")
        if not confirm:
            raise typer.Abort()

    with Spinner(f"Deleting template {template_id}...") as spinner:
        result = Sandbox.delete_template(
            template_id=template_id,
            api_key=cli_ctx.config.api_key,
            base_url=cli_ctx.config.base_url,
        )
        spinner.success(f"Template {template_id} deleted")

    if not cli_ctx.quiet:
        if cli_ctx.output_format == OutputFormat.JSON:
            console.print(result)
        else:
            console.print(f"[green]Template {template_id} deleted successfully[/green]")


@app.command("build")
@handle_errors
def build(
    ctx: typer.Context,
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Template name",
    ),
    dockerfile: str | None = typer.Option(
        None,
        "--dockerfile",
        help="Path to Dockerfile for building template",
    ),
    image: str | None = typer.Option(
        None,
        "--image",
        help="Base image (e.g., python:3.11, node:20)",
    ),
    context: str | None = typer.Option(
        None,
        "--context",
        help="Build context path (directory)",
    ),
    cpu: int = typer.Option(
        2,
        "--cpu",
        help="CPU cores",
    ),
    memory: int = typer.Option(
        2048,
        "--memory",
        help="Memory in MB",
    ),
    disk: int = typer.Option(
        10,
        "--disk",
        help="Disk size in GB",
    ),
    update: bool = typer.Option(
        False,
        "--update",
        help="Update existing template if exists",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Skip cache during build",
    ),
) -> None:
    """Build a custom template from Dockerfile or base image.

    You must provide either --dockerfile or --image (but not both).

    Examples:
        # Build from Dockerfile
        hopx template build --name my-app --dockerfile ./Dockerfile --context .

        # Build from base image
        hopx template build --name python-ml --image python:3.11

        # Update existing template
        hopx template build --name my-app --dockerfile ./Dockerfile --update

        # Build with custom resources
        hopx template build --name my-app --image node:20 --cpu 4 --memory 4096
    """
    cli_ctx: CLIContext = ctx.obj

    # Validation: must provide either dockerfile or image
    if not dockerfile and not image:
        console.print("[red]Error: Must provide either --dockerfile or --image[/red]")
        raise typer.Exit(code=1)

    if dockerfile and image:
        console.print("[red]Error: Cannot provide both --dockerfile and --image[/red]")
        raise typer.Exit(code=1)

    # Import Template builder (async)
    import asyncio

    from hopx_ai.template import BuildOptions, Template

    # Build template spec
    template_spec = Template()

    if image:
        # Parse image format (e.g., "python:3.11", "node:20")
        if "python" in image.lower():
            version = image.split(":")[-1] if ":" in image else "3.11"
            template_spec = template_spec.from_python_image(version)
        elif "node" in image.lower():
            version = image.split(":")[-1] if ":" in image else "20"
            template_spec = template_spec.from_node_image(version)
        else:
            # Generic image
            template_spec = template_spec.from_image(image)
    elif dockerfile:
        # Read and parse Dockerfile (simplified - just use from_image)
        dockerfile_path = Path(dockerfile)
        if not dockerfile_path.exists():
            console.print(f"[red]Error: Dockerfile not found: {dockerfile}[/red]")
            raise typer.Exit(code=1)

        # For now, we don't parse Dockerfile - user should use SDK directly
        # This is a limitation of the CLI vs programmatic API
        console.print("[yellow]Warning: Full Dockerfile parsing not yet supported in CLI.[/yellow]")
        console.print("[yellow]Consider using the Python SDK for complex builds.[/yellow]")
        console.print("[yellow]Example: See hopx-sdks/python/examples/template_build.py[/yellow]")
        raise typer.Exit(code=1)

    # Build options
    build_opts = BuildOptions(
        name=name,
        api_key=cli_ctx.config.api_key,
        base_url=cli_ctx.config.base_url,
        cpu=cpu,
        memory=memory,
        disk_gb=disk,
        skip_cache=no_cache,
        update=update,
        context_path=context,
    )

    # Track build progress with 4 stages
    import time

    logs_buffer = []
    build_stages = {
        "packaging": {"status": "pending", "detail": ""},
        "uploading": {"status": "pending", "detail": ""},
        "building": {"status": "pending", "detail": ""},
        "activating": {"status": "pending", "detail": ""},
    }
    current_stage = "packaging"

    def display_stages() -> None:
        """Display build stages with status."""
        stage_icons = {
            "pending": "[dim]○[/dim]",
            "running": "[cyan]⠋[/cyan]",
            "done": "[green]✓[/green]",
            "error": "[red]✗[/red]",
        }
        stage_names = {
            "packaging": "Packaging files",
            "uploading": "Uploading to registry",
            "building": "Building image",
            "activating": "Activating template",
        }

        console.print(f"\n[bold]Building template[/bold] [cyan]{name}[/cyan]\n")
        for stage, info in build_stages.items():
            icon = stage_icons.get(info["status"], "○")
            label = stage_names[stage]
            detail = f" [dim]{info['detail']}[/dim]" if info["detail"] else ""
            console.print(f"  {icon} {label}{detail}")
        console.print()

    def on_log(log_entry: dict[str, Any]) -> None:
        """Handle log entries during build."""
        nonlocal current_stage
        logs_buffer.append(log_entry)
        msg = log_entry.get("message", "").lower()

        # Update stage based on log message
        if "packaging" in msg or "tar" in msg or "compressing" in msg:
            if current_stage == "packaging":
                build_stages["packaging"]["status"] = "running"
        elif "upload" in msg or "sending" in msg:
            build_stages["packaging"]["status"] = "done"
            build_stages["uploading"]["status"] = "running"
            current_stage = "uploading"
        elif "build" in msg or "layer" in msg or "step" in msg:
            build_stages["uploading"]["status"] = "done"
            build_stages["building"]["status"] = "running"
            current_stage = "building"
            # Extract layer info if available
            if "layer" in msg:
                build_stages["building"]["detail"] = msg[:50]
        elif "activat" in msg or "publishing" in msg or "ready" in msg:
            build_stages["building"]["status"] = "done"
            build_stages["activating"]["status"] = "running"
            current_stage = "activating"

        if cli_ctx.verbose:
            console.print(f"[dim]{log_entry.get('message', '')}[/dim]")

    def on_progress(progress: int) -> None:
        """Handle progress updates during build."""
        # Update stage detail with progress
        if current_stage == "uploading":
            build_stages["uploading"]["detail"] = f"{progress}%"
        elif current_stage == "building":
            build_stages["building"]["detail"] = f"{progress}%"

        if cli_ctx.verbose:
            console.print(f"[cyan]Progress: {progress}%[/cyan]")

    build_opts.on_log = on_log
    build_opts.on_progress = on_progress

    # Run async build with staged progress
    async def run_build() -> BuildResult:
        # Start with packaging
        build_stages["packaging"]["status"] = "running"

        if not cli_ctx.quiet:
            display_stages()

        start_time = time.time()
        result = await Template.build(template_spec, build_opts)

        # Mark all stages complete
        for stage in build_stages:
            build_stages[stage]["status"] = "done"

        elapsed = int(time.time() - start_time)

        if not cli_ctx.quiet:
            console.print(f"[green]✓[/green] Template [cyan]{name}[/cyan] ready in {elapsed}s")

        return result

    try:
        result = asyncio.run(run_build())

        # Display result
        if not cli_ctx.quiet:
            if cli_ctx.output_format == OutputFormat.JSON:
                format_output(
                    {
                        "build_id": result.build_id,
                        "template_id": result.template_id,
                        "duration_ms": result.duration,
                    },
                    cli_ctx.output_format,
                )
            elif cli_ctx.output_format == OutputFormat.PLAIN:
                console.print(f"Template ID: {result.template_id}")
                console.print(f"Build ID: {result.build_id}")
                console.print(f"Duration: {result.duration}ms")
            else:
                table = Table(
                    title="Build Result",
                    show_header=False,
                    box=None,
                    padding=(0, 2),
                )
                table.add_column("Property", style="cyan bold")
                table.add_column("Value")

                table.add_row("Template ID", result.template_id)
                table.add_row("Build ID", result.build_id)
                table.add_row("Duration", f"{result.duration}ms")

                console.print(table)

                # Next steps suggestion
                console.print("\n[dim]Next steps:[/dim]")
                console.print(f"  hopx sandbox create --template {name}")
                console.print(f"  hopx template info {name}")

    except Exception as e:
        console.print(f"[red]Build failed: {e}[/red]")
        if cli_ctx.verbose and logs_buffer:
            console.print("\n[yellow]Build logs:[/yellow]")
            for log_entry in logs_buffer:
                console.print(f"  {log_entry.get('message', '')}")
        raise typer.Exit(code=1)
