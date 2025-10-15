# Sprint 1: Core Plugin Infrastructure

**Sprint Duration**: 2025-10-15 → TBD
**Sprint Goal**: Implement basic pytest hook integration, XML canonicalization, and digital signatures
**Status**: 🚀 In Progress

## Overview

Sprint 1 establishes the foundation of pytest-jux by implementing the core functionality:
- XML canonicalization (C14N) for consistent XML processing
- XMLDSig digital signature generation
- pytest plugin hook integration

This sprint focuses on the **core technical capabilities** without API integration, establishing a solid foundation for future sprints.

## User Stories

### US-1.1: XML Canonicalization
**As a** system administrator
**I want** JUnit XML reports to be canonicalized
**So that** duplicate reports can be detected via content hashing

**Acceptance Criteria**:
- [ ] Canonical form (C14N) correctly applied to JUnit XML
- [ ] SHA-256 hash generated from canonical XML
- [ ] Handles XML with namespaces, comments, and whitespace variations
- [ ] 100% test coverage for canonicalizer module

**Technical Tasks**:
- [ ] Create `pytest_jux/canonicalizer.py`
- [ ] Implement C14N using lxml
- [ ] Add hash generation function
- [ ] Write comprehensive tests including edge cases
- [ ] Property-based tests for canonicalization invariants

---

### US-1.2: XML Digital Signatures
**As a** system administrator
**I want** JUnit XML reports to be digitally signed
**So that** report integrity and authenticity can be verified

**Acceptance Criteria**:
- [ ] XMLDSig enveloped signature correctly added to XML
- [ ] Supports RSA-SHA256 and ECDSA-SHA256 algorithms
- [ ] Key loading from PEM files
- [ ] Signature validates correctly with signxml
- [ ] 100% test coverage for signer module

**Technical Tasks**:
- [ ] Create `pytest_jux/signer.py`
- [ ] Implement XMLDSig signing using signxml
- [ ] Support RSA and ECDSA key types
- [ ] Add key loading utilities
- [ ] Write comprehensive tests for signature generation
- [ ] Test signature verification

---

### US-1.3: pytest Plugin Hook Integration
**As a** developer
**I want** pytest-jux to automatically process JUnit XML reports
**So that** signing happens transparently after test execution

**Acceptance Criteria**:
- [ ] Plugin registers with pytest correctly
- [ ] `pytest_sessionfinish` hook processes JUnit XML
- [ ] Command-line options: `--jux-publish`, `--jux-key`
- [ ] Configuration via pytest.ini supported
- [ ] Graceful error handling for missing files/keys
- [ ] >85% test coverage for plugin module

**Technical Tasks**:
- [ ] Create `pytest_jux/plugin.py`
- [ ] Implement pytest hooks (pytest_addoption, pytest_sessionfinish)
- [ ] Add command-line options
- [ ] Integrate canonicalizer and signer
- [ ] Write plugin integration tests
- [ ] Test configuration loading

---

## Technical Architecture

### Module Dependencies

```
pytest (7.4+/8.x)
    ↓
pytest_jux/plugin.py (pytest hooks)
    ↓
    ├─→ pytest_jux/canonicalizer.py (C14N + hashing)
    │       ↓
    │       └─→ lxml (XML processing)
    │
    └─→ pytest_jux/signer.py (XMLDSig)
            ↓
            ├─→ signxml (signature generation)
            ├─→ cryptography (key management)
            └─→ lxml (XML manipulation)
```

### Implementation Order (TDD)

Following TDD principles, implement in this order:

1. **Canonicalizer First** (foundational)
   - Write tests: `tests/test_canonicalizer.py`
   - Implement: `pytest_jux/canonicalizer.py`
   - Validate: 100% coverage

2. **Signer Second** (depends on canonicalizer for testing)
   - Write tests: `tests/test_signer.py`
   - Implement: `pytest_jux/signer.py`
   - Validate: 100% coverage

3. **Plugin Last** (integrates both)
   - Write tests: `tests/test_plugin.py`
   - Implement: `pytest_jux/plugin.py`
   - Validate: >85% coverage

---

## Test Fixtures

### JUnit XML Samples

Create test fixtures in `tests/fixtures/junit_xml/`:

