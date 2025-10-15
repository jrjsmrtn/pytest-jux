# Sprint 2: CLI Tools

**Sprint Duration**: 2025-10-15 → TBD
**Sprint Goal**: Implement standalone CLI tools for key management, signing, verification, and report inspection
**Status**: 🚀 In Progress

## Overview

Sprint 2 adds standalone command-line tools to pytest-jux, enabling:
- Cryptographic key pair generation (RSA, ECDSA)
- Offline JUnit XML signing workflow
- Signature verification utilities
- Report inspection and metadata extraction

This sprint provides **standalone utilities** independent of pytest execution, useful for CI/CD pipelines, offline workflows, and testing.

## User Stories

### US-2.1: Key Generation
**As a** system administrator
**I want** to generate cryptographic key pairs from the command line
**So that** I can create signing keys without external tools

**Acceptance Criteria**:
- [ ] Generate RSA key pairs (2048-bit, 3072-bit, 4096-bit)
- [ ] Generate ECDSA key pairs (P-256, P-384, P-521)
- [ ] Output keys in PEM format
- [ ] Optional X.509 certificate generation (self-signed)
- [ ] Secure file permissions (0600 for private keys)
- [ ] >85% test coverage for key generation module

**Technical Tasks**:
- [ ] Add `jux-keygen` CLI command
- [ ] Implement RSA key generation
- [ ] Implement ECDSA key generation
- [ ] Add X.509 certificate generation
- [ ] Write comprehensive tests
- [ ] Add security warnings for self-signed certificates

**CLI Interface**:
```bash
# Generate RSA 2048-bit key pair
jux-keygen --type rsa --bits 2048 --output ~/.jux/signing_key.pem

# Generate ECDSA P-256 key pair with certificate
jux-keygen --type ecdsa --curve P-256 --cert --output ~/.jux/ecdsa_key.pem
```

---

### US-2.2: Offline XML Signing
**As a** CI/CD engineer
**I want** to sign JUnit XML files without running pytest
**So that** I can sign reports from other test frameworks

**Acceptance Criteria**:
- [ ] Sign any JUnit XML file from command line
- [ ] Support RSA and ECDSA private keys
- [ ] Optional X.509 certificate embedding
- [ ] Preserve original XML formatting
- [ ] Write signed XML to file or stdout
- [ ] >85% test coverage for signing command

**Technical Tasks**:
- [ ] Add `jux-sign` CLI command
- [ ] Integrate with existing `signer.py` module
- [ ] Add input/output file handling
- [ ] Support stdin/stdout for pipelines
- [ ] Write comprehensive tests
- [ ] Add error handling for invalid XML

**CLI Interface**:
```bash
# Sign XML file
jux-sign --input report.xml --output signed-report.xml \
  --key ~/.jux/signing_key.pem --cert ~/.jux/cert.pem

# Sign from stdin to stdout
cat report.xml | jux-sign --key ~/.jux/signing_key.pem > signed-report.xml
```

---

### US-2.3: Signature Verification
**As a** quality assurance engineer
**I want** to verify XML signatures from the command line
**So that** I can validate report integrity

**Acceptance Criteria**:
- [ ] Verify XMLDSig signatures in JUnit XML
- [ ] Support public key and X.509 certificate verification
- [ ] Display verification status (valid/invalid)
- [ ] Show signer information (certificate details)
- [ ] Exit code: 0 = valid, 1 = invalid
- [ ] >85% test coverage for verification command

**Technical Tasks**:
- [ ] Add `jux-verify` CLI command
- [ ] Implement signature verification using signxml
- [ ] Add certificate chain validation
- [ ] Display verification details
- [ ] Write comprehensive tests
- [ ] Test with invalid/tampered signatures

**CLI Interface**:
```bash
# Verify signature with public key
jux-verify --input signed-report.xml --key ~/.jux/signing_key.pub

# Verify signature with certificate
jux-verify --input signed-report.xml --cert ~/.jux/cert.pem

# Verify with certificate chain
jux-verify --input signed-report.xml --ca-bundle /etc/ssl/certs/ca-bundle.crt
```

---

### US-2.4: Report Inspection
**As a** developer
**I want** to inspect JUnit XML reports from the command line
**So that** I can extract metadata without parsing XML

**Acceptance Criteria**:
- [ ] Display report summary (tests, failures, errors, skipped)
- [ ] Show canonical hash (SHA-256)
- [ ] Display signature information (algorithm, timestamp)
- [ ] Extract test case details
- [ ] JSON output for scripting
- [ ] >85% test coverage for inspection command

