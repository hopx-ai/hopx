#!/bin/bash
# Hopx CLI Uninstaller v2.0.0
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/uninstall.sh | bash
#   bash scripts/uninstall.sh
#
# Environment variables:
#   HOPX_NON_INTERACTIVE  - Skip all prompts (true/false)
#   HOPX_FULL_CLEAN       - Remove all config and cache (true/false)
#   HOPX_DRY_RUN          - Preview without changes (true/false)
#
# Source: https://github.com/hopx-ai/hopx/tree/main/cli

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_VERSION="2.0.0"
PACKAGE_NAME="hopx-cli"

# Environment variable defaults
NON_INTERACTIVE="${HOPX_NON_INTERACTIVE:-false}"
FULL_CLEAN="${HOPX_FULL_CLEAN:-false}"
DRY_RUN="${HOPX_DRY_RUN:-false}"

# =============================================================================
# Color Setup
# =============================================================================
setup_colors() {
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
    printf "\n${CYAN}${BOLD}=>${NC} ${BOLD}%s${NC}\n" "$1" >&2
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

prompt_yes_no() {
    local message="$1"
    local default="${2:-n}"

    if [[ "$NON_INTERACTIVE" == "true" ]]; then
        [[ "$default" == "y" ]]
        return $?
    fi

    if ! is_interactive; then
        log_warning "Non-interactive mode, using default: $default"
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
# Print Header
# =============================================================================
print_header() {
    printf "${CYAN}${BOLD}\n" >&2
    printf "  _   _                    ____ _     ___ \n" >&2
    printf " | | | | ___  _ __ __  __ / ___| |   |_ _|\n" >&2
    printf " | |_| |/ _ \\| '_ \\\\ \\/ /| |   | |    | | \n" >&2
    printf " |  _  | (_) | |_) |>  < | |___| |___ | | \n" >&2
    printf " |_| |_|\\___/| .__//_/\\_\\ \\____|_____|___|\n" >&2
    printf "             |_|        Uninstaller v%s\n" "${SCRIPT_VERSION}" >&2
    printf "${NC}\n" >&2
}

# =============================================================================
# Python Detection
# =============================================================================
find_python() {
    for cmd in python3.13 python3.12 python3 python; do
        if command_exists "$cmd"; then
            echo "$cmd"
            return 0
        fi
    done
    return 1
}

# =============================================================================
# Uninstall Functions
# =============================================================================
uninstall_pip() {
    local python_cmd="$1"

    log_step "Uninstalling via pip..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: $python_cmd -m pip uninstall -y $PACKAGE_NAME"
        return 0
    fi

    # Try user-level uninstall
    if $python_cmd -m pip uninstall -y "$PACKAGE_NAME" 2>/dev/null; then
        log_success "Uninstalled $PACKAGE_NAME"
        return 0
    fi

    # Try system-wide with sudo
    if sudo -v 2>/dev/null; then
        sudo $python_cmd -m pip uninstall -y "$PACKAGE_NAME" 2>/dev/null || true
        log_success "Uninstalled $PACKAGE_NAME (system-wide)"
    fi
}

uninstall_pipx() {
    log_step "Checking pipx..."

    if ! command_exists pipx; then
        log_info "pipx not found, skipping"
        return 0
    fi

    if ! pipx list 2>/dev/null | grep -q "$PACKAGE_NAME"; then
        log_info "Package not installed via pipx"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: pipx uninstall $PACKAGE_NAME"
        return 0
    fi

    pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
    log_success "Uninstalled from pipx"
}

uninstall_uv() {
    log_step "Checking uv..."

    if ! command_exists uv; then
        log_info "uv not found, skipping"
        return 0
    fi

    if ! uv tool list 2>/dev/null | grep -q "$PACKAGE_NAME"; then
        log_info "Package not installed via uv"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would run: uv tool uninstall $PACKAGE_NAME"
        return 0
    fi

    uv tool uninstall "$PACKAGE_NAME" 2>/dev/null || true
    log_success "Uninstalled from uv"
}

# =============================================================================
# Cleanup Functions
# =============================================================================
clean_config() {
    log_step "Configuration files..."

    local config_dirs=(
        "$HOME/.hopx"
        "$HOME/.config/hopx"
    )

    local config_files=(
        "$HOME/.hopxrc"
        "$HOME/.hopx.yaml"
        "$HOME/.hopx.yml"
    )

    # Check if any config exists
    local found=false
    for dir in "${config_dirs[@]}"; do
        [[ -d "$dir" ]] && found=true
    done
    for file in "${config_files[@]}"; do
        [[ -f "$file" ]] && found=true
    done

    if [[ "$found" == "false" ]]; then
        log_info "No configuration files found"
        return 0
    fi

    # Ask for confirmation unless FULL_CLEAN
    if [[ "$FULL_CLEAN" != "true" ]]; then
        log_warning "This will delete API keys and settings"
        if ! prompt_yes_no "Remove configuration files?" "n"; then
            log_info "Keeping configuration files"
            return 0
        fi
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would remove configuration files"
        return 0
    fi

    # Remove directories
    for dir in "${config_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            log_info "Removed: $dir"
        fi
    done

    # Remove files
    for file in "${config_files[@]}"; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            log_info "Removed: $file"
        fi
    done

    log_success "Configuration files cleaned"
}

clean_cache() {
    log_step "Cache files..."

    local cache_dirs=(
        "$HOME/.cache/hopx"
        "$HOME/Library/Caches/hopx"
    )

    local found=false
    for dir in "${cache_dirs[@]}"; do
        [[ -d "$dir" ]] && found=true
    done

    if [[ "$found" == "false" ]]; then
        log_info "No cache files found"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would remove cache files"
        return 0
    fi

    for dir in "${cache_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            rm -rf "$dir"
            log_info "Removed: $dir"
        fi
    done

    log_success "Cache cleaned"
}

clean_path() {
    log_step "Shell configuration..."

    local shell_configs=(
        "$HOME/.bashrc"
        "$HOME/.bash_profile"
        "$HOME/.zshrc"
        "$HOME/.profile"
        "$HOME/.config/fish/config.fish"
    )

    local found_entries=false
    for config in "${shell_configs[@]}"; do
        if [[ -f "$config" ]] && grep -q "Added by Hopx CLI installer" "$config" 2>/dev/null; then
            found_entries=true
            log_info "Found Hopx entry in $config"
        fi
    done

    if [[ "$found_entries" == "false" ]]; then
        log_info "No PATH entries found"
        return 0
    fi

    if [[ "$FULL_CLEAN" != "true" ]]; then
        if ! prompt_yes_no "Remove PATH entries from shell configs?" "n"; then
            log_info "Keeping PATH entries"
            return 0
        fi
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would remove PATH entries"
        return 0
    fi

    for config in "${shell_configs[@]}"; do
        if [[ -f "$config" ]] && grep -q "Added by Hopx CLI installer" "$config" 2>/dev/null; then
            # Create backup
            cp "$config" "${config}.hopx.bak"

            # Remove Hopx lines (comment and following export line)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' '/# Added by Hopx CLI installer/,+1d' "$config" 2>/dev/null || true
            else
                sed -i '/# Added by Hopx CLI installer/,+1d' "$config" 2>/dev/null || true
            fi

            log_info "Cleaned: $config (backup: ${config}.hopx.bak)"
        fi
    done

    log_success "PATH entries removed"
    log_warning "Restart your terminal for changes to take effect"
}

# =============================================================================
# Verification
# =============================================================================
verify_uninstall() {
    log_step "Verifying uninstallation..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN: Would verify uninstallation"
        return 0
    fi

    # Check if hopx command still exists
    if command_exists hopx; then
        log_warning "'hopx' command still found"
        log_info "Location: $(which hopx)"
        log_info "You may need to restart your terminal"
        return 1
    fi

    log_success "Hopx CLI successfully uninstalled"
    return 0
}

# =============================================================================
# Completion Message
# =============================================================================
print_completion() {
    printf "\n" >&2
    printf "${GREEN}${BOLD}Hopx CLI Uninstalled${NC}\n" >&2
    printf "\n" >&2
    printf "Thank you for using Hopx CLI!\n" >&2
    printf "\n" >&2
    printf "${BOLD}Feedback:${NC}\n" >&2
    printf "  Discord: ${CYAN}https://discord.gg/hopx${NC}\n" >&2
    printf "  Email:   ${CYAN}support@hopx.ai${NC}\n" >&2
    printf "\n" >&2
    printf "${BOLD}Reinstall:${NC}\n" >&2
    printf "  ${DIM}curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash${NC}\n" >&2
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
            --full)
                FULL_CLEAN="true"
                ;;
            --non-interactive|-y)
                NON_INTERACTIVE="true"
                ;;
            --help|-h)
                print_help
                exit 0
                ;;
            --version)
                echo "Hopx CLI Uninstaller v$SCRIPT_VERSION"
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
Hopx CLI Uninstaller v$SCRIPT_VERSION

