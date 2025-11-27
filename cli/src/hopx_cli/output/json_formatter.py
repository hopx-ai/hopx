"""JSON output formatter.

Provides JSON serialization with support for Pydantic models,
datetime objects, and other Python types commonly used in the SDK.
"""

import base64
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel


def format_json(data: Any, indent: int = 2, compact: bool = False) -> str:
    """Format data as JSON string.

    Handles Pydantic models, datetime objects, bytes, and other types
    with custom serialization logic.

    Args:
        data: Data to serialize to JSON
        indent: Indentation level for pretty printing. Use None for compact.
        compact: If True, outputs compact JSON (overrides indent)

    Returns:
        JSON formatted string

    Examples:
        >>> model = SandboxInfo(...)
        >>> print(format_json(model))
        >>> print(format_json({"items": [1, 2, 3]}, compact=True))
    """
    if compact:
        indent = None

    # Handle single Pydantic model
    if isinstance(data, BaseModel):
        return data.model_dump_json(indent=indent)

    # Handle list of Pydantic models
    if isinstance(data, list) and data and isinstance(data[0], BaseModel):
        serialized = [item.model_dump() for item in data]
        return json.dumps(serialized, indent=indent, default=_json_serializer)

    # Handle dict or other types
    return json.dumps(data, indent=indent, default=_json_serializer)


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for non-standard types.

    Args:
        obj: Object to serialize

    Returns:
        Serializable representation

    Raises:
        TypeError: If object cannot be serialized
    """
    # Handle Pydantic models
    if isinstance(obj, BaseModel):
        return obj.model_dump()

    # Handle datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Handle bytes (base64 encode)
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("utf-8")

    # Handle sets
    if isinstance(obj, set):
        return list(obj)

    # Handle other types that have dict representation
    if hasattr(obj, "__dict__"):
        return obj.__dict__

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
