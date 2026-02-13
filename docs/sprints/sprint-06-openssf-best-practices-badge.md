# Sprint 6: OpenSSF Best Practices Badge (Passing Level)

**Sprint Duration**: 2-3 weeks
**Sprint Goal**: Achieve OpenSSF Best Practices Badge (Passing Level) and establish SBOM generation
**Status**: 🚧 In Progress (Week 2)

## Sprint Progress

**Started**: 2025-10-20
**Current Phase**: Week 2 - Security & Badge Application

### Completed (2025-10-20)

**Week 1: Coverage & SBOM Infrastructure** ✅
- US-6.1: Test Coverage Visibility (Already complete - 89.70% coverage, Codecov integrated)
- US-6.2: Vulnerability Disclosure Process (SECURITY.md updated, GitHub Security Advisories enabled)
- US-6.3: SBOM Generation (CycloneDX SBOM in build-release workflow, documentation added)
- Additional: Enhanced dependency scanning (pip-audit --strict, Trivy exit-code enforcement, SBOM validation job)

**Week 2: Security & Badge Application** 🚧
- Badge readiness assessment completed (100% criteria met)
- Comprehensive badge application guide created
- Evidence documentation prepared

### In Progress

- US-6.4: OpenSSF Best Practices Badge Application
  - ⏸️ Pending: Register project on bestpractices.dev
  - ⏸️ Pending: Complete badge questionnaire
  - ⏸️ Pending: Obtain Passing badge
  - ⏸️ Pending: Add badge to README

### Remaining

- Display badge on README and documentation
- Document badge maintenance process
- Sprint retrospective

## Overview

Sprint 6 focuses on obtaining the OpenSSF Best Practices Badge at the Passing level, demonstrating that pytest-jux follows industry-standard security and quality practices. This sprint also adds SBOM generation to improve supply chain transparency and prepare for future EU CRA requirements.

**Why OpenSSF Badge for pytest-jux:**
- Reinforces security positioning (XMLDSig signatures, SLSA L2)
- Trust signal for security-conscious users
- Gap analysis identifies security weaknesses
- Competitive advantage (few pytest plugins have it)
- Correlates with OpenSSF Scorecard improvements
- Demonstrates EU CRA due diligence preparation

**OpenSSF Badge Benefits:**
- Free, voluntary certification program
- Public badge demonstrates security maturity
- Automated verification of many criteria
- Industry-recognized standard
- Three progressive levels (Passing → Silver → Gold)

## Prerequisites

**Completed Sprints:**
- ✅ Sprint 5: SLSA Build Level 2 Compliance (foundation for security practices)
- ✅ Sprint 3: Configuration, Storage & Caching
- ✅ Sprint 2: CLI Tools
- ✅ Sprint 1: Core Infrastructure

**Required Infrastructure:**
- GitHub repository with CI/CD
- SLSA L2 provenance generation
- Automated test suite (pytest)
- Static analysis tools (ruff, mypy)

## User Stories

### US-6.1: Test Coverage Visibility
**As a** project contributor
**I want** automated test coverage reporting and visibility
**So that** I can identify untested code and maintain quality standards

**Acceptance Criteria**:
- [ ] pytest-cov generates coverage reports (statement + branch)
- [ ] Coverage reports uploaded to Codecov (primary) or Coveralls (fallback)
- [ ] Coverage badge displayed on README
- [ ] Coverage ≥85% statement coverage overall
- [ ] Coverage ≥90% for cryptographic modules (signer, verifier, canonicalizer)
- [ ] Coverage ≥70% branch coverage overall
- [ ] Coverage metrics visible in pull requests (diff coverage)
- [ ] Coverage trends tracked over time (Codecov dashboard)
- [ ] HTML reports generated for local analysis

**Technical Tasks**:
- [ ] Configure pytest-cov in pyproject.toml with thresholds
- [ ] Enable branch coverage tracking (`branch = true`)
- [ ] Configure coverage exclusions (TYPE_CHECKING, pragma: no cover)
- [ ] Create Codecov account and obtain token
- [ ] Add CODECOV_TOKEN to GitHub Secrets
- [ ] Create codecov.yml configuration (project/patch targets)
- [ ] Add coverage upload to .github/workflows/test.yml
- [ ] Configure PR comment behavior (diff, flags, files)
- [ ] Add coverage badge to README.md
- [ ] Add htmlcov/ to .gitignore
- [ ] Document coverage standards in ADR-0007
- [ ] Test coverage locally: pytest --cov=pytest_jux
- [ ] Verify coverage ≥85% (write tests if gaps identified)

