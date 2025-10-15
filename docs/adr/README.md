# Architecture Decision Records

This directory contains Architecture Decision Records for the pytest-jux project.

## Index

- [ADR-0001](0001-record-architecture-decisions.md): Record architecture decisions
- [ADR-0002](0002-adopt-development-best-practices.md): Adopt development best practices
- [ADR-0003](0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md): Use Python 3 with pytest, lxml, signxml, and SQLAlchemy stack
- [ADR-0004](0004-adopt-apache-license-2.0.md): Adopt Apache License 2.0
- [ADR-0005](0005-adopt-python-ecosystem-security-framework.md): Adopt Python Ecosystem Security Framework

## About ADRs

Architecture Decision Records document significant architectural decisions made during the development of pytest-jux. Each ADR captures:

- **Context**: The circumstances and requirements that led to the decision
- **Decision**: What was decided and why
- **Consequences**: The positive and negative outcomes of the decision
- **Status**: Whether the decision is proposed, accepted, deprecated, or superseded

## Creating New ADRs

When making a significant architectural decision:

1. Create a new file: `docs/adr/NNNN-title-with-dashes.md`
2. Use the next sequential number (NNNN)
3. Follow the template from ADR-0001
4. Include Status, Context, Decision, and Consequences sections
5. Update this index with the new ADR

## ADR Process

ADRs are living documents that can evolve:

- **Proposed**: Under discussion
- **Accepted**: Decision made and being implemented
- **Deprecated**: Decision no longer recommended but not yet superseded
- **Superseded**: Replaced by a newer decision (reference the new ADR)

## Significant Decisions

Decisions that warrant ADRs include:

- Technology stack choices (languages, frameworks, libraries)
- Architectural patterns and integration approaches
- Security and cryptographic strategies
- Database schema and migration approaches
- API design and protocol decisions
- Testing strategies and quality gates
- Licensing and intellectual property decisions
- Security frameworks and compliance standards

## Security ADRs

Security-related decisions are particularly important for pytest-jux due to its cryptographic nature:

- **ADR-0004**: License selection (Apache 2.0 for patent protection)
- **ADR-0005**: Comprehensive security framework (OpenSSF, PyPA tools)

See [docs/security/](../security/) for detailed security documentation.

## References

- [Architecture Decision Records](https://adr.github.io/)
- [Joel Parker Henderson's ADR repository](https://github.com/joelparkerhenderson/architecture-decision-record)
