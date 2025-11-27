#!/bin/bash
# Hopx CLI Installer v2.0.0
#
# One-liner installation:
#   curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
#
# Environment variables:
#   HOPX_INSTALL_MODE     - Installation mode: pip (default), pipx, git
#   HOPX_NON_INTERACTIVE  - Skip all prompts (true/false)
#   HOPX_SKIP_PATH_SETUP  - Don't modify shell config (true/false)
#   HOPX_QUIET            - Minimal output (true/false)
#   HOPX_DRY_RUN          - Preview without changes (true/false)
#
# Source: https://github.com/hopx-ai/hopx/tree/main/cli

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_VERSION="2.0.0"
PACKAGE_NAME="hopx-cli"
PYPI_PACKAGE="hopx-cli"
GITHUB_REPO="hopx-ai/hopx"
MIN_PYTHON_VERSION="3.12"

# Environment variable defaults (validated later)
INSTALL_MODE="${HOPX_INSTALL_MODE:-pip}"
NON_INTERACTIVE="${HOPX_NON_INTERACTIVE:-false}"
SKIP_PATH_SETUP="${HOPX_SKIP_PATH_SETUP:-false}"
QUIET="${HOPX_QUIET:-false}"
DRY_RUN="${HOPX_DRY_RUN:-false}"

# Runtime state
PYTHON_CMD=""
PYTHON_VERSION=""
INSTALL_PATH=""
SHELL_CONFIG=""
PATH_MODIFIED="false"
OS_TYPE=""
ARCH_TYPE=""
USER_SHELL=""

# =============================================================================
# Color Setup
# =============================================================================
setup_colors() {
    # Disable colors if NO_COLOR is set, TERM is dumb, or not a terminal
    if [[ -n "${NO_COLOR:-}" ]] || [[ "${TERM:-}" == "dumb" ]] || [[ ! -t 1 ]]; then
        RED=''
        GREEN=''
        YELLOW=''
        BLUE=''
        CYAN=''
        NC=''
        BOLD=''
        DIM=''
    else
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        BLUE='\033[0;34m'
        CYAN='\033[0;36m'
        NC='\033[0m'
        BOLD='\033[1m'
        DIM='\033[2m'
    fi
}

# =============================================================================
# Logging Functions
# =============================================================================
log_info() {
    [[ "$QUIET" == "true" ]] && return
    printf "${BLUE}[INFO]${NC} %s\n" "$1" >&2
}

log_success() {
    printf "${GREEN}[OK]${NC} %s\n" "$1" >&2
}

log_warning() {
    printf "${YELLOW}[WARN]${NC} %s\n" "$1" >&2
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1" >&2
}

log_step() {
    [[ "$QUIET" == "true" ]] && return
    printf "\n${CYAN}${BOLD}=>${NC} ${BOLD}%s${NC}\n" "$1" >&2
}

log_debug() {
    [[ "${HOPX_DEBUG:-}" != "true" ]] && return
    printf "${DIM}[DEBUG] %s${NC}\n" "$1" >&2
}

# =============================================================================
# Input Validation
# =============================================================================
validate_inputs() {
    # Validate INSTALL_MODE
    case "$INSTALL_MODE" in
        pip|pipx|git)
            ;;
        *)
            log_error "Invalid HOPX_INSTALL_MODE: $INSTALL_MODE"
            log_info "Valid modes: pip, pipx, git"
            exit 2
            ;;
    esac

    # Validate boolean environment variables
    validate_boolean "HOPX_NON_INTERACTIVE" "$NON_INTERACTIVE"
    validate_boolean "HOPX_SKIP_PATH_SETUP" "$SKIP_PATH_SETUP"
    validate_boolean "HOPX_QUIET" "$QUIET"
    validate_boolean "HOPX_DRY_RUN" "$DRY_RUN"
}

validate_boolean() {
    local var_name="$1"
    local value="$2"

    case "$value" in
        true|false|1|0|yes|no|"")
            ;;
        *)
            log_error "Invalid $var_name value: $value"
            log_info "Valid values: true, false, 1, 0, yes, no"
            exit 2
            ;;
    esac
}