**Definition of Done**:
- Coverage reports generated on every CI run (main, develop, PRs)
- Coverage visible on Codecov with trends
- Badge shows ≥85% (green status)
- PR comments show coverage changes (+/- diff)
- CI fails if coverage drops >5%
- HTML reports browsable locally
- All modules meet thresholds (85% overall, 90% crypto)
- ADR-0007 documents coverage standards

---

### US-6.2: Vulnerability Disclosure Process
**As a** security researcher
**I want** a clear process for reporting vulnerabilities privately
**So that** I can responsibly disclose security issues

**Acceptance Criteria**:
- [ ] SECURITY.md documents vulnerability reporting process
- [ ] Private reporting mechanism documented
- [ ] Response time commitment stated (≤60 days)
- [ ] Security policy includes severity levels
- [ ] Contact method provided (email or GitHub Security Advisories)
- [ ] PGP key provided for encrypted reports (optional)

**Technical Tasks**:
- [ ] Update docs/security/SECURITY.md with reporting process
- [ ] Enable GitHub Security Advisories
- [ ] Document severity levels (Critical, High, Medium, Low)
- [ ] Add security contact email
- [ ] Link SECURITY.md from README.md
- [ ] Test private reporting workflow

**Definition of Done**:
- SECURITY.md accessible from repository root
- GitHub Security Advisories enabled
- Clear instructions for private reporting
- Response commitment documented

---

### US-6.3: SBOM Generation
**As a** security-conscious consumer
**I want** a Software Bill of Materials (SBOM) for each release
**So that** I can audit dependencies and comply with supply chain requirements

**Acceptance Criteria**:
- [ ] SBOM generated in CycloneDX or SPDX format
- [ ] SBOM includes all direct and transitive dependencies
- [ ] SBOM uploaded to GitHub Releases
- [ ] SBOM generation automated in CI/CD
- [ ] SBOM verification documented
- [ ] SBOM covers production and development dependencies

**Technical Tasks**:
- [ ] Add cyclonedx-bom or syft to build dependencies
- [ ] Add SBOM generation step to build-release.yml
- [ ] Configure SBOM format (CycloneDX JSON recommended)
- [ ] Upload SBOM as release artifact
- [ ] Document SBOM usage in SLSA_VERIFICATION.md
- [ ] Test SBOM validation tools

**Definition of Done**:
- SBOM generated for every release
- SBOM accessible on GitHub Releases
- SBOM includes complete dependency tree
- Documentation explains SBOM usage

---

### US-6.4: OpenSSF Best Practices Badge Application
**As a** project maintainer
**I want** OpenSSF Best Practices Badge (Passing level)
**So that** pytest-jux demonstrates security maturity to users

**Acceptance Criteria**:
- [ ] Project registered on bestpractices.dev
- [ ] All MUST criteria met (100%)
- [ ] All SHOULD criteria met or justified
- [ ] All SUGGESTED criteria evaluated
- [ ] Badge earned and displayed on README
- [ ] Badge status tracked and maintained

**Technical Tasks**:
- [ ] Register project at https://www.bestpractices.dev/
- [ ] Complete badge questionnaire
- [ ] Address any identified gaps
- [ ] Submit for automated verification
- [ ] Obtain Passing badge
- [ ] Add badge to README.md
- [ ] Document badge maintenance process

**Definition of Done**:
- Passing badge earned
- Badge displayed on README
- All criteria met or documented
- Maintenance process established

---

## Sprint Timeline (2-3 Weeks)

### Week 1: Coverage & SBOM Infrastructure

**Goal**: Establish test coverage reporting and SBOM generation

**Day 1-2: Coverage Configuration**
- [ ] Configure pytest-cov in pyproject.toml (statement + branch)
- [ ] Add coverage exclusions (TYPE_CHECKING, pragmas)
- [ ] Create codecov.yml with project/patch targets
- [ ] Add htmlcov/ to .gitignore
- [ ] Test coverage locally: `pytest --cov=pytest_jux`
- [ ] Document coverage standards in ADR-0007