**Technical Tasks**:
- [ ] Add `jux-inspect` CLI command
- [ ] Integrate with `canonicalizer.py` for hashing
- [ ] Parse signature metadata
- [ ] Implement JSON output format
- [ ] Write comprehensive tests
- [ ] Add colorized terminal output (rich library)

**CLI Interface**:
```bash
# Inspect report (human-readable)
jux-inspect report.xml

# Inspect report (JSON output)
jux-inspect --json report.xml | jq '.summary.tests'

# Show only signature details
jux-inspect --signature-only signed-report.xml
```

---

## Technical Architecture

### Module Structure

```
pytest_jux/
├── cli.py                  # Main CLI entry point (click group)
├── commands/
│   ├── __init__.py
│   ├── keygen.py          # Key generation command
│   ├── sign.py            # Signing command
│   ├── verify.py          # Verification command
│   └── inspect.py         # Inspection command
├── signer.py              # (existing) Signing utilities
├── canonicalizer.py       # (existing) C14N and hashing
└── verifier.py            # (new) Signature verification
```

### CLI Framework

Using **configargparse** for CLI and configuration management:
- Drop-in replacement for argparse with config file support
- Environment variable support
- Config file support (INI, YAML, JSON)
- Rich library for colorized output
- JSON output for scripting
- stdin/stdout support for pipelines

### Implementation Order (TDD)

Following TDD principles, implement in this order:

1. **CLI Framework** (foundational)
   - Write tests: `tests/test_cli.py`
   - Implement: `pytest_jux/cli.py`
   - ConfigArgParse setup with config file support

2. **Key Generation** (independent)
   - Write tests: `tests/commands/test_keygen.py`
   - Implement: `pytest_jux/commands/keygen.py`
   - Validate: >85% coverage

3. **Offline Signing** (uses existing signer)
   - Write tests: `tests/commands/test_sign.py`
   - Implement: `pytest_jux/commands/sign.py`
   - Validate: >85% coverage

4. **Verification** (new verifier module)
   - Write tests: `tests/test_verifier.py`, `tests/commands/test_verify.py`
   - Implement: `pytest_jux/verifier.py`, `pytest_jux/commands/verify.py`
   - Validate: >85% coverage

5. **Inspection** (uses canonicalizer)
   - Write tests: `tests/commands/test_inspect.py`
   - Implement: `pytest_jux/commands/inspect.py`
   - Validate: >85% coverage

---

## CLI Entry Points

Update `pyproject.toml` to add console scripts:

```toml
[project.scripts]
jux-keygen = "pytest_jux.commands.keygen:main"
jux-sign = "pytest_jux.commands.sign:main"
jux-verify = "pytest_jux.commands.verify:main"
jux-inspect = "pytest_jux.commands.inspect:main"
```

Each command is a standalone script that uses configargparse for:
- Command-line argument parsing
- Config file support (~/.jux/config, /etc/jux/config)
- Environment variable support (JUX_KEY_PATH, JUX_CERT_PATH, etc.)

Example config file (`~/.jux/config`):
```ini
[jux]
key_path = ~/.jux/signing_key.pem
cert_path = ~/.jux/signing_key.crt
```

---

## Test Fixtures

### Additional Fixtures Needed

Create test fixtures in `tests/fixtures/`:

1. **Signed XML samples** (`junit_xml/signed/`):
   - `rsa_signed.xml`: XML signed with RSA key
   - `ecdsa_signed.xml`: XML signed with ECDSA key
   - `invalid_signature.xml`: Tampered signature
   - `expired_cert.xml`: Signature with expired certificate

2. **Public keys** (`keys/`):
   - `rsa_2048.pub`: RSA public key (corresponding to existing private key)
   - `ecdsa_p256.pub`: ECDSA public key (corresponding to existing private key)

3. **X.509 certificates** (`keys/`):
   - `ca_cert.pem`: CA certificate for chain validation
   - `intermediate_cert.pem`: Intermediate certificate
   - `expired_cert.pem`: Expired certificate for testing

---

## Definition of Done

Sprint 2 is complete when:

- [ ] All user stories meet acceptance criteria
- [ ] All tests pass (`pytest`)
- [ ] Code coverage >85% for all CLI modules
- [ ] Type checking passes (`mypy pytest_jux`)
- [ ] Linting clean (`ruff check .`)
- [ ] Formatting clean (`ruff format --check .`)
- [ ] Security scans clean (`make security-scan`)
- [ ] Documentation updated (docstrings, type hints)
- [ ] CLI help text comprehensive and clear
- [ ] Manual smoke tests: all CLI commands work end-to-end
- [ ] Changes committed to `develop` branch

