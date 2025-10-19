# pytest-jux Development Guide

_AI-assisted development context and guidelines for pytest-jux_

## Project Overview

pytest-jux is a **client-side pytest plugin** for signing and publishing JUnit XML test reports to the Jux REST API. This document provides context for AI-assisted development sessions and human developers.

### Client-Server Architecture

pytest-jux is part of a **client-server architecture**:

- **pytest-jux (this project)**: Client-side plugin responsible for:
  - Signing JUnit XML reports with XMLDSig
  - Computing canonical hashes (C14N + SHA-256)
  - Capturing environment metadata
  - Publishing signed reports to Jux REST API via HTTP

- **Jux API Server (separate project)**: Server-side backend responsible for:
  - Receiving signed reports via REST API
  - Verifying XMLDSig signatures
  - Detecting duplicate reports (canonical hash comparison)
  - Storing reports in database (SQLite/PostgreSQL)
  - Providing query API and Web UI

**IMPORTANT**: This project does **NOT** include database models, SQLAlchemy integration, or duplicate detection logic. These are handled by the Jux API Server.

## Architecture Documentation

### Architecture Decision Records (ADRs)

This project uses ADRs to track significant architectural decisions. Current decisions:

- **[ADR-0001](docs/adr/0001-record-architecture-decisions.md)**: Record architecture decisions
- **[ADR-0002](docs/adr/0002-adopt-development-best-practices.md)**: Adopt development best practices
  - TDD-focused approach (technical library, no BDD required)
  - Semantic versioning (0.1.x → 1.0.0)
  - Gitflow workflow (main/develop/feature branches)
  - Keep a Changelog format
  - C4 DSL architecture documentation
  - Sprint-based development lifecycle
  - Diátaxis documentation framework
- **[ADR-0003](docs/adr/0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md)**: Use Python 3 with pytest, lxml, signxml stack (**Partially Superseded** - see [ADR-0010](docs/adr/0010-remove-database-dependencies.md))
  - Core libraries: lxml, signxml, cryptography, requests, configargparse, rich
  - Target Python 3.11+ on Debian 12/13, openSUSE, Fedora
  - pytest plugin architecture with hook integration
  - **Note**: Database-related sections superseded by ADR-0010. SQLAlchemy removed from pytest-jux dependencies.
- **[ADR-0004](docs/adr/0004-adopt-apache-license-2.0.md)**: Adopt Apache License 2.0
  - Explicit patent grant for cryptographic code
  - Enterprise-friendly for target users (sysadmins, integrators)
  - Ecosystem alignment (signxml, cryptography use Apache 2.0)
- **[ADR-0005](docs/adr/0005-adopt-python-ecosystem-security-framework.md)**: Adopt Python Ecosystem Security Framework
  - 3-tier implementation (Essential → Supply Chain → Cryptographic Assurance)
  - Automated scanning (pip-audit, ruff, safety, trivy)
  - SLSA Build Level 2 compliance (ADR-0006)
  - OpenSSF Best Practices Badge program (ADR-0008)
- **[ADR-0009](docs/adr/0009-adopt-reuse-spdx-license-identifiers.md)**: Adopt REUSE/SPDX License Identifiers
  - Machine-readable copyright and licensing
  - 372 lines of boilerplate removed (14 lines → 2 lines per file)
  - REUSE Specification 3.0 compliant
  - Prepares for Sprint 6 SBOM generation
- **[ADR-0010](docs/adr/0010-remove-database-dependencies.md)**: Remove Database Dependencies from pytest-jux
  - SQLAlchemy, Alembic, psycopg removed (not used in client-side plugin)
  - Database functionality resides in Jux API Server (separate project)
  - Reduces installation size by ~15MB

See [docs/adr/README.md](docs/adr/README.md) for the complete ADR index.

### C4 DSL Architecture Models

Architecture models are maintained in `docs/architecture/` using Structurizr DSL. Key views:

- **System Context**: pytest-jux plugin in the Jux ecosystem
- **Container View**: Plugin components, REST API client, cryptographic signer
- **Component View**: Internal module structure and interactions

**Validation Commands**:
```bash
# Validate architecture models
podman run --rm -v "$(pwd)/docs/architecture:/usr/local/structurizr" \
  structurizr/cli validate -workspace workspace.dsl

# Generate visual diagrams
podman run --rm -p 8080:8080 \
  -v "$(pwd)/docs/architecture:/usr/local/structurizr" structurizr/lite
```

