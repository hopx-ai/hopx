# Hopx CLI

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)

Official command-line interface for [Hopx.ai](https://hopx.ai) cloud sandboxes.

## What is Hopx CLI?

Hopx CLI provides terminal access to Hopx.ai cloud sandboxes - secure, isolated VMs that start in seconds. Execute code, manage files, run commands, and build custom templates from your terminal.

**Use cases:**
- AI agent code execution
- Running untrusted code safely
- Integration testing
- Data processing pipelines
- Browser automation
- Educational environments

## Installation

### Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/hopx-ai/hopx/main/cli/scripts/install.sh | bash
```

Handles everything automatically, including PEP 668 environments on macOS/modern Linux.

### Alternative Methods

**uv** (fastest):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install hopx-cli
```

**pipx** (isolated):
```bash
pipx install hopx-cli
```

**pip**:
```bash
pip install --user hopx-cli
```

### Update

```bash
hopx self-update
```

See [INSTALL.md](INSTALL.md) for detailed options and troubleshooting.

## Quick Start

### First-Time Setup

```bash
# Interactive setup wizard
hopx init

# Or manual setup
hopx auth login
hopx auth keys create --name "my-key"
```

### Run Code

```bash
# Execute Python code
hopx run "print('Hello, World!')"

# Execute from file
hopx run -f script.py

# Execute JavaScript
hopx run "console.log('Hello')" -l javascript

# Execute Bash
hopx run "ls -la" -l bash
```

### Manage Sandboxes

```bash
# Create sandbox
hopx sandbox create --template python

# List sandboxes
hopx sandbox list

# Pause/resume
hopx sandbox pause SANDBOX_ID
hopx sandbox resume SANDBOX_ID

# Kill sandbox
hopx sandbox kill SANDBOX_ID
```

## Authentication

### Browser Login (Recommended)

```bash
hopx auth login
hopx auth keys create --name "production"
```

### Environment Variable

```bash
export HOPX_API_KEY="hopx_live_..."
```

Get your API key at [hopx.ai/dashboard](https://hopx.ai/dashboard).

### Check Status

```bash
hopx auth status
```

## Commands

### Code Execution (`run`)

Execute code in sandboxes:

```bash
# Python (default)
hopx run "import sys; print(sys.version)"

# JavaScript
hopx run "console.log(process.version)" -l javascript

# Bash
hopx run "echo $PATH" -l bash

# From file
hopx run -f script.py

# With environment variables
hopx run "import os; print(os.environ['API_KEY'])" -e API_KEY=secret

# In existing sandbox
hopx run "print('Hello')" --sandbox SANDBOX_ID

# With timeout
hopx run "import time; time.sleep(60)" --timeout 120
```

### Sandbox Management (`sandbox`, `sb`)

```bash
# Create with template
hopx sandbox create --template python

# Create with timeout (auto-kill after 1 hour)
hopx sandbox create --template nodejs --timeout 3600

# List all sandboxes
hopx sandbox list

# List running only
hopx sandbox list --status running

# Get sandbox info
hopx sandbox info SANDBOX_ID

# Pause sandbox (preserves state, saves resources)
hopx sandbox pause SANDBOX_ID

# Resume paused sandbox
hopx sandbox resume SANDBOX_ID

# Kill sandbox
hopx sandbox kill SANDBOX_ID

# Force kill without confirmation
hopx sandbox kill SANDBOX_ID --force

# Get preview URL for port
hopx sandbox url SANDBOX_ID --port 8080
```

### File Operations (`files`, `f`)

```bash
# Write file
hopx files write SANDBOX_ID /app/config.json '{"key": "value"}'

# Write from stdin
cat local.txt | hopx files write SANDBOX_ID /app/data.txt --data -

# Read file
hopx files read SANDBOX_ID /app/config.json

# List directory
hopx files list SANDBOX_ID /app/

# Delete file
hopx files delete SANDBOX_ID /app/temp.txt

# Upload local file
hopx files upload SANDBOX_ID ./local.csv /app/data.csv

# Download file
hopx files download SANDBOX_ID /app/result.csv ./result.csv
```

### Shell Commands (`cmd`)

```bash
# Run command
hopx cmd run SANDBOX_ID "ls -la /app"

# Run with timeout
hopx cmd run SANDBOX_ID "npm install" --timeout 300

# Run in background
hopx cmd run SANDBOX_ID "python server.py" --background

# Chain commands
hopx cmd run SANDBOX_ID "cd /app && npm install && npm test"
```

### Environment Variables (`env`)

```bash
# List variables
hopx env list SANDBOX_ID

# Get variable
hopx env get SANDBOX_ID API_KEY

# Set variable
hopx env set SANDBOX_ID API_KEY=secret

# Set multiple
hopx env set SANDBOX_ID API_KEY=secret DEBUG=true

# Delete variable
hopx env delete SANDBOX_ID DEBUG

# Load from file
hopx env load SANDBOX_ID .env
```

### Interactive Terminal (`terminal`, `term`)

```bash
# Connect to sandbox terminal
hopx terminal connect SANDBOX_ID

# Get terminal info
hopx terminal info SANDBOX_ID

# Get WebSocket URL
hopx terminal url SANDBOX_ID
```

### Templates (`template`, `tpl`)

```bash
# List available templates
hopx template list

# Get template info
hopx template info python

# Build custom template
hopx template build --name my-app --dockerfile ./Dockerfile

# Delete custom template
hopx template delete TEMPLATE_ID
```

### Configuration (`config`)

```bash
# Show current config
hopx config show

# Set value
hopx config set default_template python
hopx config set output_format json

# Get value
hopx config get default_template

# Show config file path
hopx config path

# List profiles
hopx config profiles list

# Create profile
hopx config profiles create production

# Switch profile
hopx config profiles use production
```

### System (`system`)

```bash
# Check API health
hopx system health

# Get sandbox metrics
hopx system metrics SANDBOX_ID

# Get agent info
hopx system agent-info SANDBOX_ID
```

## Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `init` | - | First-run setup wizard |
| `auth` | - | Authentication management |
| `sandbox` | `sb` | Manage sandbox lifecycle |
| `run` | - | Execute code in sandboxes |
| `files` | `f` | File operations |
| `cmd` | - | Run shell commands |
| `env` | - | Manage environment variables |
| `terminal` | `term` | Interactive terminal sessions |
| `template` | `tpl` | Manage templates |
| `config` | - | Configuration management |
| `system` | - | Health checks and metrics |
| `org` | - | Organization settings |
| `profile` | - | User profile management |
| `usage` | - | Usage statistics |
| `members` | - | Organization members |
| `billing` | - | Billing information |
| `self-update` | - | Update CLI to latest version |

## Global Options

```
--api-key TEXT      API key (overrides HOPX_API_KEY)
--profile TEXT      Configuration profile (default: "default")
--output, -o FORMAT Output format: table, json, plain
-q, --quiet         Suppress non-essential output
-v, --verbose       Increase output verbosity
--no-color          Disable colored output
--version           Show version and exit
--help              Show help message
```

## Output Formats

### Table (default)

```bash
hopx sandbox list
```
```
┌──────────────────┬─────────┬────────────┐
│ ID               │ Status  │ Template   │
├──────────────────┼─────────┼────────────┤
│ sb_abc123        │ running │ python     │
│ sb_def456        │ paused  │ nodejs     │
└──────────────────┴─────────┴────────────┘
```

### JSON

```bash
hopx sandbox list -o json
```
```json
[
  {"id": "sb_abc123", "status": "running", "template": "python"},
  {"id": "sb_def456", "status": "paused", "template": "nodejs"}
]
```

### Plain

```bash
hopx sandbox list -o plain
```
```
sb_abc123 running python
sb_def456 paused nodejs
```

## Shell Scripting

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | Authentication error |
| 4 | Not found |
| 5 | Timeout |
| 6 | Network error |
| 7 | Rate limit |
| 130 | Interrupted (Ctrl+C) |

### JSON Output for Scripting

```bash
# Get sandbox ID from JSON output
SANDBOX_ID=$(hopx sandbox create -t python -o json | jq -r '.sandbox_id')

# List running sandboxes
hopx sandbox list --status running -o json | jq '.[] | .sandbox_id'

# Check if sandbox exists
if hopx sandbox info sb_123 -o json 2>/dev/null; then
    echo "Sandbox exists"
fi
```

### Conditional Logic

```bash
hopx sandbox create --template python
case $? in
    0) echo "Success" ;;
    3) echo "Authentication failed - check API key" ;;
    4) echo "Template not found" ;;
    7) echo "Rate limit exceeded - wait and retry" ;;
    *) echo "Error occurred" ;;
esac
```

### Piping

```bash
# Upload file content
cat script.py | hopx files write $SANDBOX_ID /app/script.py --data -

# Execute code from stdin
echo "print(42)" | hopx run -

# Process sandbox list
hopx sandbox list -o json | jq -r '.[].id' | while read id; do
    echo "Processing $id"
done
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOPX_API_KEY` | API key for authentication | - |
| `HOPX_PROFILE` | Configuration profile name | `default` |
| `HOPX_BASE_URL` | API base URL | `https://api.hopx.dev` |
| `HOPX_DEFAULT_TEMPLATE` | Default template | `code-interpreter` |
| `HOPX_DEFAULT_TIMEOUT` | Default timeout (seconds) | `3600` |
| `HOPX_OUTPUT_FORMAT` | Default output format | `table` |
| `NO_COLOR` | Disable colored output | - |

### Config File

Location: `~/.hopx/config.yaml`

```yaml
default:
  api_key: hopx_live_...
  base_url: https://api.hopx.dev
  default_template: code-interpreter
  default_timeout: 3600
  output_format: table

production:
  api_key: hopx_live_prod_...
  default_template: python
```

### Profiles

```bash
# Create profile
hopx config profiles create staging

# Switch profile
hopx config profiles use staging

# Use profile for single command
hopx --profile production sandbox list
```

## Pre-built Templates

| Template | Description |
|----------|-------------|
| `python` | Python 3.11 with pip, numpy, pandas, requests |
| `nodejs` | Node.js 20 with npm |
| `code-interpreter` | Python with data science stack |
| `go` | Go 1.21 |
| `rust` | Rust with Cargo |
| `java` | Java 17 with Maven |

## Troubleshooting

### Command Not Found

```bash
# Check if installed
pip show hopx-cli

# Add to PATH
export PATH="$PATH:$(python3 -m site --user-base)/bin"
```

### Authentication Failed

```bash
# Check auth status
hopx auth status

# Re-authenticate
hopx auth login
hopx auth keys create --name "new-key"

# Validate API key
hopx auth validate
```

### Sandbox Creation Fails

```bash
# Check available templates
hopx template list

# Check system health
hopx system health

# Try with verbose output
hopx -v sandbox create --template python
```

### Template Not Found

```bash
# List available templates
hopx template list

# Check template name
hopx template info python
```

## Documentation

- [Full Documentation](https://docs.hopx.ai/cli)
- [Installation Guide](INSTALL.md)
- [Python SDK](https://github.com/hopx-ai/hopx/tree/main/python)
- [JavaScript SDK](https://github.com/hopx-ai/hopx/tree/main/javascript)

## Support

- Email: support@hopx.ai
- Discord: [discord.gg/hopx](https://discord.gg/hopx)
- GitHub Issues: [github.com/hopx-ai/hopx/issues](https://github.com/hopx-ai/hopx/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Website](https://hopx.ai)
- [Dashboard](https://hopx.ai/dashboard)
- [GitHub](https://github.com/hopx-ai/hopx)
- [Discord](https://discord.gg/hopx)
