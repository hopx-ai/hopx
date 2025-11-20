"""
Integration tests for Template operations.

Tests cover:
- Listing available templates
- Filtering templates by category/language
- Getting template details
- Error handling for non-existent templates
"""

import os
import pytest
from hopx_ai import Sandbox
from hopx_ai.errors import NotFoundError

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


class TestTemplateOperations:
    """Test template-related operations."""

    def test_list_templates(self, api_key):
        """Test listing available templates."""
        templates = Sandbox.list_templates(
            api_key=api_key,
            base_url=BASE_URL,
        )

        assert isinstance(templates, list)
        assert len(templates) > 0

        for template in templates:
            assert template.name is not None
            assert template.display_name is not None

    def test_list_templates_with_filter(self, api_key):
        """Test listing templates with category/language filter."""
        templates = Sandbox.list_templates(
            language="python",
            api_key=api_key,
            base_url=BASE_URL,
        )

        assert isinstance(templates, list)
        # At least one Python template should exist
        python_templates = [
            t for t in templates 
            if t.language and ("python" in t.name.lower() or "python" in t.language.lower())
        ]
        assert len(python_templates) > 0

    def test_get_template(self, api_key):
        """Test getting template details."""
        template = Sandbox.get_template(
            name=TEST_TEMPLATE,
            api_key=api_key,
            base_url=BASE_URL,
        )

        assert template.name == TEST_TEMPLATE
        assert template.display_name is not None
        if template.default_resources:
            assert template.default_resources.vcpu > 0
            assert template.default_resources.memory_mb > 0

    def test_get_nonexistent_template(self, api_key):
        """Test getting non-existent template raises error."""
        with pytest.raises(NotFoundError):
            Sandbox.get_template(
                name="nonexistent-template-12345",
                api_key=api_key,
                base_url=BASE_URL,
            )


class TestHealthCheck:
    """Test health check operations."""

    def test_health_check(self):
        """Test API health check."""
        health = Sandbox.health_check(base_url=BASE_URL)

        assert isinstance(health, dict)
        assert "status" in health or "ok" in str(health).lower()