## Development Commands

**IMPORTANT: This project uses `uv` for package and virtual environment management. Do NOT use `pip` or `python -m venv` directly.**

### Environment Setup

```bash
# Create virtual environment (using uv)
uv venv

# Install dependencies (development mode, using uv)
uv pip install -e ".[dev]"

# Install pre-commit hooks
uv run pre-commit install
```

**Why uv?**
- Faster package installation (10-100x faster than pip)
- Better dependency resolution
- Consistent environment management
- Automatic virtual environment handling with `uv run`
- No need to manually activate `.venv`

**Note:** Use `uv run <command>` to execute tools in the virtual environment without manual activation.

### Code Quality

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .
uv run ruff check --fix .  # Auto-fix where possible

# Type checking
uv run mypy pytest_jux
uv run mypy --strict pytest_jux  # Strict mode for crypto code

# Run all quality checks
uv run ruff check . && uv run mypy pytest_jux
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pytest_jux --cov-report=term-missing --cov-report=html

# Run specific test file
uv run pytest tests/test_plugin.py

# Run tests in parallel
uv run pytest -n auto

# Run tests with verbose output
uv run pytest -v

# Watch mode (requires pytest-watch)
uv run ptw
```

### Git Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/xml-signing

# Commit changes (use conventional commits)
git commit -m "feat(signer): implement XMLDSig signature generation"
git commit -m "test(signer): add property-based tests for C14N"

# Update from develop
git checkout develop
git pull origin develop
git checkout feature/xml-signing
git rebase develop

# Complete feature
git checkout develop
git merge feature/xml-signing
git push origin develop
```

### Release Process

**IMPORTANT**: The `main` branch contains ONLY tagged releases. All development happens on `develop`.

#### Gitflow Release Workflow

For releasing version `0.1.x`:

```bash
# 1. Ensure develop is up to date
git checkout develop
git pull home develop

# 2. Create release branch from develop
git checkout -b release/0.1.x develop

# 3. Update version and changelog
# Edit pyproject.toml: version = "0.1.x"
# Edit CHANGELOG.md: Move [Unreleased] items to [0.1.x] section with date
# Example CHANGELOG update:
#   ## [Unreleased]
#
#   ## [0.1.x] - 2025-10-19
#
#   ### Added
#   - Feature description

# 4. Commit release preparation
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.1.x"

# 5. Merge release branch to main (no fast-forward to preserve history)
git checkout main
git merge --no-ff release/0.1.x -m "Release version 0.1.x"

# 6. Tag the release on main
git tag -a v0.1.x -m "Release version 0.1.x"

# 7. Push main branch and tag to both remotes
git push home main
git push github main  # Note: May require temporarily disabling branch protection
git push home v0.1.x
git push github v0.1.x

# 8. Merge release branch back to develop (to sync version/changelog changes)
git checkout develop
git merge --no-ff release/0.1.x -m "Merge release/0.1.x back to develop"
git push home develop

# 9. Delete release branch (local and remote)
git branch -d release/0.1.x
git push home --delete release/0.1.x  # If pushed to remote
```

#### Quick Reference: Remote Names

