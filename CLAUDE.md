# pytest-jux Development Guide

_AI-assisted development context and guidelines for pytest-jux_

## Project Overview

pytest-jux is a pytest plugin for signing and publishing JUnit XML test reports to the Jux REST API. This document provides context for AI-assisted development sessions and human developers.

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
- **[ADR-0003](docs/adr/0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md)**: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
  - Core libraries: lxml, signxml, cryptography, SQLAlchemy, click, rich
  - Target Python 3.11+ on Debian 12/13, openSUSE, Fedora
  - pytest plugin architecture with hook integration
  - Database abstraction for SQLite and PostgreSQL

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

### Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (development mode)
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .
ruff check --fix .  # Auto-fix where possible

# Type checking
mypy pytest_jux
mypy --strict pytest_jux  # Strict mode for crypto code

# Run all quality checks
make quality  # or: ruff check . && mypy pytest_jux
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pytest_jux --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_plugin.py

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v

# Watch mode (requires pytest-watch)
ptw
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

```bash
# Create release branch
git checkout -b release/0.1.0 develop

# Update version and changelog
# Edit pyproject.toml: version = "0.1.0"
# Edit CHANGELOG.md: Add release notes

# Tag release
git checkout main
git merge release/0.1.0
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge main
```

## Technology Stack

### Core Dependencies

- **lxml** (5.x): XML parsing, XPath, C14N canonicalization
- **signxml** (3.x): XMLDSig digital signatures
- **cryptography** (41.x+): RSA/ECDSA key management
- **SQLAlchemy** (2.x): ORM for SQLite and PostgreSQL
- **pytest** (7.4+/8.x): Plugin host and test framework
- **click** (8.x): CLI interfaces
- **rich** (13.x): Terminal output formatting
- **requests** (2.x): REST API client

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
├── test_canonicalizer.py   # C14N operations
├── test_api_client.py      # REST API integration
├── test_models.py          # SQLAlchemy models
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
- Boilerplate generation (pytest hooks, SQLAlchemy models, CLI commands)
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
│   ├── canonicalizer.py    # C14N canonicalization
│   ├── api_client.py       # REST API client
│   ├── models.py           # SQLAlchemy models
│   └── cli.py              # Optional CLI commands
├── tests/                   # Test suite (TDD)
├── docs/                    # Documentation
│   ├── tutorials/          # Getting started guides
│   ├── howto/             # Problem-solving guides
│   ├── reference/         # Complete API documentation
│   ├── explanation/       # Architecture and design
│   ├── adr/              # Architecture decisions
│   ├── architecture/     # C4 DSL models
│   └── sprints/          # Sprint documentation
├── .github/                # GitHub workflows (CI/CD)
├── pyproject.toml          # Project metadata and dependencies
├── setup.py                # Setup configuration
├── .editorconfig           # Editor formatting rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── .gitignore             # Git ignore patterns
├── CHANGELOG.md            # Change log
├── README.md              # Project overview
└── CLAUDE.md              # This file
```

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
- [ ] mypy passes in strict mode
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
4. **Type Check**: Ensure mypy passes
5. **Format**: Run ruff format
6. **Coverage**: Verify >85% coverage (100% for crypto)
7. **Commit**: Use conventional commit format
8. **Update Docs**: If needed (Diátaxis structure)

### Pull Request Checklist

- [ ] All tests pass (`pytest`)
- [ ] Code coverage >85% (100% for crypto)
- [ ] Type checking passes (`mypy pytest_jux`)
- [ ] Code formatted (`ruff format --check .`)
- [ ] Linting clean (`ruff check .`)
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
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JUnit XML Schema](https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd)
- [C4 Model](https://c4model.com/)
- [Structurizr DSL](https://docs.structurizr.com/dsl)
- [AI-Assisted Project Orchestration Patterns](../ai-assisted-project-orchestration/)

## Status

**Current Phase**: Project Initialization (Sprint 0)
**Next Milestone**: Sprint 1 - Core plugin infrastructure and XML signing
**Version**: 0.1.0-dev (pre-release)

---

*This CLAUDE.md file provides AI-assisted development context. It should be updated as the project evolves.*
