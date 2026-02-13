# pytest-jux Documentation Navigation Guide

This guide helps you find the right documentation quickly, no matter what you're trying to accomplish.

## Quick Start (5 Minutes)

**New to pytest-jux?** Follow this path:

1. **[Quick Start Tutorial](tutorials/quick-start.md)** (5 min) - Install and run your first signed report
2. **[Setting Up Signing Keys](tutorials/setting-up-signing-keys.md)** (10 min) - Generate cryptographic keys
3. **[First Signed Report](tutorials/first-signed-report.md)** (15-20 min) - Complete beginner walkthrough

After these three tutorials, you'll understand pytest-jux fundamentals and be ready for production use.

---

## Finding Documentation by Your Goal

### I'm Learning pytest-jux

**Use Tutorials** - These are step-by-step learning paths:

- **Beginner** (new to pytest-jux):
  - Start with [Quick Start](tutorials/quick-start.md)
  - Then [Setting Up Signing Keys](tutorials/setting-up-signing-keys.md)
  - Complete [First Signed Report](tutorials/first-signed-report.md)

- **Intermediate** (setting up CI/CD):
  - Read [Integration Testing](tutorials/integration-testing.md)
  - Covers multi-environment setup and CI/CD integration

- **Advanced** (programmatic usage):
  - Study [Custom Signing Workflows](tutorials/custom-signing-workflows.md)
  - Learn batch processing and custom metadata

### I'm Solving a Problem

**Use How-To Guides** - These solve specific problems:

**Key Management Problems:**
- Need to change keys? → [Rotate Signing Keys](howto/rotate-signing-keys.md)
- Keys compromised? → [Rotate Signing Keys](howto/rotate-signing-keys.md) + [Secure Key Storage](howto/secure-key-storage.md)
- Need to backup keys? → [Backup & Restore Keys](howto/backup-restore-keys.md)
- Keys not secure? → [Secure Key Storage](howto/secure-key-storage.md)

**Storage Problems:**
- Running out of space? → [Manage Report Cache](howto/manage-report-cache.md)
- Need to move storage? → [Migrate Storage Paths](howto/migrate-storage-paths.md)
- Which storage mode? → [Choosing Storage Modes](howto/choosing-storage-modes.md)

**Configuration Problems:**
- Multiple environments? → [Multi-Environment Configuration](howto/multi-environment-config.md)
- Setting up CI/CD? → [CI/CD Deployment](howto/ci-cd-deployment.md)

**Integration Problems:**
- Using pytest plugins? → [Integrate with pytest Plugins](howto/integrate-pytest-plugins.md)
- Need custom metadata? → [Add Metadata to Reports](howto/add-metadata-to-reports.md)

**Something's Broken:**
- Signature verification fails? → [Troubleshooting Guide](howto/troubleshooting.md) (Signature Verification section)
- Configuration errors? → [Troubleshooting Guide](howto/troubleshooting.md) (Configuration Issues section)
- Performance problems? → [Troubleshooting Guide](howto/troubleshooting.md) (Performance Optimization section)
- CI/CD issues? → [Troubleshooting Guide](howto/troubleshooting.md) (CI/CD Integration section)

### I'm Looking Up Something Specific

**Use Reference Documentation** - These provide complete technical details:

**API Reference:**
- Python API documentation? → [API Index](reference/api/index.md)
- Specific module? → [API Index](reference/api/index.md) (links to all 7 modules)
- Function signature? → Search the specific module API doc

**CLI Reference:**
- Command options? → [CLI Index](reference/cli/index.md)
- Specific command? → [CLI Index](reference/cli/index.md) (auto-generated docs for all 6 commands)
- Exit codes? → [CLI Index](reference/cli/index.md) (includes exit codes)

**Configuration:**
- All configuration options? → [Configuration Reference](reference/configuration.md)
- Option precedence? → [Configuration Reference](reference/configuration.md) (Precedence section)
- Environment variables? → [Configuration Reference](reference/configuration.md) (Environment Variables section)

**Error Codes:**
- What does error code X mean? → [Error Code Reference](reference/error-codes.md)
- How to fix error X? → [Error Code Reference](reference/error-codes.md) (includes solutions)

### I Want to Understand How It Works

**Use Explanations** - These provide conceptual understanding:

**Fundamental Concepts:**
- What is pytest-jux? → [Understanding pytest-jux](explanation/understanding-pytest-jux.md)
- How is it architected? → [Architecture](explanation/architecture.md)
- Why sign test reports? → [Security](explanation/security.md) (Why Sign Test Reports section)
- What's the performance impact? → [Performance](explanation/performance.md)

