# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          | Status            |
| ------- | ------------------ | ----------------- |
| 0.2.x   | :white_check_mark: | Current Release   |
| 0.1.x   | :white_check_mark: | Security Fixes    |
| < 0.1.0 | :x:                | Unsupported       |

Once version 1.0.0 is released, we will support:
- Latest major version (full support)
- Previous major version (security fixes only)

## Security Guarantees

pytest-jux provides the following security guarantees:

### Cryptographic Operations
- ✅ XML signature generation and verification using industry-standard signxml library
- ✅ Approved cryptographic algorithms only (RSA-SHA256, ECDSA-SHA256)
- ✅ Minimum key lengths enforced (RSA 2048-bit, ECDSA P-256)
- ✅ Secure random number generation for nonces

### Data Protection
- ✅ No private key material written to logs or error messages
- ✅ Sensitive data cleared from memory where possible
- ✅ No credentials stored in source code or configuration

### XML Security
- ✅ Protection against XML External Entity (XXE) attacks
- ✅ Protection against XML bomb attacks (billion laughs)
- ✅ XML size limits to prevent denial of service
- ✅ Input validation against JUnit XML schema

### Supply Chain
- ✅ All releases signed with Sigstore (post-1.0)
- ✅ Software Bill of Materials (SBOM) provided for each release
- ✅ Dependencies pinned with cryptographic hashes
- ✅ Automated vulnerability scanning via pip-audit

## Known Limitations

### What We Protect Against
- Signature verification bypass attempts
- XML injection and manipulation attacks
- Dependency vulnerabilities (automated scanning)
- Supply chain attacks (Trusted Publishers, Sigstore)

### What We Don't Protect Against
- ❌ Compromised private keys (user responsibility)
- ❌ Man-in-the-middle attacks on API communication (use HTTPS)
- ❌ Malicious pytest plugins loaded alongside pytest-jux
- ❌ System clock manipulation for timestamp validation
- ❌ Physical access to systems with private keys

### User Responsibilities
- Securely generate and store private keys
- Use HTTPS for Jux API endpoints
- Keep pytest-jux and dependencies updated
- Review security advisories regularly
- Rotate signing keys according to policy

## Reporting a Vulnerability

**IMPORTANT: Do NOT open public issues for security vulnerabilities.**

### How to Report

**Preferred Method**: Email
- **Address**: jrjsmrtn+security@gmail.com
- **Subject**: [SECURITY] pytest-jux vulnerability report
- **Encryption**: PGP key available on request

**What to Include**:
1. Description of the vulnerability
2. Steps to reproduce
3. Affected versions
4. Potential impact assessment
5. Suggested fix (if available)
6. Your preferred contact method

### What to Expect

**Response Timeline**:
- **Initial Response**: Within 48 hours (acknowledgment)
- **Triage Assessment**: Within 5 business days
- **Fix Development**: Depends on severity (see below)
- **Public Disclosure**: 90 days after initial report (coordinated disclosure)

**Severity Levels**:

| Severity | Description | Target Fix Time |
|----------|-------------|-----------------|
| **Critical** | Remote code execution, private key compromise | 7 days |
| **High** | Signature bypass, authentication bypass | 14 days |
| **Medium** | Information disclosure, DoS | 30 days |
| **Low** | Minor security issues | Next release |

### Coordinated Disclosure Process

We follow responsible disclosure principles:

1. **Private Reporting**: Vulnerability reported privately
2. **Acknowledgment**: We confirm receipt within 48 hours
3. **Assessment**: We validate and assess severity (5 days)
4. **Fix Development**: We develop and test fix
5. **Pre-Disclosure**: We notify reporter before public disclosure
6. **Public Disclosure**: CVE assigned, advisory published, fix released
7. **Credit**: Reporter credited in advisory (if desired)

**Embargo Period**: 90 days from initial report  
**Early Disclosure**: If vulnerability is actively exploited or publicly disclosed

## Security Advisories

Security advisories will be published:

