#!/usr/bin/env python3
"""Example demonstrating core module usage.

This example shows how to use the core utilities in CLI commands:
- Configuration loading
- Context management
- Error handling
- SDK integration
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hopx_cli.core import (
    CLIConfig,
    CLIContext,
    CLIError,
    OutputFormat,
    get_sandbox,
    run_async,
)


def example_config():
    """Example: Configuration management."""
    print("=" * 60)
    print("1. Configuration Management")
    print("=" * 60)

    # Create config with defaults
    config = CLIConfig()
    print("\nDefault configuration:")
    print(f"  Base URL: {config.base_url}")
    print(f"  Default template: {config.default_template}")
    print(f"  Default timeout: {config.default_timeout}s")
    print(f"  Output format: {config.output_format}")
    print(f"  Profile: {config.profile}")

    # Set API key (normally from env var)
    if not config.api_key:
        print("\n  API key: Not set (set HOPX_API_KEY environment variable)")
    else:
        print(f"\n  API key: {config.api_key[:20]}...")


def example_context():
    """Example: CLI context."""
    print("\n" + "=" * 60)
    print("2. CLI Context")
    print("=" * 60)

    config = CLIConfig()
    ctx = CLIContext(
        config=config,
        output_format=OutputFormat.TABLE,
        verbose=True,
        quiet=False,
    )

    print("\nContext settings:")
    print(f"  Output format: {ctx.output_format.value}")
    print(f"  Verbose: {ctx.verbose}")
    print(f"  Quiet: {ctx.quiet}")

    # Check output format
    if ctx.is_table_output():
        print("  Format check: Table output enabled")

    # Runtime state
    ctx.set_state("example_key", "example_value")
    value = ctx.get_state("example_key")
    print(f"  Runtime state: {value}")


def example_errors():
    """Example: Error handling."""
    print("\n" + "=" * 60)
    print("3. Error Handling")
    print("=" * 60)

    # Example 1: Manual error handling
    try:
        raise CLIError(
            "Example error occurred",
            suggestion="This is how you would fix it",
        )
    except CLIError as e:
        print("\nCaught CLIError:")
        print(f"  Message: {e.message}")
        print(f"  Suggestion: {e.suggestion}")
        print(f"  Exit code: {e.exit_code}")

    # Example 2: Using decorator (would exit on error in real command)
    print("\nError decorator example:")
    print("  Use @handle_errors on CLI command functions")
    print("  SDK errors are automatically caught and mapped")
    print("  User-friendly error messages with suggestions")


def example_sdk_integration():
    """Example: SDK integration."""
    print("\n" + "=" * 60)
    print("4. SDK Integration")
    print("=" * 60)

    config = CLIConfig()

    print("\nSDK client functions:")
    print("  get_sandbox(config) - Get sync sandbox client")
    print("  get_async_sandbox(config) - Get async sandbox client")
    print("  clear_sandbox_cache() - Clear cached instances")

    # Only create client if API key is set
    if config.api_key:
        print("\n  Creating sandbox client...")
        try:
            _sandbox = get_sandbox(config)
            print("  ✓ Sandbox client created")
            print(f"    Base URL: {config.base_url}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print("\n  Skipping client creation (API key not set)")


@run_async
async def example_async():
    """Example: Async helpers."""
    import asyncio

    print("\n" + "=" * 60)
    print("5. Async Helpers")
    print("=" * 60)

    print("\n@run_async decorator allows async functions in sync code")

    # Simulate async work
    await asyncio.sleep(0.1)
    print("  ✓ Async operation completed")


def example_full_command():
    """Example: Full CLI command implementation."""
    print("\n" + "=" * 60)
    print("6. Full CLI Command Example")
    print("=" * 60)

    print("""
Example command implementation:

@handle_errors
def sandbox_create(
    template: str,
    verbose: bool = False,
    output_format: str = "table"
):
    '''Create a new sandbox.'''
    # Load configuration
    config = CLIConfig.load()

    # Create context
    ctx = CLIContext(
        config=config,
        output_format=OutputFormat(output_format),
        verbose=verbose
    )

    # Get sandbox client
    sandbox = get_sandbox(ctx.config)

    # Create sandbox
    new_sandbox = sandbox.create(template=template)

    # Output based on format
    if ctx.is_json_output():
        print(json.dumps({"id": new_sandbox.sandbox_id}))
    else:
        print(f"Created sandbox: {new_sandbox.sandbox_id}")

    return 0
""")


def main():
    """Run all examples."""
    print("\nHOPX CLI CORE MODULE USAGE EXAMPLES\n")

    examples = [
        example_config,
        example_context,
        example_errors,
        example_sdk_integration,
        example_async,
        example_full_command,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in example: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - /home/ubuntu/bns/hopx-sdks/python/hopx_cli/core/README.md")
    print("  - Individual module docstrings")
    print()


if __name__ == "__main__":
    main()
