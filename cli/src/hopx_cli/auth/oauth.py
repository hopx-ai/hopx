"""
OAuth authentication flow for Hopx CLI.

Implements browser-based OAuth login with local callback server.
"""

import html
import http.server
import secrets
import socketserver
import threading
import time
import urllib.parse
import webbrowser
from typing import Any

import httpx

# WorkOS OAuth client ID for Hopx CLI
# This is a public client ID (not a secret) - it's sent to the browser during OAuth
CLI_CLIENT_ID = "client_01K8REAP8X81GX10ZGTZKNRFMT"

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hopx CLI - Authentication Successful</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 400px;
        }
        h1 {
            color: #2d3748;
            margin: 0 0 1rem 0;
            font-size: 1.75rem;
        }
        p {
            color: #4a5568;
            margin: 0.5rem 0;
            line-height: 1.6;
        }
        .checkmark {
            color: #48bb78;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">✓</div>
        <h1>Authentication Successful</h1>
        <p>You are now logged in to Hopx CLI.</p>
        <p>You can close this window and return to your terminal.</p>
    </div>
</body>
</html>
"""

ERROR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hopx CLI - Authentication Failed</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #f56565 0%, #c53030 100%);
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 400px;
        }
        h1 {
            color: #2d3748;
            margin: 0 0 1rem 0;
            font-size: 1.75rem;
        }
        p {
            color: #4a5568;
            margin: 0.5rem 0;
            line-height: 1.6;
        }
        .error-icon {
            color: #f56565;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .error-details {
            background: #fed7d7;
            color: #742a2a;
            padding: 1rem;
            border-radius: 6px;
            margin-top: 1rem;
            font-family: monospace;
            font-size: 0.875rem;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">✗</div>
        <h1>Authentication Failed</h1>
        <p>Could not complete the login process.</p>
        <p>Please try again or contact support.</p>
        {error_details}
    </div>
</body>
</html>
"""


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle OAuth callback from browser."""

    auth_code: str | None = None
    error: str | None = None
    expected_state: str | None = None
    _server_should_stop = False

    def do_GET(self) -> None:
        """Handle GET request from OAuth redirect."""
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        # Verify CSRF state parameter
        received_state = query.get("state", [None])[0]
        if received_state != OAuthCallbackHandler.expected_state:
            OAuthCallbackHandler.error = "Invalid state parameter (possible CSRF attack)"
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            error_html = ERROR_HTML.format(
                error_details='<div class="error-details">Security Error: Invalid state parameter</div>'
            )
            self.wfile.write(error_html.encode())
            OAuthCallbackHandler._server_should_stop = True
            return

        if "code" in query:
            OAuthCallbackHandler.auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(SUCCESS_HTML.encode())
        else:
            error = query.get("error", ["Unknown error"])[0]
            error_desc = query.get("error_description", ["No details provided"])[0]
            OAuthCallbackHandler.error = f"{error}: {error_desc}"

            # Escape HTML to prevent XSS
            safe_error = html.escape(error)
            safe_desc = html.escape(error_desc)
            error_html = ERROR_HTML.format(
                error_details=f'<div class="error-details">{safe_error}<br>{safe_desc}</div>'
            )

            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(error_html.encode())

        OAuthCallbackHandler._server_should_stop = True

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress server logs."""
        pass


ALLOWED_PROVIDERS = ["GoogleOAuth", "GitHubOAuth", "MicrosoftOAuth"]

# Fixed callback port registered with WorkOS
OAUTH_CALLBACK_PORT = 39123
OAUTH_CALLBACK_HOST = "127.0.0.1"


def browser_login_headless(provider: str = "GoogleOAuth") -> dict[str, Any]:
    """
    OAuth login for headless/server environments without a local browser.

    Flow:
    1. Display auth URL with QR code for easy mobile scanning
    2. User authenticates in browser (can be on any device)
    3. Browser redirects to localhost (connection refused - expected)
    4. User copies callback URL and pastes into CLI
    5. CLI validates and exchanges code for tokens

    Args:
        provider: OAuth provider (GoogleOAuth, GitHubOAuth, MicrosoftOAuth)

    Returns:
        Dictionary containing access_token, refresh_token, and expires_at

    Raises:
        ValueError: If provider is not allowed
        RuntimeError: If OAuth flow fails
    """
    from hopx_cli.auth.display import (
        prompt_callback_url,
        show_auth_url,
        show_headless_instructions,
        show_progress,
    )

    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(
            f"Invalid provider '{provider}'. Must be one of: {', '.join(ALLOWED_PROVIDERS)}"
        )

    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)
    redirect_uri = f"http://{OAUTH_CALLBACK_HOST}:{OAUTH_CALLBACK_PORT}/callback"

    auth_url = (
        f"https://api.workos.com/user_management/authorize?"
        f"client_id={CLI_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code&"
        f"provider={provider}&"
        f"state={state}"
    )

    # Display URL with QR code and clipboard
    show_auth_url(
        url=auth_url,
        title="Headless Login",
        show_qr=True,
        auto_copy=True,
    )

    # Instructions
    show_headless_instructions()

    # Get callback URL from user
    callback_url = prompt_callback_url()

    if not callback_url:
        raise RuntimeError("No callback URL provided")

    # Parse and validate
    code = _parse_callback_url(callback_url, state)

    # Exchange code for tokens with progress
    with show_progress("Exchanging tokens..."):
        return exchange_code_for_token(code, redirect_uri)


