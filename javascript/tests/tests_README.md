# Hopx JavaScript SDK Test Suite

Comprehensive test suite for the Hopx JavaScript SDK covering all major functionality areas.

## Prerequisites

- Node.js >= 18.0.0
- Valid Hopx API key
- Network access to Hopx API endpoints

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set your API key**:
   ```bash
   export HOPX_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file in the project root:
   ```env
   HOPX_API_KEY=your-api-key-here
   ```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run a specific test file
```bash
npm test sdk-actions.test.ts
```

### Run tests matching a pattern
```bash
npm test -- --grep "file operations"
```

## Test Suites

| Test File | Coverage |
|-----------|----------|
| `sdk-actions.test.ts` | Core SDK actions (code execution, files, commands, env vars) |
| `sdk-advanced.test.ts` | Advanced features (binary files, processes, streaming, health) |
| `sdk-desktop.test.ts` | Desktop/GUI features (VNC, screenshots, windows) |
| `sdk-lifecycle.test.ts` | Lifecycle management (connect, pause/resume, iteration) |
| `sdk-templates.test.ts` | Template listing and filtering |
| `sdk-terminal.test.ts` | Terminal WebSocket interactions |

## Test Utilities

The `test-helpers.ts` file provides shared utilities:

- **`delayForRateLimit(ms)`** - Prevents API rate limiting
- **`retryWithBackoff(fn, maxRetries, initialDelay)`** - Generic retry with exponential backoff
- **`createSandboxWithRetry(options, maxRetries, initialDelay)`** - Robust sandbox creation

## Important Notes

### Timeouts
- Default test timeout: 30 seconds
- Lifecycle operations: 5 minutes
- Adjust timeouts if running on slower networks

### Cleanup
All tests automatically clean up created sandboxes in `afterAll` hooks, even on test failures.

### Rate Limiting
Tests include delays and retry logic to handle API rate limits. If running all tests in parallel, some may be staggered to prevent rate limit errors.

### Known Issues

**Binary File Operations**: The `readBytes` and `download` methods currently return JSON-wrapped responses. Tests include workarounds to extract the actual content.

**Desktop Features**: Tests gracefully handle environments where X11/VNC may not be available.

## Debugging

Enable verbose logging:
```bash
npm test -- --reporter=verbose
```

Run a single test:
```bash
npm test -- -t "should execute code"
```

## CI/CD Integration

For CI environments, ensure:
1. `HOPX_API_KEY` is set as a secret environment variable
2. Network access to Hopx API endpoints is allowed
3. Sufficient timeout values for slower CI runners

Example GitHub Actions:
```yaml
- name: Run tests
  env:
    HOPX_API_KEY: ${{ secrets.HOPX_API_KEY }}
  run: npm test
```

## Contributing

When adding new tests:
1. Use the utilities in `test-helpers.ts` for sandbox creation
2. Always clean up resources in `afterAll` hooks
3. Add appropriate timeouts for long-running operations
4. Include descriptive console logging for debugging
5. Handle expected failures gracefully (e.g., unsupported features)