**Day 3: Codecov Integration**
- [ ] Create Codecov account (login with GitHub)
- [ ] Obtain CODECOV_TOKEN
- [ ] Add CODECOV_TOKEN to GitHub Secrets
- [ ] Update .github/workflows/test.yml with coverage upload
- [ ] Push test commit to verify upload works
- [ ] Verify Codecov dashboard populates

**Day 4: Coverage Analysis**
- [ ] Review coverage report (identify gaps)
- [ ] Verify overall coverage ≥85%
- [ ] Verify crypto modules ≥90% (signer, verifier, canonicalizer)
- [ ] Write additional tests if needed (target gaps)
- [ ] Add coverage badge to README.md

**Day 5: SBOM Infrastructure**
- [ ] Add cyclonedx-bom to build dependencies
- [ ] Update .github/workflows/build-release.yml with SBOM generation
- [ ] Test SBOM generation locally
- [ ] Verify SBOM validates (cyclonedx-cli or online validator)
- [ ] Document SBOM usage in SLSA_VERIFICATION.md

**Deliverables**:
- ADR-0007: Test Coverage Visibility Standards
- Coverage reports on Codecov
- Coverage badge on README (≥85%, green)
- SBOM generation pipeline
- codecov.yml configuration

**Success Criteria**:
- Coverage ≥85% statement overall
- Coverage ≥90% for crypto modules
- Coverage ≥70% branch overall
- Codecov dashboard shows trends
- PR comments enabled
- SBOM validates successfully

---

### Week 2: Security & Badge Application

**Goal**: Complete vulnerability process and apply for badge

**Tasks**:
- [ ] Update SECURITY.md with reporting process
- [ ] Enable GitHub Security Advisories
- [ ] Document severity levels and response times
- [ ] Register project on bestpractices.dev
- [ ] Complete badge questionnaire (all categories)
- [ ] Review automated criteria validation
- [ ] Address any identified gaps

**Deliverables**:
- Updated SECURITY.md
- Badge application submitted
- Gap analysis completed

**Success Criteria**:
- Clear vulnerability reporting process
- Badge application 80%+ complete
- No critical gaps identified

---

### Week 3: Badge Completion & Documentation

**Goal**: Obtain Passing badge and finalize documentation

**Tasks**:
- [ ] Complete remaining badge criteria
- [ ] Submit badge for final review
- [ ] Obtain Passing badge
- [ ] Add badge to README.md
- [ ] Update documentation with SBOM usage
- [ ] Document badge maintenance process
- [ ] Sprint retrospective

**Deliverables**:
- OpenSSF Passing badge earned
- Complete documentation
- Sprint retrospective notes

**Success Criteria**:
- Badge displayed on README
- All documentation updated
- No outstanding gaps

---

## Technical Architecture

### Test Coverage Infrastructure

```yaml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov=pytest_jux",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=85",
]

[tool.coverage.run]
source = ["pytest_jux"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

```yaml
# .github/workflows/test.yml (add coverage upload)
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    file: ./coverage.xml
    flags: unittests
    name: pytest-jux-coverage
    fail_ci_if_error: true
```

### SBOM Generation

```yaml
# .github/workflows/build-release.yml (add to build job)
- name: Install SBOM generator
  run: |
    uv pip install cyclonedx-bom

- name: Generate SBOM
  run: |
    cyclonedx-py \
      --format json \
      --output dist/pytest-jux-${{ steps.version.outputs.version }}-sbom.json \
      --pyproject pyproject.toml

- name: Validate SBOM
  run: |
    # Install cyclonedx-cli for validation
    npm install -g @cyclonedx/cyclonedx-cli
    cyclonedx validate \
      --input-file dist/pytest-jux-${{ steps.version.outputs.version }}-sbom.json \
      --input-format json \
      --fail-on-errors

