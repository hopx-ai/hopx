"""
Template Builder - Fluent API for building templates
"""

import json
from typing import List, Dict, Optional, Union
from .types import (
    Step,
    StepType,
    CopyOptions,
    ReadyCheck,
    BuildOptions,
    BuildResult,
    RegistryAuth,
    GCPRegistryAuth,
    AWSRegistryAuth,
)
from .build_flow import build_template


class Template:
    """Fluent API for building templates"""

    def __init__(self, from_image: Optional[str] = None):
        """
        Initialize template with base image

        Args:
            from_image: Base Docker image (e.g. "python:3.11-slim", "ubuntu:22.04")
        """
        self.from_image: Optional[str] = from_image
        self.steps: List[Step] = []
        self.start_cmd: Optional[str] = None
        self.ready_check: Optional[ReadyCheck] = None
        self.registry_auth: Optional[RegistryAuth] = None

    # ==================== Base Images ====================

    def from_ubuntu_image(self, version: str) -> "Template":
        """Start from Ubuntu base image"""
        self.from_image = f"ubuntu:{version}"
        return self

    def from_python_image(self, version: str) -> "Template":
        """Start from Python base image"""
        self.from_image = f"python:{version}"
        return self

    def from_node_image(self, version: str) -> "Template":
        """
        Use a Node.js base image (Debian-based slim variant)

        Note: Alpine variants are not compatible with our VM agent system
        due to musl libc limitations. This method uses the official slim
        variant which is Debian-based.

        Args:
            version: Node.js version (e.g., '18', '20', '22')

        Returns:
            Template builder for method chaining

        Example:
            template.from_node_image('20')  # Uses node:20-slim

        See: https://hub.docker.com/_/node
        """
        self.from_image = f"node:{version}-slim"
        return self

    def from_private_image(self, image: str, auth: RegistryAuth) -> "Template":
        """
        Use a Docker image from a private registry with basic authentication

        Args:
            image: Docker image URL (e.g. "registry.example.com/myimage:tag")
            auth: Registry credentials (username and password/token)

        Returns:
            Template builder for method chaining

        Examples:
            # Docker Hub private repository
            template.from_private_image('myuser/private-app:v1', RegistryAuth(
                username='myuser',
                password=os.getenv('DOCKER_HUB_TOKEN')
            ))

            # GitLab Container Registry
            template.from_private_image('registry.gitlab.com/mygroup/myproject/app:latest', RegistryAuth(
                username='gitlab-ci-token',
                password=os.getenv('CI_JOB_TOKEN')
            ))
        """
        self.from_image = image
        self.registry_auth = auth
        return self

    def from_gcp_private_image(self, image: str, auth: GCPRegistryAuth) -> "Template":
        """
        Use a Docker image from Google Container Registry (GCR) or Artifact Registry

        Args:
            image: GCP registry image URL (e.g. "gcr.io/myproject/myimage:tag" or
                   "us-docker.pkg.dev/myproject/myrepo/myimage:tag")
            auth: GCP service account credentials

        Returns:
            Template builder for method chaining

        Examples:
            # With service account JSON file path
            template.from_gcp_private_image('gcr.io/myproject/api-server:v1', GCPRegistryAuth(
                service_account_json='./service-account.json'
            ))

            # With service account JSON object
            service_account = json.loads(os.getenv('GCP_SERVICE_ACCOUNT'))
            template.from_gcp_private_image('us-docker.pkg.dev/myproject/myrepo/app:latest', GCPRegistryAuth(
                service_account_json=service_account
            ))
        """
        # Parse service account JSON
        if isinstance(auth.service_account_json, str):
            # It's a file path
            with open(auth.service_account_json, "r") as f:
                service_account = json.load(f)
        else:
            # It's already a dict
            service_account = auth.service_account_json

        # GCP uses _json_key as username
        registry_auth = RegistryAuth(username="_json_key", password=json.dumps(service_account))

        self.from_image = image
        self.registry_auth = registry_auth
        return self

    def from_aws_private_image(self, image: str, auth: AWSRegistryAuth) -> "Template":
        """
        Use a Docker image from AWS Elastic Container Registry (ECR)

        The backend will handle ECR authentication token exchange using the provided credentials.

        Args:
            image: ECR image URL (e.g. "123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest")
            auth: AWS IAM credentials with ECR pull permissions

        Returns:
            Template builder for method chaining

        Examples:
            template.from_aws_private_image('123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:v1', AWSRegistryAuth(
                access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region='us-west-2'
            ))

            # With session token for temporary credentials
            template.from_aws_private_image('123456789012.dkr.ecr.us-east-1.amazonaws.com/api:latest', AWSRegistryAuth(
                access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region='us-east-1',
                session_token=os.getenv('AWS_SESSION_TOKEN')
            ))
        """
        # Store AWS credentials - backend will handle ECR token exchange
        self.from_image = image
        self.registry_auth = RegistryAuth(
            username=auth.access_key_id, password=auth.secret_access_key
        )
        return self

    # ==================== File Operations ====================

    def copy(
        self, src: Union[str, List[str]], dest: str, options: Optional[CopyOptions] = None
    ) -> "Template":
        """
        Copy files to the template

        Args:
            src: Source path(s) - local file/directory to upload (e.g. ".", "src/", ["file1.py", "file2.py"])
            dest: Destination path in template (e.g. "/app", "/home/user/code")
            options: Optional copy options (owner, permissions)

        Note: Files are automatically uploaded to R2 and the hash is calculated.
              The API receives only the destination path and hash.
        """
        sources = src if isinstance(src, list) else [src]

        self.steps.append(
            Step(
                type=StepType.COPY,
                args=[",".join(sources), dest],  # Local sources for upload, destination for API
                skip_cache=False,
            )
        )
        return self

    # ==================== Commands ====================

    def run_cmd(self, cmd: str) -> "Template":
        """Run a command during build"""
        self.steps.append(Step(type=StepType.RUN, args=[cmd]))
        return self

    # ==================== Environment ====================

    def set_env(self, key: str, value: str) -> "Template":
        """Set an environment variable"""
        self.steps.append(Step(type=StepType.ENV, args=[key, value]))
        return self

    def set_envs(self, vars: Dict[str, str]) -> "Template":
        """Set multiple environment variables"""
        for key, value in vars.items():
            self.set_env(key, value)
        return self

    # ==================== Working Directory ====================

    def set_workdir(self, directory: str) -> "Template":
        """Set working directory"""
        self.steps.append(Step(type=StepType.WORKDIR, args=[directory]))
        return self

    # ==================== User ====================

    def set_user(self, user: str) -> "Template":
        """Set user"""
        self.steps.append(Step(type=StepType.USER, args=[user]))
        return self

    # ==================== Smart Helpers ====================

    def apt_install(self, *packages: Union[str, List[str]]) -> "Template":
        """
        Install packages with apt

        Examples:
            .apt_install("curl", "git", "vim")  # Multiple args
            .apt_install(["curl", "git", "vim"])  # List
            .apt_install("curl").apt_install("git")  # Chained
        """
        # Flatten args
        pkg_list = []
        for pkg in packages:
            if isinstance(pkg, list):
                pkg_list.extend(pkg)
            else:
                pkg_list.append(pkg)

        if not pkg_list:
            raise ValueError("apt_install requires at least one package")

        pkgs = " ".join(pkg_list)
        self.run_cmd(
            f"apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y {pkgs}"
        )
        return self

    def pip_install(self, *packages: Union[str, List[str], None]) -> "Template":
        """
        Install Python packages with pip

        Examples:
            .pip_install("numpy", "pandas")  # Multiple args
            .pip_install(["numpy", "pandas"])  # List
            .pip_install("numpy").pip_install("pandas")  # Chained
            .pip_install()  # Install from requirements.txt
        """
        # Handle no args (requirements.txt)
        if not packages:
            self.run_cmd("/usr/local/bin/pip3 install --no-cache-dir -r requirements.txt")
            return self

        # Flatten args
        pkg_list = []
        for pkg in packages:
            if pkg is None:
                continue
            if isinstance(pkg, list):
                pkg_list.extend(pkg)
            else:
                pkg_list.append(pkg)

        if not pkg_list:
            raise ValueError(
                "pip_install requires at least one package or no args for requirements.txt"
            )

        pkgs = " ".join(pkg_list)
        # Use full path for pip (works after systemd restart)
        self.run_cmd(f"/usr/local/bin/pip3 install --no-cache-dir {pkgs}")
        return self

    def npm_install(self, *packages: Union[str, List[str], None]) -> "Template":
        """
        Install Node packages with npm

        Examples:
            .npm_install("typescript", "tsx")  # Multiple args
            .npm_install(["typescript", "tsx"])  # List
            .npm_install("typescript").npm_install("tsx")  # Chained
            .npm_install()  # Install from package.json
        """
        # Handle no args (package.json)
        if not packages:
            self.run_cmd("/usr/local/bin/npm install")
            return self

        # Flatten args
        pkg_list = []
        for pkg in packages:
            if pkg is None:
                continue
            if isinstance(pkg, list):
                pkg_list.extend(pkg)
            else:
                pkg_list.append(pkg)

        if not pkg_list:
            raise ValueError(
                "npm_install requires at least one package or no args for package.json"
            )

        pkgs = " ".join(pkg_list)
        # Use full path for npm (works after systemd restart)
        self.run_cmd(f"/usr/local/bin/npm install -g {pkgs}")
        return self

    def go_install(self, packages: List[str]) -> "Template":
        """Install Go packages"""
        for pkg in packages:
            self.run_cmd(f"go install {pkg}")
        return self

    def cargo_install(self, packages: List[str]) -> "Template":
        """Install Rust packages with cargo"""
        for pkg in packages:
            self.run_cmd(f"cargo install {pkg}")
        return self

    def git_clone(self, url: str, dest: str) -> "Template":
        """Clone a git repository"""
        self.run_cmd(f"git clone {url} {dest}")
        return self

    # ==================== Caching ====================

    def skip_cache(self) -> "Template":
        """Skip cache for the last step"""
        if self.steps:
            self.steps[-1].skip_cache = True
        return self

    # ==================== Start Command ====================

    def set_start_cmd(self, cmd: str, ready: Optional[ReadyCheck] = None) -> "Template":
        """Set the start command and ready check"""
        self.start_cmd = cmd
        self.ready_check = ready
        return self

    # ==================== Build ====================

    def get_from_image(self) -> Optional[str]:
        """Get base image"""
        return self.from_image

    def get_registry_auth(self) -> Optional[RegistryAuth]:
        """Get registry authentication"""
        return self.registry_auth

    def get_steps(self) -> List[Step]:
        """Get all steps (excludes FROM - that's in from_image)"""
        return self.steps

    def get_start_cmd(self) -> Optional[str]:
        """Get start command"""
        return self.start_cmd

    def get_ready_check(self) -> Optional[ReadyCheck]:
        """Get ready check"""
        return self.ready_check

    @staticmethod
    async def build(template: "Template", options: BuildOptions) -> BuildResult:
        """Build the template and wait for it to become active."""
        return await build_template(template, options)


def create_template(from_image: Optional[str] = None) -> Template:
    """
    Factory function to create a new template

    Args:
        from_image: Base Docker image (e.g. "python:3.11-slim")

    Example:
        ```python
        from hopx_ai.template import create_template

        template = create_template("python:3.11-slim")
        template.run_cmd("pip install numpy pandas")
        ```
    """
    return Template(from_image=from_image)
