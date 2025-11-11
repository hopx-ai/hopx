# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**⚠️ Please DO NOT open public issues for security vulnerabilities!**

To report a security issue, please email: **security@hopx.ai**

### What to Include

When reporting a vulnerability, please provide:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Potential impact** assessment
- **Affected versions** (if known)
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up

### What to Expect

We take security seriously and will respond promptly:

1. **Acknowledgment** within 48 hours
2. **Initial assessment** within 1 week
3. **Regular updates** on our progress
4. **Public disclosure** coordinated with you
5. **Credit** in the security advisory (unless you prefer anonymity)

## Security Best Practices

When using Hopx SDKs, follow these guidelines:

### 🔐 API Keys
- **Never commit** API keys to version control
- Use **environment variables** (`HOPX_API_KEY`)
- Rotate keys regularly
- Use separate keys for development/production

### 🔒 Sandbox Configuration
- Set appropriate **timeout limits** to prevent runaway processes
- Disable **internet access** when not needed
- Monitor **resource usage** (CPU, memory, disk)
- Use **templates** instead of running arbitrary code when possible

### 📝 Code Execution
- **Validate** user input before execution
- **Sanitize** file paths and commands
- **Limit** execution time with timeouts
- **Log** all code executions for audit trails

### 🌐 Network Security
- Use **HTTPS** for all API communications (enforced)
- Validate **SSL certificates**
- Don't expose sandbox **internal IPs**

### 📦 Dependencies
- Keep SDK **up to date** with latest versions
- Regularly check for **security advisories**
- Use `pip install --upgrade hopx-ai` or `npm update @hopx-ai/sdk`

## Known Security Considerations

### Sandbox Isolation
- Sandboxes are **VM-isolated** but share infrastructure
- Not suitable for **highly sensitive** cryptographic operations
- **Network isolation** can be configured per sandbox

### Data Privacy
- Code and files are **temporary** and deleted after timeout
- **Logs** are retained for 30 days for debugging
- **API keys** are never logged

### Rate Limits
- Rate limits prevent **abuse** and **DDoS**
- Contact support for **custom limits** if needed

## Security Updates

Security updates are released as:
- **Patch versions** (e.g., 0.1.19 → 0.1.20) for minor fixes
- **Minor versions** (e.g., 0.1.x → 0.2.0) for significant changes

Subscribe to our **security mailing list**: security-announce@hopx.ai

## Bug Bounty Program

We currently don't have a formal bug bounty program, but we:
- **Appreciate** responsible disclosure
- **Acknowledge** contributors in security advisories
- May provide **swag or credits** for significant findings

## Contact

- **Security Issues**: security@hopx.ai
- **General Support**: support@hopx.ai
- **PGP Key**: Available upon request

## Compliance

Hopx follows industry best practices:
- **SOC 2 Type II** (in progress)
- **GDPR** compliant data handling
- **ISO 27001** aligned security controls

---

Thank you for helping keep Hopx secure! 🔒

