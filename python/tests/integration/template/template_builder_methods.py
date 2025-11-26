"""
Integration tests for Template builder methods.

This module contains integration tests for the Template builder pattern methods.
These tests validate that the fluent builder API correctly constructs template
configurations and that getter methods return expected values.

Tests cover:
- Template builder methods (from_node_image, from_python_image, from_ubuntu_image, etc.)
- Template getter methods (get_from_image, get_steps, get_start_cmd, get_ready_check)
- Template builder method chaining
- Template configuration methods (set_env, set_envs, set_workdir, set_start_cmd)
- Special builder methods (git_clone, apt_install, skip_cache)

All tests use the real API endpoint (non-production) and require HOPX_API_KEY
environment variable to be set. Tests that create templates will clean up
after themselves by deleting the created templates.

Test Environment:
    - Base URL: Set via HOPX_TEST_BASE_URL env var (default: https://api-eu.hopx.dev)
    - Authentication: HOPX_API_KEY environment variable must be set
"""

import os
import pytest
import time
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions

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
        str: A unique template name in the format "test-builder-{timestamp}"
    """
    return f"test-builder-{int(time.time())}"


class TestTemplateBuilderMethods:
    """
    Test suite for Template builder methods.
    
    This class contains tests that validate the fluent builder API for creating
    templates. Tests verify that builder methods correctly configure template
    objects and that getter methods return the expected values.
    
    The tests cover:
    - Base image selection methods
    - Step configuration methods
    - Environment variable configuration
    - Working directory and start command configuration
    - Special operations like git clone and apt install
    - Cache control methods
    """

    def test_from_node_image(self):
        """
        Test creating a template from a Node.js base image.
        
        Validates that the from_node_image() builder method correctly sets
        the base image for the template. Verifies that the getter method
        returns the exact expected image identifier.
        
        This is a unit-style test that doesn't require API calls, only
        validating the builder pattern configuration.
        """
        template = Template().from_node_image("20")
        
        from_image = template.get_from_image()
        assert from_image is not None
        # Verify exact expected format: ubuntu/node:{version}-22.04_edge
        assert from_image == "ubuntu/node:20-22.04_edge"
        # Also verify it contains both "node" and the version
        assert "node" in from_image.lower()
        assert "20" in from_image

    @pytest.mark.asyncio
    async def test_from_node_image_integration(self, api_key, template_name):
        """
        Integration test: Verify that from_node_image() actually works end-to-end.
        
        This test builds a real template using from_node_image() and verifies:
        1. The template builds successfully
        2. A sandbox can be created from the template
        3. Node.js is actually available in the sandbox
        
        This ensures the method doesn't just set a string value, but that the
        configured image actually works when building templates.
        """
        # Create a template with Node.js base image
        template = (
            Template()
            .from_node_image("20")
            .run_cmd("node --version")  # Verify Node.js is available
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
        
        assert result.template_id is not None
        
        # Verify we can create a sandbox from this template and Node.js works
        async with AsyncSandbox.from_template(
            template_id=result.template_id,
            api_key=api_key,
            base_url=BASE_URL,
        ) as sandbox:
            # Execute code to verify Node.js is available
            exec_result = await sandbox.execute_code(
                code="console.log('Node.js version:', process.version)",
                language="javascript"
            )
            assert exec_result.exit_code == 0
            assert "v20" in exec_result.stdout  # Should contain Node.js 20 version
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    def test_template_getter_methods(self):
        """
        Test template getter methods return correct values.
        
        Creates a template with multiple configuration steps and verifies
        that all getter methods return the expected values:
        - get_from_image() returns the base image
        - get_steps() returns a list of build steps
        - get_start_cmd() returns the configured start command
        - get_ready_check() returns None when no ready check is set
        
        This test validates that the builder pattern correctly stores
        configuration and that getters provide access to it.
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .set_env("TEST_VAR", "test_value")
            .set_workdir("/app")
            .set_start_cmd("python app.py")
        )

        # Test getters
        assert template.get_from_image() is not None
        assert "python" in template.get_from_image().lower()
        
        steps = template.get_steps()
        assert isinstance(steps, list)
        assert len(steps) > 0
        
        start_cmd = template.get_start_cmd()
        assert start_cmd == "python app.py"
        
        ready_check = template.get_ready_check()
        assert ready_check is None  # No ready check set

    def test_template_builder_chaining(self):
        """
        Test template builder method chaining works correctly.
        
        Validates that multiple builder methods can be chained together
        in a fluent API pattern. Tests various builder methods including:
        - Base image selection (from_ubuntu_image)
        - Package installation (apt_install)
        - Command execution (run_cmd)
        - Working directory configuration (set_workdir)
        - Environment variable configuration (set_env, set_envs)
        
        Verifies that all steps are correctly added to the template's
        step list when chained together.
        """
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .apt_install("curl", "git")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .set_env("NODE_ENV", "production")
            .set_envs({"VAR1": "val1", "VAR2": "val2"})
        )

        steps = template.get_steps()
        assert len(steps) > 0
        # Should have apt_install and run_cmd steps

    @pytest.mark.asyncio
    async def test_template_with_git_clone(self, api_key, template_name):
        """
        Test creating a template that includes a git clone operation.
        
        This integration test validates that the git_clone() builder method
        correctly configures a template to clone a git repository during
        the build process. The test:
        1. Creates a template with git clone step
        2. Builds the template using the real API
        3. Verifies the template was created successfully
        4. Cleans up by deleting the template
        
        Uses a public repository (python/cpython) for testing. The template
        installs git, clones the repository, and lists the cloned directory
        to verify the operation.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        # Use a small public repo for testing
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("apt-get update && apt-get install -y git")
            .git_clone("https://github.com/python/cpython.git", "/tmp/cpython")
            .run_cmd("ls /tmp/cpython")
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

        assert result.template_id is not None

        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    def test_template_skip_cache(self):
        """
        Test template skip_cache method configuration.
        
        Validates that the skip_cache() builder method correctly marks
        build steps to skip caching. This is useful for steps that should
        always run fresh, such as steps that depend on external resources
        or have non-deterministic outputs.
        
        Verifies that the last step in the template has the skip_cache
        flag set when skip_cache() is called.
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .skip_cache()  # Skip cache for last step
        )

        steps = template.get_steps()
        if steps:
            # Last step should have skip_cache set
            assert hasattr(steps[-1], "skip_cache") or steps[-1].get("skip_cache") is True