---

## Risks & Mitigations

### Risk 1: X.509 Certificate Validation Complexity
**Impact**: High
**Probability**: Medium
**Mitigation**: Use cryptography library's certificate validation, test with known certificates

### Risk 2: CLI UX Inconsistency
**Impact**: Medium
**Probability**: Low
**Mitigation**: Follow argparse/configargparse best practices, get user feedback early

### Risk 3: File Permission Security
**Impact**: High (private keys)
**Probability**: Low
**Mitigation**: Enforce 0600 permissions, warn on insecure permissions

---

## Success Metrics

- **Code Coverage**: >85% for all CLI modules
- **Type Safety**: 0 mypy errors in strict mode
- **Security**: 0 findings from Bandit/Safety
- **Performance**: Key generation <1 second, signing <100ms
- **Usability**: CLI help text clear, error messages actionable

---

## Sprint Backlog

### Week 1: Foundation & Key Generation

**Day 1-2: CLI Framework**
- [ ] Create `pytest_jux/cli.py`
- [ ] Set up click command group
- [ ] Add console script entry points
- [ ] Write framework tests
- [ ] Test CLI invocation

**Day 3-4: Key Generation**
- [ ] Create `pytest_jux/commands/keygen.py`
- [ ] Implement RSA key generation
- [ ] Implement ECDSA key generation
- [ ] Add X.509 certificate generation
- [ ] Write comprehensive tests
- [ ] Achieve >85% coverage

**Day 5: Offline Signing**
- [ ] Create `pytest_jux/commands/sign.py`
- [ ] Integrate with existing `signer.py`
- [ ] Add stdin/stdout support
- [ ] Write comprehensive tests
- [ ] Achieve >85% coverage

### Week 2: Verification & Inspection

**Day 6-7: Signature Verification**
- [ ] Create `pytest_jux/verifier.py`
- [ ] Implement signature verification
- [ ] Create `pytest_jux/commands/verify.py`
- [ ] Add certificate chain validation
- [ ] Write comprehensive tests
- [ ] Achieve >85% coverage

**Day 8-9: Report Inspection**
- [ ] Create `pytest_jux/commands/inspect.py`
- [ ] Implement report parsing
- [ ] Add JSON output format
- [ ] Add colorized output (rich)
- [ ] Write comprehensive tests
- [ ] Achieve >85% coverage

**Day 10: Polish & Documentation**
- [ ] Update CLI help text
- [ ] Write usage examples
- [ ] Update CHANGELOG.md
- [ ] Sprint review
- [ ] Merge to `develop`

---

## Out of Scope (Future Sprints)

The following are explicitly **NOT** in Sprint 2:

- ❌ REST API client (`api_client.py`)
- ❌ SQLAlchemy models (`models.py`)
- ❌ Database integration
- ❌ Publishing to Jux REST API
- ❌ Key rotation utilities
- ❌ Certificate Authority (CA) setup
- ❌ Hardware security module (HSM) integration
- ❌ Batch processing of multiple reports

These will be addressed in Sprint 3 and beyond.

---

## CLI Examples

### Complete Workflow Example

```bash
# 1. Generate signing key
jux keygen --type rsa --bits 2048 --cert \
  --output ~/.jux/signing_key.pem

# 2. Sign a JUnit XML report
jux sign --input report.xml --output signed-report.xml \
  --key ~/.jux/signing_key.pem \
  --cert ~/.jux/signing_key.crt

# 3. Verify signature
jux verify --input signed-report.xml \
  --cert ~/.jux/signing_key.crt
# Output: ✓ Signature valid

# 4. Inspect report
jux inspect signed-report.xml
# Output:
#   Tests: 42
#   Failures: 2
#   Errors: 0
#   Skipped: 1
#   Duration: 12.34s
#   Canonical Hash: sha256:abc123...
#   Signature: RSA-SHA256 (valid)
```

---

## Notes

- **TDD Approach**: Write tests first, then implement
- **Security Focus**: File permissions, key storage warnings
- **Type Hints**: Use strict type checking for all functions
- **Documentation**: Every CLI command needs comprehensive help text
- **Rich Output**: Use rich library for colored, formatted terminal output

---

**Sprint Lead**: AI-Assisted Development
**Reviewed By**: Georges Martin
**Last Updated**: 2025-10-15
