# pytest-jux

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![pytest](https://img.shields.io/badge/pytest-7.4%2B%20%7C%208.x-blue.svg)](https://pytest.org/)
[![Security](https://img.shields.io/badge/security-framework-green.svg)](docs/security/SECURITY.md)

_A pytest plugin for signing and publishing JUnit XML test reports to the Jux REST API_

## Overview

pytest-jux is a pytest plugin that automatically signs JUnit XML test reports using XML digital signatures (XMLDSig) and publishes them to a Jux REST API for storage and analysis. It enables system administrators, integrators, and infrastructure engineers to maintain a chain-of-trust for test results across local and distributed environments.

## Features

- **Automatic Report Signing**: Signs JUnit XML reports with XML digital signatures after test execution
- **XML Canonicalization**: Uses C14N for detecting duplicate reports via canonical hash
- **Chain-of-Trust**: Cryptographic verification ensures report integrity and provenance
- **REST API Integration**: Publishes signed reports to Jux backend (SQLite or PostgreSQL)
- **pytest Integration**: Seamless integration via pytest hooks (post-session processing)
- **Duplicate Detection**: Canonical hash-based deduplication prevents redundant storage
- **Environment Metadata**: Captures test environment context (hostname, user, platform)
- **Security Framework**: Comprehensive security with automated scanning and threat modeling

## Security

pytest-jux implements a comprehensive security framework:

- **Automated Scanning**: pip-audit, Bandit, Safety, Trivy
- **Threat Modeling**: STRIDE methodology with 19 identified threats
- **Cryptographic Standards**: NIST-compliant algorithms (RSA-SHA256, ECDSA-SHA256)
- **Supply Chain**: Dependabot, OpenSSF Scorecard, planned Sigstore signing
- **Vulnerability Reporting**: Coordinated disclosure with 48-hour response time

See [Security Policy](docs/security/SECURITY.md) for vulnerability reporting and [Security Framework](docs/security/IMPLEMENTATION_SUMMARY.md) for complete details.

## Architecture Documentation

This project uses Architecture Decision Records (ADRs) to track significant architectural decisions:

- **[ADR-0001](docs/adr/0001-record-architecture-decisions.md)**: Record architecture decisions
- **[ADR-0002](docs/adr/0002-adopt-development-best-practices.md)**: Adopt development best practices
- **[ADR-0003](docs/adr/0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md)**: Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
- **[ADR-0004](docs/adr/0004-adopt-apache-license-2.0.md)**: Adopt Apache License 2.0
- **[ADR-0005](docs/adr/0005-adopt-python-ecosystem-security-framework.md)**: Adopt Python Ecosystem Security Framework

See the [docs/adr/](docs/adr/) directory for complete decision history.

## Requirements

- Python 3.11+
- pytest 7.4+ or 8.x
- Supported OS: Debian 12/13, latest openSUSE, latest Fedora

## Installation

```bash
# From PyPI (when published)
uv pip install pytest-jux

# From source (development)
cd pytest-jux
uv pip install -e ".[dev,security]"
```

## Usage

### Basic Usage

```bash
# Run tests with JUnit XML generation and auto-publish
pytest --junit-xml=report.xml \
       --jux-publish \
       --jux-api-url=https://jux.example.com/api \
       --jux-key=~/.jux/private_key.pem
```

### Configuration via pytest.ini

```ini
[pytest]
addopts = --junit-xml=report.xml
jux_api_url = https://jux.example.com/api
jux_key_path = ~/.jux/private_key.pem
```

### Plugin Options

- `--jux-publish`: Enable pytest-jux plugin (default: disabled)
- `--jux-api-url URL`: Jux REST API endpoint
- `--jux-key PATH`: Path to private key for signing (PEM format)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/jrjsmrtn/pytest-jux.git
cd pytest-jux

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install development dependencies
uv pip install -e ".[dev,security]"

# Install pre-commit hooks
pre-commit install
```

### Development Commands

#### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# All quality checks
make quality
```

#### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run security tests
make test-security
```

#### Security

```bash
# Run security scanners
make security-scan

# Run security test suite
make security-test

# Complete security validation
make security-full
```

#### Architecture Validation

```bash
# Validate C4 DSL architecture model
podman run --rm -v "$(pwd)/docs/architecture:/usr/local/structurizr" \
  structurizr/cli validate -workspace workspace.dsl

# Generate architecture diagrams
podman run --rm -p 8080:8080 \
  -v "$(pwd)/docs/architecture:/usr/local/structurizr" structurizr/lite
# Open http://localhost:8080
```

### Project Structure

```
pytest-jux/
├── pytest_jux/              # Plugin source code
│   ├── __init__.py
│   ├── plugin.py           # pytest hooks
│   ├── signer.py           # XML signing
│   ├── canonicalizer.py    # C14N operations
│   ├── api_client.py       # REST API client
│   └── models.py           # SQLAlchemy models
├── tests/                   # Test suite
│   ├── test_plugin.py
│   ├── test_signer.py
│   ├── security/           # Security tests
│   └── fixtures/           # JUnit XML fixtures
├── docs/                    # Documentation
│   ├── tutorials/          # Learning-oriented
│   ├── howto/             # Problem-oriented
│   ├── reference/         # Information-oriented
│   ├── explanation/       # Understanding-oriented
│   ├── adr/              # Architecture decisions
│   ├── architecture/     # C4 DSL models
│   └── security/         # Security documentation
├── .github/
│   └── workflows/
│       └── security.yml    # Security scanning workflow
├── LICENSE                 # Apache License 2.0
├── NOTICE                  # Copyright notices
├── Makefile                # Development commands
├── pyproject.toml          # Project metadata
└── README.md              # This file
```

## Architecture Overview

### pytest Plugin Integration

pytest-jux integrates with pytest via the `pytest_sessionfinish` hook, processing JUnit XML reports after test execution completes.

### XML Signature Workflow

1. **Generate**: pytest creates JUnit XML report (`--junit-xml`)
2. **Canonicalize**: Convert XML to canonical form (C14N)
3. **Hash**: Calculate SHA-256 hash of canonical XML (for deduplication)
4. **Sign**: Generate XMLDSig signature using private key
5. **Publish**: POST signed report to Jux REST API

### C4 DSL Architecture Models

The project's architecture is documented using C4 DSL models in `docs/architecture/`. See the architecture documentation for:

- System context: pytest-jux in the Jux ecosystem
- Container view: Plugin components and REST API integration
- Component view: Internal module structure

## AI-Assisted Development Notes

### AI Collaboration Context

- This project follows AI-Assisted Project Orchestration patterns
- ADRs provide AI context across development sessions
- Sprint documentation maintains development continuity (see `docs/sprints/`)
- C4 DSL models provide visual architecture context
- TDD approach guides AI-assisted test and implementation generation

### Development Practices Integration

- AI assistance for boilerplate generation (pytest hooks, SQLAlchemy models)
- Human review required for cryptographic code (security-critical)
- Quality gates: all tests pass, type checking clean, code coverage >85%
- Context management: ADRs and sprint docs enable session continuity

## Contributing

Contributions welcome! Please:

1. Read the [Architecture Decision Records](docs/adr/) to understand project direction
2. Follow the [development best practices](docs/adr/0002-adopt-development-best-practices.md)
3. Review [security guidelines](docs/security/SECURITY.md) for security-sensitive changes
4. Ensure all tests pass and coverage remains >85%
5. Run security scanners: `make security-full`
6. Update documentation for new features
7. Use conventional commits for clear changelog generation

## License

Copyright 2025 Georges Martin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [LICENSE](LICENSE) for the full license text.

## Related Projects

- **Jux**: JUnit XML toolkit (Elixir/Phoenix)
  - Parent project providing REST API backend
  - SQLite (local) and PostgreSQL (distributed) storage
  - Web and CLI interfaces for browsing test reports

## Support

- Documentation: [docs/](docs/)
- Security: [Security Policy](docs/security/SECURITY.md)
- Issues: [GitHub Issues](https://github.com/jrjsmrtn/pytest-jux/issues)
- Discussions: [GitHub Discussions](https://github.com/jrjsmrtn/pytest-jux/discussions)