# Normalize boolean values
normalize_boolean() {
    local value="$1"
    case "$value" in
        true|1|yes)
            echo "true"
            ;;
        *)
            echo "false"
            ;;
    esac
}

# =============================================================================
# Utility Functions
# =============================================================================
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

is_interactive() {
    [[ -t 0 && -t 1 ]]
}

# Compare versions: returns 0 if $1 >= $2
version_gte() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Prompt user (respects NON_INTERACTIVE)
prompt_yes_no() {
    local message="$1"
    local default="${2:-n}"

    if [[ "$NON_INTERACTIVE" == "true" ]]; then
        [[ "$default" == "y" ]]
        return $?
    fi

    if ! is_interactive; then
        log_warning "Non-interactive mode detected, using default: $default"
        [[ "$default" == "y" ]]
        return $?
    fi

    local prompt
    if [[ "$default" == "y" ]]; then
        prompt="$message [Y/n] "
    else
        prompt="$message [y/N] "
    fi

    read -p "$prompt" -n 1 -r
    echo >&2

    if [[ -z "$REPLY" ]]; then
        [[ "$default" == "y" ]]
        return $?
    fi

    [[ $REPLY =~ ^[Yy]$ ]]
}

# =============================================================================
# Cleanup Handler
# =============================================================================
cleanup() {
    local exit_code=$?

    if [[ $exit_code -ne 0 && $exit_code -ne 130 ]]; then
        printf "\n" >&2
        log_error "Installation failed (exit code: $exit_code)"
        log_info "For help: https://docs.hopx.ai/cli/troubleshooting"
        log_info "Support: support@hopx.ai"
    fi

    exit $exit_code
}

trap cleanup EXIT
trap 'log_warning "Installation interrupted"; exit 130' INT TERM

# =============================================================================
# Print Header
# =============================================================================
print_header() {
    [[ "$QUIET" == "true" ]] && return

    printf "${CYAN}${BOLD}\n" >&2
    printf "  _   _                    ____ _     ___ \n" >&2
    printf " | | | | ___  _ __ __  __ / ___| |   |_ _|\n" >&2
    printf " | |_| |/ _ \\| '_ \\\\ \\/ /| |   | |    | | \n" >&2
    printf " |  _  | (_) | |_) |>  < | |___| |___ | | \n" >&2
    printf " |_| |_|\\___/| .__//_/\\_\\ \\____|_____|___|\n" >&2
    printf "             |_|          Installer v%s\n" "${SCRIPT_VERSION}" >&2
    printf "${NC}\n" >&2
}

# =============================================================================
# Platform Detection
# =============================================================================
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        log_error "Windows is not supported. Please use WSL (Windows Subsystem for Linux)."
        exit 1
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    ARCH_TYPE=$(uname -m)
    case "$ARCH_TYPE" in
        x86_64|amd64)
            ARCH_TYPE="x64"
            ;;
        aarch64|arm64)
            ARCH_TYPE="arm64"
            ;;
        *)
            log_warning "Unknown architecture: $ARCH_TYPE"
            ;;
    esac

    log_info "Detected: $OS_TYPE ($ARCH_TYPE)"
}

detect_package_manager() {
    if [[ "$OS_TYPE" == "macos" ]]; then
        if command_exists brew; then
            echo "brew"
        else
            echo "none"
        fi
    elif [[ "$OS_TYPE" == "linux" ]]; then
        if command_exists apt-get; then
            echo "apt"
        elif command_exists dnf; then
            echo "dnf"
        elif command_exists yum; then
            echo "yum"
        elif command_exists pacman; then
            echo "pacman"
        elif command_exists apk; then
            echo "apk"
        elif command_exists zypper; then
            echo "zypper"
        else
            echo "none"
        fi
    fi
}

detect_user_shell() {
    # Get user's default shell from $SHELL
    USER_SHELL="$(basename "${SHELL:-/bin/bash}")"
    log_debug "User shell: $USER_SHELL"
}

