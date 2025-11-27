"""Plain text output formatter.

Provides plain text output suitable for scripting, piping to other commands,
and machine parsing. No colors, no formatting, just raw values.
"""

from typing import Any

from pydantic import BaseModel


def format_plain(data: Any, field: str | None = None) -> str:
    """Format data as plain text output.

    Produces simple text output suitable for scripting and piping.
    For lists: one value per line. For dicts: key: value format.
    For Pydantic models: extracts specified field or formats all fields.

    Args:
        data: Data to format
        field: Specific field to extract from objects (e.g., "sandbox_id")

    Returns:
        Plain text string with newline-separated values

    Examples:
        >>> format_plain(["id1", "id2", "id3"])
        'id1\\nid2\\nid3'
        >>> format_plain({"name": "test", "value": 42})
        'name: test\\nvalue: 42'
        >>> format_plain([sandbox1, sandbox2], field="sandbox_id")
        'sb_123\\nsb_456'
    """
    # Handle None
    if data is None:
        return ""

    # Handle empty collections
    if not data and isinstance(data, (list, dict)):
        return ""

    # Handle list of items
    if isinstance(data, list):
        return _format_list(data, field)

    # Handle single Pydantic model
    if isinstance(data, BaseModel):
        return _format_model(data, field)

    # Handle dict
    if isinstance(data, dict):
        return _format_dict(data, field)

    # Handle primitive types
    return str(data)


def _format_list(items: list[Any], field: str | None = None) -> str:
    """Format list of items as plain text.

    Args:
        items: List of items to format
        field: Field to extract from each item

    Returns:
        Newline-separated values
    """
    if not items:
        return ""

    lines: list[str] = []

    for item in items:
        if field:
            # Extract specific field
            value = _extract_field(item, field)
            if value is not None:
                lines.append(str(value))
        elif isinstance(item, BaseModel):
            # Format model - use primary ID field
            id_field = _get_primary_id_field(item)
            if id_field:
                value = getattr(item, id_field, None)
                if value is not None:
                    lines.append(str(value))
            else:
                # No ID field - output all fields
                lines.append(_format_model(item, None))
        elif isinstance(item, dict):
            # Format dict - extract ID or format all
            id_value = item.get("id") or item.get("sandbox_id") or item.get("name")
            if id_value:
                lines.append(str(id_value))
            else:
                lines.append(_format_dict(item, None))
        else:
            # Primitive type
            lines.append(str(item))

    return "\n".join(lines)


def _format_model(model: BaseModel, field: str | None = None) -> str:
    """Format Pydantic model as plain text.

    Args:
        model: Pydantic model instance
        field: Specific field to extract

    Returns:
        Plain text representation
    """
    if field:
        value = getattr(model, field, None)
        return str(value) if value is not None else ""

    # Format all fields as key: value
    data = model.model_dump()
    return _format_dict(data, None)


def _format_dict(data: dict[str, Any], field: str | None = None) -> str:
    """Format dictionary as plain text.

    Args:
        data: Dictionary to format
        field: Specific field to extract

    Returns:
        Plain text representation
    """
    if field:
        value = data.get(field)
        return str(value) if value is not None else ""

    # Format as key: value pairs
    lines: list[str] = []
    for key, value in data.items():
        # Skip None values
        if value is None:
            continue

        # Format value
        if isinstance(value, (list, dict)):
            # Skip complex nested structures in plain output
            continue
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)


def _extract_field(obj: Any, field: str) -> Any:
    """Extract field value from object.

    Args:
        obj: Object (model, dict, or other)
        field: Field name to extract

    Returns:
        Field value or None
    """
    if isinstance(obj, BaseModel):
        return getattr(obj, field, None)
    elif isinstance(obj, dict):
        return obj.get(field)
    else:
        return getattr(obj, field, None)


def _get_primary_id_field(model: BaseModel) -> str | None:
    """Get the primary ID field name for a model.

    Args:
        model: Pydantic model instance

    Returns:
        Primary ID field name or None
    """
    # Common ID field names in priority order
    id_fields = ["sandbox_id", "id", "template_id", "name", "build_id"]

    for field in id_fields:
        if hasattr(model, field):
            return field

    return None
