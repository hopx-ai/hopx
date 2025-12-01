## 📝 Description

<!-- Provide a clear description of what this PR does -->

## 🎯 Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📖 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] 🧪 Test improvements
- [ ] 🚀 Performance improvement

## 🔗 Related Issues

<!-- Link to related issues -->
Fixes #(issue)
Closes #(issue)
Related to #(issue)

## 🧪 Testing

<!-- Describe the tests you ran -->

**Test Configuration:**
- SDK: Python / JavaScript
- OS: 
- Version:

**Tests added/updated:**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

**Test commands:**
```bash
# Python
pytest tests/test_feature.py

# JavaScript
npm test
```

## 🎯 Test Scope Configuration (Optional)

<!-- Control which tests run in CI by using test directives -->

**Default Behavior:** Tests are automatically selected based on changed files.

**Override Test Selection:** You can specify which tests to run by adding a test directive in your PR description or commit messages.

### Test Directive Format

Use `[test: ...]` format anywhere in your PR description or commit messages:

- **Run specific feature tests:** `[test: desktop]` - Runs all desktop tests
- **Run specific test type:** `[test: integration]` - Runs all integration tests
- **Run feature + type:** `[test: desktop, integration]` - Runs only desktop integration tests
- **Run all tests:** `[test: all]` - Runs all tests (overrides file-based detection)

### Examples

**In PR Description:**
```markdown
## Changes
Fixes desktop VNC connection issue

[test: desktop, integration]
```

**In Commit Message:**
```bash
git commit -m "fix: desktop VNC bug [test: desktop]"
```

**Available Test Scopes:**
- `desktop` - Desktop automation tests
- `sandbox` - Sandbox tests (integration + e2e)
- `async_sandbox` or `async-sandbox` - Async sandbox tests
- `template` - Template building tests
- `terminal` - Terminal/WebSocket tests
- Full path: `tests/integration/desktop/` (also supported)

**Test Types:**
- `integration` - Integration tests only
- `e2e` - End-to-end tests only
- `all` - Both integration and e2e (default)

**Priority Order:**
1. PR description directive (highest priority)
2. Commit message directive
3. File-based auto-detection (default)

## 📸 Screenshots / Videos

<!-- If applicable, add screenshots or videos -->

## ✅ Checklist

Before submitting, make sure you've done the following:

- [ ] 📖 Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] 🧪 All tests pass locally
- [ ] 📝 Code follows existing style guidelines
- [ ] 💬 Added/updated comments for complex code
- [ ] 📚 Updated documentation (README, API docs)
- [ ] 📋 Updated CHANGELOG.md (for user-facing changes)
- [ ] 🔍 Self-reviewed my code
- [ ] ⚠️ Checked for breaking changes
- [ ] 🎨 Ran linter and formatter

## 💭 Additional Notes

<!-- Any additional information reviewers should know -->

## 🔍 Review Focus

<!-- What should reviewers pay special attention to? -->

---

**By submitting this PR, I confirm that:**
- My contribution is made under the MIT License
- I have the right to submit this work
- I agree to the project's Code of Conduct