get_shell_config_file() {
    local shell_name="$1"

    case "$shell_name" in
        bash)
            if [[ "$OS_TYPE" == "macos" ]]; then
                # macOS uses .bash_profile for login shells
                if [[ -f "$HOME/.bash_profile" ]]; then
                    echo "$HOME/.bash_profile"
                elif [[ -f "$HOME/.bashrc" ]]; then
                    echo "$HOME/.bashrc"
                else
                    echo "$HOME/.bash_profile"
                fi
            else
                echo "$HOME/.bashrc"
            fi
            ;;
        zsh)
            echo "$HOME/.zshrc"
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            echo "$HOME/.profile"
            ;;
    esac
}

# =============================================================================
# Python Detection and Installation
# =============================================================================
detect_python() {
    local python_cmd=""
    local version=""

    # Try Python commands in order of preference
    for cmd in python3.13 python3.12 python3 python; do
        if command_exists "$cmd"; then
            version=$($cmd --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
            if version_gte "$version" "$MIN_PYTHON_VERSION"; then
                python_cmd="$cmd"
                PYTHON_VERSION=$($cmd --version 2>&1 | awk '{print $2}')
                break
            fi
        fi
    done

    if [[ -z "$python_cmd" ]]; then
        return 1
    fi

    PYTHON_CMD="$python_cmd"
    log_info "Found Python: $PYTHON_CMD (version $PYTHON_VERSION)"
    return 0
}

install_python() {
    local pkg_manager
    pkg_manager=$(detect_package_manager)

    log_step "Installing Python ${MIN_PYTHON_VERSION}+"

    case "$pkg_manager" in
        apt)
            install_python_apt
            ;;
        dnf)
            install_python_dnf
            ;;
        yum)
            install_python_yum
            ;;
        pacman)
            install_python_pacman
            ;;
        apk)
            install_python_apk
            ;;
        brew)
            install_python_brew
            ;;
        *)
            log_error "No supported package manager found."
            log_info "Please install Python ${MIN_PYTHON_VERSION}+ manually:"
            log_info "  https://www.python.org/downloads/"
            exit 1
            ;;
    esac
}

install_python_apt() {
    log_info "Using apt to install Python..."

    local commands=(
        "sudo apt-get update"
        "sudo apt-get install -y software-properties-common"
        "sudo add-apt-repository -y ppa:deadsnakes/ppa"
        "sudo apt-get update"
        "sudo apt-get install -y python3.12 python3.12-venv python3.12-distutils python3-pip"
    )

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would execute:"
        for cmd in "${commands[@]}"; do
            echo "  $cmd" >&2
        done
        return 0
    fi

    # Try direct install first (newer Ubuntu)
    if sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv python3-pip 2>/dev/null; then
        log_success "Python 3.12 installed"
        return 0
    fi

    # Fallback to deadsnakes PPA for older Ubuntu
    log_info "Adding deadsnakes PPA for Python 3.12..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-venv python3.12-distutils

    log_success "Python 3.12 installed via deadsnakes PPA"
}

install_python_dnf() {
    log_info "Using dnf to install Python..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: sudo dnf install -y python3.12 python3-pip"
        return 0
    fi

    sudo dnf install -y python3.12 python3-pip || {
        log_error "Failed to install Python 3.12 via dnf"
        log_info "Try: sudo dnf module enable python3.12 && sudo dnf install python3.12"
        exit 1
    }

    log_success "Python 3.12 installed"
}

install_python_yum() {
    log_info "Using yum to install Python..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: sudo yum install -y python3.12 python3-pip"
        return 0
    fi

    # Try EPEL repository for older RHEL/CentOS
    if ! sudo yum install -y python3.12 python3-pip 2>/dev/null; then
        log_info "Enabling EPEL repository..."
        sudo yum install -y epel-release || true
        sudo yum install -y python3.12 python3-pip
    fi

    log_success "Python 3.12 installed"
}

install_python_pacman() {
    log_info "Using pacman to install Python..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: sudo pacman -S --noconfirm python python-pip"
        return 0
    fi

    sudo pacman -Sy --noconfirm python python-pip
    log_success "Python installed"
}

install_python_apk() {
    log_info "Using apk to install Python..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: apk add --no-cache python3 py3-pip"
        return 0
    fi

    apk add --no-cache python3 py3-pip
    log_success "Python installed"
}

