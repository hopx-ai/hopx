"""
Template Building Types
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime


class StepType(str, Enum):
    """Step types for template building"""
    FROM = "FROM"
    COPY = "COPY"
    RUN = "RUN"
    ENV = "ENV"
    WORKDIR = "WORKDIR"
    USER = "USER"
    CMD = "CMD"


@dataclass
class RegistryAuth:
    """Basic registry authentication"""
    username: str
    password: str


@dataclass
class GCPRegistryAuth:
    """GCP Container Registry authentication"""
    service_account_json: Any  # str (file path) or dict


@dataclass
class AWSRegistryAuth:
    """AWS ECR authentication"""
    access_key_id: str
    secret_access_key: str
    region: str
    session_token: Optional[str] = None


@dataclass
class Step:
    """Represents a build step"""
    type: StepType
    args: List[str]
    files_hash: Optional[str] = None
    skip_cache: bool = False
    registry_auth: Optional[RegistryAuth] = None
    gcp_auth: Optional[GCPRegistryAuth] = None
    aws_auth: Optional[AWSRegistryAuth] = None


@dataclass
class CopyOptions:
    """Options for COPY steps"""
    owner: Optional[str] = None
    permissions: Optional[str] = None


class ReadyCheckType(str, Enum):
    """Types of ready checks"""
    PORT = "port"
    URL = "url"
    FILE = "file"
    PROCESS = "process"
    COMMAND = "command"


@dataclass
class ReadyCheck:
    """Ready check configuration"""
    type: ReadyCheckType
    port: Optional[int] = None
    url: Optional[str] = None
    path: Optional[str] = None
    process_name: Optional[str] = None
    command: Optional[str] = None
    timeout: int = 30000
    interval: int = 2000


@dataclass
class BuildOptions:
    """Options for building a template"""
    alias: str
    api_key: str
    base_url: str = "https://api.hopx.dev"
    cpu: int = 2
    memory: int = 2048
    disk_gb: int = 10
    skip_cache: bool = False
    context_path: Optional[str] = None
    on_log: Optional[Callable[[Dict[str, Any]], None]] = None
    on_progress: Optional[Callable[[int], None]] = None


@dataclass
class LogEntry:
    """Log entry from build"""
    timestamp: str
    level: str
    message: str


@dataclass
class StatusUpdate:
    """Status update from build"""
    status: str
    progress: int
    current_step: Optional[str] = None


@dataclass
class CreateVMOptions:
    """Options for creating a VM from template"""
    alias: Optional[str] = None
    cpu: Optional[int] = None
    memory: Optional[int] = None
    disk_gb: Optional[int] = None
    env_vars: Optional[Dict[str, str]] = None


@dataclass
class VM:
    """Represents a VM instance"""
    vm_id: str
    template_id: str
    status: str
    ip: str
    agent_url: str
    started_at: str
    _delete_func: Optional[Callable[[], None]] = None
    
    async def delete(self):
        """Delete this VM"""
        if self._delete_func:
            await self._delete_func()


@dataclass
class BuildResult:
    """Result of a template build"""
    build_id: str
    template_id: str
    duration: int
    _create_vm_func: Optional[Callable[[CreateVMOptions], Any]] = None
    
    async def create_vm(self, options: CreateVMOptions = None) -> VM:
        """Create a VM from this template"""
        if self._create_vm_func:
            return await self._create_vm_func(options or CreateVMOptions())
        raise RuntimeError("create_vm function not available")


@dataclass
class UploadLinkResponse:
    """Response from upload link request"""
    present: bool
    upload_url: Optional[str] = None
    expires_at: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class BuildResponse:
    """Response from build trigger"""
    build_id: str
    template_id: str
    status: str
    logs_url: str
    request_id: Optional[str] = None


@dataclass
class BuildStatusResponse:
    """Response from build status check"""
    build_id: str
    template_id: str
    status: str
    progress: int
    started_at: str
    current_step: Optional[str] = None
    estimated_completion: Optional[str] = None
    error: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class LogsResponse:
    """Response from build logs polling"""
    logs: str
    offset: int
    status: str
    complete: bool
    request_id: Optional[str] = None

