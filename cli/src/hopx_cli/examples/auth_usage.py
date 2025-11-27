#!/usr/bin/env python3
"""
Example usage of Hopx CLI auth commands.

This script demonstrates the authentication commands available in the Hopx CLI.
It shows the expected output formats and command usage patterns.

NOTE: This is a documentation script showing command examples.
Run the actual commands via the CLI: hopx auth <command>
"""

import sys


def print_section(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main() -> None:
    """Print auth command examples."""
    print("\n╭─ Hopx CLI Authentication Examples ─╮")
    print("│                                     │")
    print("│  Run these commands in your shell  │")
    print("│                                     │")
    print("╰─────────────────────────────────────╯\n")

    print_section("1. OAuth Login (Recommended)")
    print("# Default: Google OAuth")
    print("$ hopx auth login\n")
    print("# Or use GitHub")
    print("$ hopx auth login --provider GitHubOAuth\n")
    print("Expected output:")
    print("  - Opens browser for authentication")
    print("  - Shows success message with token expiry")
    print("  - Stores credentials securely in system keyring")

    print_section("2. API Key Login")
    print("$ hopx auth login --api-key\n")
    print("Expected output:")
    print("  - Prompts for API key (password input)")
    print("  - Validates key format and API access")
    print("  - Stores key securely")

    print_section("3. Check Authentication Status")
    print("$ hopx auth status\n")
    print("Expected output when authenticated:")
    print("  ╭─ Authentication Status ─╮")
    print("  │ Profile:     default     │")
    print("  │ Method:      OAuth       │")
    print("  │ Expires:     2025-11-28  │")
    print("  │ Time left:   23h 45m     │")
    print("  │ Status:      ✓ Auth'd    │")
    print("  ╰─────────────────────────╯")

    print_section("4. Refresh OAuth Token")
    print("$ hopx auth refresh\n")
    print("Expected output:")
    print("  ✓ Token refreshed successfully")
    print("  New expiry: 2025-11-28 15:30:00 UTC")

    print_section("5. List API Keys (OAuth required)")
    print("$ hopx auth keys list\n")
    print("Expected output:")
    print("  ╭─ API Keys ──────────────────────────────────────╮")
    print("  │ ID           Name        Created      Expires   │")
    print("  │ NXAXAV4s     Production  2025-11-20   Never     │")
    print("  │ ABC123xy     Development 2025-11-25   2026-11   │")
    print("  ╰─────────────────────────────────────────────────╯")

    print_section("6. Create API Key (OAuth required)")
    print("# Create key without expiration")
    print("$ hopx auth keys create --name 'Production Server'\n")
    print("# Create key that expires in 1 year")
    print("$ hopx auth keys create --name 'CI/CD' --expires 1year\n")
    print("# Create and copy to clipboard")
    print("$ hopx auth keys create --name 'Dev' --copy\n")
    print("# Create and use as current credentials")
    print("$ hopx auth keys create --name 'Local' --use\n")
    print("Expected output:")
    print("  ╭─ API Key Created ───────────────────────╮")
    print("  │ Name:     Production Server             │")
    print("  │ Key ID:   NXAXAV4sU3Ii                  │")
    print("  │ Expires:  Never                         │")
    print("  │                                         │")
    print("  │ Warning: Copy this key now!             │")
    print("  │                                         │")
    print("  │ hopx_live_NXAXAV4sU3Ii.EXi3vR9kOJ...   │")
    print("  ╰─────────────────────────────────────────╯")

    print_section("7. Get API Key Info (OAuth required)")
    print("$ hopx auth keys info NXAXAV4sU3Ii\n")
    print("Expected output:")
    print("  ╭─ API Key: NXAXAV4sU3Ii ─╮")
    print("  │ ID:         NXAXAV4sU3Ii │")
    print("  │ Name:       Production   │")
    print("  │ Created:    2025-11-20   │")
    print("  │ Expires:    Never        │")
    print("  │ Last Used:  2 hours ago  │")
    print("  ╰──────────────────────────╯")

    print_section("8. Revoke API Key (OAuth required)")
    print("$ hopx auth keys revoke NXAXAV4sU3Ii\n")
    print("# Skip confirmation")
    print("$ hopx auth keys revoke NXAXAV4sU3Ii --force\n")
    print("Expected output:")
    print("  ✓ Revoked API key NXAXAV4sU3Ii")

    print_section("9. Logout")
    print("# Logout current profile")
    print("$ hopx auth logout\n")
    print("# Logout all profiles")
    print("$ hopx auth logout --all\n")
    print("Expected output:")
    print("  ✓ Cleared credentials for profile default")

    print_section("Multiple Profiles")
    print("# Use different profile")
    print("$ hopx --profile production auth login\n")
    print("$ hopx --profile production auth status\n")
    print("# Or use environment variable")
    print("$ export HOPX_PROFILE=production")
    print("$ hopx auth status\n")

    print_section("API Key Format")
    print("Valid API key format:")
    print("  hopx_live_<12 chars>.<base64url>\n")
    print("Examples:")
    print("  ✓ hopx_live_NXAXAV4sU3Ii.EXi3vR9kOJuhfbR5z42aFx5rhGjH1xnz")
    print("  ✓ hopx_live_ABC123xyz789.dGhpc2lzYXNlY3JldHRva2VuZm9ydGVzdA")
    print("  ✗ hopx_test_ABC123xyz789.token (wrong prefix)")
    print("  ✗ hopx_live_ABC.token (ID too short)")

    print("\n" + "=" * 70)
    print("  For more help: hopx auth --help")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