install_python_brew() {
    log_info "Using Homebrew to install Python..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: brew install python@3.12"
        return 0
    fi

    brew install python@3.12

    # Add Homebrew Python to PATH for this session
    if [[ -d "/opt/homebrew/opt/python@3.12/bin" ]]; then
        export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"
    elif [[ -d "/usr/local/opt/python@3.12/bin" ]]; then
        export PATH="/usr/local/opt/python@3.12/bin:$PATH"
    fi

    log_success "Python 3.12 installed via Homebrew"
}

ensure_pip() {
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        log_info "Installing pip..."

        if [[ "$DRY_RUN" == "true" ]]; then
            log_warning "DRY RUN: Would install pip"
            return 0
        fi

        $PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || {
            # Fallback: download get-pip.py
            log_info "Using get-pip.py..."
            curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
        }
    fi

    log_info "pip is available"
}

# =============================================================================
# Installation Functions
# =============================================================================
install_with_pip() {
    log_step "Installing Hopx CLI via pip..."

    local pip_args=(
        "$PYTHON_CMD" "-m" "pip" "install"
        "--upgrade"
        "$PYPI_PACKAGE"
    )

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: ${pip_args[*]} --user"
        return 0
    fi

    # Try user-level install first (no sudo needed)
    if "${pip_args[@]}" --user 2>/dev/null; then
        log_success "Installed $PYPI_PACKAGE (user-level)"
        INSTALL_PATH=$($PYTHON_CMD -m site --user-base)/bin
        return 0
    fi

    # Check for externally-managed-environment (PEP 668)
    if $PYTHON_CMD -m pip install --user "$PYPI_PACKAGE" 2>&1 | grep -q "externally-managed"; then
        log_warning "System Python is externally managed (PEP 668)"
        log_info "Switching to pipx installation..."
        install_with_pipx
        return $?
    fi

    # Fallback to system-wide install
    log_info "User-level install failed, trying system-wide..."
    if sudo "${pip_args[@]}"; then
        log_success "Installed $PYPI_PACKAGE (system-wide)"
        INSTALL_PATH="/usr/local/bin"
    else
        log_error "pip installation failed"
        log_info "Try: $PYTHON_CMD -m pip install --user $PYPI_PACKAGE"
        exit 1
    fi
}

install_with_pipx() {
    log_step "Installing Hopx CLI via pipx..."

    # Install pipx if not available
    if ! command_exists pipx; then
        log_info "Installing pipx..."

        if [[ "$DRY_RUN" == "true" ]]; then
            log_warning "DRY RUN: Would install pipx"
        else
            $PYTHON_CMD -m pip install --user pipx
            $PYTHON_CMD -m pipx ensurepath

            # Add pipx bin to current PATH
            export PATH="$HOME/.local/bin:$PATH"
        fi
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: pipx install $PYPI_PACKAGE"
        return 0
    fi

    # Install or upgrade the package
    if pipx list 2>/dev/null | grep -q "$PACKAGE_NAME"; then
        pipx upgrade "$PYPI_PACKAGE"
        log_success "Upgraded $PYPI_PACKAGE via pipx"
    else
        pipx install "$PYPI_PACKAGE"
        log_success "Installed $PYPI_PACKAGE via pipx"
    fi

    INSTALL_PATH="$HOME/.local/bin"
}

install_from_git() {
    log_step "Installing Hopx CLI from GitHub..."
    log_warning "Installing development version - may be unstable"

    local git_url="git+https://github.com/$GITHUB_REPO.git#subdirectory=cli"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: $PYTHON_CMD -m pip install --user $git_url"
        return 0
    fi

    if $PYTHON_CMD -m pip install --user "$git_url" 2>/dev/null; then
        log_success "Installed from GitHub (user-level)"
        INSTALL_PATH=$($PYTHON_CMD -m site --user-base)/bin
    else
        log_info "User-level install failed, trying system-wide..."
        sudo $PYTHON_CMD -m pip install "$git_url"
        log_success "Installed from GitHub (system-wide)"
        INSTALL_PATH="/usr/local/bin"
    fi
}

