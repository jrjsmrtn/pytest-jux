# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