**Deep Dives:**
- System design? → [Architecture](explanation/architecture.md) (Design Principles, Components)
- Security guarantees? → [Security](explanation/security.md) (Security Model, Threat Model)
- What attacks are mitigated? → [Security](explanation/security.md) (Threat Model section)
- Performance characteristics? → [Performance](explanation/performance.md) (Benchmarks, Scalability)

---

## Finding Documentation by Topic

### Security

1. **Getting Started with Security**:
   - [Security Explanation](explanation/security.md) - Why sign reports, security model
   - [Setting Up Signing Keys](tutorials/setting-up-signing-keys.md) - Key generation

2. **Operational Security**:
   - [Secure Key Storage](howto/secure-key-storage.md) - Production key management
   - [Rotate Signing Keys](howto/rotate-signing-keys.md) - Safe key rotation
   - [Backup & Restore Keys](howto/backup-restore-keys.md) - Disaster recovery

3. **Security Reference**:
   - [Security Policy](security/SECURITY.md) - Vulnerability reporting
   - [Threat Model](security/THREAT_MODEL.md) - Threat analysis
   - [Cryptographic Standards](security/CRYPTO_STANDARDS.md) - Algorithms
   - [SLSA Verification](security/SLSA_VERIFICATION.md) - Supply chain security

### Configuration

1. **Getting Started**:
   - [Multi-Environment Configuration](howto/multi-environment-config.md) - Dev, staging, production

2. **Reference**:
   - [Configuration Reference](reference/configuration.md) - All options
   - [Config API](reference/api/config.md) - Python API

3. **CLI Tools**:
   - [CLI Index](reference/cli/index.md) - jux-config command

### Storage & Caching

1. **Getting Started**:
   - [Choosing Storage Modes](howto/choosing-storage-modes.md) - Which mode to use

2. **Operations**:
   - [Manage Report Cache](howto/manage-report-cache.md) - Cleanup, backup
   - [Migrate Storage Paths](howto/migrate-storage-paths.md) - Change location

3. **Reference**:
   - [Storage API](reference/api/storage.md) - Python API
   - [CLI Index](reference/cli/index.md) - jux-cache command

### CI/CD Integration

1. **Getting Started**:
   - [Integration Testing Tutorial](tutorials/integration-testing.md) - CI/CD setup

2. **Specific CI Systems**:
   - [CI/CD Deployment](howto/ci-cd-deployment.md):
     - GitHub Actions section
     - GitLab CI section
     - Jenkins section

3. **Troubleshooting**:
   - [Troubleshooting Guide](howto/troubleshooting.md) - CI/CD Integration section

### Key Management

1. **Getting Started**:
   - [Setting Up Signing Keys](tutorials/setting-up-signing-keys.md) - Generate keys

2. **Operations**:
   - [Rotate Signing Keys](howto/rotate-signing-keys.md) - Change keys safely
   - [Secure Key Storage](howto/secure-key-storage.md) - Production best practices
   - [Backup & Restore Keys](howto/backup-restore-keys.md) - Disaster recovery

3. **Reference**:
   - [CLI Index](reference/cli/index.md) - jux-keygen command
   - [Cryptographic Standards](security/CRYPTO_STANDARDS.md) - Algorithms

---

## Documentation Framework (Diátaxis)

