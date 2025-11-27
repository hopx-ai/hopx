"""Version checking and update utilities for the Hopx CLI."""

from __future__ import annotations

import shutil
import subprocess
import sys
import sysconfig
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
from packaging.version import Version

if TYPE_CHECKING:
    pass

# PyPI API URL
PYPI_URL = "https://pypi.org/pypi/hopx-cli/json"

# Installation methods
INSTALL_PIP_USER = "pip_user"
INSTALL_PIP_SYSTEM = "pip_system"
INSTALL_PIPX = "pipx"
INSTALL_UV = "uv"
INSTALL_GIT = "git"
INSTALL_UNKNOWN = "unknown"


@dataclass
class VersionInfo:
    """Information about CLI versions."""

    current: str
    latest: str
    update_available: bool
    is_prerelease: bool = False
    release_url: str | None = None


async def check_pypi_version(
    package: str = "hopx-cli",
    include_prerelease: bool = False,
    timeout: float = 10.0,
) -> VersionInfo:
    """Check PyPI for the latest version of a package.

    Args:
        package: Package name on PyPI
        include_prerelease: Whether to include pre-release versions
        timeout: Request timeout in seconds

    Returns:
        VersionInfo with current and latest versions

    Raises:
        httpx.TimeoutException: If request times out
        httpx.HTTPError: If request fails
    """
    from hopx_cli import __version__

    current = __version__

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f"https://pypi.org/pypi/{package}/json")
        response.raise_for_status()
        data = response.json()

    # Get latest stable version from info
    latest_stable = data["info"]["version"]

    # If including pre-releases, check all releases
    if include_prerelease:
        all_versions = sorted(
            (Version(v) for v in data["releases"]),
            reverse=True,
        )
        latest = str(all_versions[0]) if all_versions else latest_stable
    else:
        latest = latest_stable

    # Check if update is available
    current_ver = Version(current)
    latest_ver = Version(latest)
    update_available = latest_ver > current_ver

    # Check if latest is a prerelease
    is_prerelease = latest_ver.is_prerelease

    # Get release URL
    release_url = data["info"].get("project_url") or data["info"].get("home_page")
    if not release_url:
        release_url = f"https://pypi.org/project/{package}/"

    return VersionInfo(
        current=current,
        latest=latest,
        update_available=update_available,
        is_prerelease=is_prerelease,
        release_url=release_url,
    )


def compare_versions(current: str, target: str) -> int:
    """Compare two semantic versions.

    Args:
        current: Current version string
        target: Target version string

    Returns:
        -1 if current < target
         0 if current == target
         1 if current > target
    """
    current_ver = Version(current)
    target_ver = Version(target)

    if current_ver < target_ver:
        return -1
    elif current_ver > target_ver:
        return 1
    return 0


def detect_install_method() -> str:
    """Detect how hopx-cli was installed.

    Checks in order:
    1. pipx installation
    2. uv tool installation
    3. pip installation (user or system)
    4. git/editable installation

    Returns:
        One of: pip_user, pip_system, pipx, uv, git, unknown
    """
    # Check for pipx
    if shutil.which("pipx"):
        try:
            result = subprocess.run(
                ["pipx", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "hopx-cli" in result.stdout:
                return INSTALL_PIPX
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Check for uv tool
    if shutil.which("uv"):
        try:
            result = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "hopx-cli" in result.stdout:
                return INSTALL_UV
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Check pip installation
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "hopx-cli"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            location = ""
            editable = False

            for line in result.stdout.split("\n"):
                if line.startswith("Location:"):
                    location = line.split(":", 1)[1].strip()
                if line.startswith("Editable project location"):
                    editable = True

            # Editable install = development/git
            if editable:
                return INSTALL_GIT

            # Check if user-level install
            user_site = sysconfig.get_path("purelib", "posix_user") or ""
            user_base = sysconfig.get_path("data", "posix_user") or ""

            if location:
                # Check various user paths
                if ".local" in location or user_site in location or user_base in location:
                    return INSTALL_PIP_USER
                return INSTALL_PIP_SYSTEM

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return INSTALL_UNKNOWN


def get_update_command(method: str, version: str | None = None) -> list[str]:
    """Generate the appropriate update command for the installation method.

    Args:
        method: Installation method (from detect_install_method)
        version: Specific version to install (None for latest)

    Returns:
        Command as list of strings
    """
    package = "hopx-cli"
    if version:
        package = f"hopx-cli=={version}"

    match method:
        case "pip_user":
            return [sys.executable, "-m", "pip", "install", "--user", "--upgrade", package]
        case "pip_system":
            return [sys.executable, "-m", "pip", "install", "--upgrade", package]
        case "pipx":
            if version:
                # pipx install with force to overwrite
                return ["pipx", "install", f"hopx-cli=={version}", "--force"]
            return ["pipx", "upgrade", "hopx-cli"]
        case "uv":
            if version:
                return ["uv", "tool", "install", f"hopx-cli=={version}", "--force"]
            return ["uv", "tool", "upgrade", "hopx-cli"]
        case "git":
            return [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "git+https://github.com/hopx-ai/hopx.git#subdirectory=cli",
            ]
        case _:
            # Default to pip user install
            return [sys.executable, "-m", "pip", "install", "--user", "--upgrade", package]


def get_install_method_display(method: str) -> str:
    """Get human-readable name for installation method."""
    return {
        INSTALL_PIP_USER: "pip (user)",
        INSTALL_PIP_SYSTEM: "pip (system)",
        INSTALL_PIPX: "pipx",
        INSTALL_UV: "uv",
        INSTALL_GIT: "git (development)",
        INSTALL_UNKNOWN: "unknown",
    }.get(method, method)
