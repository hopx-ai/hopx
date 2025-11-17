#!/usr/bin/env python3
"""
Environment Variables

Manage environment variables in sandboxes:
- Set env vars during sandbox creation
- Set/update env vars after creation
- Get individual and all env vars
- Per-request env var overrides
- Environment variable precedence
"""

from hopx_ai import Sandbox


def main():
    print("Environment Variables\n")

    # 1. Create sandbox with environment variables
    print("1. Creating sandbox with environment variables...")
    sandbox = Sandbox.create(
        template="code-interpreter",
        env_vars={
            "DATABASE_URL": "postgresql://localhost:5432/mydb",
            "API_KEY": "sk-prod-abc123xyz",
            "DEBUG": "true",
            "MAX_RETRIES": "3",
        },
    )
    print(f"Sandbox created: {sandbox.sandbox_id}\n")

    try:
        # 2. Verify env vars are available in code execution
        print("2. Verifying environment variables...")
        result = sandbox.run_code(
            """
import os

print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"API_KEY: {os.environ.get('API_KEY')[:10]}...")  # Mask sensitive data
print(f"DEBUG: {os.environ.get('DEBUG')}")
print(f"MAX_RETRIES: {os.environ.get('MAX_RETRIES')}")
""",
            language="python",
        )
        print(f"   Output:\n{result.stdout}")

        # 3. Get individual environment variable
        print("3. Getting individual environment variable...")
        debug_value = sandbox.env.get("DEBUG")
        print(f"   DEBUG = {debug_value}\n")

        # 4. Update environment variables
        print("4. Updating environment variables...")
        sandbox.env.update(
            {
                "DEBUG": "false",  # Change existing
                "LOG_LEVEL": "info",  # Add new
                "CACHE_ENABLED": "true",  # Add new
            }
        )
        print("   Environment variables updated\n")

        # 5. Verify updates
        print("5. Verifying updates...")
        result = sandbox.run_code(
            """
import os

print(f"DEBUG (updated): {os.environ.get('DEBUG')}")
print(f"LOG_LEVEL (new): {os.environ.get('LOG_LEVEL')}")
print(f"CACHE_ENABLED (new): {os.environ.get('CACHE_ENABLED')}")
""",
            language="python",
        )
        print(f"   Output:\n{result.stdout}")

        # 6. Get all environment variables
        print("6. Getting all environment variables...")
        all_vars = sandbox.env.get_all()
        print(f"   Found {len(all_vars)} environment variables")
        print("   Custom variables:")
        custom_vars = [
            "DATABASE_URL",
            "API_KEY",
            "DEBUG",
            "MAX_RETRIES",
            "LOG_LEVEL",
            "CACHE_ENABLED",
        ]
        for var in custom_vars:
            value = all_vars.get(var, "NOT SET")
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var or "PASSWORD" in var:
                value = "***MASKED***" if value != "NOT SET" else value
            print(f"      {var}: {value}")
        print()

        # 7. Per-request environment variable override
        print("7. Per-request environment variable override...")
        print("   Running code with request-specific env vars...")
        result = sandbox.run_code(
            """
import os

print(f"DEBUG (request override): {os.environ.get('DEBUG')}")
print(f"CUSTOM_VAR (request only): {os.environ.get('CUSTOM_VAR')}")
""",
            language="python",
            env={"DEBUG": "verbose", "CUSTOM_VAR": "request-specific"},
        )
        print(f"   Output:\n{result.stdout}")

        # 8. Verify sandbox-level env is unchanged
        print("8. Verifying sandbox-level env is unchanged...")
        result = sandbox.run_code(
            'import os; print(f"DEBUG: {os.environ.get(\'DEBUG\')}")',
            language="python",
        )
        print(f"   Output: {result.stdout.strip()}\n")

        # 9. Set individual environment variable
        print("9. Setting individual environment variable...")
        sandbox.env.set("FEATURE_FLAG_NEW_UI", "enabled")
        result = sandbox.run_code(
            'import os; print(os.environ.get("FEATURE_FLAG_NEW_UI"))',
            language="python",
        )
        print(f"   FEATURE_FLAG_NEW_UI = {result.stdout.strip()}\n")

        # 10. Delete environment variable
        print("10. Deleting environment variable...")
        sandbox.env.delete("CACHE_ENABLED")
        result = sandbox.run_code(
            'import os; print(os.environ.get("CACHE_ENABLED", "NOT SET"))',
            language="python",
        )
        print(f"   CACHE_ENABLED after deletion: {result.stdout.strip()}\n")

        # 11. Environment variables in commands
        print("11. Environment variables in shell commands...")
        result = sandbox.commands.run('echo "DEBUG=$DEBUG, LOG_LEVEL=$LOG_LEVEL"')
        print(f"   Command output: {result.stdout.strip()}\n")

        # 12. Command with request-specific env
        print("12. Command with request-specific env override...")
        result = sandbox.commands.run(
            'echo "TEMP_VAR=$TEMP_VAR"', env={"TEMP_VAR": "temporary-value"}
        )
        print(f"   Command output: {result.stdout.strip()}\n")

        print("Environment variable operations complete")

        print("\nEnvironment Variable Precedence (highest to lowest):")
        print("   1. Request-specific env (via run_code(..., env={...}))")
        print("   2. Sandbox-level env (via sandbox.env.set/update)")
        print("   3. Creation-time env (via Sandbox.create(env_vars={...}))")
        print("   4. Template/system default env")

    finally:
        # Cleanup
        print("\nCleaning up...")
        sandbox.kill()
        print("Sandbox destroyed")


if __name__ == "__main__":
    main()