pytest-jux documentation follows the [Diátaxis framework](https://diataxis.fr/), which organizes content by user needs:

### 📚 Tutorials (Learning-Oriented)

**When to use**: You're learning pytest-jux for the first time.

**What you'll find**:
- Step-by-step instructions
- Complete, working examples
- Progressive learning path (beginner → advanced)
- Safe to follow without understanding everything

**Examples**:
- "Follow these steps to sign your first report"
- "Complete this tutorial to understand the workflow"

### 🛠️ How-To Guides (Problem-Oriented)

**When to use**: You have a specific problem to solve.

**What you'll find**:
- Solutions to common problems
- Practical, actionable steps
- Assumes you understand pytest-jux basics
- Focused on achieving a specific goal

**Examples**:
- "How to rotate signing keys"
- "How to set up GitHub Actions"

### 📖 Reference (Information-Oriented)

**When to use**: You need to look up specific details.

**What you'll find**:
- Complete API documentation
- All CLI command options
- All configuration options
- Technical specifications
- Dry, factual information

**Examples**:
- "What parameters does this function accept?"
- "What are all the configuration options?"

### 💡 Explanation (Understanding-Oriented)

**When to use**: You want to understand concepts and design.

**What you'll find**:
- Why things work the way they do
- Design decisions and trade-offs
- Conceptual discussions
- Background knowledge

**Examples**:
- "Why does pytest-jux use XMLDSig?"
- "What are the security guarantees?"

---

## Search Strategies

### In Sphinx Documentation (HTML)

If you're viewing the built HTML documentation:

1. **Use the search box** in the navigation bar
2. **Use quotes** for exact phrases: `"XMLDSig signature"`
3. **Search is full-text** and indexes all content

### In GitHub

When browsing on GitHub:

1. **File finder**: Press `t` and type the filename
2. **GitHub search**: `repo:jrjsmrtn/pytest-jux <search term>`
3. **Browse by directory**:
   - `docs/tutorials/` - Tutorials
   - `docs/howto/` - How-to guides
   - `docs/reference/` - Reference docs
   - `docs/explanation/` - Explanations

### In Local Repository

When working locally:

```bash
# Search all markdown files
grep -r "search term" docs/

# Search specific category
grep -r "search term" docs/howto/

# Search with line numbers
grep -rn "search term" docs/

# Search for function names
grep -r "def function_name" pytest_jux/

# Search for class names
grep -r "class ClassName" pytest_jux/
```

---

## Common Navigation Patterns

### "I just want to get started"

1. [Quick Start](tutorials/quick-start.md) - 5 minutes
2. [Setting Up Signing Keys](tutorials/setting-up-signing-keys.md) - 10 minutes
3. [First Signed Report](tutorials/first-signed-report.md) - 15-20 minutes

### "I need to set up CI/CD"

1. [Integration Testing Tutorial](tutorials/integration-testing.md) - Understand multi-environment setup
2. [CI/CD Deployment](howto/ci-cd-deployment.md) - Your specific CI system
3. [Troubleshooting Guide](howto/troubleshooting.md) - If issues arise

### "Something's not working"

1. **Start here**: [Troubleshooting Guide](howto/troubleshooting.md)
2. **Check error code**: [Error Code Reference](reference/error-codes.md)
3. **Still stuck?**: [GitHub Issues](https://github.com/jux-tools/pytest-jux/issues)

### "I want to use pytest-jux programmatically"

1. [Custom Signing Workflows Tutorial](tutorials/custom-signing-workflows.md) - Learn patterns
2. [API Index](reference/api/index.md) - Look up specific APIs
3. [Architecture Explanation](explanation/architecture.md) - Understand design

### "I need to understand security"

1. [Security Explanation](explanation/security.md) - Why sign reports, threat model
2. [Threat Model](security/THREAT_MODEL.md) - Detailed threat analysis
3. [Cryptographic Standards](security/CRYPTO_STANDARDS.md) - Algorithms and compliance
4. [Secure Key Storage](howto/secure-key-storage.md) - Operational security

---

## Documentation Updates

**Documentation Version**: v0.4.1 (Sprint 4 Complete)
**Last Updated**: 2026-01-08

**Recent Additions**:
- ✅ Complete API reference (7 modules, auto-generated + enhanced)
- ✅ Complete CLI reference (6 commands, auto-generated)
- ✅ 3 complete tutorials (beginner, intermediate, advanced)
- ✅ 10 comprehensive how-to guides
- ✅ 3 explanation documents (architecture, security, performance)
- ✅ Configuration and error code references

**Staying Updated**:
- Check [CHANGELOG.md](../CHANGELOG.md) for documentation changes
- Follow [GitHub Releases](https://github.com/jux-tools/pytest-jux/releases) for updates

---

## Still Can't Find What You Need?

1. **Check the [Complete Documentation Index](INDEX.md)** - Full map of all docs
2. **Search the documentation** - Use strategies above
3. **Check [GitHub Issues](https://github.com/jux-tools/pytest-jux/issues)** - See if others asked
4. **Review [ADRs](adr/README.md)** - Understand design decisions
5. **Read [Security Documentation](security/SECURITY.md)** - Security-related questions

**Still stuck?**
- Open a [GitHub Issue](https://github.com/jux-tools/pytest-jux/issues/new)
- Start a [GitHub Discussion](https://github.com/jux-tools/pytest-jux/discussions)
- Check the [Contributing Guide](../CONTRIBUTING.md) for community guidelines

---

**Happy Navigating!** 🧭

---

*This navigation guide is maintained as part of Sprint 5: Documentation & User Experience. For documentation issues or suggestions, please open a GitHub issue.*
