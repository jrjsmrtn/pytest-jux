# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
