"""
Template Builder - Fluent API for building templates
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from .types import Step, StepType, CopyOptions, ReadyCheck, BuildOptions, BuildResult, RegistryAuth, GCPRegistryAuth, AWSRegistryAuth
from .build_flow import build_template


class Template:
    """Fluent API for building templates"""
    
    def __init__(self):
        self.steps: List[Step] = []
        self.start_cmd: Optional[str] = None
        self.ready_check: Optional[ReadyCheck] = None
    
    # ==================== Base Images ====================
    
    def from_ubuntu_image(self, version: str) -> 'Template':
        """Start from Ubuntu base image"""
        self.steps.append(Step(
            type=StepType.FROM,
            args=[f"ubuntu:{version}"]
        ))
        return self
    
    def from_python_image(self, version: str) -> 'Template':
        """Start from Python base image"""
        self.steps.append(Step(
            type=StepType.FROM,
            args=[f"python:{version}"]
        ))
        return self
    
    def from_node_image(self, version: str) -> 'Template':
        """Start from Node.js base image"""
        self.steps.append(Step(
            type=StepType.FROM,
            args=[f"node:{version}"]
        ))
        return self
    
    def from_image(self, image: str, auth: Optional[RegistryAuth] = None) -> 'Template':
        """Start from any Docker image (with optional authentication)"""
        self.steps.append(Step(
            type=StepType.FROM,
            args=[image],
            registry_auth=auth
        ))
        return self
    
    def from_gcp_registry(self, image: str, auth: GCPRegistryAuth) -> 'Template':
        """Start from GCP Container Registry image"""
        # Parse service account JSON
        if isinstance(auth.service_account_json, str):
            # It's a file path
            with open(auth.service_account_json, 'r') as f:
                service_account = json.load(f)
        else:
            # It's already a dict
            service_account = auth.service_account_json
        
        # GCP uses _json_key as username
        registry_auth = RegistryAuth(
            username='_json_key',
            password=json.dumps(service_account)
        )
        
        return self.from_image(image, registry_auth)
    
    def from_aws_registry(self, image: str, auth: AWSRegistryAuth) -> 'Template':
        """Start from AWS ECR image"""
        self.steps.append(Step(
            type=StepType.FROM,
            args=[image],
            aws_auth=auth
        ))
        return self
    
    # ==================== File Operations ====================
    
    def copy(
        self, 
        src: Union[str, List[str]], 
        dest: str, 
        options: Optional[CopyOptions] = None
    ) -> 'Template':
        """Copy files to the template"""
        sources = src if isinstance(src, list) else [src]
        
        self.steps.append(Step(
            type=StepType.COPY,
            args=[','.join(sources), dest, str(options or {})]
        ))
        return self
    
    # ==================== Commands ====================
    
    def run_cmd(self, cmd: str) -> 'Template':
        """Run a command during build"""
        self.steps.append(Step(
            type=StepType.RUN,
            args=[cmd]
        ))
        return self
    
    # ==================== Environment ====================
    
    def set_env(self, key: str, value: str) -> 'Template':
        """Set an environment variable"""
        self.steps.append(Step(
            type=StepType.ENV,
            args=[key, value]
        ))
        return self
    
    def set_envs(self, vars: Dict[str, str]) -> 'Template':
        """Set multiple environment variables"""
        for key, value in vars.items():
            self.set_env(key, value)
        return self
    
    # ==================== Working Directory ====================
    
    def set_workdir(self, directory: str) -> 'Template':
        """Set working directory"""
        self.steps.append(Step(
            type=StepType.WORKDIR,
            args=[directory]
        ))
        return self
    
    # ==================== User ====================
    
    def set_user(self, user: str) -> 'Template':
        """Set user"""
        self.steps.append(Step(
            type=StepType.USER,
            args=[user]
        ))
        return self
    
    # ==================== Smart Helpers ====================
    
    def apt_install(self, *packages: Union[str, List[str]]) -> 'Template':
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
        
        pkgs = ' '.join(pkg_list)
        self.run_cmd(
            f"apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y {pkgs}"
        )
        return self
    
    def pip_install(self, *packages: Union[str, List[str], None]) -> 'Template':
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
            raise ValueError("pip_install requires at least one package or no args for requirements.txt")
        
        pkgs = ' '.join(pkg_list)
        # Use full path for pip (works after systemd restart)
        self.run_cmd(f"/usr/local/bin/pip3 install --no-cache-dir {pkgs}")
        return self
    
    def npm_install(self, *packages: Union[str, List[str], None]) -> 'Template':
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
            self.run_cmd("/usr/bin/npm install")
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
            raise ValueError("npm_install requires at least one package or no args for package.json")
        
        pkgs = ' '.join(pkg_list)
        # Use full path for npm (works after systemd restart)
        self.run_cmd(f"/usr/bin/npm install -g {pkgs}")
        return self
    
    def go_install(self, packages: List[str]) -> 'Template':
        """Install Go packages"""
        for pkg in packages:
            self.run_cmd(f"go install {pkg}")
        return self
    
    def cargo_install(self, packages: List[str]) -> 'Template':
        """Install Rust packages with cargo"""
        for pkg in packages:
            self.run_cmd(f"cargo install {pkg}")
        return self
    
    def git_clone(self, url: str, dest: str) -> 'Template':
        """Clone a git repository"""
        self.run_cmd(f"git clone {url} {dest}")
        return self
    
    # ==================== Caching ====================
    
    def skip_cache(self) -> 'Template':
        """Skip cache for the last step"""
        if self.steps:
            self.steps[-1].skip_cache = True
        return self
    
    # ==================== Start Command ====================
    
    def set_start_cmd(
        self, 
        cmd: str, 
        ready: Optional[ReadyCheck] = None
    ) -> 'Template':
        """Set the start command and ready check"""
        self.start_cmd = cmd
        self.ready_check = ready
        return self
    
    # ==================== Build ====================
    
    def get_steps(self) -> List[Step]:
        """Get all steps"""
        return self.steps
    
    def get_start_cmd(self) -> Optional[str]:
        """Get start command"""
        return self.start_cmd
    
    def get_ready_check(self) -> Optional[ReadyCheck]:
        """Get ready check"""
        return self.ready_check
    
    @staticmethod
    async def build(template: 'Template', options: BuildOptions) -> BuildResult:
        """Build the template"""
        return await build_template(template, options)


def create_template() -> Template:
    """Factory function to create a new template"""
    return Template()

