#!/usr/bin/env python3
"""
Ollama Template Example

Build a custom template with Ollama and a small language model.

Steps:
1. Build template with Python 3.13 and Ollama
2. Pull smollm language model
3. Create sandbox from template
4. Save sandbox ID for reuse
5. Run commands in sandbox

Template building takes 5-10 minutes on first run.
Subsequent runs reuse the saved sandbox.
"""

import os
import asyncio
import time

from hopx_ai import Sandbox, Template, __version__
from hopx_ai.template.types import BuildOptions, BuildResult

# Configuration
OLLAMA_MODEL = "smollm"  # Small model for faster testing
HOPX_TEMPLATE_NAME = f"ollama-example-{int(time.time())}"
SANDBOX_ID_FILE = ".hopx_ollama_sandbox_id"


def create_ollama_template() -> Template:
    """
    Create a template with Ollama installed.

    Returns a template configured with:
    - Python 3.13 base image
    - Workspace directory
    - Ollama installation
    - smollm language model
    - Environment variables for operation
    """
    return (
        Template()
        .from_python_image("3.13")

        # Wait for VM agent to be fully ready
        .run_cmd("sleep 3")

        # Create workspace directory
        .run_cmd("mkdir -p /workspace")
        .run_cmd("sleep 3")

        # Set environment variables
        .set_env("LANG", "en_US.UTF-8")
        .set_env("LC_ALL", "en_US.UTF-8")
        .set_env("PYTHONUNBUFFERED", "1")
        .set_env("HOME", "/workspace")

        # Install Ollama
        .run_cmd("curl -fsSL https://ollama.com/install.sh | sh")
        .run_cmd("sleep 3")  # Wait for ollama installation

        # Pull the model (this will be baked into the template)
        .run_cmd(f"/usr/local/bin/ollama pull {OLLAMA_MODEL}")

        # Set working directory
        .set_workdir("/workspace")
    )


def create_build_options(api_key: str) -> BuildOptions:
    """Configure template build options with logging."""
    return BuildOptions(
        name=HOPX_TEMPLATE_NAME,
        api_key=api_key,
        base_url=os.environ.get("HOPX_BASE_URL", "https://api.hopx.dev"),
        cpu=2,
        memory=2048,
        disk_gb=20,
        on_log=lambda log: print(f"  [{log.get('level', 'INFO')}] {log.get('message', '')}"),
        on_progress=lambda p: print(f"  Progress: {p}%"),
    )


async def build_ollama_template_and_create_sandbox(api_key: str) -> Sandbox:
    """Build the Ollama template and create a sandbox from it."""
    print("Building Ollama template (takes 5-10 minutes)...")
    print(f"   Template name: {HOPX_TEMPLATE_NAME}")
    print()

    template = create_ollama_template()
    build_options = create_build_options(api_key)

    # Build the template
    result: BuildResult = await Template.build(template, build_options)

    print()
    print(f"Template built")
    print(f"   Template ID: {result.template_id}")
    print(f"   Build ID: {result.build_id}")
    print(f"   Duration: {result.duration}ms")
    print()

    # Create sandbox from the template
    print("Creating sandbox from template...")
    sandbox = Sandbox.create(
        template=HOPX_TEMPLATE_NAME,
        api_key=api_key
    )

    # Save sandbox ID for reuse
    with open(SANDBOX_ID_FILE, "w") as f:
        f.write(sandbox.sandbox_id)

    print(f"Sandbox created: {sandbox.sandbox_id}")
    print(f"   Saved ID to: {SANDBOX_ID_FILE}")
    print()

    return sandbox


async def get_or_create_sandbox() -> Sandbox:
    """
    Get existing sandbox or create new one.

    Returns existing sandbox if ID file exists, otherwise builds new template
    and creates sandbox. Saves sandbox ID for future reuse.
    """
    api_key = os.environ.get("HOPX_API_KEY", "")
    if not api_key:
        raise ValueError("HOPX_API_KEY environment variable not set")

    # Check if we have a saved sandbox ID
    if os.path.exists(SANDBOX_ID_FILE):
        with open(SANDBOX_ID_FILE, "r") as f:
            sandbox_id = f.read().strip()

        print(f"Found existing sandbox ID: {sandbox_id}")
        print("   Connecting to existing sandbox...")

        try:
            sandbox = Sandbox.connect(sandbox_id, api_key=api_key)
            info = sandbox.get_info()
            print(f"Connected to sandbox: {sandbox.sandbox_id}")
            print(f"   Status: {info.status}")
            return sandbox
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("   Building new sandbox...")

    # No saved sandbox or connection failed - build new one
    print("No existing sandbox found")
    return await build_ollama_template_and_create_sandbox(api_key)


async def main():
    print("=" * 70)
    print("Ollama Template Example")
    print("=" * 70)
    print(f"HopX SDK version: {__version__}")
    print()

    # Get or create sandbox
    start_time = time.time()
    sandbox = await get_or_create_sandbox()
    duration = time.time() - start_time
    print(f"Sandbox ready in {duration:.2f} seconds")
    print()

    # Test 1: Simple command
    print("Step 1: Running simple command...")
    result = sandbox.commands.run("uname -a", timeout=30)
    print(f"   Output: {result.stdout.strip()}")
    print(f"   Test 1 passed")
    print()

    # Test 2: Check Ollama installation
    print("Step 2: Verifying Ollama installation...")
    result = sandbox.commands.run("/usr/local/bin/ollama --version", timeout=30)
    print(f"   {result.stdout.strip()}")
    print(f"   Test 2 passed")
    print()

    # Test 3: List available models
    print("Step 3: Listing Ollama models...")
    result = sandbox.commands.run("/usr/local/bin/ollama list", timeout=30)
    print(f"   Available models:")
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            print(f"      {line}")
    print(f"   Test 3 passed")
    print()

    # Test 4: Run Ollama model
    print(f"Step 4: Running Ollama model '{OLLAMA_MODEL}'...")
    prompt = "Say hello to the HopX AI team in one sentence!"
    print(f"   Prompt: {prompt}")
    print(f"   Running (takes 30-60 seconds)...")

    start_time = time.time()
    result = sandbox.commands.run(
        f"/usr/local/bin/ollama run {OLLAMA_MODEL} '{prompt}'",
        timeout=240
    )
    duration = time.time() - start_time

    print(f"   Response ({duration:.1f}s):")
    print(f"   {result.stdout.strip()}")
    print(f"   Test 4 passed")
    print()

    print("=" * 70)
    print("All tests completed")
    print("=" * 70)
    print()
    print("Tips:")
    print(f"   - Sandbox ID saved to: {SANDBOX_ID_FILE}")
    print(f"   - Rerun this script to reuse the same sandbox")
    print(f"   - Delete {SANDBOX_ID_FILE} to build a new template")
    print(f"   - Run: sandbox.kill() to destroy the sandbox")


if __name__ == "__main__":
    asyncio.run(main())