- **home**: Primary remote (ssh://gm@yoda.local:2022/volume1/git/pytest-jux.git)
  - All branches can be pushed here
- **github**: Secondary remote (git@github.com:jrjsmrtn/pytest-jux.git)
  - Only `main` branch allowed (enforced by pre-push hook)
  - Branch protection may require temporary disabling for force pushes

#### Emergency: Force Push to GitHub Main

If GitHub branch protection prevents pushing to main:

```bash
# Option 1: Temporarily disable branch protection
# 1. Go to GitHub Settings → Branches → Branch protection rules
# 2. Temporarily disable protection for main
# 3. Run: git push github main --force
# 4. Re-enable branch protection

# Option 2: Use GitHub web interface
# 1. Create a temporary branch: git push github release/0.1.x:temp-main-update
# 2. Open PR from temp-main-update to main
# 3. Merge (may require admin override)
# 4. Delete temp branch
```

#### Hotfix Releases

For critical fixes to production (main):

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/0.1.x main

# 2. Make and commit fix
git commit -m "fix(critical): description"

# 3. Update version (patch bump)
# Edit pyproject.toml and CHANGELOG.md

# 4. Merge to main and tag
git checkout main
git merge --no-ff hotfix/0.1.x -m "Hotfix version 0.1.x"
git tag -a v0.1.x -m "Hotfix version 0.1.x"
git push home main v0.1.x
git push github main v0.1.x

# 5. Merge back to develop
git checkout develop
git merge --no-ff hotfix/0.1.x
git push home develop

# 6. Delete hotfix branch
git branch -d hotfix/0.1.x
```

## Technology Stack

### Core Dependencies

**IMPORTANT**: pytest-jux is a **client-side only** plugin. Database models, persistence, and server-side logic are handled by the separate Jux API Server project.

- **lxml** (5.x): XML parsing, XPath, C14N canonicalization
- **signxml** (3.x): XMLDSig digital signatures
- **cryptography** (41.x+): RSA/ECDSA key management
- **pytest** (7.4+/8.x): Plugin host and test framework
- **configargparse** (1.x): Configuration management (CLI, environment, files)
- **pydantic** (2.5+): Configuration validation and metadata schemas
- **rich** (13.x): Terminal output formatting
- **requests** (2.x): REST API client (HTTP POST to Jux API) - **postponed in Sprint 3**

**Note**: This project does NOT include:
- Database functionality (server-side only - Jux API Server)
- Database models or migrations (server-side only)
- Hardware Security Module (HSM) support (future consideration)

**Dependencies Removed** (ADR-0010):
- SQLAlchemy, Alembic, psycopg (not used, removed in v0.1.9)

### Development Tools

- **ruff**: Fast linter and formatter (replaces black, isort, flake8)
- **mypy**: Static type checking
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support
- **pytest-xdist**: Parallel test execution

## Testing Strategy

### TDD Approach

Following ADR-0002, this project uses **TDD-only** (no BDD) because it's a technical library:

1. **Red**: Write failing test for desired behavior
2. **Green**: Implement minimal code to pass test
3. **Refactor**: Improve code while maintaining tests

### Test Coverage Requirements

- **Overall**: >85% code coverage
- **Cryptographic Code**: 100% coverage (security-critical)
- **Property-Based Testing**: Use hypothesis for C14N edge cases

### Test Structure

```
tests/
├── test_plugin.py           # pytest hook integration
├── test_signer.py          # XML signature generation
├── test_verifier.py        # Signature verification
├── test_canonicalizer.py   # C14N operations
├── test_config.py          # Configuration management (Sprint 3)
├── test_metadata.py        # Environment metadata (Sprint 3)
├── test_storage.py         # Local storage & caching (Sprint 3)
├── commands/               # CLI command tests
│   ├── test_keygen.py      # Key generation tests
│   ├── test_sign.py        # Signing command tests
│   ├── test_verify.py      # Verification command tests
│   ├── test_inspect.py     # Inspection command tests
│   ├── test_cache.py       # Cache management tests (Sprint 3)
│   └── test_config_cmd.py  # Config management tests (Sprint 3)
├── security/               # Security tests
└── fixtures/
    ├── junit_xml/          # Sample JUnit XML files
    └── keys/               # Test signing keys
```

## AI-Assisted Development Guidelines

### AI Collaboration Context

This project follows the **AI-Assisted Project Orchestration** pattern language. Key practices:

1. **ADRs as Context**: Architecture decisions provide AI session continuity
2. **Sprint Documentation**: `docs/sprints/` maintains development progress
3. **C4 DSL Models**: Visual architecture aids AI understanding
4. **Test-First**: TDD guides AI-assisted implementation
5. **Quality Gates**: Human review required for crypto code

### Using AI for Development

**Appropriate AI Tasks**:
- Boilerplate generation (pytest hooks, configuration schemas, CLI commands)
- Test generation following TDD patterns
- Documentation writing (following Diátaxis structure)
- Code refactoring suggestions
- Architecture diagram updates

**Human-Required Tasks**:
- Cryptographic code review (security-critical)
- Architecture decision-making (documented in ADRs)
- API design decisions
- Security vulnerability assessment
- Final code approval before merge

### AI Context Management

**Before AI Session**:
- Review relevant ADRs for background context
- Check current sprint goals (`docs/sprints/`)
- Note any specific security considerations

**During AI Session**:
- Reference ADRs when making decisions
- Keep C4 DSL models updated
- Maintain test coverage >85%
- Use type hints for all functions

**After AI Session**:
- Review all cryptographic code changes
- Run full test suite and type checking
- Update documentation if needed
- Document new ADRs for significant decisions

## Project Structure

```
pytest-jux/
├── pytest_jux/              # Source code
│   ├── __init__.py         # Package initialization
│   ├── plugin.py           # pytest hook integration
│   ├── signer.py           # XMLDSig signing
│   ├── verifier.py         # Signature verification
│   ├── canonicalizer.py    # C14N canonicalization
│   ├── config.py           # Configuration management (Sprint 3 ✓)
│   ├── metadata.py         # Environment metadata (Sprint 3 ✓)
│   ├── storage.py          # Local storage & caching (Sprint 3 ✓)
│   ├── api_client.py       # REST API client (Sprint 3 - postponed)
│   └── commands/           # CLI commands
│       ├── __init__.py
│       ├── keygen.py       # Key generation (Sprint 2 ✓)
│       ├── sign.py         # Offline signing (Sprint 2 ✓)
│       ├── verify.py       # Signature verification (Sprint 2 ✓)
│       ├── inspect.py      # Report inspection (Sprint 2 ✓)
│       ├── cache.py        # Cache management (Sprint 3 ✓)
│       ├── config_cmd.py   # Config management (Sprint 3 ✓)
│       └── publish.py      # Manual publishing (Sprint 3 - postponed)
├── tests/                   # Test suite (TDD)
│   ├── test_plugin.py      # Sprint 1 ✓
│   ├── test_signer.py      # Sprint 1 ✓
│   ├── test_verifier.py    # Sprint 2 ✓
│   ├── test_canonicalizer.py  # Sprint 1 ✓
│   ├── test_config.py      # Sprint 3 ✓
│   ├── test_metadata.py    # Sprint 3 ✓
│   ├── test_storage.py     # Sprint 3 ✓
│   ├── commands/           # CLI command tests
│   │   ├── test_keygen.py  # Sprint 2 ✓
│   │   ├── test_sign.py    # Sprint 2 ✓
│   │   ├── test_verify.py  # Sprint 2 ✓
│   │   ├── test_inspect.py # Sprint 2 ✓
│   │   ├── test_cache.py   # Sprint 3 ✓
│   │   └── test_config_cmd.py  # Sprint 3 ✓
│   ├── security/           # Security tests
│   └── fixtures/           # Test fixtures
├── docs/                    # Documentation
│   ├── tutorials/          # Getting started guides
│   ├── howto/             # Problem-solving guides
│   ├── reference/         # Complete API documentation
│   ├── explanation/       # Architecture and design
│   ├── adr/              # Architecture decisions
│   ├── architecture/     # C4 DSL models
│   ├── sprints/          # Sprint documentation
│   └── security/         # Security documentation
├── .github/                # GitHub workflows (CI/CD)
├── pyproject.toml          # Project metadata and dependencies
├── .editorconfig           # Editor formatting rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore             # Git ignore patterns
├── CHANGELOG.md            # Change log
├── README.md              # Project overview
└── CLAUDE.md              # This file
```

**Note**: Database models and database integration are **NOT** part of this project. These are implemented in the Jux API Server (separate project). SQLAlchemy, Alembic, and psycopg dependencies were removed in v0.1.9 (see [ADR-0010](docs/adr/0010-remove-database-dependencies.md)).

## Documentation Framework (Diátaxis)

### Documentation Categories

1. **Tutorials** (`docs/tutorials/`): Learning-oriented
   - Getting started with pytest-jux
   - First signed report walkthrough

2. **How-To Guides** (`docs/howto/`): Problem-oriented
   - How to configure signing keys
   - How to integrate with CI/CD
   - How to troubleshoot signature verification

3. **Reference** (`docs/reference/`): Information-oriented
   - Plugin API reference
   - Configuration options
   - Library dependencies

4. **Explanation** (`docs/explanation/`): Understanding-oriented
   - Why XML signatures for test reports
   - Plugin architecture design
   - Security considerations

## Security Considerations

### Cryptographic Code Requirements

1. **100% Test Coverage**: All crypto code paths must be tested
2. **Type Checking**: Use mypy strict mode
3. **Human Review**: All crypto changes require manual review
4. **Dependency Auditing**: Regular security scans of dependencies
5. **Key Management**: Document secure key storage practices

### Security Checklist

Before committing crypto-related changes:

- [ ] 100% test coverage for new crypto code
- [ ] mypy passes in strict mode (`uv run mypy --strict pytest_jux`)
- [ ] Manual code review completed
- [ ] Security implications documented
- [ ] Test with invalid/malicious inputs
- [ ] Error handling covers edge cases

## Sprint Planning

Current sprint documentation: `docs/sprints/`

### Sprint Template

Each sprint should have:
- Sprint goal and duration
- User stories with acceptance criteria
- Technical tasks breakdown
- Definition of done
- Risk and dependencies
- Success metrics

## Contributing

### Before Starting Work

1. Check [Architecture Decision Records](docs/adr/) for project direction
2. Review current sprint goals (`docs/sprints/`)
3. Ensure development environment is set up
4. Create feature branch from `develop`

### Development Workflow

1. **Write Test** (Red): Test that fails for new behavior
2. **Implement** (Green): Minimal code to pass test
3. **Refactor**: Improve code quality
4. **Type Check**: Ensure mypy passes (`uv run mypy pytest_jux`)
5. **Format**: Run ruff format (`uv run ruff format .`)
6. **Coverage**: Verify >85% coverage (100% for crypto)
7. **Commit**: Use conventional commit format
8. **Update Docs**: If needed (Diátaxis structure)

### Pull Request Checklist

- [ ] All tests pass (`uv run pytest`)
- [ ] Code coverage >85% (100% for crypto)
- [ ] Type checking passes (`uv run mypy pytest_jux`)
- [ ] Code formatted (`uv run ruff format --check .`)
- [ ] Linting clean (`uv run ruff check .`)
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Conventional commit format used
- [ ] ADR created if significant decision made

## Resources

### Internal Documentation

- [Architecture Decision Records](docs/adr/)
- [Tutorials](docs/tutorials/)
- [How-To Guides](docs/howto/)
- [Reference Documentation](docs/reference/)
- [Architecture Explanations](docs/explanation/)

### External References

- [pytest Plugin Development](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)
- [lxml Documentation](https://lxml.de/)
- [signxml Documentation](https://signxml.readthedocs.io/)
- [JUnit XML Schema](https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd)
- [C4 Model](https://c4model.com/)
- [Structurizr DSL](https://docs.structurizr.com/dsl)
- [AI-Assisted Project Orchestration Patterns](../ai-assisted-project-orchestration/)

## Status

**Current Phase**: Sprint 3 Complete - Ready for Sprint 4
**Completed Sprints**:
- ✅ Sprint 0: Project Initialization (Security framework, ADRs, documentation)
- ✅ Sprint 1: Core Plugin Infrastructure (XML canonicalization, signing, pytest hooks)
- ✅ Sprint 2: CLI Tools (jux-keygen, jux-sign, jux-verify, jux-inspect)
- ✅ Sprint 3: Configuration, Storage & Caching (v0.1.3, v0.1.4)

**Sprint 3 Completed** (Configuration, Storage & Caching):
- ✅ Configuration management (config.py, 25 tests, 85.05% coverage)
- ✅ Environment metadata (metadata.py, 19 tests, 92.98% coverage)
- ✅ Local storage & caching (storage.py, 33 tests, 80.33% coverage)
- ✅ Cache management CLI (cache.py, 16 tests, 84.13% coverage)
- ✅ Config management CLI (config_cmd.py, 25 tests, 91.32% coverage)
- ✅ Multi-environment configuration guide (766 lines)
- ✅ CLAUDE.md updated with uv run best practices
- ⏸️ REST API client & publishing (postponed - no API server yet)

**Total Sprint 3**: 5 modules, 118 tests, 86.76% average coverage

**Next Sprint**: Sprint 4 - REST API Client & Plugin Integration
- 📋 Planned (awaiting Jux API Server availability)
- Target: v0.2.0 (Beta Milestone)
- Duration: 12-16 days (can span multiple calendar periods)
- See: [Sprint 4 Plan](docs/sprints/sprint-04-api-integration.md)

**Version**: 0.1.5 (released 2025-10-19)
**Current Branch**: develop

---

*This CLAUDE.md file provides AI-assisted development context. It should be updated as the project evolves.*