# =============================================================================
# PATH Setup
# =============================================================================
setup_path() {
    if [[ "$SKIP_PATH_SETUP" == "true" ]]; then
        log_info "Skipping PATH setup (HOPX_SKIP_PATH_SETUP=true)"
        return 0
    fi

    if [[ -z "$INSTALL_PATH" ]]; then
        # Note: site --user-base may return non-zero even on success
        INSTALL_PATH=$($PYTHON_CMD -m site --user-base 2>/dev/null || true)/bin
    fi

    # Check if already in PATH
    if [[ ":$PATH:" == *":$INSTALL_PATH:"* ]]; then
        log_info "PATH already configured"
        return 0
    fi

    log_step "Configuring PATH..."

    detect_user_shell
    SHELL_CONFIG=$(get_shell_config_file "$USER_SHELL")

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would add to $SHELL_CONFIG"
        return 0
    fi

    # Create config file if it doesn't exist
    if [[ ! -f "$SHELL_CONFIG" ]]; then
        mkdir -p "$(dirname "$SHELL_CONFIG")"
        touch "$SHELL_CONFIG"
    fi

    # Add PATH based on shell type
    if [[ "$USER_SHELL" == "fish" ]]; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Added by Hopx CLI installer" >> "$SHELL_CONFIG"
        echo "fish_add_path $INSTALL_PATH" >> "$SHELL_CONFIG"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# Added by Hopx CLI installer" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$INSTALL_PATH\"" >> "$SHELL_CONFIG"
    fi

    PATH_MODIFIED="true"
    log_success "Added to PATH in $SHELL_CONFIG"

    # Add to current session
    export PATH="$PATH:$INSTALL_PATH"
}

# =============================================================================
# Verification
# =============================================================================
verify_installation() {
    log_step "Verifying installation..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would verify with: hopx --version"
        return 0
    fi

    # Wait briefly for filesystem sync
    sleep 1

    if command_exists hopx; then
        local version
        version=$(hopx --version 2>&1 | head -n 1 || echo "unknown")
        log_success "Hopx CLI installed successfully!"
        log_info "Version: $version"
        return 0
    else
        log_warning "'hopx' command not found in current PATH"

        if [[ "$PATH_MODIFIED" == "true" ]]; then
            log_info "Restart your terminal or run: source $SHELL_CONFIG"
        else
            log_info "You may need to add $INSTALL_PATH to your PATH"
        fi

        return 0
    fi
}

# =============================================================================
# Summary and Quick Start
# =============================================================================
print_summary() {
    [[ "$QUIET" == "true" ]] && return

    printf "\n" >&2
    printf "${BOLD}Installation Summary${NC}\n" >&2
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" >&2
    printf "  %-20s %s\n" "Python:" "$PYTHON_CMD ($PYTHON_VERSION)" >&2
    printf "  %-20s %s\n" "Install mode:" "$INSTALL_MODE" >&2
    printf "  %-20s %s\n" "Install location:" "${INSTALL_PATH:-auto}" >&2
    printf "  %-20s %s\n" "Shell config:" "${SHELL_CONFIG:-not modified}" >&2
    printf "  %-20s %s\n" "PATH modified:" "$PATH_MODIFIED" >&2
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" >&2
}