Usage: $0 [OPTIONS]

Options:
  --dry-run         Preview changes without uninstalling
  --full            Remove all files without prompting
  --non-interactive Skip all prompts
  --help            Show this help message
  --version         Show uninstaller version

Environment Variables:
  HOPX_NON_INTERACTIVE   Skip prompts (true/false)
  HOPX_FULL_CLEAN        Full cleanup (true/false)
  HOPX_DRY_RUN           Preview mode (true/false)

Examples:
  # Interactive uninstall
  bash uninstall.sh

  # Full cleanup without prompts
  bash uninstall.sh --full --non-interactive

  # Preview what would be removed
  bash uninstall.sh --dry-run

EOF
}

# =============================================================================
# Main
# =============================================================================
main() {
    parse_arguments "$@"

    # Normalize booleans
    NON_INTERACTIVE=$(normalize_boolean "$NON_INTERACTIVE")
    FULL_CLEAN=$(normalize_boolean "$FULL_CLEAN")
    DRY_RUN=$(normalize_boolean "$DRY_RUN")

    setup_colors
    print_header

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    # Confirm uninstallation
    # Skip confirmation if NON_INTERACTIVE or FULL_CLEAN (--full implies yes)
    if [[ "$NON_INTERACTIVE" != "true" && "$FULL_CLEAN" != "true" ]]; then
        printf "\n" >&2
        printf "${YELLOW}This will uninstall Hopx CLI from your system.${NC}\n" >&2
        printf "\n" >&2

        if ! prompt_yes_no "Continue?" "n"; then
            log_info "Uninstallation cancelled"
            exit 0
        fi
    fi

    # Find Python
    log_step "Looking for Python..."
    local python_cmd=""
    if python_cmd=$(find_python); then
        log_info "Found: $python_cmd"
    else
        log_warning "Python not found, skipping pip uninstall"
    fi

    # Uninstall from various sources
    [[ -n "$python_cmd" ]] && uninstall_pip "$python_cmd"
    uninstall_pipx
    uninstall_uv

    # Cleanup
    clean_config
    clean_cache
    clean_path

    # Verify
    if verify_uninstall; then
        print_completion
    else
        log_warning "Uninstallation completed with warnings"
    fi
}

main "$@"
