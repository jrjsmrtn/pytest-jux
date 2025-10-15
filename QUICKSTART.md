# pytest-jux Quick Start Guide

**Author**: Georges Martin (jrjsmrtn@gmail.com)  
**License**: Apache License 2.0  
**Version**: 0.1.0-dev

## What Is This?

pytest-jux is a pytest plugin that:
1. Signs JUnit XML test reports with XMLDSig digital signatures
2. Calculates canonical hashes for duplicate detection
3. Publishes signed reports to Jux REST API

## Project Initialized ✅

The project follows the AI-Assisted Project Orchestration pattern language with:

- **4 ADRs**: Foundation decisions documented
- **Apache License 2.0**: With proper copyright (Georges Martin, 2025)
- **Complete Structure**: Diátaxis docs, C4 DSL architecture, tests
- **Dev Tools**: ruff, mypy, pre-commit hooks configured
- **Python Package**: Ready for development

## Quick Commands

### Setup Development Environment

```bash
cd ~/Projects/jux-tools/pytest-jux

# Initialize git repository
chmod +x init-git.sh
./init-git.sh

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Workflow

```bash
# Start new feature
git checkout develop
git checkout -b feature/xml-signing

# Write tests first (TDD)
# Edit tests/test_signer.py

# Run tests
pytest

# Implement feature
# Edit pytest_jux/signer.py

# Code quality
ruff format .
ruff check .
mypy pytest_jux

# Commit with conventional commits
git commit -m "feat(signer): implement XMLDSig signature generation"

# Complete feature
git checkout develop
git merge feature/xml-signing
```

### Key Files

- **CLAUDE.md**: AI-assisted development context
- **docs/adr/**: Architecture decisions
- **PROJECT_INIT_SUMMARY.md**: What was created and why
- **README.md**: Project overview
- **pyproject.toml**: Python configuration

## Technology Stack

- **Python 3.11+**: Core language
- **lxml**: XML parsing and C14N
- **signxml**: XMLDSig signatures
- **cryptography**: Key management
- **SQLAlchemy**: Database ORM
- **pytest**: Plugin framework and testing
- **ruff**: Linting and formatting
- **mypy**: Type checking

## Next Steps

### Sprint 1: Core Plugin Infrastructure

1. Implement pytest hooks in `pytest_jux/plugin.py`
2. Implement XML signing in `pytest_jux/signer.py`
3. Implement canonicalization in `pytest_jux/canonicalizer.py`
4. Write comprehensive tests (TDD)
5. Document in `docs/tutorials/`

### Quality Gates

- ✅ All tests pass
- ✅ mypy strict mode clean
- ✅ ruff format and lint clean
- ✅ >85% code coverage (100% for crypto)

## Important Reminders

1. **TDD First**: Write tests before implementation
2. **Type Hints**: Use for all functions (mypy strict)
3. **Security**: 100% coverage for cryptographic code
4. **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`
5. **Review ADRs**: Check `docs/adr/` before major decisions

## Resources

- ADRs: `docs/adr/README.md`
- AI Context: `CLAUDE.md`
- Full Summary: `PROJECT_INIT_SUMMARY.md`
- License: `LICENSE` (Apache 2.0)

---

**Status**: Project initialized, ready for Sprint 1 development

"Ready you are. Begin the coding, you may."