print_quick_start() {
    [[ "$QUIET" == "true" ]] && return

    printf "\n" >&2
    printf "${GREEN}${BOLD}Installation Complete!${NC}\n" >&2
    printf "\n" >&2

    if [[ "$PATH_MODIFIED" == "true" ]]; then
        printf "${YELLOW}Note:${NC} Restart your terminal or run:\n" >&2
        printf "  ${CYAN}source %s${NC}\n" "$SHELL_CONFIG" >&2
        printf "\n" >&2
    fi

    printf "${BOLD}Quick Start:${NC}\n" >&2
    printf "\n" >&2
    printf "  ${CYAN}1.${NC} Set your API key:\n" >&2
    printf "     ${DIM}export HOPX_API_KEY=\"hopx_live_...\"${NC}\n" >&2
    printf "\n" >&2
    printf "  ${CYAN}2.${NC} Run your first command:\n" >&2
    printf "     ${DIM}hopx run \"print('Hello from Hopx!')\"${NC}\n" >&2
    printf "\n" >&2
    printf "  ${CYAN}3.${NC} Explore commands:\n" >&2
    printf "     ${DIM}hopx --help${NC}\n" >&2
    printf "\n" >&2
    printf "${BOLD}Common Commands:${NC}\n" >&2
    printf "  hopx run \"code\"          Execute code in sandbox\n" >&2
    printf "  hopx sandbox list        List active sandboxes\n" >&2
    printf "  hopx template list       List available templates\n" >&2
    printf "  hopx self-update         Update to latest version\n" >&2
    printf "\n" >&2
    printf "${BOLD}Resources:${NC}\n" >&2
    printf "  Docs:    ${CYAN}https://docs.hopx.ai/cli${NC}\n" >&2
    printf "  Discord: ${CYAN}https://discord.gg/hopx${NC}\n" >&2
    printf "  Support: ${CYAN}support@hopx.ai${NC}\n" >&2
    printf "\n" >&2
}

# =============================================================================
# Argument Parsing
# =============================================================================
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN="true"
                ;;
            --non-interactive|-y)
                NON_INTERACTIVE="true"
                ;;
            --quiet|-q)
                QUIET="true"
                ;;
            --mode)
                INSTALL_MODE="$2"
                shift
                ;;
            --skip-path)
                SKIP_PATH_SETUP="true"
                ;;
            --help|-h)
                print_help
                exit 0
                ;;
            --version)
                echo "Hopx CLI Installer v$SCRIPT_VERSION"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                log_info "Run with --help for usage"
                exit 1
                ;;
        esac
        shift
    done
}

print_help() {
    cat << EOF
Hopx CLI Installer v$SCRIPT_VERSION

Usage: $0 [OPTIONS]

Options:
  --mode MODE       Installation mode: pip (default), pipx, git
  --dry-run         Preview changes without installing
  --non-interactive Skip all prompts (use defaults)
  --quiet           Minimal output
  --skip-path       Don't modify shell configuration
  --help            Show this help message
  --version         Show installer version

Environment Variables:
  HOPX_INSTALL_MODE      Installation mode (pip, pipx, git)
  HOPX_NON_INTERACTIVE   Skip prompts (true/false)
  HOPX_SKIP_PATH_SETUP   Don't modify PATH (true/false)
  HOPX_QUIET             Minimal output (true/false)
  HOPX_DRY_RUN           Preview mode (true/false)

Examples:
  # Standard installation
  curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash

  # CI/CD installation
  HOPX_NON_INTERACTIVE=true curl -fsSL ... | bash

  # Install with pipx
  curl -fsSL ... | bash -s -- --mode pipx

  # Dry run
  bash install.sh --dry-run

EOF
}

# =============================================================================
# Main
# =============================================================================
main() {
    parse_arguments "$@"

    # Normalize boolean values
    NON_INTERACTIVE=$(normalize_boolean "$NON_INTERACTIVE")
    SKIP_PATH_SETUP=$(normalize_boolean "$SKIP_PATH_SETUP")
    QUIET=$(normalize_boolean "$QUIET")
    DRY_RUN=$(normalize_boolean "$DRY_RUN")

    setup_colors
    validate_inputs

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    print_header

    # Detect system
    log_step "Detecting system configuration..."
    detect_os

    # Check/install Python
    log_step "Checking Python installation..."
    if ! detect_python; then
        log_warning "Python ${MIN_PYTHON_VERSION}+ not found"
        install_python

        # Re-detect after installation
        if ! detect_python; then
            log_error "Python installation failed or version too old"
            exit 1
        fi
    fi

    # Ensure pip
    ensure_pip

    # Install based on mode
    case "$INSTALL_MODE" in
        pip)
            install_with_pip
            ;;
        pipx)
            install_with_pipx
            ;;
        git)
            install_from_git
            ;;
    esac

    # Setup PATH
    setup_path

    # Verify and show results
    verify_installation
    print_summary
    print_quick_start
}

main "$@"
