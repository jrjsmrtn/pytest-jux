# pytest-jux Documentation Index

Welcome to the pytest-jux documentation! This index provides a complete map of all available documentation organized by type and purpose.

## 📖 Documentation Structure

This documentation follows the [Diátaxis framework](https://diataxis.fr/), organizing content into four categories:

- **Tutorials**: Learning-oriented, step-by-step guides for getting started
- **How-To Guides**: Problem-oriented, practical solutions to specific tasks
- **Reference**: Information-oriented, technical descriptions of APIs and commands
- **Explanation**: Understanding-oriented, conceptual discussions and design decisions

---

## 🚀 Quick Start

**New to pytest-jux?** Start here:

1. **[Quick Start Guide](tutorials/quick-start.md)** - Install and run your first signed test report (5 minutes)
2. **[Setting Up Signing Keys](tutorials/setting-up-signing-keys.md)** - Generate and configure cryptographic keys (10 minutes)
3. **[First Signed Report Tutorial](tutorials/first-signed-report.md)** - Complete beginner tutorial with tamper detection (15-20 minutes)

---

## 📚 Tutorials (Learning-Oriented)

Step-by-step guides to learn pytest-jux from beginner to advanced:

### Beginner
- **[Quick Start](tutorials/quick-start.md)** - Get started in 5 minutes
- **[Setting Up Signing Keys](tutorials/setting-up-signing-keys.md)** - Key generation tutorial
- **[First Signed Report](tutorials/first-signed-report.md)** - Complete beginner walkthrough (15-20 min)

### Intermediate
- **[Integration Testing](tutorials/integration-testing.md)** - Multi-environment setup and CI/CD integration (30-45 min)

### Advanced
- **[Custom Signing Workflows](tutorials/custom-signing-workflows.md)** - Programmatic API usage, batch processing, custom metadata (30-40 min)

---

## 🛠️ How-To Guides (Problem-Oriented)

Practical solutions to specific problems:

### Key Management
- **[Rotate Signing Keys](howto/rotate-signing-keys.md)** - Safe key rotation procedure
- **[Secure Key Storage](howto/secure-key-storage.md)** - Best practices for production key management
- **[Backup & Restore Keys](howto/backup-restore-keys.md)** - Key backup and disaster recovery

### Storage & Cache Management
- **[Migrate Storage Paths](howto/migrate-storage-paths.md)** - Change storage locations without data loss
- **[Manage Report Cache](howto/manage-report-cache.md)** - Cache cleanup, backup, and optimization
- **[Choosing Storage Modes](howto/choosing-storage-modes.md)** - Select the right storage strategy

### Configuration
- **[Multi-Environment Configuration](howto/multi-environment-config.md)** - Manage dev, staging, and production configs
- **[CI/CD Deployment](howto/ci-cd-deployment.md)** - GitHub Actions, GitLab CI, Jenkins integration

### Integration
- **[Integrate with pytest Plugins](howto/integrate-pytest-plugins.md)** - Work with pytest-html, pytest-metadata, pytest-xdist
- **[Add Metadata to Reports](howto/add-metadata-to-reports.md)** - Custom environment metadata

### Troubleshooting
- **[Troubleshooting Guide](howto/troubleshooting.md)** - Diagnose and fix common issues

### Publishing (PyPI)
- **[PyPI Trusted Publishing Setup](howto/pypi-trusted-publishing-setup.md)** - GitHub Actions OIDC publishing

---

## 📖 Reference (Information-Oriented)

Complete technical reference documentation:

### API Reference
- **[API Index](reference/api/index.md)** - Overview of all modules
- **[Canonicalizer API](reference/api/canonicalizer.md)** - XML canonicalization and hashing
- **[Signer API](reference/api/signer.md)** - XMLDSig signature generation
- **[Verifier API](reference/api/verifier.md)** - Signature verification
- **[Storage API](reference/api/storage.md)** - Report caching and storage
- **[Config API](reference/api/config.md)** - Configuration management
- **[Metadata API](reference/api/metadata.md)** - Environment metadata collection
- **[Plugin API](reference/api/plugin.md)** - pytest plugin hooks

### CLI Reference
- **[CLI Index](reference/cli/index.md)** - Overview of all commands
- **Commands**:
  - `jux-keygen` - Key generation
  - `jux-sign` - Report signing
  - `jux-verify` - Signature verification
  - `jux-inspect` - Report inspection
  - `jux-cache` - Cache management (list, show, stats, clean)
  - `jux-config` - Configuration management (list, dump, view, init, validate)

### Configuration & Error Codes
- **[Configuration Reference](reference/configuration.md)** - All configuration options (CLI, environment, files)
- **[Error Code Reference](reference/error-codes.md)** - Complete error catalog with solutions

---

## 💡 Explanation (Understanding-Oriented)

Conceptual understanding and design discussions:

### Core Concepts
- **[Understanding pytest-jux](explanation/understanding-pytest-jux.md)** - High-level overview and use cases
- **[Architecture](explanation/architecture.md)** - System design, components, and design decisions
- **[Security](explanation/security.md)** - Why sign test reports, threat model, security best practices
- **[Performance](explanation/performance.md)** - Performance characteristics, benchmarks, optimization

---

## 🔒 Security Documentation

Security-critical documentation:

- **[SECURITY.md](security/SECURITY.md)** - Security policy and vulnerability reporting
- **[THREAT_MODEL.md](security/THREAT_MODEL.md)** - Threat analysis and mitigation strategies
- **[CRYPTO_STANDARDS.md](security/CRYPTO_STANDARDS.md)** - Cryptographic standards and algorithms
- **[IMPLEMENTATION_SUMMARY.md](security/IMPLEMENTATION_SUMMARY.md)** - Security implementation details
- **[SLSA_VERIFICATION.md](security/SLSA_VERIFICATION.md)** - SLSA provenance verification

---

## 🏗️ Architecture Decision Records (ADRs)

Significant architectural decisions and their rationale:

- **[ADR Index](adr/README.md)** - Complete list of all ADRs
- **Key ADRs**:
  - [ADR-0001](adr/0001-record-architecture-decisions.md) - Record architecture decisions
  - [ADR-0002](adr/0002-adopt-development-best-practices.md) - Development best practices (TDD, Diátaxis, Gitflow)
  - [ADR-0003](adr/0003-use-python3-pytest-lxml-signxml-sqlalchemy-stack.md) - Technology stack
  - [ADR-0004](adr/0004-adopt-apache-license-2.0.md) - Apache License 2.0
  - [ADR-0005](adr/0005-adopt-python-ecosystem-security-framework.md) - Security framework
  - [ADR-0006](adr/0006-adopt-slsa-build-level-2-compliance.md) - SLSA Build Level 2
  - [ADR-0007](adr/0007-adopt-test-coverage-visibility-standards.md) - Test coverage standards
  - [ADR-0008](adr/0008-adopt-openssf-best-practices-badge-program.md) - OpenSSF Best Practices
  - [ADR-0009](adr/0009-adopt-reuse-spdx-license-identifiers.md) - REUSE SPDX compliance
  - [ADR-0010](adr/0010-remove-database-dependencies.md) - Remove database dependencies

---

## 📋 Project Information

Project management and planning documents:

- **[README.md](../README.md)** - Project overview and quick start
- **[CHANGELOG.md](../CHANGELOG.md)** - Release history and changes
- **[ROADMAP.md](ROADMAP.md)** - Strategic roadmap and future plans
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[LICENSE](../LICENSE)** - Apache License 2.0

---

## 🎯 Documentation by Task

### I want to...

#### Get Started
- **Install pytest-jux** → [Quick Start](tutorials/quick-start.md)
- **Generate signing keys** → [Setting Up Signing Keys](tutorials/setting-up-signing-keys.md)
- **Sign my first report** → [First Signed Report](tutorials/first-signed-report.md)

#### Set Up in CI/CD
- **Configure GitHub Actions** → [CI/CD Deployment](howto/ci-cd-deployment.md) (GitHub Actions section)
- **Configure GitLab CI** → [CI/CD Deployment](howto/ci-cd-deployment.md) (GitLab CI section)
- **Configure Jenkins** → [CI/CD Deployment](howto/ci-cd-deployment.md) (Jenkins section)
- **Set up multi-environment config** → [Multi-Environment Configuration](howto/multi-environment-config.md)

#### Manage Keys
- **Rotate signing keys** → [Rotate Signing Keys](howto/rotate-signing-keys.md)
- **Store keys securely** → [Secure Key Storage](howto/secure-key-storage.md)
- **Backup keys** → [Backup & Restore Keys](howto/backup-restore-keys.md)

#### Manage Storage
- **Choose storage mode** → [Choosing Storage Modes](howto/choosing-storage-modes.md)
- **Clean up cache** → [Manage Report Cache](howto/manage-report-cache.md)
- **Migrate storage location** → [Migrate Storage Paths](howto/migrate-storage-paths.md)

#### Integrate with Tools
- **Use with pytest-html** → [Integrate with pytest Plugins](howto/integrate-pytest-plugins.md)
- **Use with pytest-metadata** → [Add Metadata to Reports](howto/add-metadata-to-reports.md)
- **Use programmatically** → [Custom Signing Workflows](tutorials/custom-signing-workflows.md)

#### Troubleshoot Issues
- **Fix signature verification errors** → [Troubleshooting Guide](howto/troubleshooting.md) (Signature Verification)
- **Fix configuration errors** → [Troubleshooting Guide](howto/troubleshooting.md) (Configuration Issues)
- **Optimize performance** → [Troubleshooting Guide](howto/troubleshooting.md) (Performance Optimization)
- **Debug CI/CD issues** → [Troubleshooting Guide](howto/troubleshooting.md) (CI/CD Integration)

#### Understand Concepts
- **Why sign test reports?** → [Security Explanation](explanation/security.md)
- **How does signing work?** → [Architecture Explanation](explanation/architecture.md)
- **What are the security guarantees?** → [Security Explanation](explanation/security.md) (Security Model)
- **What's the performance impact?** → [Performance Explanation](explanation/performance.md)

#### Look Up Reference
- **CLI command options** → [CLI Reference](reference/cli/index.md)
- **Python API usage** → [API Reference](reference/api/index.md)
- **Configuration options** → [Configuration Reference](reference/configuration.md)
- **Error codes** → [Error Code Reference](reference/error-codes.md)

---

## 📊 Documentation Statistics

**Total Documents**: 50+ documents

**By Category**:
- **Tutorials**: 4 guides
- **How-To Guides**: 10 guides
- **Reference**: 15 documents (7 API + 7 CLI + 2 config/errors)
- **Explanation**: 4 documents
- **Security**: 5 documents
- **ADRs**: 11 decisions
- **Project**: 4 documents

**Total Lines**: ~30,000+ lines of documentation

---

## 🔍 Search Tips

**In Sphinx Documentation** (if using built HTML):
- Use the search box in the navigation bar
- Search is full-text and indexes all content
- Use quotes for exact phrases: `"XMLDSig signature"`

**In GitHub**:
- Use GitHub's file finder: Press `t` and type filename
- Use GitHub search: `repo:jrjsmrtn/pytest-jux <search term>`

**In Local Repository**:
```bash
# Search all markdown files
grep -r "search term" docs/

# Search specific category
grep -r "search term" docs/howto/

# Search with line numbers
grep -rn "search term" docs/
```

---

## 🆘 Need Help?

**Can't find what you need?**

1. **Check the [Troubleshooting Guide](howto/troubleshooting.md)** - Covers most common issues
2. **Search the documentation** - Use tips above
3. **Check [GitHub Issues](https://github.com/jrjsmrtn/pytest-jux/issues)** - See if others had similar questions
4. **Review [ADRs](adr/README.md)** - Understand design decisions
5. **Read the [Security Documentation](security/SECURITY.md)** - For security-related questions

**Still stuck?**
- Open a [GitHub Issue](https://github.com/jrjsmrtn/pytest-jux/issues/new)
- Check the [Contributing Guide](../CONTRIBUTING.md) for community guidelines

---

## 📅 Documentation Updates

**Last Updated**: 2026-01-08
**Version**: v0.4.1
**Sprint**: Sprint 4 Complete (REST API Client & Plugin Integration)

**Recent Additions** (Sprint 5):
- ✅ All 7 API modules documented (auto-generated + enhanced)
- ✅ Complete CLI reference with sphinx-argparse-cli
- ✅ Configuration and error code references
- ✅ 3 complete tutorials (beginner, intermediate, advanced)
- ✅ 10 comprehensive how-to guides
- ✅ 3 explanation documents (architecture, security, performance)
- ✅ Enhanced CLI help text
- ✅ Improved error messages
- ✅ Shell completion scripts (bash, zsh, fish)

---

## 🤝 Contributing to Documentation

Found a typo? Want to improve a guide? See **[CONTRIBUTING.md](../CONTRIBUTING.md)** for:
- Documentation standards
- How to submit improvements
- Documentation review process
- Diátaxis principles

---

**Happy Learning!** 🎉

---

*This documentation index is maintained as part of Sprint 5: Documentation & User Experience. For documentation issues or suggestions, please open a GitHub issue.*