- name: Upload SBOM artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: dist/*-sbom.json
```

```yaml
# Add SBOM to GitHub Release (in create-release job)
files: |
  dist/*.whl
  dist/*.tar.gz
  dist/*.intoto.jsonl
  dist/*-sbom.json
  dist/checksums.txt
```

### Vulnerability Disclosure Process

```markdown
# docs/security/SECURITY.md

## Reporting a Vulnerability

**We take security seriously.** If you discover a security vulnerability in pytest-jux, please report it privately.

### Reporting Process

**Preferred Method: GitHub Security Advisories**
1. Go to https://github.com/jux-tools/pytest-jux/security/advisories
2. Click "Report a vulnerability"
3. Fill in the advisory form with details

**Alternative Method: Email**
- Email: security@example.com (replace with actual email)
- Subject: "[SECURITY] pytest-jux vulnerability report"
- Include: Description, reproduction steps, impact assessment

### What to Include

- **Description**: Clear explanation of the vulnerability
- **Affected Versions**: Which versions are vulnerable
- **Reproduction**: Steps to reproduce the issue
- **Impact**: Potential security impact (severity assessment)
- **Suggested Fix**: If you have one (optional)

### Severity Levels

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Remote code execution, credential theft | Arbitrary code execution via malicious XML |
| **High** | Privilege escalation, data exposure | Private key leakage in logs |
| **Medium** | Information disclosure, DoS | Signature bypass under specific conditions |
| **Low** | Minor issues with limited impact | Verbose error messages revealing versions |

### Response Timeline

- **Initial Response**: Within 3 business days
- **Severity Assessment**: Within 7 days
- **Fix Timeline**:
  - Critical/High: Within 30 days
  - Medium: Within 60 days
  - Low: Next scheduled release

### What Happens Next

1. **Acknowledgment**: We confirm receipt of your report
2. **Validation**: We reproduce and validate the vulnerability
3. **Fix Development**: We develop and test a fix
4. **Coordinated Disclosure**: We coordinate public disclosure with you
5. **CVE Assignment**: We request CVE if applicable
6. **Release**: We release patched version
7. **Credit**: We credit you in release notes (if desired)

### Security Advisories

Published security advisories: https://github.com/jux-tools/pytest-jux/security/advisories

### Out of Scope

The following are **not** considered security vulnerabilities:
- Issues in unsupported versions (see CHANGELOG.md for support policy)
- Issues requiring physical access to the machine
- Social engineering attacks
- Vulnerabilities in dependencies (report to upstream)

### Bug Bounty

We currently do not offer a bug bounty program, but we greatly appreciate responsible disclosure and will credit researchers in our security advisories.

## Security Best Practices for Users

### Key Management
- **Never commit private keys** to version control
- Store keys in secure locations (e.g., ~/.ssh/, KMS)
- Use strong passphrases for key encryption
- Rotate keys periodically

### Configuration
- Review configuration files for sensitive data
- Use environment variables for secrets
- Enable audit logging in production

### Updates
- Subscribe to security advisories
- Update pytest-jux promptly when fixes are released
- Review CHANGELOG.md for security-related updates

## Security Features

pytest-jux implements the following security features:

- ✅ **XMLDSig Signatures**: Cryptographically signed test reports
- ✅ **SLSA Build Level 2**: Verifiable build provenance
- ✅ **Secure RNG**: Uses cryptographically secure random number generation
- ✅ **No Credential Storage**: No hardcoded passwords or keys
- ✅ **HTTPS**: All downloads via HTTPS (PyPI)
- ✅ **Static Analysis**: mypy strict mode, ruff linting
- ✅ **Dependency Scanning**: Automated dependency updates

## Related Documentation

- [Threat Model](THREAT_MODEL.md)
- [SLSA Verification Guide](SLSA_VERIFICATION.md)
- [ADR-0005: Python Ecosystem Security Framework](../adr/0005-adopt-python-ecosystem-security-framework.md)
- [ADR-0006: SLSA Build Level 2 Compliance](../adr/0006-adopt-slsa-build-level-2-compliance.md)

---

**Last Updated**: 2025-10-19
**Security Contact**: security@example.com (replace with actual)
```

### OpenSSF Badge Criteria Mapping

**Already Meeting (Estimated 80% of Passing Criteria):**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **basics_oss** | ✅ Met | MIT license in pyproject.toml |
| **repo_public** | ✅ Met | https://github.com/jux-tools/pytest-jux |
| **repo_track** | ✅ Met | Git with GitHub |
| **version_unique** | ✅ Met | Semantic versioning in pyproject.toml |
| **version_semver** | ✅ Met | 0.1.x format |
| **changelog** | ✅ Met | CHANGELOG.md (Keep a Changelog format) |
| **test** | ✅ Met | pytest test suite |
| **test_invocation** | ✅ Met | `pytest` command documented |
| **test_most** | ✅ Met | Comprehensive test coverage |
| **test_continuous_integration** | ✅ Met | GitHub Actions |
| **static_analysis** | ✅ Met | ruff, mypy |
| **static_analysis_fixed** | ✅ Met | Pre-commit hooks enforce |
| **crypto_random** | ✅ Met | Uses secrets module, cryptography library |
| **delivery_mitm** | ✅ Met | HTTPS via PyPI |
| **no_leaked_credentials** | ✅ Met | No hardcoded secrets |
| **build_reproducible** | ✅ Met | SLSA L2 reproducible builds |
| **provenance_available** | ✅ Met | SLSA provenance on GitHub Releases |

**Gaps to Address (Estimated 20%):**

| Criterion | Status | Action Required |
|-----------|--------|-----------------|
| **vulnerability_report_process** | ⚠️ Gap | Update SECURITY.md (Week 2) |
| **vulnerability_report_private** | ⚠️ Gap | Enable GitHub Security Advisories (Week 2) |
| **vulnerability_report_response** | ⚠️ Gap | Document 60-day response SLA (Week 2) |
| **test_statement_coverage80** | ⚠️ Gap | Measure coverage, ensure ≥85% (Week 1) |
| **release_notes** | ⚠️ Gap | Link CHANGELOG.md from releases (Week 3) |
| **release_notes_vulns** | ⚠️ Gap | Document security fixes in CHANGELOG (Week 2) |

---

## Dependencies

### External Services
- **Codecov or Coveralls**: Test coverage hosting (free for open source)
- **bestpractices.dev**: Badge registration and tracking
- **GitHub Security Advisories**: Private vulnerability reporting
- **npm** (optional): For cyclonedx-cli SBOM validation

### Tools and Libraries
- **pytest-cov**: Coverage measurement (already in dev dependencies)
- **cyclonedx-bom**: SBOM generation (Python)
- **cyclonedx-cli**: SBOM validation (Node.js, optional)
- **codecov-action**: GitHub Actions integration

### Documentation References
- [OpenSSF Best Practices Badge](https://www.bestpractices.dev/)
- [CycloneDX SBOM Specification](https://cyclonedx.org/)
- [SPDX SBOM Specification](https://spdx.dev/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)

---

## Risk Assessment

### Medium Risk
**Badge Criteria Interpretation**
- **Risk**: Misunderstanding badge requirements
- **Impact**: Delays in badge completion
- **Mitigation**: Review criteria carefully, ask for clarification if needed, review other projects' badges

**Coverage Thresholds**
- **Risk**: Some modules may fall below 85% coverage
- **Impact**: Need additional tests to meet threshold
- **Mitigation**: Identify gaps early, write targeted tests, allow exceptions for edge cases

### Low Risk
**SBOM Generation Failures**
- **Risk**: SBOM tools may fail on complex dependencies
- **Impact**: Cannot generate complete SBOM
- **Mitigation**: Test with multiple tools (cyclonedx-bom, syft), manual fallback if needed

**Badge Maintenance Overhead**
- **Risk**: Badge requires periodic re-verification
- **Impact**: Additional maintenance burden
- **Mitigation**: Automate checks where possible, schedule quarterly reviews

---

## Success Metrics

### Technical Metrics
- [ ] Test coverage ≥85% overall
- [ ] Test coverage ≥90% for crypto modules
- [ ] SBOM generated for 100% of releases
- [ ] SBOM validates successfully (CycloneDX/SPDX)
- [ ] 100% of MUST criteria met
- [ ] 100% of SHOULD criteria met or justified

### Quality Metrics
- [ ] OpenSSF Passing badge earned
- [ ] Badge displayed on README
- [ ] Coverage badge displayed on README
- [ ] SECURITY.md complete and accessible
- [ ] GitHub Security Advisories enabled
- [ ] Documentation updated

### Security Metrics
- [ ] Vulnerability reporting process documented
- [ ] Response time commitment stated (≤60 days)
- [ ] SBOM includes all dependencies
- [ ] No credentials in codebase (verified)
- [ ] Static analysis passing (ruff, mypy)

### Community Metrics
- [ ] Badge publicly visible on README
- [ ] Trust signal for security-conscious users
- [ ] Competitive positioning improved
- [ ] OpenSSF Scorecard improvement (if applicable)

---

## Definition of Done

Sprint 6 is complete when:

### Coverage Infrastructure
- [ ] pytest-cov configured with thresholds
- [ ] Coverage reports uploaded to Codecov/Coveralls
- [ ] Coverage ≥85% overall, ≥90% crypto
- [ ] Coverage badge on README
- [ ] Coverage visible on pull requests

### SBOM Generation
- [ ] cyclonedx-bom integrated in build workflow
- [ ] SBOM generated for every release
- [ ] SBOM uploaded to GitHub Releases
- [ ] SBOM validates successfully
- [ ] SBOM documentation complete

### Security Process
- [ ] SECURITY.md updated with reporting process
- [ ] GitHub Security Advisories enabled
- [ ] Severity levels documented
- [ ] Response timeline committed (≤60 days)
- [ ] Contact method provided

### OpenSSF Badge
- [ ] Project registered on bestpractices.dev
- [ ] All MUST criteria met (100%)
- [ ] All SHOULD criteria met or justified
- [ ] Passing badge earned
- [ ] Badge displayed on README
- [ ] Maintenance process documented

### Documentation
- [ ] SBOM usage documented in SLSA_VERIFICATION.md
- [ ] Coverage process documented
- [ ] Badge criteria tracked
- [ ] Sprint retrospective complete

### Quality Gates
- [ ] All tests pass (100%)
- [ ] Coverage thresholds met
- [ ] Static analysis passing
- [ ] No regressions introduced
- [ ] Backward compatibility maintained

---

## Post-Sprint Activities

### Monitoring
- Monitor badge status (quarterly re-verification)
- Monitor coverage trends (should stay ≥85%)
- Monitor SBOM generation success rate
- Monitor vulnerability reports (response within SLA)

### Future Enhancements (Sprint 7+)
- **Silver Badge**: 2FA enforcement, signed commits, 80%+ coverage
- **Gold Badge**: 90%+ branch coverage, external security review
- **Enhanced SBOM**: Include license compliance scanning
- **Dependency Scanning**: Automated vulnerability detection (Dependabot)
- **Fuzzing**: Add fuzzing for crypto code (hypothesis property tests)

### Documentation Improvements
- SBOM consumer guide
- Badge maintenance playbook
- Security incident response plan
- Vulnerability disclosure examples

---

## Related Documentation

- **Sprint 5**: SLSA Build Level 2 Compliance (foundation)
- **ADR-0006**: Adopt SLSA Build Level 2 Compliance
- **ADR-0005**: Adopt Python Ecosystem Security Framework
- **ADR-0002**: Adopt Development Best Practices
- **docs/security/SECURITY.md**: Security policy (to be updated)
- **docs/security/SLSA_VERIFICATION.md**: SLSA verification guide

---

## Notes

**Sprint Sequencing**: Sprint 6 builds on Sprint 5 (SLSA L2). The badge application leverages existing security infrastructure (SLSA provenance, static analysis, testing).

**Silver/Gold Badges**: This sprint targets Passing level only. Silver and Gold require additional infrastructure (2FA enforcement, signed commits, higher coverage) and are deferred to future sprints.

**SBOM Standards**: We'll use CycloneDX (JSON format) as primary SBOM format due to better Python tooling. SPDX is an alternative if CycloneDX fails.

**EU CRA Preparation**: SBOM generation prepares for EU Cyber Resilience Act requirements (December 2027), even though pytest-jux may qualify for open source exemptions.

**Maintenance Commitment**: Badge requires periodic re-verification (typically quarterly). We'll document this in the maintenance playbook.

---

**Sprint Start Date**: 2025-10-20
**Sprint Owner**: jrjsmrtn
**Last Updated**: 2025-10-20
