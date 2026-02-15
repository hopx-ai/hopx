# Integration Tests

This directory contains integration tests for the Hopx Python SDK.

## Organization

Tests are organized by SDK class/feature, with each test class in its own file:

```
integration/
├── sandbox/
│   ├── creation/
│   │   └── sandbox_creation.py
│   ├── connection/
│   │   └── sandbox_connection.py
│   ├── info/
│   │   └── sandbox_info.py
│   ├── lifecycle/
│   │   └── sandbox_lifecycle.py
│   ├── listing/
│   │   └── sandbox_listing.py
│   ├── templates/
│   │   └── template_operations.py
│   ├── code_execution/
│   │   ├── code_execution.py
│   │   ├── rich_output.py
│   │   ├── background_execution.py
│   │   └── code_execution_with_resources.py
│   └── resources/
│       ├── files/
│       │   └── files_resource.py
│       ├── commands/
│       │   └── commands_resource.py
│       ├── env_vars/
│       │   └── env_vars_resource.py
│       ├── cache/
│       │   └── cache_resource.py
│       └── agent_info/
│           └── agent_info.py
└── [other features...]
```

## Principles

1. **One class per file** - Each test class is in its own file for easier navigation and maintenance.
2. **Feature-based organization** - Tests are grouped into folders by functionality.
3. **Clear naming** - Files follow the pattern `<class_name>.py` (without `test_` prefix, e.g., `sandbox_creation.py`).
4. **Self-contained** - Each test file includes necessary fixtures and setup.

**Note:** Pytest is configured to discover all `.py` files in the tests directory, so the `test_` prefix is not required in file names.

## Running Tests

See the main [tests README](../README.md) for instructions on running tests

