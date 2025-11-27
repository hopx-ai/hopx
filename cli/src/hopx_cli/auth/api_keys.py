"""
API key management for Hopx CLI.

Provides interface to list, create, and revoke API keys (requires OAuth).
Matches console implementation exactly (api-client.ts lines 856-872).
"""

from typing import Any, Literal

import httpx

# Valid expiration options - must match API schema exactly
# From types.ts line 245: expires_in: "1month" | "3months" | "6months" | "1year" | "never"
ExpiresIn = Literal["1month", "3months", "6months", "1year", "never"]
EXPIRES_OPTIONS: list[str] = ["1month", "3months", "6months", "1year", "never"]


class APIKeyManager:
    """Manages API keys via Hopx API (requires OAuth authentication).

    Endpoints (from api-client.ts lines 856-872):
    - GET  /auth/api-keys        - List all keys
    - POST /auth/api-keys        - Create new key
    - DELETE /auth/api-keys/{id} - Revoke key
    """

    def __init__(self, oauth_token: str, base_url: str = "https://api.hopx.dev") -> None:
        """
        Initialize API key manager.

        Args:
            oauth_token: Valid OAuth access token (WorkOS Bearer token)
            base_url: Hopx API base URL (default: https://api.hopx.dev)
        """
        self.token = oauth_token
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {oauth_token}"},
            timeout=30.0,
        )

    def __enter__(self) -> "APIKeyManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close HTTP client."""
        self.close()

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()

    def list_keys(self) -> list[dict[str, Any]]:
        """
        List all API keys for the organization.

        Endpoint: GET /auth/api-keys (api-client.ts line 858)

        Returns:
            List of API key objects with id, key_id, name, status, masked_key,
            created_at, expires_at

        Response format (types.ts lines 237-241):
            {
                "success": true,
                "api_keys": [...],  # NOT "keys"!
                "count": 5
            }

        Raises:
            httpx.HTTPError: If request fails
            RuntimeError: If API returns success=false
        """
        response = self.client.get("/auth/api-keys")  # FIXED: /auth prefix
        response.raise_for_status()
        data = response.json()

        if not data.get("success", True):
            raise RuntimeError(data.get("message", "Failed to list API keys"))

        return data.get("api_keys", [])  # FIXED: api_keys not keys

    def create_key(self, name: str, expires_in: ExpiresIn = "never") -> dict[str, Any]:
        """
        Create a new API key. Returns full key value (only shown once).

        Endpoint: POST /auth/api-keys (api-client.ts lines 861-865)

        Args:
            name: Human-readable name for the key
            expires_in: Expiration enum - "1month", "3months", "6months", "1year", "never"
                       (NOT an ISO date string!)

        Returns:
            Dictionary with structure:
            {
                "full_key": "hopx_live_xxx.secret",  # The actual secret - ONLY returned once!
                "api_key": {...},                    # Key metadata
                "message": "API key created successfully"
            }

        Request format (types.ts lines 243-246):
            {"name": "my-key", "expires_in": "never"}

        Response format (types.ts lines 248-253):
            {
                "success": true,
                "message": "API key created successfully",
                "api_key": {...},
                "full_key": "hopx_live_xxx.actual_secret"
            }

        Raises:
            httpx.HTTPError: If request fails
            RuntimeError: If API returns success=false
        """
        # Validate expires_in
        if expires_in not in EXPIRES_OPTIONS:
            raise ValueError(
                f"Invalid expires_in: {expires_in}. Must be one of: {', '.join(EXPIRES_OPTIONS)}"
            )

        # FIXED: Use expires_in enum, not expires ISO date
        response = self.client.post(
            "/auth/api-keys",  # FIXED: /auth prefix
            json={"name": name, "expires_in": expires_in},
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success", True):
            raise RuntimeError(data.get("message", "Failed to create API key"))

        # FIXED: Return structured response with full_key and api_key
        return {
            "full_key": data.get("full_key"),  # The actual secret
            "api_key": data.get("api_key", {}),  # Key metadata
            "message": data.get("message"),
        }

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key by ID.

        Endpoint: DELETE /auth/api-keys/{keyId} (api-client.ts lines 868-871)

        Args:
            key_id: API key ID to revoke

        Returns:
            True if revocation successful

        Response format (types.ts lines 255-258):
            {"success": true, "message": "API key revoked successfully"}

        Raises:
            httpx.HTTPError: If request fails
        """
        response = self.client.delete(f"/auth/api-keys/{key_id}")  # FIXED: /auth prefix
        response.raise_for_status()
        data = response.json()
        return data.get("success", False)

    def get_key(self, key_id: str) -> dict[str, Any]:
        """
        Get details for a specific API key by ID.

        Endpoint: GET /auth/api-keys/{keyId}

        Args:
            key_id: API key ID to retrieve

        Returns:
            API key object with id, key_id, name, status, masked_key,
            created_at, expires_at

        Raises:
            httpx.HTTPError: If request fails
            RuntimeError: If API returns success=false
        """
        response = self.client.get(f"/auth/api-keys/{key_id}")
        response.raise_for_status()
        data = response.json()

        if not data.get("success", True):
            raise RuntimeError(data.get("message", "Failed to get API key"))

        return data.get("api_key", {})
