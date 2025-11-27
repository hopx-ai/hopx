"""
Pure parsing functions for Hopx SDK.

This module contains pure functions (no I/O) for parsing API responses.
These functions are shared between Sandbox and AsyncSandbox to reduce code duplication.

All functions in this module:
- Accept data structures as input
- Return data structures as output
- Perform no I/O operations
- Are safe to call from both sync and async contexts
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


def _parse_iso_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 timestamp string to datetime.

    Handles 'Z' suffix conversion to UTC timezone.
    Returns None for invalid/missing timestamps.

    Args:
        timestamp_str: ISO 8601 timestamp string (e.g., "2025-01-15T10:30:00Z")

    Returns:
        datetime object or None if parsing fails

    Example:
        >>> _parse_iso_timestamp("2025-01-15T10:30:00Z")
        datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        >>> _parse_iso_timestamp(None)
        None
        >>> _parse_iso_timestamp("invalid")
        None
    """
    if not timestamp_str:
        return None

    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError):
        return None


def _parse_sandbox_info_response(response: Dict[str, Any]) -> "SandboxInfo":
    """
    Parse /v1/sandboxes/{id} API response into SandboxInfo object.

    Pure data transformation - no I/O operations.
    Handles resource parsing, timestamp conversion, and field mapping.

    Args:
        response: Raw API response dictionary

    Returns:
        SandboxInfo object with parsed data

    Example:
        >>> response = {
        ...     "id": "sandbox_123",
        ...     "status": "running",
        ...     "public_host": "https://sandbox.hopx.dev",
        ...     "resources": {"vcpu": 2, "memory_mb": 4096, "disk_mb": 10240},
        ...     "created_at": "2025-01-15T10:30:00Z"
        ... }
        >>> info = _parse_sandbox_info_response(response)
        >>> info.sandbox_id
        'sandbox_123'
    """
    from .models import SandboxInfo, Resources

    # Parse resources if present
    resources = None
    if response.get("resources"):
        resources = Resources(
            vcpu=response["resources"]["vcpu"],
            memory_mb=response["resources"]["memory_mb"],
            disk_mb=response["resources"]["disk_mb"],
        )

    # Parse timestamps using utility function
    created_at = _parse_iso_timestamp(response.get("created_at"))
    expires_at = _parse_iso_timestamp(response.get("expires_at"))

    return SandboxInfo(
        sandbox_id=response["id"],
        template_id=response.get("template_id"),
        template_name=response.get("template_name"),
        organization_id=response.get("organization_id", 0),
        node_id=response.get("node_id"),
        region=response.get("region"),
        status=response["status"],
        public_host=response.get("public_host") or response.get("direct_url", ""),
        direct_url=response.get("direct_url"),
        preview_url=response.get("preview_url"),
        resources=resources,
        internet_access=response.get("internet_access"),
        live_mode=response.get("live_mode"),
        timeout_seconds=response.get("timeout_seconds"),
        expires_at=expires_at,
        created_at=created_at,
        # Legacy fields for backward compatibility
        started_at=None,
        end_at=expires_at,  # Map expires_at to end_at for backward compat
    )


def _parse_rich_outputs(data: Dict[str, Any]) -> List["RichOutput"]:
    """
    Parse rich outputs from code execution response.

    Extracts PNG images (matplotlib), HTML (pandas, plotly),
    JSON (plotly), and DataFrame outputs from execution results.

    Pure data transformation - no I/O operations.

    Args:
        data: Execution response data dictionary

    Returns:
        List of RichOutput objects

    Example:
        >>> data = {
        ...     "stdout": "Hello",
        ...     "png": "iVBORw0KGgoAAAANSUhEUgA...",  # base64 PNG
        ...     "html": "<table>...</table>"
        ... }
        >>> outputs = _parse_rich_outputs(data)
        >>> len(outputs)
        2
        >>> outputs[0].type
        'image/png'
    """
    from .models import RichOutput

    rich_outputs = []
    if not data or not isinstance(data, dict):
        return rich_outputs

    # Check for PNG (Matplotlib)
    if data.get("png"):
        rich_outputs.append(
            RichOutput(
                type="image/png", data={"image/png": data["png"]}, metadata=None, timestamp=None
            )
        )

    # Check for HTML (Pandas, Plotly)
    if data.get("html"):
        rich_outputs.append(
            RichOutput(
                type="text/html", data={"text/html": data["html"]}, metadata=None, timestamp=None
            )
        )

    # Check for JSON (Plotly)
    if data.get("json"):
        rich_outputs.append(
            RichOutput(
                type="application/json",
                data={"application/json": data["json"]},
                metadata=None,
                timestamp=None,
            )
        )

    # Check for DataFrame JSON
    if data.get("dataframe"):
        rich_outputs.append(
            RichOutput(
                type="application/vnd.dataframe+json",
                data={"application/vnd.dataframe+json": data["dataframe"]},
                metadata=None,
                timestamp=None,
            )
        )

    return rich_outputs


def _parse_template_response(response: Dict[str, Any]) -> "Template":
    """
    Parse /v1/templates/{name} API response into Template object.

    Simple wrapper that constructs Template from response dict.

    Args:
        response: Raw API response dictionary

    Returns:
        Template object

    Example:
        >>> response = {"name": "python", "display_name": "Python 3.11", ...}
        >>> template = _parse_template_response(response)
        >>> template.name
        'python'
    """
    from .models import Template

    return Template(**response)


def _parse_template_list_response(response: Dict[str, Any]) -> List["Template"]:
    """
    Parse /v1/templates API response into list of Template objects.

    Extracts "data" array from response and constructs Template objects.

    Args:
        response: Raw API response dictionary with "data" field

    Returns:
        List of Template objects

    Example:
        >>> response = {"data": [{"name": "python", ...}, {"name": "nodejs", ...}]}
        >>> templates = _parse_template_list_response(response)
        >>> len(templates)
        2
    """
    from .models import Template

    templates_data = response.get("data") or []
    return [Template(**t) for t in templates_data]
