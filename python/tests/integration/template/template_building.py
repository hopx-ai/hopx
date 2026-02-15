"""
Integration tests for Template building operations.

This module contains integration tests for the template building workflow.
These tests validate the end-to-end process of creating, building, and using
custom templates with the HOPX API.

Tests cover:
- Creating templates from base images (Python, Ubuntu)
- Building templates with various configuration steps
- Creating sandboxes from custom templates
- Template build result validation (template_id, build_id, duration)
- Template lifecycle management (creation and cleanup)

All tests use the real API endpoint (non-production) and require HOPX_API_KEY
environment variable to be set. Tests that create templates will clean up
after themselves by deleting the created templates and any sandboxes created
from them.

Test Environment:
    - Base URL: Set via HOPX_TEST_BASE_URL env var (default: https://api-eu.hopx.dev)
    - Authentication: HOPX_API_KEY environment variable must be set
    - All created templates and sandboxes are cleaned up after tests complete
"""

import os
import pytest
import time
import logging
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions, wait_for_port

# Import cleanup registration functions
from tests.conftest import _register_template, _register_async_sandbox

# Import debugging utilities
try:
    from tests.integration.debug_utils import timed_operation, ProgressIndicator
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False
    # Fallback if debug_utils not available
    from contextlib import nullcontext as timed_operation
    ProgressIndicator = None

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")




@pytest.fixture
def template_name():
    """
    Pytest fixture generating unique template names for testing.
    
    Creates a unique template name by appending a timestamp to a base prefix.
    This ensures that each test run uses a unique template name, preventing
    conflicts when running tests in parallel or repeatedly.
    
    Returns:
        str: A unique template name in the format "test-template-{timestamp}"
    """
    return f"test-template-{int(time.time())}"


class TestTemplateBuilding:
    """
    Test suite for Template building operations.
    
    This class contains integration tests that validate the template building
    workflow. Tests cover creating templates from various base images,
    configuring them with build steps, and using them to create sandboxes.
    
    The tests validate:
    - Template creation with different base images
    - Template building with various configuration steps
    - Template build result properties (template_id, build_id, duration)
    - Creating sandboxes from custom templates
    - Proper cleanup of created resources
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(300)
    async def test_create_simple_template(self, api_key, template_name, cleanup_template):
        """
        Test creating a simple template with basic configuration.
        
        This test validates the basic template creation workflow:
        1. Creates a template from a Python base image
        2. Adds a build step to install a package
        3. Sets an environment variable
        4. Builds the template using the real API
        5. Validates the build result contains expected properties
        6. Cleans up by deleting the template
        
        The test verifies that:
        - The template is successfully built (template_id is not None)
        - The build process completes (build_id is not None)
        - The build takes measurable time (duration > 0)
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        # Define a simple template
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .set_env("TEST_VAR", "test_value")
        )

        result = None
        template_id = None
        try:
            # Build the template (this can take 1+ minutes)
            with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name):
                result = await Template.build(
                    template,
                    BuildOptions(
                        name=template_name,
                        api_key=api_key,
                        base_url=BASE_URL,
                        cpu=1,
                        memory=1024,
                        disk_gb=5,
                    ),
                )

            assert result.template_id is not None
            assert result.build_id is not None
            assert result.duration > 0

            # Register template for automatic cleanup (safety net)
            template_id = str(result.template_id)
            cleanup_template(template_id, api_key, BASE_URL)
        finally:
            # Always cleanup template, even if test fails
            if result and result.template_id:
                try:
                    await AsyncSandbox.delete_template(
                        template_id=result.template_id,
                        api_key=api_key,
                        base_url=BASE_URL,
                    )
                except Exception as e:
                    logger = logging.getLogger("hopx.test.cleanup")
                    logger.warning(f"Failed to cleanup template {template_id or result.template_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(300)
    async def test_create_template_with_start_cmd(self, api_key, template_name, cleanup_template):
        """
        Test creating template with start command and ready check.
        
        This test validates the complete workflow of creating a template with
        a start command and ready check, then using that template to create
        a sandbox. The test:
        1. Creates a template with an HTTP server start command
        2. Uses wait_for_port ready check to ensure the server is ready
        3. Builds the template using the real API
        4. Creates a sandbox from the built template
        5. Verifies the sandbox is running and ready
        6. Cleans up both the sandbox and template
        
        This test validates that templates with start commands and ready checks
        work correctly end-to-end, and that sandboxes created from such templates
        are properly initialized and ready to use.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        # Define template with start command
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > main.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Hello</h1>")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python main.py", wait_for_port(8000))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name):
            result = await Template.build(
                template,
                BuildOptions(
                    name=template_name,
                    api_key=api_key,
                    base_url=BASE_URL,
                    cpu=1,
                    memory=1024,
                    disk_gb=5,
                ),
            )

        # Register template for automatic cleanup immediately after creation
        template_id = str(result.template_id)
        cleanup_template(template_id, api_key, BASE_URL)
        
        try:
            assert result.template_id is not None

            # Create sandbox from template (can take 30+ seconds)
            # Use template_id from build result, not template name
            with timed_operation("AsyncSandbox.create", warn_threshold=30.0, template=template_name):
                async with AsyncSandbox.create(
                    template_id=result.template_id,
                    api_key=api_key,
                    base_url=BASE_URL,
                    timeout_seconds=120,  # Add timeout to prevent hanging
                ) as sandbox:
                    # Register sandbox for cleanup
                    _register_async_sandbox(sandbox)
                    
                    # Verify sandbox is running
                    info = await sandbox.get_info()
                    assert info.status == "running"
        finally:
            # Always cleanup template, even if test fails
            try:
                await AsyncSandbox.delete_template(
                    template_id=result.template_id,
                    api_key=api_key,
                    base_url=BASE_URL,
                )
            except Exception as e:
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup template {template_id}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.timeout(300)
    async def test_template_from_ubuntu(self, api_key, template_name, cleanup_template):
        """
        Test creating template from Ubuntu base image.
        
        This test validates that templates can be created from Ubuntu base
        images, not just language-specific images like Python. The test:
        1. Creates a template from Ubuntu 22.04 base image
        2. Adds build steps to update package lists and install packages
        3. Builds the template using the real API
        4. Validates the template is successfully created
        5. Cleans up by deleting the template
        
        This test is important for validating that the template system supports
        generic Linux distributions, not just pre-configured language images.
        This enables users to create templates with custom base environments.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .run_cmd("apt-get update")
            .run_cmd("apt-get install -y curl")
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name):
            result = await Template.build(
                template,
                BuildOptions(
                    name=template_name,
                    api_key=api_key,
                    base_url=BASE_URL,
                    cpu=1,
                    memory=1024,
                    disk_gb=5,
                ),
            )

        # Register template for automatic cleanup immediately after creation
        template_id = str(result.template_id)
        cleanup_template(template_id, api_key, BASE_URL)
        
        try:
            assert result.template_id is not None
        finally:
            # Always cleanup template, even if test fails
            try:
                await AsyncSandbox.delete_template(
                    template_id=result.template_id,
                    api_key=api_key,
                    base_url=BASE_URL,
                )
            except Exception as e:
                logger = logging.getLogger("hopx.test.cleanup")
                logger.warning(f"Failed to cleanup template {template_id}: {e}")

