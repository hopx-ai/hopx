"""Factory classes for creating SDK mocks.

These factories provide reusable mock objects for hopx_ai SDK classes
with various configurations for testing different scenarios.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock


class SandboxMockFactory:
    """Factory for creating Sandbox mocks with various states."""

    @staticmethod
    def create(
        sandbox_id: str = "sb_test123",
        status: str = "running",
        template: str = "python",
        region: str = "us-east-1",
        timeout_seconds: int = 3600,
        internet_access: bool = True,
        **kwargs: Any,
    ) -> MagicMock:
        """Create a mock Sandbox with specified configuration.

        Args:
            sandbox_id: Sandbox identifier
            status: Sandbox status (running, paused, etc.)
            template: Template name
            region: Region identifier
            timeout_seconds: Timeout in seconds
            internet_access: Whether internet is enabled
            **kwargs: Additional sandbox attributes

        Returns:
            MagicMock configured as a Sandbox
        """
        sandbox = MagicMock()
        sandbox.sandbox_id = sandbox_id
        sandbox.status = status
        sandbox.template_name = template

        # Create sandbox info
        info = MagicMock()
        info.sandbox_id = sandbox_id
        info.status = status
        info.template_name = template
        info.region = region
        info.public_host = f"https://{sandbox_id}.vms.hopx.dev"
        info.timeout_seconds = timeout_seconds
        info.expires_at = kwargs.get("expires_at")
        info.created_at = kwargs.get("created_at", datetime.now(UTC))
        info.resources = kwargs.get("resources")
        info.internet_access = internet_access

        info.model_dump = lambda: {
            "sandbox_id": sandbox_id,
            "status": status,
            "template_name": template,
            "region": region,
            "public_host": f"https://{sandbox_id}.vms.hopx.dev",
            "timeout_seconds": timeout_seconds,
            "internet_access": internet_access,
        }

        sandbox.get_info.return_value = info
        sandbox.is_healthy.return_value = status == "running"
        sandbox.get_preview_url.side_effect = (
            lambda port: f"https://{port}-{sandbox_id}.vms.hopx.dev"
        )

        # Mock resource managers
        sandbox.files = MagicMock()
        sandbox.commands = MagicMock()
        sandbox.env = MagicMock()
        sandbox.terminal = MagicMock()

        # Mock common operations
        sandbox.kill.return_value = None
        sandbox.pause.return_value = None
        sandbox.resume.return_value = None

        return sandbox

    @staticmethod
    def create_running(sandbox_id: str = "sb_running") -> MagicMock:
        """Create a running sandbox mock."""
        return SandboxMockFactory.create(sandbox_id=sandbox_id, status="running")

    @staticmethod
    def create_paused(sandbox_id: str = "sb_paused") -> MagicMock:
        """Create a paused sandbox mock."""
        return SandboxMockFactory.create(sandbox_id=sandbox_id, status="paused")

    @staticmethod
    def create_expired(sandbox_id: str = "sb_expired") -> MagicMock:
        """Create an expired sandbox mock."""
        return SandboxMockFactory.create(sandbox_id=sandbox_id, status="expired")

    @staticmethod
    def create_list(count: int = 3) -> list[MagicMock]:
        """Create a list of sandbox mocks.

        Args:
            count: Number of sandboxes to create

        Returns:
            List of mock sandboxes
        """
        sandboxes = []
        statuses = ["running", "paused", "running"]
        templates = ["python", "nodejs", "code-interpreter"]

        for i in range(count):
            sandbox = SandboxMockFactory.create(
                sandbox_id=f"sb_test{i:03d}",
                status=statuses[i % len(statuses)],
                template=templates[i % len(templates)],
            )
            sandboxes.append(sandbox)

        return sandboxes


class TemplateMockFactory:
    """Factory for creating Template mocks."""

    @staticmethod
    def create(
        name: str = "custom-template",
        status: str = "active",
        description: str | None = None,
        **kwargs: Any,
    ) -> MagicMock:
        """Create a mock Template.

        Args:
            name: Template name
            status: Template status
            description: Optional description
            **kwargs: Additional template attributes

        Returns:
            MagicMock configured as a Template
        """
        template = MagicMock()
        template.name = name
        template.status = status
        template.description = description
        template.created_at = kwargs.get("created_at", datetime.now(UTC))
        template.updated_at = kwargs.get("updated_at")

        template.model_dump = lambda: {
            "name": name,
            "status": status,
            "description": description,
        }

        return template

    @staticmethod
    def create_building(name: str = "building-template") -> MagicMock:
        """Create a template in building state."""
        return TemplateMockFactory.create(name=name, status="building")

    @staticmethod
    def create_active(name: str = "active-template") -> MagicMock:
        """Create an active template."""
        return TemplateMockFactory.create(name=name, status="active")

    @staticmethod
    def create_list() -> list[MagicMock]:
        """Create a list of common templates.

        Returns:
            List of mock templates
        """
        templates = [
            TemplateMockFactory.create(name="python", status="active"),
            TemplateMockFactory.create(name="nodejs", status="active"),
            TemplateMockFactory.create(name="code-interpreter", status="active"),
        ]
        return templates


class ExecutionResultMockFactory:
    """Factory for creating code execution result mocks."""

    @staticmethod
    def create(
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        **kwargs: Any,
    ) -> MagicMock:
        """Create a mock execution result.

        Args:
            stdout: Standard output
            stderr: Standard error
            exit_code: Exit code
            **kwargs: Additional result attributes

        Returns:
            MagicMock configured as an execution result
        """
        result = MagicMock()
        result.stdout = stdout
        result.stderr = stderr
        result.exit_code = exit_code
        result.duration = kwargs.get("duration", 0.1)

        result.model_dump = lambda: {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
        }

        return result

    @staticmethod
    def create_success(stdout: str = "Hello, World!") -> MagicMock:
        """Create a successful execution result."""
        return ExecutionResultMockFactory.create(stdout=stdout, exit_code=0)

    @staticmethod
    def create_error(stderr: str = "Error occurred", exit_code: int = 1) -> MagicMock:
        """Create a failed execution result."""
        return ExecutionResultMockFactory.create(stderr=stderr, exit_code=exit_code)


class FileMockFactory:
    """Factory for creating file operation mocks."""

    @staticmethod
    def create_file_info(
        path: str = "/app/test.py",
        size: int = 1024,
        is_directory: bool = False,
        **kwargs: Any,
    ) -> MagicMock:
        """Create a mock file info.

        Args:
            path: File path
            size: File size in bytes
            is_directory: Whether it's a directory
            **kwargs: Additional file attributes

        Returns:
            MagicMock configured as file info
        """
        file_info = MagicMock()
        file_info.path = path
        file_info.name = path.split("/")[-1]
        file_info.size = size
        file_info.is_directory = is_directory
        file_info.modified_at = kwargs.get("modified_at", datetime.now(UTC))

        file_info.model_dump = lambda: {
            "path": path,
            "name": file_info.name,
            "size": size,
            "is_directory": is_directory,
        }

        return file_info

    @staticmethod
    def create_file_list() -> list[MagicMock]:
        """Create a list of mock files.

        Returns:
            List of mock file info objects
        """
        return [
            FileMockFactory.create_file_info(path="/app/main.py", size=2048),
            FileMockFactory.create_file_info(path="/app/test.py", size=1024),
            FileMockFactory.create_file_info(path="/app/data", size=0, is_directory=True),
        ]
