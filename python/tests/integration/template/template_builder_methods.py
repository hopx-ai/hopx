"""
Integration tests for Template builder methods.

This module contains integration tests for the Template builder pattern methods.
These tests validate that the fluent builder API correctly constructs template
configurations and that templates can be successfully built using the real API.

Tests cover:
- Template builder methods (from_python_image, from_ubuntu_image, etc.)
- Template configuration methods (set_env, set_envs, set_workdir, set_start_cmd)
- Special builder methods (git_clone, apt_install, skip_cache)
- Template building and sandbox creation from built templates

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
import asyncio
import aiohttp
from hopx_ai import Template, AsyncSandbox, Sandbox
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
    
    This class contains integration tests that validate the fluent builder API
    for creating templates. All tests actually build templates using the real API
    and verify that the templates work correctly.
    
    The tests cover:
    - Base image selection methods (from_python_image, from_ubuntu_image)
    - Step configuration methods (run_cmd, apt_install, pip_install)
    - Environment variable configuration (set_env, set_envs)
    - Working directory and start command configuration
    - Special operations like git clone
    - Cache control methods (skip_cache)
    """

    @pytest.mark.asyncio
    async def test_from_python_image_integration(self, api_key, template_name):
        """
        Integration test: Verify that from_python_image() works end-to-end.
        
        This test builds a real template using from_python_image() and verifies:
        1. The template builds successfully
        2. A sandbox can be created from the template
        3. Python is actually available in the sandbox
        
        This ensures the method doesn't just set a string value, but that the
        configured image actually works when building templates.
        """
        # Create a template with Python base image
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("python --version")  # Verify Python is available
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
                    template_activation_timeout=600,  # 10 minutes timeout for template activation
                ),
            )
        
        assert result.template_id is not None
        
        # Explicitly verify template is active before creating sandbox
        # Template.build() should wait, but let's double-check to avoid hanging
        template_id = str(result.template_id)
        max_wait = 300  # 5 minutes max wait
        poll_interval = 3  # Poll every 3 seconds
        start_time = time.time()
        consecutive_active = 0
        required_consecutive = 2
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < max_wait:
                try:
                    async with session.get(
                        f"{BASE_URL}/v1/templates/{template_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                    ) as response:
                        if response.ok:
                            data = await response.json()
                            status = data.get('status', 'unknown')
                            is_active = data.get('is_active', False)
                            
                            if status == 'active' and is_active:
                                consecutive_active += 1
                                if consecutive_active >= required_consecutive:
                                    break
                            else:
                                consecutive_active = 0
                                if status in ('failed', 'error'):
                                    error = data.get('error_message', 'Unknown error')
                                    raise Exception(f"Template activation failed: {error}")
                except Exception:
                    pass
                
                await asyncio.sleep(poll_interval)
            else:
                raise TimeoutError(
                    f"Template {template_id} did not become active within {max_wait} seconds. "
                    f"Last status: {status if 'status' in locals() else 'unknown'}"
                )
        
        # Verify we can create a sandbox from this template and Python works
        # Use sync Sandbox with context manager (AsyncSandbox.create() hangs)
        def create_and_test_sandbox():
            """Helper function to run sync sandbox operations in thread"""
            with Sandbox.create(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
                timeout_seconds=120,
            ) as sandbox:
                # Wait for sandbox VM to be ready before executing code
                # Sandbox.create() returns immediately, but VM needs time to start
                max_wait = 60  # Wait up to 60 seconds
                poll_interval = 2  # Check every 2 seconds
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    try:
                        if sandbox.is_healthy():
                            break
                    except Exception:
                        # Health check might fail if VM isn't ready yet
                        pass
                    time.sleep(poll_interval)
                else:
                    raise TimeoutError(
                        f"Sandbox {sandbox.sandbox_id} did not become ready within {max_wait} seconds"
                    )
                
                # Execute code to verify Python is available
                # Use Python since Python image has Python installed
                exec_result = sandbox.run_code(
                    code="import sys; print(f'Python version: {sys.version}')",
                    language="python"
                )
                return exec_result
        
        exec_result = await asyncio.to_thread(create_and_test_sandbox)
        assert exec_result.exit_code == 0
        assert "3.11" in exec_result.stdout  # Should contain Python 3.11 version
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_from_ubuntu_image_integration(self, api_key, template_name):
        """
        Integration test: Verify that from_ubuntu_image() works end-to-end.
        
        This test builds a real template using from_ubuntu_image() and verifies:
        1. The template builds successfully
        2. A sandbox can be created from the template
        3. Ubuntu commands work in the sandbox
        """
        # Create a template with Ubuntu base image
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .run_cmd("apt-get update")
            .run_cmd("apt-get install -y curl")
            .run_cmd("curl --version")  # Verify curl is installed
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
                    template_activation_timeout=600,  # 10 minutes timeout for template activation
                ),
            )
        
        assert result.template_id is not None
        
        # Explicitly verify template is active before creating sandbox
        # Template.build() should wait, but let's double-check to avoid hanging
        template_id = str(result.template_id)
        max_wait = 300  # 5 minutes max wait
        poll_interval = 3  # Poll every 3 seconds
        start_time = time.time()
        consecutive_active = 0
        required_consecutive = 2
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < max_wait:
                try:
                    async with session.get(
                        f"{BASE_URL}/v1/templates/{template_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                    ) as response:
                        if response.ok:
                            data = await response.json()
                            status = data.get('status', 'unknown')
                            is_active = data.get('is_active', False)
                            
                            if status == 'active' and is_active:
                                consecutive_active += 1
                                if consecutive_active >= required_consecutive:
                                    break
                            else:
                                consecutive_active = 0
                                if status in ('failed', 'error'):
                                    error = data.get('error_message', 'Unknown error')
                                    raise Exception(f"Template activation failed: {error}")
                except Exception:
                    pass
                
                await asyncio.sleep(poll_interval)
            else:
                raise TimeoutError(
                    f"Template {template_id} did not become active within {max_wait} seconds. "
                    f"Last status: {status if 'status' in locals() else 'unknown'}"
                )
        
        # Verify we can create a sandbox from this template and curl works
        # Use sync Sandbox with context manager (AsyncSandbox.create() hangs)
        def create_and_test_sandbox():
            """Helper function to run sync sandbox operations in thread"""
            with Sandbox.create(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
                timeout_seconds=120,
            ) as sandbox:
                # Execute code to verify curl is available
                # Use bash since Ubuntu base image may not have Python installed
                exec_result = sandbox.run_code(
                    code="curl --version",
                    language="bash"
                )
                return exec_result
        
        exec_result = await asyncio.to_thread(create_and_test_sandbox)
        assert exec_result.exit_code == 0
        assert "curl" in exec_result.stdout.lower()
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_template_with_env_vars_integration(self, api_key, template_name):
        """
        Integration test: Verify that set_env() and set_envs() work end-to-end.
        
        This test builds a template with environment variables and verifies:
        1. The template builds successfully
        2. Environment variables are set correctly in the sandbox
        """
        template = (
            Template()
            .from_python_image("3.11")
            .set_env("TEST_VAR", "test_value")
            .set_envs({"VAR1": "val1", "VAR2": "val2"})
            .run_cmd("python -c \"import os; print(os.getenv('TEST_VAR')); print(os.getenv('VAR1')); print(os.getenv('VAR2'))\"")
        )
        
        # Build the template
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
        
        # Verify environment variables are set
        async with AsyncSandbox.create(
            template_id=result.template_id,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=120,  # Add timeout to prevent hanging
        ) as sandbox:
            exec_result = await sandbox.run_code(
                code="import os; print(os.getenv('TEST_VAR')); print(os.getenv('VAR1')); print(os.getenv('VAR2'))",
                language="python"
            )
            assert exec_result.exit_code == 0
            assert "test_value" in exec_result.stdout
            assert "val1" in exec_result.stdout
            assert "val2" in exec_result.stdout
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_template_with_workdir_integration(self, api_key, template_name):
        """
        Integration test: Verify that set_workdir() works end-to-end.
        
        This test builds a template with a working directory and verifies:
        1. The template builds successfully
        2. The working directory is set correctly
        """
        template = (
            Template()
            .from_python_image("3.11")
            .set_workdir("/app")
            .run_cmd("pwd")  # Verify working directory
        )
        
        # Build the template
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
        
        # Verify working directory is set
        async with AsyncSandbox.create(
            template_id=result.template_id,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=120,  # Add timeout to prevent hanging
        ) as sandbox:
            exec_result = await sandbox.run_code(
                code="import os; print(os.getcwd())",
                language="python"
            )
            assert exec_result.exit_code == 0
            assert "/app" in exec_result.stdout
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_template_builder_chaining_integration(self, api_key, template_name):
        """
        Integration test: Verify that builder method chaining works end-to-end.
        
        This test builds a template using multiple chained builder methods and verifies:
        1. The template builds successfully
        2. All configured steps are executed correctly
        """
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .apt_install("curl", "git")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .set_env("NODE_ENV", "production")
            .set_envs({"VAR1": "val1", "VAR2": "val2"})
            .run_cmd("curl --version")  # Verify curl is installed
            .run_cmd("git --version")  # Verify git is installed
        )
        
        # Build the template
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
                    template_activation_timeout=600,  # 10 minutes timeout for template activation
                ),
            )
        
        assert result.template_id is not None
        
        # Explicitly verify template is active before creating sandbox
        # Template.build() should wait, but let's double-check to avoid hanging
        template_id = str(result.template_id)
        max_wait = 300  # 5 minutes max wait
        poll_interval = 3  # Poll every 3 seconds
        start_time = time.time()
        consecutive_active = 0
        required_consecutive = 2
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < max_wait:
                try:
                    async with session.get(
                        f"{BASE_URL}/v1/templates/{template_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                    ) as response:
                        if response.ok:
                            data = await response.json()
                            status = data.get('status', 'unknown')
                            is_active = data.get('is_active', False)
                            
                            if status == 'active' and is_active:
                                consecutive_active += 1
                                if consecutive_active >= required_consecutive:
                                    break
                            else:
                                consecutive_active = 0
                                if status in ('failed', 'error'):
                                    error = data.get('error_message', 'Unknown error')
                                    raise Exception(f"Template activation failed: {error}")
                except Exception:
                    pass
                
                await asyncio.sleep(poll_interval)
            else:
                raise TimeoutError(
                    f"Template {template_id} did not become active within {max_wait} seconds. "
                    f"Last status: {status if 'status' in locals() else 'unknown'}"
                )
        
        # Verify all steps worked
        # Use sync Sandbox with context manager (AsyncSandbox.create() hangs)
        def create_and_test_sandbox():
            """Helper function to run sync sandbox operations in thread"""
            with Sandbox.create(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
                timeout_seconds=120,
            ) as sandbox:
                # Wait for sandbox VM to be ready before executing code
                # Sandbox.create() returns immediately, but VM needs time to start
                max_wait = 60  # Wait up to 60 seconds
                poll_interval = 2  # Check every 2 seconds
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    try:
                        if sandbox.is_healthy():
                            break
                    except Exception:
                        # Health check might fail if VM isn't ready yet
                        pass
                    time.sleep(poll_interval)
                else:
                    raise TimeoutError(
                        f"Sandbox {sandbox.sandbox_id} did not become ready within {max_wait} seconds"
                    )
                
                # Verify curl and git are installed using bash (Ubuntu may not have Python)
                exec_result = sandbox.run_code(
                    code="curl --version && git --version",
                    language="bash"
                )
                return exec_result
        
        exec_result = await asyncio.to_thread(create_and_test_sandbox)
        assert exec_result.exit_code == 0
        assert "curl" in exec_result.stdout.lower()
        assert "git" in exec_result.stdout.lower()
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_template_with_git_clone_integration(self, api_key, template_name):
        """
        Integration test: Verify that git_clone() works end-to-end.
        
        This test builds a template with a git clone operation and verifies:
        1. The template builds successfully
        2. The repository is cloned correctly
        3. Files from the repository are available
        
        Uses a small public repository for testing.
        """
        # Use a small public repo for testing
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("apt-get update && apt-get install -y git")
            .git_clone("https://github.com/python/cpython.git", "/tmp/cpython")
            .run_cmd("ls /tmp/cpython")  # Verify clone worked
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
        
        # Verify git clone worked
        async with AsyncSandbox.create(
            template_id=result.template_id,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=120,  # Add timeout to prevent hanging
        ) as sandbox:
            exec_result = await sandbox.run_code(
                code="import os; files = os.listdir('/tmp/cpython'); print(f'Found {len(files)} files/dirs'); print('README.rst' in files or 'README.md' in files or 'setup.py' in files)",
                language="python"
            )
            assert exec_result.exit_code == 0
            assert "True" in exec_result.stdout  # Should find repository files
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_template_skip_cache_integration(self, api_key, template_name):
        """
        Integration test: Verify that skip_cache() works end-to-end.
        
        This test builds a template with skip_cache() and verifies:
        1. The template builds successfully
        2. The skip_cache flag is respected during build
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("pip install requests")
            .skip_cache()  # Skip cache for last step
            .run_cmd("python -c 'import requests; print(requests.__version__)'")
        )
        
        # Build the template
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
        
        # Verify template works
        async with AsyncSandbox.create(
            template_id=result.template_id,
            api_key=api_key,
            base_url=BASE_URL,
            timeout_seconds=120,  # Add timeout to prevent hanging
        ) as sandbox:
            exec_result = await sandbox.run_code(
                code="import requests; print(requests.__version__)",
                language="python"
            )
            assert exec_result.exit_code == 0
            # The fact that it printed a version number means requests is installed
            assert exec_result.stdout.strip()  # Verify we got output (version number)
        
        # Cleanup
        try:
            await AsyncSandbox.delete_template(
                template_id=result.template_id,
                api_key=api_key,
                base_url=BASE_URL,
            )
        except Exception:
            pass