def _parse_callback_url(callback_url: str, expected_state: str) -> str:
    """Parse callback URL and extract authorization code.

    Args:
        callback_url: Full callback URL or just the code
        expected_state: Expected CSRF state parameter

    Returns:
        Authorization code

    Raises:
        RuntimeError: If validation fails
    """
    callback_url = callback_url.strip()

    # If it looks like just a code (alphanumeric, reasonable length)
    if not callback_url.startswith("http") and len(callback_url) > 10:
        # User pasted just the code - can't validate state
        return callback_url

    # Parse as URL
    try:
        parsed = urllib.parse.urlparse(callback_url)
        query = urllib.parse.parse_qs(parsed.query)
    except Exception as e:
        raise RuntimeError(f"Invalid URL format: {e}") from e

    # Validate state (CSRF protection)
    received_state = query.get("state", [None])[0]
    if received_state != expected_state:
        raise RuntimeError("Security error: state mismatch. Please start a new login.")

    # Check for OAuth errors
    if "error" in query:
        error = query.get("error", ["Unknown error"])[0]
        error_desc = query.get("error_description", ["No details"])[0]
        raise RuntimeError(f"OAuth error: {error} - {error_desc}")

    # Extract authorization code
    code = query.get("code", [None])[0]
    if not code:
        raise RuntimeError("No authorization code found. Copy the complete URL including ?code=...")

    return code


