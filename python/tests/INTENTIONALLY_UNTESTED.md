# Intentionally Untested Methods

This document lists SDK methods that are intentionally not covered by integration tests, along with the reasoning.

## Debug and Development Utilities

### `Sandbox.debug()`
**Status:** Intentionally not tested  
**Reason:** This is a debugging utility that bypasses the public API and connects directly to an agent. It requires manual setup of agent URLs and JWT tokens, which are not suitable for automated integration tests. This method is intended for SDK development and debugging scenarios.

**Usage:** Manual testing only, typically used during SDK development.

---

## Internal/Utility Methods

### `Sandbox.get_token()`
**Status:** Partially tested (indirectly)  
**Reason:** This is an internal utility method primarily used for debugging and token inspection. While it's tested indirectly through other operations, dedicated tests are not necessary as it's not part of the primary SDK surface.

**Note:** Token management is tested through `refresh_token()` operations.

---

## Advanced/Edge Case Features

### Template Builder - Private Registry Images
**Status:** Not tested  
**Reason:** Testing private registry authentication requires:
- Valid credentials for GCP/AWS/Private registries
- Access to private registries
- Complex setup that varies by provider

**Methods:**
- `Template.from_private_image()`
- `Template.from_gcp_private_image()`
- `Template.from_aws_private_image()`

**Recommendation:** These should be tested manually or in a separate test suite with proper credentials management.

---

## Methods with External Dependencies

### `Sandbox.run_code_async()` / `AsyncSandbox.run_code_async()`
**Status:** Basic structure tested, full webhook callback not tested  
**Reason:** Full testing requires:
- A publicly accessible webhook endpoint
- Network connectivity to receive callbacks
- Long-running test setup

**Current Coverage:** Tests verify the method returns an execution_id and accepts parameters correctly.

**Note:** The webhook callback functionality itself requires external infrastructure that is difficult to test in automated integration tests.

---

## Methods Requiring Specific Templates

### Desktop Methods (when Desktop not available)
**Status:** Tests skip gracefully  
**Reason:** Many Desktop methods require templates with desktop automation capabilities. Tests are written to skip gracefully when Desktop is not available, but full coverage requires desktop-enabled templates.

**Methods affected:**
- All Desktop methods when used with non-desktop templates

**Current Approach:** Tests use `pytest.skip()` when `DesktopNotAvailableError` is raised.

---

## Summary

| Category | Count | Rationale |
|---------|-------|-----------|
| Debug utilities | 1 | Manual testing only |
| Internal utilities | 1 | Not primary SDK surface |
| Private registry | 3 | Requires credentials/setup |
| External dependencies | 2 | Requires external infrastructure |
| Template-specific | Many | Gracefully skipped when unavailable |

**Total intentionally untested:** ~7 methods + template-specific variations

---

## Testing Recommendations

1. **Manual Testing:** Debug utilities and private registry features should be tested manually with proper credentials.

2. **Separate Test Suite:** Consider creating a separate test suite for:
   - Private registry authentication
   - Webhook callback testing (with test webhook server)

3. **Documentation:** Ensure all intentionally untested methods are well-documented with usage examples.

