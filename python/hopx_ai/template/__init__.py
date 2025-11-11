"""
Template Building Module

Provides fluent API for building custom templates.
"""

from .builder import Template, create_template
from .build_flow import get_logs
from .ready_checks import (
    wait_for_port,
    wait_for_url,
    wait_for_file,
    wait_for_process,
    wait_for_command,
)
from .types import (
    StepType,
    Step,
    ReadyCheck,
    ReadyCheckType,
    BuildOptions,
    BuildResult,
    CreateVMOptions,
    VM,
    LogsResponse,
)

__all__ = [
    "Template",
    "create_template",
    "get_logs",
    "wait_for_port",
    "wait_for_url",
    "wait_for_file",
    "wait_for_process",
    "wait_for_command",
    "StepType",
    "Step",
    "ReadyCheck",
    "ReadyCheckType",
    "BuildOptions",
    "BuildResult",
    "CreateVMOptions",
    "VM",
    "LogsResponse",
]

