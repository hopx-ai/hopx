# Sandbox Integration Tests

This directory contains integration tests for the `Sandbox` class, organized by feature area.

## Directory Structure

Each test class is in its own file, organized into folders by functionality:

```
sandbox/
├── creation/
│   └── sandbox_creation.py               # TestSandboxCreation
├── connection/
│   └── sandbox_connection.py             # TestSandboxConnection
├── info/
│   └── sandbox_info.py                   # TestSandboxInfo
├── lifecycle/
│   └── sandbox_lifecycle.py              # TestSandboxLifecycle
├── listing/
│   └── sandbox_listing.py                # TestSandboxListing
├── templates/
│   └── template_operations.py           # TestTemplateOperations, TestHealthCheck
├── code_execution/
│   ├── code_execution.py                 # TestCodeExecution
│   ├── rich_output.py                    # TestRichOutput
│   ├── background_execution.py           # TestBackgroundExecution
│   └── code_execution_with_resources.py  # TestCodeExecutionWithResources
└── resources/
    ├── files/
    │   └── files_resource.py             # TestFilesResource
    ├── commands/
    │   └── commands_resource.py          # TestCommandsResource
    ├── env_vars/
    │   └── env_vars_resource.py          # TestEnvironmentVariables
    ├── cache/
    │   └── cache_resource.py             # TestCacheResource
    └── agent_info/
        └── agent_info.py                 # TestAgentInfo
```

## Running Tests

### Run all sandbox integration tests:
```bash
pytest python/tests/integration/sandbox/
```

### Run tests for a specific feature:
```bash
pytest python/tests/integration/sandbox/creation/
pytest python/tests/integration/sandbox/lifecycle/
pytest python/tests/integration/sandbox/code_execution/
```

### Run a specific test class:
```bash
pytest python/tests/integration/sandbox/creation/sandbox_creation.py
```

### Run a specific test:
```bash
pytest python/tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_from_template_name
```

## Test Organization Principles

1. **One class per file** - Each test class is in its own file for easier navigation and maintenance.
2. **Feature-based folders** - Tests are grouped by functionality (creation, lifecycle, code_execution, etc.).
3. **Clear naming** - File names follow the pattern `<class_name>.py` (without `test_` prefix) where the class name is in CamelCase (e.g., `sandbox_creation.py` for `TestSandboxCreation`).
4. **Shared fixtures** - Common fixtures (api_key, sandbox) are defined in each test file or can be moved to `conftest.py` if shared across multiple files.

## Adding New Tests

When adding new tests:

1. **Identify the feature area** - Determine which folder the test belongs to.
2. **Create or update the test file** - If a test class already exists, add to it. Otherwise, create a new file.
3. **Follow naming conventions** - Use `<class_name>.py` for the filename (without `test_` prefix, e.g., `sandbox_creation.py`).
4. **Include docstrings** - Add a module docstring describing what the test class covers.

**Note:** Pytest is configured to discover all `.py` files in the tests directory, so the `test_` prefix is not required in file names.

