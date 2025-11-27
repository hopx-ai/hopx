"""
Utility functions for sandbox operations.

This module contains pure utility functions for sandbox management.
These functions are shared between Sandbox and AsyncSandbox to reduce code duplication.
"""

from typing import Optional, Dict, Any
from ._utils import remove_none_values


def build_sandbox_create_payload(
    template: Optional[str],
    template_id: Optional[str],
    region: Optional[str],
    timeout_seconds: Optional[int],
    internet_access: Optional[bool],
    env_vars: Optional[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Build payload for POST /v1/sandboxes (sandbox creation).

    Validates that either template or template_id is provided.
    Removes None values to avoid sending unnecessary fields.

    Args:
        template: Template name (e.g., "code-interpreter", "base")
        template_id: Template ID (alternative to template name)
        region: Preferred region (optional)
        timeout_seconds: Auto-kill timeout in seconds (optional)
        internet_access: Enable internet access (optional)
        env_vars: Environment variables dict (optional)

    Returns:
        Request payload dict ready for JSON serialization

    Raises:
        ValueError: If neither template nor template_id is provided

    Example:
        >>> payload = build_sandbox_create_payload(
        ...     template="code-interpreter",
        ...     template_id=None,
        ...     region="us-east-1",
        ...     timeout_seconds=600,
        ...     internet_access=True,
        ...     env_vars={"DEBUG": "true"}
        ... )
        >>> payload["template_name"]
        'code-interpreter'
        >>> payload["timeout_seconds"]
        600
    """
    if template_id:
        # Create from template ID (resources auto-loaded from template)
        # Convert template_id to string if it's an int (API may return int from build)
        return remove_none_values(
            {
                "template_id": str(template_id),
                "region": region,
                "timeout_seconds": timeout_seconds,
                "internet_access": internet_access,
                "env_vars": env_vars,
            }
        )
    elif template:
        # Create from template name (resources auto-loaded from template)
        return remove_none_values(
            {
                "template_name": template,
                "region": region,
                "timeout_seconds": timeout_seconds,
                "internet_access": internet_access,
                "env_vars": env_vars,
            }
        )
    else:
        raise ValueError("Either 'template' or 'template_id' must be provided")


def build_list_sandboxes_params(
    status: Optional[str], region: Optional[str], limit: int = 100, cursor: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build query parameters for GET /v1/sandboxes (list sandboxes).

    Args:
        status: Filter by status (running, stopped, paused, creating)
        region: Filter by region
        limit: Maximum number of results (default: 100)
        cursor: Pagination cursor from previous response

    Returns:
        Query parameters dict

    Example:
        >>> params = build_list_sandboxes_params(
        ...     status="running",
        ...     region="us-east-1",
        ...     limit=50
        ... )
        >>> params["status"]
        'running'
        >>> params["limit"]
        50
    """
    params = remove_none_values(
        {
            "status": status,
            "region": region,
            "limit": limit,
            "cursor": cursor,
        }
    )
    return params


def build_list_templates_params(category: Optional[str], language: Optional[str]) -> Dict[str, Any]:
    """
    Build query parameters for GET /v1/templates (list templates).

    Args:
        category: Filter by category (development, infrastructure, operating-system)
        language: Filter by language (python, nodejs, etc.)

    Returns:
        Query parameters dict

    Example:
        >>> params = build_list_templates_params(
        ...     category="development",
        ...     language="python"
        ... )
        >>> params["category"]
        'development'
    """
    return remove_none_values(
        {
            "category": category,
            "language": language,
        }
    )


def build_set_timeout_payload(seconds: int) -> Dict[str, Any]:
    """
    Build payload for PUT /v1/sandboxes/{id}/timeout (set timeout).

    Args:
        seconds: Timeout duration in seconds

    Returns:
        Request payload dict

    Example:
        >>> payload = build_set_timeout_payload(600)
        >>> payload["timeout_seconds"]
        600
    """
    return {"timeout_seconds": seconds}
