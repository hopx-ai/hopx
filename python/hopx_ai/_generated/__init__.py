"""
Auto-generated models from OpenAPI spec v3.1.2.

These models are automatically generated from the HOPX VM Agent API OpenAPI specification.
DO NOT EDIT MANUALLY - regenerate using scripts/generate_models.sh

All models are type-safe Pydantic v2 models with built-in validation.

Usage:
    from hopx_ai._generated import ExecuteRequest, ExecuteResponse
    
    request = ExecuteRequest(code="print('hello')", language="python")
    # Pydantic validates automatically!
"""

# Re-export all models from models.py
from .models import *

__all__ = [
    # Export everything from models
    # This is populated automatically from models.py
]
