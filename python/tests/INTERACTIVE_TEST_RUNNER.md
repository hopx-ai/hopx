# Interactive Test Runner

An interactive, hierarchical test runner that allows you to navigate and run tests at any level.

## Usage

Run from the `python/` directory:

```bash
python3 tests/run_tests_interactive.py
```

Or make it executable and run directly:

```bash
chmod +x tests/run_tests_interactive.py
./tests/run_tests_interactive.py
```

## Navigation

The script provides a hierarchical menu system:

### Level 1: Test Suite Selection
- **integration** - All integration tests
- **e2e** - All end-to-end tests

### Level 2: Category Selection
After selecting a suite, you'll see categories (directories):
- **sandbox/** - Sandbox-related tests
- **async_sandbox/** - Async sandbox tests
- **desktop/** - Desktop automation tests
- **template/** - Template building tests
- **terminal/** - Terminal/WebSocket tests

### Level 3: Test File Selection
After selecting a category, you'll see test files:
- Each file shows: `filename.py (X classes, Y methods)`
- Select a file to see its test classes

### Level 4: Test Class Selection
After selecting a file, you'll see test classes:
- Each class can be run individually
- Select a class to see its test methods

### Level 5: Test Method Selection
After selecting a class, you'll see individual test methods:
- Each method can be run individually

## Features

### Run All Option
At every level, you can select **"Run All Tests"** to execute all tests at that level:
- Suite level: Run all integration or e2e tests
- Category level: Run all tests in that category
- File level: Run all tests in that file
- Class level: Run all tests in that class

### Navigation
- **← Back** - Return to the previous menu level
- **Run All** - Execute all tests at current level
- **Number selection** - Navigate deeper or run specific test

### Test Execution
When you select a test to run:
- Tests execute with verbose output (`-v --showlocals`)
- HTML and JUnit XML reports are automatically generated
- Reports are saved to `tests/reports/` with organized folder structure
- Results are displayed with color-coded output

## Report Structure

Reports are automatically saved to:
```
tests/reports/
├── integration_sandbox_code_execution_code_execution/
│   ├── report.html
│   └── junit.xml
├── integration_sandbox_code_execution_code_execution_testcodeexecution/
│   ├── report.html
│   └── junit.xml
└── ...
```

## Keyboard Shortcuts

- **Ctrl+C** - Exit the interactive runner at any time
- **Enter** - Confirm selection or continue after test execution

## Example Workflow

1. Start the script: `python3 tests/run_tests_interactive.py`
2. Select `1` for **integration** tests
3. Select `1` for **sandbox** category
4. Select `1` for **code_execution** file
5. Select `1` for **TestCodeExecution** class
6. Select `1` for **test_run_simple_code** method
7. Test executes with reports generated
8. Press Enter to return to menu
9. Use "← Back" to navigate back up the hierarchy

## Requirements

- Python 3.8+
- pytest installed
- pytest-html installed (for HTML reports)
- All test dependencies installed

## Notes

- The script automatically builds the test hierarchy on startup
- Test classes must start with `Test` to be detected
- Test methods must start with `test_` to be detected
- Reports are generated in the same directory structure as the test organization