1. **GitHub Security Advisories**: Primary publication channel
   - URL: https://github.com/jrjsmrtn/pytest-jux/security/advisories
2. **CHANGELOG.md**: Security fixes documented
3. **PyPI Release Notes**: Referenced in release description
4. **Mailing List**: (Future) Security-announce mailing list

### Advisory Format

Each advisory includes:
- CVE identifier
- Affected versions
- Severity rating (CVSS score)
- Description of vulnerability
- Mitigation steps
- Fixed versions
- Credit to reporter

## Security Updates

### How to Stay Informed

1. **GitHub Watch**: Enable "Security alerts" notifications
2. **Dependabot**: Automatic pull requests for vulnerable dependencies
3. **RSS Feed**: Subscribe to GitHub releases
4. **Future**: Security-announce mailing list (post-1.0)

### Updating

**For Users**:
```bash
# Check for updates
uv pip list --outdated | grep pytest-jux

# Update to latest version
uv pip install --upgrade pytest-jux

# Verify installation
pytest-jux --version
pip-audit | grep pytest-jux
```

**For CI/CD**:
```yaml
# Dependabot configuration (.github/dependabot.yml)
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## Security Best Practices

### For Users

**Key Management**:
- Generate strong keys: RSA 2048+ bits or ECDSA P-256+
- Store private keys securely (file permissions 0600)
- Use hardware security modules (HSM) for production (future support)
- Rotate signing keys annually
- Never commit private keys to version control

**Configuration**:
- Use HTTPS for all Jux API endpoints
- Validate TLS certificates (no self-signed in production)
- Use environment variables for sensitive configuration
- Enable pytest-jux only when needed (--jux-publish flag)

**Operational**:
- Monitor for security advisories
- Update dependencies regularly
- Run pip-audit before deployments
- Review test logs for suspicious activity

### For Developers

**Secure Coding**:
- Follow docs/security/SECURE_CODING.md guidelines
- Use type hints for all functions
- Validate all inputs
- Handle errors securely (no stack traces to users)
- Use constant-time comparison for signatures

**Cryptographic Code**:
- 100% test coverage required
- Mandatory 2-person code review
- Security champion approval
- Document in CRYPTO_REVIEWS.md

**Testing**:
- Run security test suite: `pytest tests/security/`
- Fuzz test with malformed inputs
- Test error handling paths
- Verify constant-time operations

## Security Tools

We use the following tools to maintain security:

### Automated Scanning
- **pip-audit**: Vulnerability scanning (PyPA official)
- **ruff**: Static security analysis (flake8-bandit rules)
- **safety**: Dependency vulnerability database
- **Trivy**: Container and filesystem scanning

### Supply Chain
- **Dependabot**: Automated dependency updates
- **Sigstore**: Keyless signing for releases
- **CycloneDX**: SBOM generation
- **OpenSSF Scorecard**: Security best practices scoring

### CI/CD Integration
All security tools run automatically in CI/CD pipeline on every commit and pull request.

## Compliance and Standards

pytest-jux aims to comply with:

- **SLSA Level 3**: Supply chain security framework
- **OpenSSF Best Practices**: Open source security guidelines
- **OWASP Top 10**: Web application security risks
- **CWE Top 25**: Most dangerous software weaknesses
- **NIST Guidelines**: Cryptographic algorithm standards

## Hall of Fame

We recognize and thank security researchers who responsibly disclose vulnerabilities:

<!-- Hall of Fame entries will be added here -->

*No vulnerabilities reported yet.*

To be added to the Hall of Fame:
1. Report a valid security vulnerability
2. Follow responsible disclosure process
3. Indicate desire to be credited

## Questions?

For security-related questions (non-vulnerabilities):
- Open a GitHub Discussion (Security category)
- Email: jrjsmrtn@gmail.com (non-urgent)

For vulnerability reports:
- Email: jrjsmrtn+security@gmail.com (urgent)

---

**Last Updated**: 2025-10-20
**Next Review**: 2026-01-20 (quarterly review)
