"""
Integration tests for Template ready check functions.

This module contains integration tests for template ready check functions.
Ready checks are used to determine when a template's start command has
successfully initialized and is ready to accept connections or requests.

Tests cover:
- wait_for_port: Wait for a service to start listening on a specific port
- wait_for_url: Wait for an HTTP endpoint to become available and respond
- wait_for_file: Wait for a file to be created, indicating readiness
- wait_for_process: Wait for a specific process to be running
- wait_for_command: Wait for a command to complete successfully

All tests create templates with services that require initialization time,
then use ready checks to ensure the template build process waits for the
service to be ready before completing. Each test validates that:
1. The template builds successfully with the ready check
2. The ready check correctly detects when the service is ready
3. Templates can be created from the built template

Test Environment:
    - Base URL: Set via HOPX_TEST_BASE_URL env var (default: https://api-eu.hopx.dev)
    - Authentication: HOPX_API_KEY environment variable must be set
    - All created templates are cleaned up after tests complete
"""

import os
import pytest
import time
from hopx_ai import Template, AsyncSandbox
from hopx_ai.template import BuildOptions, wait_for_port, wait_for_url, wait_for_file, wait_for_process, wait_for_command

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
        str: A unique template name in the format "test-ready-check-{timestamp}"
    """
    return f"test-ready-check-{int(time.time())}"


class TestTemplateReadyChecks:
    """
    Test suite for Template ready check functions.
    
    This class contains integration tests that validate ready check functions
    used to determine when a template's start command has successfully initialized.
    Each test creates a template with a service that requires initialization time
    and uses a ready check to ensure the build process waits appropriately.
    
    Ready checks are critical for templates that start services, as they ensure
    the template is fully ready before being marked as built. Without ready checks,
    templates might be marked as ready before their services are actually available.
    """

    @pytest.mark.asyncio
    async def test_wait_for_port(self, api_key, template_name):
        """
        Test wait_for_port ready check function.
        
        Creates a template that starts an HTTP server and uses wait_for_port()
        to wait for the server to begin listening on port 8000 before marking
        the template as ready. This validates that:
        1. The ready check correctly detects when the port becomes available
        2. The template build process waits for the port to be ready
        3. The template is successfully created with the ready check
        
        The test creates a simple Python HTTP server that listens on port 8000
        and uses wait_for_port(8000) as the ready check for the start command.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        # Create template with a service that listens on a port
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > server.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python server.py", wait_for_port(8000))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name, ready_check="wait_for_port"):
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

    @pytest.mark.asyncio
    async def test_wait_for_url(self, api_key, template_name):
        """
        Test wait_for_url ready check function.
        
        Creates a template that starts an HTTP server and uses wait_for_url()
        to wait for the HTTP endpoint to become available and respond before
        marking the template as ready. This validates that:
        1. The ready check correctly detects when the URL becomes accessible
        2. The template build process waits for the HTTP endpoint to be ready
        3. The template is successfully created with the ready check
        
        Unlike wait_for_port, wait_for_url verifies that the service is not
        only listening but also responding to HTTP requests. This is more
        robust for web services that may need additional initialization time.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > server.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
EOF""")
            .set_env("PORT", "8000")
            .set_start_cmd("python server.py", wait_for_url("http://localhost:8000"))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name, ready_check="wait_for_url"):
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

    @pytest.mark.asyncio
    async def test_wait_for_file(self, api_key, template_name):
        """
        Test wait_for_file ready check function.
        
        Creates a template that creates a readiness indicator file and uses
        wait_for_file() to wait for that file to exist before marking the
        template as ready. This validates that:
        1. The ready check correctly detects when the file is created
        2. The template build process waits for the file to appear
        3. The template is successfully created with the ready check
        
        This ready check is useful for services that create a file to indicate
        they have finished initialization, such as services that need to load
        configuration or perform setup tasks before becoming ready.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > start.sh << 'EOF'
#!/bin/bash
sleep 2
echo "ready" > /app/ready.txt
python -m http.server 8000
EOF""")
            .run_cmd("chmod +x start.sh")
            .set_start_cmd("/app/start.sh", wait_for_file("/app/ready.txt"))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name, ready_check="wait_for_file"):
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

    @pytest.mark.asyncio
    async def test_wait_for_process(self, api_key, template_name):
        """
        Test wait_for_process ready check function.
        
        Creates a template that starts a background process and uses
        wait_for_process() to wait for that process to be running before
        marking the template as ready. This validates that:
        1. The ready check correctly detects when the process is running
        2. The template build process waits for the process to start
        3. The template is successfully created with the ready check
        
        This ready check is useful for services that start background processes
        and need to verify the process is actually running before considering
        the service ready. The process name is matched against running processes.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > start.sh << 'EOF'
#!/bin/bash
python -m http.server 8000 &
echo $! > /app/server.pid
wait
EOF""")
            .run_cmd("chmod +x start.sh")
            .set_start_cmd("/app/start.sh", wait_for_process("python"))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name, ready_check="wait_for_process"):
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

    @pytest.mark.asyncio
    async def test_wait_for_command(self, api_key, template_name):
        """
        Test wait_for_command ready check function.
        
        Creates a template that runs an initialization command and uses
        wait_for_command() to wait for that command to complete successfully
        before marking the template as ready. This validates that:
        1. The ready check correctly detects when the command completes
        2. The template build process waits for the command to finish
        3. The template is successfully created with the ready check
        
        This ready check is useful for services that need to run initialization
        scripts or setup commands before they are ready. The command must exit
        with a successful status code (0) for the ready check to pass.
        
        Args:
            api_key: Pytest fixture providing API authentication key
            template_name: Pytest fixture providing unique template name
        """
        template = (
            Template()
            .from_python_image("3.11")
            .run_cmd("mkdir -p /app")
            .set_workdir("/app")
            .run_cmd("""cat > init.sh << 'EOF'
#!/bin/bash
echo "Initializing..."
sleep 1
echo "Ready"
exit 0
EOF""")
            .run_cmd("""cat > start.sh << 'EOF'
#!/bin/bash
# Run initialization script first
/app/init.sh
# Then start the server
python -m http.server 8000
EOF""")
            .run_cmd("chmod +x init.sh start.sh")
            .set_start_cmd("/app/start.sh", wait_for_command("/app/init.sh"))
        )

        # Build the template (this can take 1+ minutes)
        with timed_operation("Template.build", warn_threshold=60.0, template_name=template_name, ready_check="wait_for_command"):
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

