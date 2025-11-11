# Contributing to Hopx

Thank you for your interest in contributing to Hopx! 🎉

We love contributions from the community and welcome all types of contributions:
- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions
- 🌍 Translations

## 🚀 Quick Start

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/hopx.git
cd hopx
```

### 2. Set Up Development Environment

#### Python SDK
```bash
cd python
pip install -e ".[dev]"
```

#### JavaScript SDK
```bash
cd javascript
npm install
```

### 3. Create a Branch

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

### 4. Make Your Changes

- Write clear, readable code
- Add tests for new features
- Update documentation
- Follow existing code style

### 5. Run Tests

#### Python
```bash
cd python
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_foo.py # Specific test
```

#### JavaScript
```bash
cd javascript
npm test                 # Run all tests
npm run lint            # Check code style
npm run type-check      # TypeScript checks
```

### 6. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for custom templates"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Build/tooling changes

### 7. Push & Open PR

```bash
git push origin feature/amazing-feature
```

Then open a Pull Request on GitHub.

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows existing style
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for user-facing changes)
- [ ] Commit messages are clear

### PR Description

Include:
- **What** the PR does
- **Why** the change is needed
- **How** it's implemented
- **Testing** steps
- **Screenshots** (if UI changes)
- **Breaking changes** (if any)

### Example PR Title

```
feat(sandbox): add support for GPU sandboxes
fix(files): handle large file uploads correctly
docs(readme): improve quick start examples
```

## 🐛 Bug Reports

Use GitHub Issues and include:

### Required Information
- **SDK version** (Python/JavaScript)
- **OS and version**
- **Python/Node.js version**
- **Code snippet** to reproduce
- **Expected behavior**
- **Actual behavior**
- **Error messages** and stack traces

### Example Bug Report

```markdown
**Description**
File upload fails for files > 10MB

**Environment**
- SDK: Python 0.1.19
- OS: Ubuntu 22.04
- Python: 3.11

**Code to Reproduce**
```python
sandbox = Sandbox.create(template="python")
sandbox.files.write("/tmp/large.bin", "x" * 15_000_000)
```

**Expected**: File uploaded successfully
**Actual**: Timeout error after 30s

**Error Message**
```
TimeoutError: Request timed out after 30s
```
```

## 💡 Feature Requests

Open a GitHub Issue with:

- **Use case** - What problem does it solve?
- **Proposed solution** - How should it work?
- **Example usage** - Show API design
- **Alternatives** - What else did you consider?
- **Additional context** - Screenshots, links, etc.

### Example Feature Request

```markdown
**Feature**: Support for custom Docker images

**Use Case**: I want to use my own base images with pre-installed dependencies

**Proposed API**:
```python
template = Template.from_docker("my-registry.com/my-image:latest")
```

**Alternatives**: Use Template.run() to install dependencies each time (slower)

**Additional Context**: Similar to E2B's custom templates
```

## 📖 Documentation

Help improve our docs:

### What to Contribute
- Fix typos and grammar
- Add code examples
- Clarify confusing sections
- Add missing API documentation
- Create tutorials and guides
- Translate to other languages

### Documentation Structure
- `README.md` - Main SDK documentation
- `CHANGELOG.md` - Version history
- `examples/` - Usage examples
- `cookbook/` - Advanced patterns
- API docs - Generated from code comments

## 🎨 Code Style

### Python
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Max line length: 100 characters
- Use `ruff` for linting
- Use `black` for formatting

### JavaScript/TypeScript
- Follow existing ESLint config
- Use TypeScript for all new code
- Max line length: 100 characters
- Use Prettier for formatting

## 🧪 Testing

### Writing Tests

#### Python
```python
def test_sandbox_creation():
    """Test basic sandbox creation."""
    sandbox = Sandbox.create(template="python")
    assert sandbox.sandbox_id is not None
    sandbox.kill()
```

#### JavaScript
```typescript
describe('Sandbox', () => {
  it('should create a sandbox', async () => {
    const sandbox = await Sandbox.create({ template: 'nodejs' });
    expect(sandbox.sandboxId).toBeDefined();
    await sandbox.kill();
  });
});
```

### Test Coverage

We aim for >80% test coverage. Run coverage reports:

```bash
# Python
pytest --cov=hopx_ai --cov-report=html

# JavaScript
npm run test:coverage
```

## 🏗️ Development Workflow

### Branch Naming
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Merge Process
1. Open PR with clear description
2. Wait for CI checks to pass
3. Address review feedback
4. Maintainer approves and merges
5. Changes included in next release

## 🔐 Security

**Do not** open public issues for security vulnerabilities!

Report to: security@hopx.ai

See [SECURITY.md](SECURITY.md) for details.

## 📜 Code of Conduct

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

Be respectful, inclusive, and professional. We have zero tolerance for harassment.

## ✨ Recognition

Contributors are:
- Listed in CHANGELOG for their contributions
- Mentioned in release notes
- Added to contributors list
- May receive Hopx swag or credits

## 🆘 Getting Help

Need help contributing?

- **Discord**: [discord.gg/hopx](https://discord.gg/hopx)
- **Email**: support@hopx.ai
- **GitHub Discussions**: Ask questions and share ideas

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Hopx better! ❤️

**Happy coding!** 🚀

