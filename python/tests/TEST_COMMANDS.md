# Test Execution Commands
This document provides commands to run tests individually by file, class, or method.
All commands should be run from the `python/` directory.

## Report Options

All commands can be enhanced with the following options:

- **Verbose output**: Add `-v` or `-vv` for more detailed output
- **Show locals on failure**: Add `--showlocals`
- **Generate HTML report**: Add `--html=reports/path/to/report.html --self-contained-html`
- **Generate JUnit XML**: Add `--junitxml=reports/path/to/junit.xml`
- **Show print statements**: Add `-s` (don't capture output)

Reports will be saved to `tests/reports/` with organized folder structure:
- File-level reports: `tests/reports/{category}/{filename}/`
- Class-level reports: `tests/reports/{category}/{filename}/{classname}/`
- Method-level reports: `tests/reports/{category}/{filename}/{classname}/{methodname}/`

**Note:** Report directories will be created automatically by pytest when generating reports.

---

## e2e → async_sandbox

### async_sandbox_complete_workflow_e2e.py

**File Path:** `tests/e2e/async_sandbox/async_sandbox_complete_workflow_e2e.py`

#### Run entire file:
```bash
pytest tests/e2e/async_sandbox/async_sandbox_complete_workflow_e2e.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/e2e_async_sandbox/async_sandbox_complete_workflow_e2e/report.html --self-contained-html --junitxml=reports/e2e_async_sandbox/async_sandbox_complete_workflow_e2e/junit.xml tests/e2e/async_sandbox/async_sandbox_complete_workflow_e2e.py
```

*No test classes found in this file.*

---

## e2e → sandbox

### sandbox_complete_lifecycle_e2e.py

**File Path:** `tests/e2e/sandbox/sandbox_complete_lifecycle_e2e.py`

#### Run entire file:
```bash
pytest tests/e2e/sandbox/sandbox_complete_lifecycle_e2e.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/e2e_sandbox/sandbox_complete_lifecycle_e2e/report.html --self-contained-html --junitxml=reports/e2e_sandbox/sandbox_complete_lifecycle_e2e/junit.xml tests/e2e/sandbox/sandbox_complete_lifecycle_e2e.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → auth

### async_token_management.py

**File Path:** `tests/integration/async_sandbox/auth/async_token_management.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/auth/async_token_management.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_auth/async_token_management/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_auth/async_token_management/junit.xml tests/integration/async_sandbox/auth/async_token_management.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → code_execution

### async_code_execution.py

**File Path:** `tests/integration/async_sandbox/code_execution/async_code_execution.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/code_execution/async_code_execution.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_code_execution/async_code_execution/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_code_execution/async_code_execution/junit.xml tests/integration/async_sandbox/code_execution/async_code_execution.py
```

*No test classes found in this file.*

---

### async_code_execution_webhook.py

**File Path:** `tests/integration/async_sandbox/code_execution/async_code_execution_webhook.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/code_execution/async_code_execution_webhook.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_code_execution/async_code_execution_webhook/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_code_execution/async_code_execution_webhook/junit.xml tests/integration/async_sandbox/code_execution/async_code_execution_webhook.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → connection

### async_sandbox_connection.py

**File Path:** `tests/integration/async_sandbox/connection/async_sandbox_connection.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/connection/async_sandbox_connection.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_connection/async_sandbox_connection/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_connection/async_sandbox_connection/junit.xml tests/integration/async_sandbox/connection/async_sandbox_connection.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → creation

### async_sandbox_creation.py

**File Path:** `tests/integration/async_sandbox/creation/async_sandbox_creation.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/creation/async_sandbox_creation.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_creation/async_sandbox_creation/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_creation/async_sandbox_creation/junit.xml tests/integration/async_sandbox/creation/async_sandbox_creation.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → lifecycle

### async_sandbox_lifecycle.py

**File Path:** `tests/integration/async_sandbox/lifecycle/async_sandbox_lifecycle.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/lifecycle/async_sandbox_lifecycle.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_lifecycle/async_sandbox_lifecycle/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_lifecycle/async_sandbox_lifecycle/junit.xml tests/integration/async_sandbox/lifecycle/async_sandbox_lifecycle.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → listing

### async_sandbox_listing.py

**File Path:** `tests/integration/async_sandbox/listing/async_sandbox_listing.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/listing/async_sandbox_listing.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_listing/async_sandbox_listing/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_listing/async_sandbox_listing/junit.xml tests/integration/async_sandbox/listing/async_sandbox_listing.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → resources → commands

### async_commands_resource.py

**File Path:** `tests/integration/async_sandbox/resources/commands/async_commands_resource.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/commands/async_commands_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_commands/async_commands_resource/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_commands/async_commands_resource/junit.xml tests/integration/async_sandbox/resources/commands/async_commands_resource.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → resources → env_vars

### async_env_vars_resource.py

**File Path:** `tests/integration/async_sandbox/resources/env_vars/async_env_vars_resource.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/env_vars/async_env_vars_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_env_vars/async_env_vars_resource/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_env_vars/async_env_vars_resource/junit.xml tests/integration/async_sandbox/resources/env_vars/async_env_vars_resource.py
```

*No test classes found in this file.*

---

## integration → async_sandbox → resources → files

### async_files_binary_operations.py

**File Path:** `tests/integration/async_sandbox/resources/files/async_files_binary_operations.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/files/async_files_binary_operations.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_files/async_files_binary_operations/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_files/async_files_binary_operations/junit.xml tests/integration/async_sandbox/resources/files/async_files_binary_operations.py
```

*No test classes found in this file.*

---

### async_files_resource.py

**File Path:** `tests/integration/async_sandbox/resources/files/async_files_resource.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/files/async_files_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_files/async_files_resource/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_files/async_files_resource/junit.xml tests/integration/async_sandbox/resources/files/async_files_resource.py
```

*No test classes found in this file.*

---

### async_files_upload_download.py

**File Path:** `tests/integration/async_sandbox/resources/files/async_files_upload_download.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/files/async_files_upload_download.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_files/async_files_upload_download/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_files/async_files_upload_download/junit.xml tests/integration/async_sandbox/resources/files/async_files_upload_download.py
```

*No test classes found in this file.*

---

### async_files_watch.py

**File Path:** `tests/integration/async_sandbox/resources/files/async_files_watch.py`

#### Run entire file:
```bash
pytest tests/integration/async_sandbox/resources/files/async_files_watch.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_async_sandbox_resources_files/async_files_watch/report.html --self-contained-html --junitxml=reports/integration_async_sandbox_resources_files/async_files_watch/junit.xml tests/integration/async_sandbox/resources/files/async_files_watch.py
```

*No test classes found in this file.*

---

## integration → desktop

### desktop_debug.py

**File Path:** `tests/integration/desktop/desktop_debug.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_debug.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_debug/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_debug/junit.xml tests/integration/desktop/desktop_debug.py
```

#### Class: `TestDesktopDebug`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_debug.py::TestDesktopDebug
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_debug/testdesktopdebug/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_debug/testdesktopdebug/junit.xml tests/integration/desktop/desktop_debug.py::TestDesktopDebug
```
**Run individual test methods:**
- `test_get_debug_logs`:
  ```bash
  pytest tests/integration/desktop/desktop_debug.py::TestDesktopDebug::test_get_debug_logs
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_debug/testdesktopdebug/test_get_debug_logs/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_debug/testdesktopdebug/test_get_debug_logs/junit.xml tests/integration/desktop/desktop_debug.py::TestDesktopDebug::test_get_debug_logs
  ```
- `test_get_debug_processes`:
  ```bash
  pytest tests/integration/desktop/desktop_debug.py::TestDesktopDebug::test_get_debug_processes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_debug/testdesktopdebug/test_get_debug_processes/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_debug/testdesktopdebug/test_get_debug_processes/junit.xml tests/integration/desktop/desktop_debug.py::TestDesktopDebug::test_get_debug_processes
  ```

---

### desktop_input.py

**File Path:** `tests/integration/desktop/desktop_input.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_input.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_input/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/junit.xml tests/integration/desktop/desktop_input.py
```

#### Class: `TestDesktopInput`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_input.py::TestDesktopInput
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput
```
**Run individual test methods:**
- `test_click`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_click
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_click/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_click/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_click
  ```
- `test_clipboard_operations`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_clipboard_operations
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_clipboard_operations/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_clipboard_operations/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_clipboard_operations
  ```
- `test_combination`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_combination
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_combination/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_combination/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_combination
  ```
- `test_drag`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_drag
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_drag/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_drag/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_drag
  ```
- `test_move`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_move
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_move/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_move/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_move
  ```
- `test_press`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_press
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_press/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_press/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_press
  ```
- `test_scroll`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_scroll
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_scroll/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_scroll/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_scroll
  ```
- `test_type`:
  ```bash
  pytest tests/integration/desktop/desktop_input.py::TestDesktopInput::test_type
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_input/testdesktopinput/test_type/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_input/testdesktopinput/test_type/junit.xml tests/integration/desktop/desktop_input.py::TestDesktopInput::test_type
  ```

---

### desktop_recordings.py

**File Path:** `tests/integration/desktop/desktop_recordings.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_recordings.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_recordings/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_recordings/junit.xml tests/integration/desktop/desktop_recordings.py
```

#### Class: `TestDesktopRecordings`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_recordings/testdesktoprecordings/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_recordings/testdesktoprecordings/junit.xml tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings
```
**Run individual test methods:**
- `test_download_recording`:
  ```bash
  pytest tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_download_recording
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_download_recording/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_download_recording/junit.xml tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_download_recording
  ```
- `test_get_recording_status`:
  ```bash
  pytest tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_get_recording_status
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_get_recording_status/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_get_recording_status/junit.xml tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_get_recording_status
  ```
- `test_start_recording`:
  ```bash
  pytest tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_start_recording
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_start_recording/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_recordings/testdesktoprecordings/test_start_recording/junit.xml tests/integration/desktop/desktop_recordings.py::TestDesktopRecordings::test_start_recording
  ```

---

### desktop_screenshots.py

**File Path:** `tests/integration/desktop/desktop_screenshots.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_screenshots.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_screenshots/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_screenshots/junit.xml tests/integration/desktop/desktop_screenshots.py
```

#### Class: `TestDesktopScreenshots`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/junit.xml tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots
```
**Run individual test methods:**
- `test_capture_window`:
  ```bash
  pytest tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_capture_window
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_capture_window/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_capture_window/junit.xml tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_capture_window
  ```
- `test_screenshot`:
  ```bash
  pytest tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_screenshot
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_screenshot/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_screenshot/junit.xml tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_screenshot
  ```
- `test_screenshot_region`:
  ```bash
  pytest tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_screenshot_region
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_screenshot_region/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_screenshots/testdesktopscreenshots/test_screenshot_region/junit.xml tests/integration/desktop/desktop_screenshots.py::TestDesktopScreenshots::test_screenshot_region
  ```

---

### desktop_ui_automation.py

**File Path:** `tests/integration/desktop/desktop_ui_automation.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_ui_automation.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/junit.xml tests/integration/desktop/desktop_ui_automation.py
```

#### Class: `TestDesktopUIAutomation`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation
```
**Run individual test methods:**
- `test_drag_drop`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_drag_drop
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_drag_drop/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_drag_drop/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_drag_drop
  ```
- `test_find_element`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_find_element
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_find_element/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_find_element/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_find_element
  ```
- `test_get_bounds`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_get_bounds
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_get_bounds/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_get_bounds/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_get_bounds
  ```
- `test_hotkey`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_hotkey
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_hotkey/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_hotkey/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_hotkey
  ```
- `test_ocr`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_ocr
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_ocr/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_ocr/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_ocr
  ```
- `test_wait_for`:
  ```bash
  pytest tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_wait_for
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_wait_for/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_ui_automation/testdesktopuiautomation/test_wait_for/junit.xml tests/integration/desktop/desktop_ui_automation.py::TestDesktopUIAutomation::test_wait_for
  ```

---

### desktop_vnc.py

**File Path:** `tests/integration/desktop/desktop_vnc.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_vnc.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/junit.xml tests/integration/desktop/desktop_vnc.py
```

#### Class: `TestDesktopVNC`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_vnc.py::TestDesktopVNC
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/testdesktopvnc/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/testdesktopvnc/junit.xml tests/integration/desktop/desktop_vnc.py::TestDesktopVNC
```
**Run individual test methods:**
- `test_get_vnc_status`:
  ```bash
  pytest tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_get_vnc_status
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_get_vnc_status/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_get_vnc_status/junit.xml tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_get_vnc_status
  ```
- `test_get_vnc_url`:
  ```bash
  pytest tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_get_vnc_url
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_get_vnc_url/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_get_vnc_url/junit.xml tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_get_vnc_url
  ```
- `test_start_vnc`:
  ```bash
  pytest tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_start_vnc
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_start_vnc/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_start_vnc/junit.xml tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_start_vnc
  ```
- `test_stop_vnc`:
  ```bash
  pytest tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_stop_vnc
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_stop_vnc/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_vnc/testdesktopvnc/test_stop_vnc/junit.xml tests/integration/desktop/desktop_vnc.py::TestDesktopVNC::test_stop_vnc
  ```

---

### desktop_window_operations.py

**File Path:** `tests/integration/desktop/desktop_window_operations.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_window_operations.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/junit.xml tests/integration/desktop/desktop_window_operations.py
```

#### Class: `TestDesktopWindowOperations`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations
```
**Run individual test methods:**
- `test_focus_window`:
  ```bash
  pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_focus_window
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_focus_window/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_focus_window/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_focus_window
  ```
- `test_get_clipboard_history`:
  ```bash
  pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_get_clipboard_history
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_get_clipboard_history/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_get_clipboard_history/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_get_clipboard_history
  ```
- `test_minimize_window`:
  ```bash
  pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_minimize_window
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_minimize_window/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_minimize_window/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_minimize_window
  ```
- `test_resize_window`:
  ```bash
  pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_resize_window
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_resize_window/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_resize_window/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_resize_window
  ```
- `test_set_resolution`:
  ```bash
  pytest tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_set_resolution
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_set_resolution/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_window_operations/testdesktopwindowoperations/test_set_resolution/junit.xml tests/integration/desktop/desktop_window_operations.py::TestDesktopWindowOperations::test_set_resolution
  ```

---

### desktop_windows.py

**File Path:** `tests/integration/desktop/desktop_windows.py`

#### Run entire file:
```bash
pytest tests/integration/desktop/desktop_windows.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_windows/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_windows/junit.xml tests/integration/desktop/desktop_windows.py
```

#### Class: `TestDesktopWindows`
**Run entire class:**
```bash
pytest tests/integration/desktop/desktop_windows.py::TestDesktopWindows
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_desktop/desktop_windows/testdesktopwindows/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_windows/testdesktopwindows/junit.xml tests/integration/desktop/desktop_windows.py::TestDesktopWindows
```
**Run individual test methods:**
- `test_get_available_resolutions`:
  ```bash
  pytest tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_available_resolutions
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_available_resolutions/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_available_resolutions/junit.xml tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_available_resolutions
  ```
- `test_get_display`:
  ```bash
  pytest tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_display
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_display/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_display/junit.xml tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_display
  ```
- `test_get_windows`:
  ```bash
  pytest tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_windows
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_windows/report.html --self-contained-html --junitxml=reports/integration_desktop/desktop_windows/testdesktopwindows/test_get_windows/junit.xml tests/integration/desktop/desktop_windows.py::TestDesktopWindows::test_get_windows
  ```

---

## integration → sandbox → auth

### token_management.py

**File Path:** `tests/integration/sandbox/auth/token_management.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/auth/token_management.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_auth/token_management/report.html --self-contained-html --junitxml=reports/integration_sandbox_auth/token_management/junit.xml tests/integration/sandbox/auth/token_management.py
```

#### Class: `TestTokenManagement`
**Run entire class:**
```bash
pytest tests/integration/sandbox/auth/token_management.py::TestTokenManagement
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_auth/token_management/testtokenmanagement/report.html --self-contained-html --junitxml=reports/integration_sandbox_auth/token_management/testtokenmanagement/junit.xml tests/integration/sandbox/auth/token_management.py::TestTokenManagement
```
**Run individual test methods:**
- `test_get_token`:
  ```bash
  pytest tests/integration/sandbox/auth/token_management.py::TestTokenManagement::test_get_token
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_auth/token_management/testtokenmanagement/test_get_token/report.html --self-contained-html --junitxml=reports/integration_sandbox_auth/token_management/testtokenmanagement/test_get_token/junit.xml tests/integration/sandbox/auth/token_management.py::TestTokenManagement::test_get_token
  ```
- `test_refresh_token`:
  ```bash
  pytest tests/integration/sandbox/auth/token_management.py::TestTokenManagement::test_refresh_token
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_auth/token_management/testtokenmanagement/test_refresh_token/report.html --self-contained-html --junitxml=reports/integration_sandbox_auth/token_management/testtokenmanagement/test_refresh_token/junit.xml tests/integration/sandbox/auth/token_management.py::TestTokenManagement::test_refresh_token
  ```

---

## integration → sandbox → code_execution

### background_execution.py

**File Path:** `tests/integration/sandbox/code_execution/background_execution.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/background_execution.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/background_execution/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/background_execution/junit.xml tests/integration/sandbox/code_execution/background_execution.py
```

#### Class: `TestBackgroundExecution`
**Run entire class:**
```bash
pytest tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/junit.xml tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution
```
**Run individual test methods:**
- `test_kill_process`:
  ```bash
  pytest tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_kill_process
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_kill_process/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_kill_process/junit.xml tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_kill_process
  ```
- `test_list_processes`:
  ```bash
  pytest tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_list_processes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_list_processes/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_list_processes/junit.xml tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_list_processes
  ```
- `test_run_code_background`:
  ```bash
  pytest tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_run_code_background
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_run_code_background/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/background_execution/testbackgroundexecution/test_run_code_background/junit.xml tests/integration/sandbox/code_execution/background_execution.py::TestBackgroundExecution::test_run_code_background
  ```

---

### code_execution.py

**File Path:** `tests/integration/sandbox/code_execution/code_execution.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/code_execution.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/junit.xml tests/integration/sandbox/code_execution/code_execution.py
```

#### Class: `TestCodeExecution`
**Run entire class:**
```bash
pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution
```
**Run individual test methods:**
- `test_run_code_different_languages`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_different_languages
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_different_languages/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_different_languages/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_different_languages
  ```
- `test_run_code_with_env_vars`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_env_vars
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_env_vars/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_env_vars/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_env_vars
  ```
- `test_run_code_with_error`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_error
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_error/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_error/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_error
  ```
- `test_run_code_with_timeout`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_timeout
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_timeout/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_code_with_timeout/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_code_with_timeout
  ```
- `test_run_simple_code`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_simple_code
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_simple_code/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution/testcodeexecution/test_run_simple_code/junit.xml tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_simple_code
  ```

---

### code_execution_async_webhook.py

**File Path:** `tests/integration/sandbox/code_execution/code_execution_async_webhook.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/code_execution_async_webhook.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_async_webhook/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_async_webhook/junit.xml tests/integration/sandbox/code_execution/code_execution_async_webhook.py
```

#### Class: `TestCodeExecutionAsyncWebhook`
**Run entire class:**
```bash
pytest tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/junit.xml tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook
```
**Run individual test methods:**
- `test_run_code_async`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook::test_run_code_async
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/test_run_code_async/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/test_run_code_async/junit.xml tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook::test_run_code_async
  ```
- `test_run_code_async_with_custom_headers`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook::test_run_code_async_with_custom_headers
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/test_run_code_async_with_custom_headers/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_async_webhook/testcodeexecutionasyncwebhook/test_run_code_async_with_custom_headers/junit.xml tests/integration/sandbox/code_execution/code_execution_async_webhook.py::TestCodeExecutionAsyncWebhook::test_run_code_async_with_custom_headers
  ```

---

### code_execution_stream.py

**File Path:** `tests/integration/sandbox/code_execution/code_execution_stream.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/code_execution_stream.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_stream/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_stream/junit.xml tests/integration/sandbox/code_execution/code_execution_stream.py
```

*No test classes found in this file.*

---

### code_execution_with_resources.py

**File Path:** `tests/integration/sandbox/code_execution/code_execution_with_resources.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/code_execution_with_resources.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_with_resources/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_with_resources/junit.xml tests/integration/sandbox/code_execution/code_execution_with_resources.py
```

#### Class: `TestCodeExecutionWithResources`
**Run entire class:**
```bash
pytest tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/junit.xml tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources
```
**Run individual test methods:**
- `test_run_code_in_working_dir`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources::test_run_code_in_working_dir
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/test_run_code_in_working_dir/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/test_run_code_in_working_dir/junit.xml tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources::test_run_code_in_working_dir
  ```
- `test_run_code_with_global_env`:
  ```bash
  pytest tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources::test_run_code_with_global_env
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/test_run_code_with_global_env/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/code_execution_with_resources/testcodeexecutionwithresources/test_run_code_with_global_env/junit.xml tests/integration/sandbox/code_execution/code_execution_with_resources.py::TestCodeExecutionWithResources::test_run_code_with_global_env
  ```

---

### rich_output.py

**File Path:** `tests/integration/sandbox/code_execution/rich_output.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/code_execution/rich_output.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/rich_output/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/rich_output/junit.xml tests/integration/sandbox/code_execution/rich_output.py
```

#### Class: `TestRichOutput`
**Run entire class:**
```bash
pytest tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_code_execution/rich_output/testrichoutput/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/rich_output/testrichoutput/junit.xml tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput
```
**Run individual test methods:**
- `test_capture_stderr`:
  ```bash
  pytest tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_capture_stderr
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_capture_stderr/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_capture_stderr/junit.xml tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_capture_stderr
  ```
- `test_capture_stdout`:
  ```bash
  pytest tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_capture_stdout
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_capture_stdout/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_capture_stdout/junit.xml tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_capture_stdout
  ```
- `test_rich_outputs_property`:
  ```bash
  pytest tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_rich_outputs_property
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_rich_outputs_property/report.html --self-contained-html --junitxml=reports/integration_sandbox_code_execution/rich_output/testrichoutput/test_rich_outputs_property/junit.xml tests/integration/sandbox/code_execution/rich_output.py::TestRichOutput::test_rich_outputs_property
  ```

---

## integration → sandbox → connection

### sandbox_connection.py

**File Path:** `tests/integration/sandbox/connection/sandbox_connection.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/connection/sandbox_connection.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_connection/sandbox_connection/report.html --self-contained-html --junitxml=reports/integration_sandbox_connection/sandbox_connection/junit.xml tests/integration/sandbox/connection/sandbox_connection.py
```

#### Class: `TestSandboxConnection`
**Run entire class:**
```bash
pytest tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/report.html --self-contained-html --junitxml=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/junit.xml tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection
```
**Run individual test methods:**
- `test_connect_to_existing_sandbox`:
  ```bash
  pytest tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection::test_connect_to_existing_sandbox
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/test_connect_to_existing_sandbox/report.html --self-contained-html --junitxml=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/test_connect_to_existing_sandbox/junit.xml tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection::test_connect_to_existing_sandbox
  ```
- `test_connect_to_nonexistent_sandbox`:
  ```bash
  pytest tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection::test_connect_to_nonexistent_sandbox
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/test_connect_to_nonexistent_sandbox/report.html --self-contained-html --junitxml=reports/integration_sandbox_connection/sandbox_connection/testsandboxconnection/test_connect_to_nonexistent_sandbox/junit.xml tests/integration/sandbox/connection/sandbox_connection.py::TestSandboxConnection::test_connect_to_nonexistent_sandbox
  ```

---

## integration → sandbox → creation

### sandbox_creation.py

**File Path:** `tests/integration/sandbox/creation/sandbox_creation.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/creation/sandbox_creation.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/junit.xml tests/integration/sandbox/creation/sandbox_creation.py
```

#### Class: `TestSandboxCreation`
**Run entire class:**
```bash
pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation
```
**Run individual test methods:**
- `test_create_from_template_name`:
  ```bash
  pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_from_template_name
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_from_template_name/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_from_template_name/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_from_template_name
  ```
- `test_create_invalid_template`:
  ```bash
  pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_invalid_template
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_invalid_template/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_invalid_template/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_invalid_template
  ```
- `test_create_with_env_vars`:
  ```bash
  pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_with_env_vars
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_with_env_vars/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_with_env_vars/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_with_env_vars
  ```
- `test_create_with_timeout`:
  ```bash
  pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_with_timeout
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_with_timeout/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_with_timeout/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_with_timeout
  ```
- `test_create_without_internet`:
  ```bash
  pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_without_internet
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_without_internet/report.html --self-contained-html --junitxml=reports/integration_sandbox_creation/sandbox_creation/testsandboxcreation/test_create_without_internet/junit.xml tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_without_internet
  ```

---

## integration → sandbox → info

### sandbox_info.py

**File Path:** `tests/integration/sandbox/info/sandbox_info.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/info/sandbox_info.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/junit.xml tests/integration/sandbox/info/sandbox_info.py
```

#### Class: `TestSandboxInfo`
**Run entire class:**
```bash
pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo
```
**Run individual test methods:**
- `test_agent_url_property`:
  ```bash
  pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_agent_url_property
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_agent_url_property/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_agent_url_property/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_agent_url_property
  ```
- `test_get_info`:
  ```bash
  pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_info
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_info/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_info/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_info
  ```
- `test_get_info_contains_resources`:
  ```bash
  pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_info_contains_resources
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_info_contains_resources/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_info_contains_resources/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_info_contains_resources
  ```
- `test_get_preview_url`:
  ```bash
  pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_preview_url
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_preview_url/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_preview_url/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_preview_url
  ```
- `test_get_preview_url_default_port`:
  ```bash
  pytest tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_preview_url_default_port
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_preview_url_default_port/report.html --self-contained-html --junitxml=reports/integration_sandbox_info/sandbox_info/testsandboxinfo/test_get_preview_url_default_port/junit.xml tests/integration/sandbox/info/sandbox_info.py::TestSandboxInfo::test_get_preview_url_default_port
  ```

---

## integration → sandbox → lifecycle

### sandbox_lifecycle.py

**File Path:** `tests/integration/sandbox/lifecycle/sandbox_lifecycle.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/lifecycle/sandbox_lifecycle.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_lifecycle/sandbox_lifecycle/report.html --self-contained-html --junitxml=reports/integration_sandbox_lifecycle/sandbox_lifecycle/junit.xml tests/integration/sandbox/lifecycle/sandbox_lifecycle.py
```

#### Class: `TestSandboxLifecycle`
**Run entire class:**
```bash
pytest tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/report.html --self-contained-html --junitxml=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/junit.xml tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle
```
**Run individual test methods:**
- `test_kill_sandbox`:
  ```bash
  pytest tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_kill_sandbox
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_kill_sandbox/report.html --self-contained-html --junitxml=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_kill_sandbox/junit.xml tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_kill_sandbox
  ```
- `test_pause_and_resume`:
  ```bash
  pytest tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_pause_and_resume
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_pause_and_resume/report.html --self-contained-html --junitxml=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_pause_and_resume/junit.xml tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_pause_and_resume
  ```
- `test_set_timeout`:
  ```bash
  pytest tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_set_timeout
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_set_timeout/report.html --self-contained-html --junitxml=reports/integration_sandbox_lifecycle/sandbox_lifecycle/testsandboxlifecycle/test_set_timeout/junit.xml tests/integration/sandbox/lifecycle/sandbox_lifecycle.py::TestSandboxLifecycle::test_set_timeout
  ```

---

## integration → sandbox → listing

### sandbox_listing.py

**File Path:** `tests/integration/sandbox/listing/sandbox_listing.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/listing/sandbox_listing.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_listing/sandbox_listing/report.html --self-contained-html --junitxml=reports/integration_sandbox_listing/sandbox_listing/junit.xml tests/integration/sandbox/listing/sandbox_listing.py
```

#### Class: `TestSandboxListing`
**Run entire class:**
```bash
pytest tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/report.html --self-contained-html --junitxml=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/junit.xml tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing
```
**Run individual test methods:**
- `test_iter_sandboxes`:
  ```bash
  pytest tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_iter_sandboxes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_iter_sandboxes/report.html --self-contained-html --junitxml=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_iter_sandboxes/junit.xml tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_iter_sandboxes
  ```
- `test_list_sandboxes`:
  ```bash
  pytest tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_list_sandboxes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_list_sandboxes/report.html --self-contained-html --junitxml=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_list_sandboxes/junit.xml tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_list_sandboxes
  ```
- `test_list_sandboxes_with_status_filter`:
  ```bash
  pytest tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_list_sandboxes_with_status_filter
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_list_sandboxes_with_status_filter/report.html --self-contained-html --junitxml=reports/integration_sandbox_listing/sandbox_listing/testsandboxlisting/test_list_sandboxes_with_status_filter/junit.xml tests/integration/sandbox/listing/sandbox_listing.py::TestSandboxListing::test_list_sandboxes_with_status_filter
  ```

---

## integration → sandbox → resources → agent_info

### agent_info.py

**File Path:** `tests/integration/sandbox/resources/agent_info/agent_info.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/agent_info/agent_info.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py
```

#### Class: `TestAgentInfo`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo
```
**Run individual test methods:**
- `test_get_agent_info`:
  ```bash
  pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_agent_info
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_agent_info/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_agent_info/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_agent_info
  ```
- `test_get_agent_metrics`:
  ```bash
  pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_agent_metrics
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_agent_metrics/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_agent_metrics/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_agent_metrics
  ```
- `test_get_jupyter_sessions`:
  ```bash
  pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_jupyter_sessions
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_jupyter_sessions/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_jupyter_sessions/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_jupyter_sessions
  ```
- `test_get_metrics_snapshot`:
  ```bash
  pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_metrics_snapshot
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_metrics_snapshot/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_get_metrics_snapshot/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_get_metrics_snapshot
  ```
- `test_list_system_processes`:
  ```bash
  pytest tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_list_system_processes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_list_system_processes/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_agent_info/agent_info/testagentinfo/test_list_system_processes/junit.xml tests/integration/sandbox/resources/agent_info/agent_info.py::TestAgentInfo::test_list_system_processes
  ```

---

## integration → sandbox → resources → cache

### cache_resource.py

**File Path:** `tests/integration/sandbox/resources/cache/cache_resource.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/cache/cache_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_cache/cache_resource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_cache/cache_resource/junit.xml tests/integration/sandbox/resources/cache/cache_resource.py
```

#### Class: `TestCacheResource`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/junit.xml tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource
```
**Run individual test methods:**
- `test_cache_stats`:
  ```bash
  pytest tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource::test_cache_stats
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/test_cache_stats/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/test_cache_stats/junit.xml tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource::test_cache_stats
  ```
- `test_clear_cache`:
  ```bash
  pytest tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource::test_clear_cache
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/test_clear_cache/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_cache/cache_resource/testcacheresource/test_clear_cache/junit.xml tests/integration/sandbox/resources/cache/cache_resource.py::TestCacheResource::test_clear_cache
  ```

---

## integration → sandbox → resources → commands

### commands_resource.py

**File Path:** `tests/integration/sandbox/resources/commands/commands_resource.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/commands/commands_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_commands/commands_resource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_commands/commands_resource/junit.xml tests/integration/sandbox/resources/commands/commands_resource.py
```

#### Class: `TestCommandsResource`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/junit.xml tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource
```
**Run individual test methods:**
- `test_run_command`:
  ```bash
  pytest tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command/junit.xml tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command
  ```
- `test_run_command_background`:
  ```bash
  pytest tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command_background
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command_background/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command_background/junit.xml tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command_background
  ```
- `test_run_command_with_error`:
  ```bash
  pytest tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command_with_error
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command_with_error/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_commands/commands_resource/testcommandsresource/test_run_command_with_error/junit.xml tests/integration/sandbox/resources/commands/commands_resource.py::TestCommandsResource::test_run_command_with_error
  ```

---

## integration → sandbox → resources → env_vars

### env_vars_resource.py

**File Path:** `tests/integration/sandbox/resources/env_vars/env_vars_resource.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py
```

#### Class: `TestEnvironmentVariables`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables
```
**Run individual test methods:**
- `test_delete_env_var`:
  ```bash
  pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_delete_env_var
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_delete_env_var/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_delete_env_var/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_delete_env_var
  ```
- `test_get_all_env_vars`:
  ```bash
  pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_get_all_env_vars
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_get_all_env_vars/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_get_all_env_vars/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_get_all_env_vars
  ```
- `test_get_single_env_var`:
  ```bash
  pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_get_single_env_var
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_get_single_env_var/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_get_single_env_var/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_get_single_env_var
  ```
- `test_set_all_env_vars`:
  ```bash
  pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_set_all_env_vars
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_set_all_env_vars/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_set_all_env_vars/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_set_all_env_vars
  ```
- `test_update_env_vars`:
  ```bash
  pytest tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_update_env_vars
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_update_env_vars/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_env_vars/env_vars_resource/testenvironmentvariables/test_update_env_vars/junit.xml tests/integration/sandbox/resources/env_vars/env_vars_resource.py::TestEnvironmentVariables::test_update_env_vars
  ```

---

## integration → sandbox → resources → files

### files_binary_operations.py

**File Path:** `tests/integration/sandbox/resources/files/files_binary_operations.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/files/files_binary_operations.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_binary_operations/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_binary_operations/junit.xml tests/integration/sandbox/resources/files/files_binary_operations.py
```

#### Class: `TestFilesBinaryOperations`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/junit.xml tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations
```
**Run individual test methods:**
- `test_read_bytes`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_read_bytes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_read_bytes/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_read_bytes/junit.xml tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_read_bytes
  ```
- `test_write_bytes`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_write_bytes
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_write_bytes/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_write_bytes/junit.xml tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_write_bytes
  ```
- `test_write_bytes_png_image`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_write_bytes_png_image
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_write_bytes_png_image/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_binary_operations/testfilesbinaryoperations/test_write_bytes_png_image/junit.xml tests/integration/sandbox/resources/files/files_binary_operations.py::TestFilesBinaryOperations::test_write_bytes_png_image
  ```

---

### files_resource.py

**File Path:** `tests/integration/sandbox/resources/files/files_resource.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/files/files_resource.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/junit.xml tests/integration/sandbox/resources/files/files_resource.py
```

#### Class: `TestFilesResource`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource
```
**Run individual test methods:**
- `test_file_exists`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_file_exists
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_file_exists/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_file_exists/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_file_exists
  ```
- `test_list_files`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_list_files
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_list_files/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_list_files/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_list_files
  ```
- `test_mkdir`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_mkdir
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_mkdir/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_mkdir/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_mkdir
  ```
- `test_remove_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_remove_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_remove_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_remove_file/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_remove_file
  ```
- `test_write_and_read_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_write_and_read_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_write_and_read_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_resource/testfilesresource/test_write_and_read_file/junit.xml tests/integration/sandbox/resources/files/files_resource.py::TestFilesResource::test_write_and_read_file
  ```

---

### files_upload_download.py

**File Path:** `tests/integration/sandbox/resources/files/files_upload_download.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/files/files_upload_download.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py
```

#### Class: `TestFilesUploadDownload`
**Run entire class:**
```bash
pytest tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload
```
**Run individual test methods:**
- `test_download_binary_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_download_binary_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_download_binary_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_download_binary_file/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_download_binary_file
  ```
- `test_download_text_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_download_text_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_download_text_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_download_text_file/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_download_text_file
  ```
- `test_upload_binary_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_upload_binary_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_upload_binary_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_upload_binary_file/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_upload_binary_file
  ```
- `test_upload_text_file`:
  ```bash
  pytest tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_upload_text_file
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_upload_text_file/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_upload_download/testfilesuploaddownload/test_upload_text_file/junit.xml tests/integration/sandbox/resources/files/files_upload_download.py::TestFilesUploadDownload::test_upload_text_file
  ```

---

### files_watch.py

**File Path:** `tests/integration/sandbox/resources/files/files_watch.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/resources/files/files_watch.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_resources_files/files_watch/report.html --self-contained-html --junitxml=reports/integration_sandbox_resources_files/files_watch/junit.xml tests/integration/sandbox/resources/files/files_watch.py
```

*No test classes found in this file.*

---

## integration → sandbox → templates

### template_operations.py

**File Path:** `tests/integration/sandbox/templates/template_operations.py`

#### Run entire file:
```bash
pytest tests/integration/sandbox/templates/template_operations.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/junit.xml tests/integration/sandbox/templates/template_operations.py
```

#### Class: `TestTemplateOperations`
**Run entire class:**
```bash
pytest tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testtemplateoperations/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testtemplateoperations/junit.xml tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations
```
**Run individual test methods:**
- `test_get_nonexistent_template`:
  ```bash
  pytest tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_get_nonexistent_template
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_get_nonexistent_template/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_get_nonexistent_template/junit.xml tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_get_nonexistent_template
  ```
- `test_get_template`:
  ```bash
  pytest tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_get_template
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_get_template/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_get_template/junit.xml tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_get_template
  ```
- `test_list_templates`:
  ```bash
  pytest tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_list_templates
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_list_templates/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_list_templates/junit.xml tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_list_templates
  ```
- `test_list_templates_with_filter`:
  ```bash
  pytest tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_list_templates_with_filter
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_list_templates_with_filter/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testtemplateoperations/test_list_templates_with_filter/junit.xml tests/integration/sandbox/templates/template_operations.py::TestTemplateOperations::test_list_templates_with_filter
  ```

#### Class: `TestHealthCheck`
**Run entire class:**
```bash
pytest tests/integration/sandbox/templates/template_operations.py::TestHealthCheck
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testhealthcheck/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testhealthcheck/junit.xml tests/integration/sandbox/templates/template_operations.py::TestHealthCheck
```
**Run individual test methods:**
- `test_health_check`:
  ```bash
  pytest tests/integration/sandbox/templates/template_operations.py::TestHealthCheck::test_health_check
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_sandbox_templates/template_operations/testhealthcheck/test_health_check/report.html --self-contained-html --junitxml=reports/integration_sandbox_templates/template_operations/testhealthcheck/test_health_check/junit.xml tests/integration/sandbox/templates/template_operations.py::TestHealthCheck::test_health_check
  ```

---

## integration → template

### template_builder_methods.py

**File Path:** `tests/integration/template/template_builder_methods.py`

#### Run entire file:
```bash
pytest tests/integration/template/template_builder_methods.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_template/template_builder_methods/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/junit.xml tests/integration/template/template_builder_methods.py
```

#### Class: `TestTemplateBuilderMethods`
**Run entire class:**
```bash
pytest tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_template/template_builder_methods/testtemplatebuildermethods/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/testtemplatebuildermethods/junit.xml tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods
```
**Run individual test methods:**
- `test_from_node_image`:
  ```bash
  pytest tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_from_node_image
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_from_node_image/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_from_node_image/junit.xml tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_from_node_image
  ```
- `test_template_builder_chaining`:
  ```bash
  pytest tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_builder_chaining
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_builder_chaining/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_builder_chaining/junit.xml tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_builder_chaining
  ```
- `test_template_getter_methods`:
  ```bash
  pytest tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_getter_methods
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_getter_methods/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_getter_methods/junit.xml tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_getter_methods
  ```
- `test_template_skip_cache`:
  ```bash
  pytest tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_skip_cache
  ```
  **With verbose output and reports:**
  ```bash
  pytest -v --showlocals --html=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_skip_cache/report.html --self-contained-html --junitxml=reports/integration_template/template_builder_methods/testtemplatebuildermethods/test_template_skip_cache/junit.xml tests/integration/template/template_builder_methods.py::TestTemplateBuilderMethods::test_template_skip_cache
  ```

---

### template_building.py

**File Path:** `tests/integration/template/template_building.py`

#### Run entire file:
```bash
pytest tests/integration/template/template_building.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_template/template_building/report.html --self-contained-html --junitxml=reports/integration_template/template_building/junit.xml tests/integration/template/template_building.py
```

*No test classes found in this file.*

---

### template_ready_checks.py

**File Path:** `tests/integration/template/template_ready_checks.py`

#### Run entire file:
```bash
pytest tests/integration/template/template_ready_checks.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_template/template_ready_checks/report.html --self-contained-html --junitxml=reports/integration_template/template_ready_checks/junit.xml tests/integration/template/template_ready_checks.py
```

*No test classes found in this file.*

---

## integration → terminal

### terminal_websocket.py

**File Path:** `tests/integration/terminal/terminal_websocket.py`

#### Run entire file:
```bash
pytest tests/integration/terminal/terminal_websocket.py
```
**With verbose output and reports:**
```bash
pytest -v --showlocals --html=reports/integration_terminal/terminal_websocket/report.html --self-contained-html --junitxml=reports/integration_terminal/terminal_websocket/junit.xml tests/integration/terminal/terminal_websocket.py
```

*No test classes found in this file.*

---