1. **simple.xml**: Minimal JUnit XML with 1 test
2. **passing.xml**: Multiple passing tests
3. **failing.xml**: Tests with failures
4. **errors.xml**: Tests with errors
5. **skipped.xml**: Tests with skips
6. **namespaced.xml**: XML with namespaces
7. **large.xml**: Large report (100+ tests)

### Cryptographic Keys

Create test keys in `tests/fixtures/keys/`:

1. **rsa_2048.pem**: RSA 2048-bit private key
2. **rsa_2048.pub**: Corresponding public key
3. **ecdsa_p256.pem**: ECDSA P-256 private key
4. **ecdsa_p256.pub**: Corresponding public key

**Security Note**: Test keys only, never commit real keys!

---

## Definition of Done

Sprint 1 is complete when:

- [ ] All user stories meet acceptance criteria
- [ ] All tests pass (`pytest`)
- [ ] Code coverage >85% overall (100% for crypto modules)
- [ ] Type checking passes (`mypy pytest_jux`)
- [ ] Linting clean (`ruff check .`)
- [ ] Formatting clean (`ruff format --check .`)
- [ ] Security scans clean (`make security-scan`)
- [ ] Documentation updated (docstrings, type hints)
- [ ] Manual smoke test: sign a real JUnit XML file
- [ ] Changes committed to `develop` branch

---

## Risks & Mitigations

### Risk 1: XML Canonicalization Edge Cases
**Impact**: Medium
**Probability**: Medium
**Mitigation**: Property-based testing with hypothesis, comprehensive fixture coverage

### Risk 2: Signature Verification Complexity
**Impact**: High
**Probability**: Low
**Mitigation**: Use signxml library (well-tested), validate against known-good signatures

### Risk 3: pytest Hook Integration Issues
**Impact**: Medium
**Probability**: Medium
**Mitigation**: Study pytest plugin examples, test with multiple pytest versions (7.4, 8.x)

---

## Success Metrics

- **Code Coverage**: >85% (100% for canonicalizer and signer)
- **Type Safety**: 0 mypy errors in strict mode
- **Security**: 0 findings from Bandit/Safety
- **Performance**: Signing 1000 reports in <10 seconds
- **Test Execution**: Full test suite in <5 seconds

---

## Sprint Backlog

### Week 1: Foundation

**Day 1-2: Canonicalizer**
- [ ] Create test fixtures (JUnit XML samples)
- [ ] Write `tests/test_canonicalizer.py`
- [ ] Implement `pytest_jux/canonicalizer.py`
- [ ] Achieve 100% coverage

**Day 3-4: Signer**
- [ ] Create test fixtures (cryptographic keys)
- [ ] Write `tests/test_signer.py`
- [ ] Implement `pytest_jux/signer.py`
- [ ] Achieve 100% coverage

**Day 5-7: Plugin**
- [ ] Write `tests/test_plugin.py`
- [ ] Implement `pytest_jux/plugin.py`
- [ ] Integration testing
- [ ] Achieve >85% coverage

### Week 2: Polish & Documentation

**Day 8-9: Quality & Security**
- [ ] Run all quality checks
- [ ] Security scanning and fixes
- [ ] Performance testing
- [ ] Edge case testing

**Day 10: Documentation & Release**
- [ ] Update docstrings
- [ ] Write usage examples
- [ ] Update CHANGELOG.md
- [ ] Sprint review
- [ ] Merge to `develop`

---

## Out of Scope (Future Sprints)

The following are explicitly **NOT** in Sprint 1:

- ❌ REST API client (`api_client.py`)
- ❌ SQLAlchemy models (`models.py`)
- ❌ Database integration
- ❌ Publishing to Jux REST API
- ❌ CLI commands (`cli.py`)
- ❌ Configuration file support (beyond pytest.ini)
- ❌ Key generation utilities
- ❌ Signature verification utilities

These will be addressed in Sprint 2 and beyond.

---

## Notes

- **TDD Approach**: Write tests first, then implement
- **Security Focus**: All cryptographic code requires 100% coverage
- **Type Hints**: Use strict type checking for all functions
- **Documentation**: Every public function needs docstrings

---

**Sprint Lead**: AI-Assisted Development
**Reviewed By**: Georges Martin
**Last Updated**: 2025-10-15