def browser_login(provider: str = "GoogleOAuth", timeout: int = 120) -> dict[str, Any]:
    """
    Open browser for OAuth login and return tokens.

    Flow:
    1. Start local HTTP server on fixed port (39123)
    2. Open browser to WorkOS OAuth URL with CSRF state
    3. Handle callback with authorization code
    4. Exchange code for tokens via Hopx backend
    5. Return access token and refresh token

    Args:
        provider: OAuth provider (GoogleOAuth, GitHubOAuth, MicrosoftOAuth)
        timeout: Maximum seconds to wait for callback (default: 120)

    Returns:
        Dictionary containing access_token, refresh_token, and expires_at

    Raises:
        ValueError: If provider is not allowed
        TimeoutError: If user does not complete login within timeout
        RuntimeError: If OAuth flow fails
    """
    # Validate provider to prevent URL manipulation
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(
            f"Invalid provider '{provider}'. Must be one of: {', '.join(ALLOWED_PROVIDERS)}"
        )

    # Reset handler state
    OAuthCallbackHandler.auth_code = None
    OAuthCallbackHandler.error = None
    OAuthCallbackHandler._server_should_stop = False

    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)
    OAuthCallbackHandler.expected_state = state

    # Use fixed port to match WorkOS callback configuration
    redirect_uri = f"http://{OAUTH_CALLBACK_HOST}:{OAUTH_CALLBACK_PORT}/callback"

    try:
        httpd = socketserver.TCPServer(
            (OAUTH_CALLBACK_HOST, OAUTH_CALLBACK_PORT), OAuthCallbackHandler
        )
    except OSError as e:
        raise RuntimeError(
            f"Cannot start OAuth callback server on port {OAUTH_CALLBACK_PORT}. "
            f"Port may be in use. Error: {e}"
        ) from e

    try:
        # Start server BEFORE opening browser to avoid race condition
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        auth_url = (
            f"https://api.workos.com/user_management/authorize?"
            f"client_id={CLI_CLIENT_ID}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"response_type=code&"
            f"provider={provider}&"
            f"state={state}"
        )

        from rich.console import Console

        console = Console()

        # Open browser first (responsive UX)
        console.print()
        console.print(f"Opening {provider.replace('OAuth', '')} authentication in your browser...")
        webbrowser.open(auth_url)

        # Show fallback URL (no QR code for browser flow - keep it clean)
        console.print()
        console.print("[dim]If the browser didn't open, visit:[/dim]")
        console.print(f"[dim]  {auth_url}[/dim]", highlight=False)
        console.print()

        start_time = time.time()
        while not OAuthCallbackHandler._server_should_stop:
            if time.time() - start_time > timeout:
                httpd.shutdown()
                raise TimeoutError(
                    f"Authentication timed out after {timeout} seconds. Please try again."
                )
            time.sleep(0.1)

        httpd.shutdown()
        server_thread.join(timeout=1)

        if OAuthCallbackHandler.error:
            raise RuntimeError(f"OAuth error: {OAuthCallbackHandler.error}")

        if not OAuthCallbackHandler.auth_code:
            raise RuntimeError("No authorization code received")

        return exchange_code_for_token(OAuthCallbackHandler.auth_code, redirect_uri)
    finally:
        httpd.server_close()


def exchange_code_for_token(code: str, redirect_uri: str) -> dict[str, Any]:
    """
    Exchange authorization code for access token via Hopx API.

    Args:
        code: Authorization code from OAuth provider
        redirect_uri: Redirect URI used in initial OAuth request

    Returns:
        Dictionary containing access_token, refresh_token, and expires_at

    Raises:
        RuntimeError: If token exchange fails
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.hopx.dev/auth/workos-callback",
                json={
                    "code": code,
                    "source": "cli",
                    "redirect_uri": redirect_uri,
                },
            )
            response.raise_for_status()
            data = response.json()

            if "access_token" not in data:
                raise RuntimeError("No access token in response")

            return {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token"),
                "expires_at": data.get("expires_at"),
            }
    except httpx.HTTPError as e:
        raise RuntimeError(f"Token exchange failed: {e}") from e


def refresh_oauth_token(refresh_token: str) -> dict[str, Any]:
    """
    Refresh expired OAuth access token.

    Args:
        refresh_token: Refresh token from initial login

    Returns:
        Dictionary containing new access_token and expires_at

    Raises:
        RuntimeError: If token refresh fails
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.hopx.dev/auth/refresh",
                json={"refresh_token": refresh_token},
            )
            response.raise_for_status()
            data = response.json()

            if "access_token" not in data:
                raise RuntimeError("No access token in refresh response")

            return {
                "access_token": data["access_token"],
                "expires_at": data.get("expires_at"),
            }
    except httpx.HTTPError as e:
        raise RuntimeError(f"Token refresh failed: {e}") from e
