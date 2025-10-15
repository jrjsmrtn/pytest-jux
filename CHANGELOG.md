# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-15

### Added
- Sprint 2 (CLI Tools) - Complete
- Standalone CLI commands for offline operations:
  - `jux-keygen`: Cryptographic key pair generation
    - RSA key generation (2048, 3072, 4096 bits)
    - ECDSA key generation (P-256, P-384, P-521 curves)
    - X.509 self-signed certificate generation
    - Secure file permissions (0600 for private keys)
    - 31 comprehensive tests, 92.59% code coverage
  - `jux-sign`: Offline JUnit XML signing
    - Sign any JUnit XML file without pytest
    - Support for RSA and ECDSA keys
    - Optional X.509 certificate embedding
    - Stdin/stdout pipeline support
    - 18 comprehensive tests, 93.33% code coverage
  - `jux-verify`: XML signature verification
    - Verify XMLDSig signatures with certificates
    - Exit codes: 0 = valid, 1 = invalid
    - JSON output for scripting
    - Quiet mode option
    - 11 comprehensive tests, 78.48% code coverage
  - `jux-inspect`: JUnit XML report inspection
    - Display test summary (tests, failures, errors, skipped)
    - Show canonical SHA-256 hash
    - Detect signature presence
    - JSON output for scripting
    - Rich formatted terminal output
    - 9 comprehensive tests, 90.12% code coverage
- XML signature verification module (`pytest_jux.verifier`):
  - Verify XMLDSig signatures using signxml
  - Support for RSA and ECDSA signatures
  - Certificate validation
  - 6 comprehensive tests, 73.81% code coverage
- Configuration management:
  - configargparse for CLI with config file support
  - Environment variable support (JUX_KEY_PATH, JUX_CERT_PATH)
  - Config file support (~/.jux/config, /etc/jux/config)

### Changed
- Package management now uses `uv` (fast alternative to pip)
- Development documentation updated with uv usage
- CLI framework changed from click to configargparse for better config management

## [0.1.1] - 2025-10-15

### Added
- Sprint 1 (Core Plugin Infrastructure) - Complete
- XML canonicalization module (`pytest_jux.canonicalizer`):
  - C14N (Canonical XML) implementation for duplicate detection
  - SHA-256 canonical hash computation
  - Support for loading XML from files, strings, and bytes
  - 25 comprehensive tests, 82% code coverage
- XML digital signature module (`pytest_jux.signer`):
  - XMLDSig enveloped signature generation
  - RSA-SHA256 and ECDSA-SHA256 signature algorithms
  - Support for PEM-encoded RSA and ECDSA private keys
  - Optional X.509 certificate embedding
  - 28 comprehensive tests (21 passing, 7 xfail for self-signed cert limitations), 82% coverage
  - Test cryptographic keys (RSA 2048-bit, ECDSA P-256) for development
- pytest plugin hooks (`pytest_jux.plugin`):
  - `pytest_addoption`: CLI options (--jux-sign, --jux-key, --jux-cert)
  - `pytest_configure`: Configuration validation
  - `pytest_sessionfinish`: Automatic JUnit XML signing after test run
  - 21 comprehensive tests, 73% code coverage
  - End-to-end validated with actual pytest execution

### Security
- Test-only cryptographic keys clearly marked with security warnings
- Self-signed X.509 certificates for testing (not for production use)
- Comprehensive documentation on secure key management practices

## [0.1.0] - 2025-10-15

### Added
- Initial project structure following AI-Assisted Project Orchestration patterns
- Architecture Decision Records (ADRs):
  - ADR-0001: Record architecture decisions
  - ADR-0002: Adopt development best practices
  - ADR-0003: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
  - ADR-0004: Adopt Apache License 2.0
  - ADR-0005: Adopt Python Ecosystem Security Framework
- Apache License 2.0 with copyright attribution
- LICENSE and NOTICE files with proper copyright notices
- Comprehensive security framework:
  - Security documentation (SECURITY.md, THREAT_MODEL.md, CRYPTO_STANDARDS.md)
  - Automated security scanning (pip-audit, bandit, safety, trivy)
  - GitHub Actions security workflow
  - Dependabot configuration
  - Pre-commit security hooks
  - OpenSSF Scorecard integration
  - Security test suite structure
- Diátaxis documentation framework structure
- C4 DSL architecture documentation structure
- Development environment configuration (.editorconfig, .pre-commit-config.yaml)
- Makefile with security targets
- Foundation for pytest plugin development
- Copyright headers in all source files

### Security
- Implemented Python ecosystem security framework (ADR-0005)
- STRIDE threat model with 19 identified threats
- Cryptographic standards documentation (NIST, RFC compliance)
- Vulnerability reporting process established
- Coordinated disclosure policy (90-day embargo)

[Unreleased]: https://github.com/jrjsmrtn/pytest-jux/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jrjsmrtn/pytest-jux/releases/tag/v0.1.0
