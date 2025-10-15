# Threat Model: pytest-jux

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Next Review**: 2026-01-15  
**Methodology**: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)

## Executive Summary

pytest-jux is a pytest plugin that signs JUnit XML test reports with XML digital signatures and publishes them to a Jux REST API. This creates multiple threat surfaces:

1. **Cryptographic Operations**: Signature generation and verification
2. **Network Communication**: REST API interaction with Jux backend
3. **File System Access**: Reading JUnit XML reports and private keys
4. **Supply Chain**: Plugin distribution and dependency integrity
5. **CI/CD Integration**: Execution in automated test pipelines

This document identifies threats using the STRIDE model and documents mitigations.

## System Overview

### Components

```
┌─────────────────────────────────────────────────────┐
│                  CI/CD Pipeline                      │
│  ┌──────────────────────────────────────────────┐  │
│  │              pytest Test Suite                │  │
│  │                                               │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │        pytest-jux Plugin             │  │  │
│  │  │                                       │  │  │
│  │  │  1. Read JUnit XML                   │  │  │
│  │  │  2. Canonicalize (C14N)              │  │  │
│  │  │  3. Calculate hash                   │  │  │
│  │  │  4. Sign with private key            │  │  │
│  │  │  5. POST to Jux API                  │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
              ┌──────────────────────┐
              │     Jux REST API     │
              │                      │
              │  1. Verify signature │
              │  2. Check duplicate  │
              │  3. Store report     │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  PostgreSQL/SQLite   │
              └──────────────────────┘
```

### Trust Boundaries

1. **Filesystem Boundary**: Reading JUnit XML and private keys from disk
2. **Process Boundary**: pytest-jux running within pytest process
3. **Network Boundary**: HTTPS communication with Jux API
4. **Storage Boundary**: Database storage of signed reports

### Assets

1. **Private Signing Keys**: RSA/ECDSA private keys for signature generation
2. **JUnit XML Reports**: Test results (may contain sensitive system information)
3. **Signed Reports**: Authenticated test results with chain-of-trust
4. **API Credentials**: Authentication tokens for Jux API
5. **Test Infrastructure**: CI/CD pipeline integrity

## STRIDE Threat Analysis

### S - Spoofing Identity

#### Threat S-1: Fake Report Submission
**Description**: Attacker submits unsigned or fake-signed reports to Jux API pretending to be legitimate test runner.

**Attack Scenarios**:
- Submit reports without valid signature
- Reuse signatures from legitimate reports on modified content
- Generate reports with stolen/compromised private key

**Impact**: High - Pollutes test report database with fake results, undermines trust chain

**Mitigations**:
- ✅ XMLDSig signature verification on Jux API (ADR-0003)
- ✅ Canonical hash validation prevents signature reuse
- ⚠️ Key rotation policy required (user responsibility)
- ⚠️ Certificate-based key authorization (future enhancement)

**Residual Risk**: Medium - Depends on user key management practices

---

#### Threat S-2: Man-in-the-Middle API Impersonation
**Description**: Attacker intercepts network traffic and impersonates Jux API endpoint.

**Attack Scenarios**:
- DNS spoofing to redirect to malicious server
- Certificate authority compromise
- Downgrade attack (HTTPS → HTTP)

**Impact**: Medium - Legitimate reports sent to attacker's server, information disclosure

**Mitigations**:
- ✅ HTTPS required for API communication (user configuration)
- ✅ TLS certificate validation enabled by default (requests library)
- ⚠️ Certificate pinning not implemented (future enhancement)
- 📋 User guidance to use HTTPS in docs/security/SECURITY.md

**Residual Risk**: Low - Standard HTTPS protection with user responsibility

---

### T - Tampering

#### Threat T-1: XML Report Modification
**Description**: Attacker modifies JUnit XML report before or after signing.

**Attack Scenarios**:
- Modify XML file after pytest writes it, before plugin signs it
- Strip signature from signed report
- Modify signed XML without updating signature (signature wrapping)

**Impact**: High - Falsified test results appear legitimate

**Mitigations**:
- ✅ File system permissions protect pytest output directory
- ✅ Canonical hash detects any modification
- ✅ Signature verification on Jux API detects tampering
- 🔒 Signature wrapping attack tests required (Sprint 1)
- 🔒 Atomic file operations for report writing (implementation detail)

**Residual Risk**: Low - Multiple layers of protection

---

#### Threat T-2: Signature Stripping Attack
**Description**: Attacker removes signature from signed report and resubmits.

**Attack Scenarios**:
- Remove <Signature> element from signed XML
- Submit original unsigned report

**Impact**: Medium - Unsigned reports could be accepted if validation skipped

**Mitigations**:
- ✅ Jux API requires valid signature (reject unsigned)
- 🔒 Signature presence validation required (implementation)
- 📋 Document signature stripping tests in test suite

**Residual Risk**: Low - API-side validation prevents acceptance

---

#### Threat T-3: Dependency Tampering
**Description**: Attacker compromises pytest-jux dependencies to inject malicious code.

**Attack Scenarios**:
- Typosquatting attack (fake package names)
- Compromised PyPI account of dependency maintainer
- Malicious update pushed to legitimate package

**Impact**: Critical - Complete compromise of signing infrastructure

**Mitigations**:
- ✅ Dependency pinning with hashes (pip-tools --require-hashes)
- ✅ Automated vulnerability scanning (pip-audit, safety)
- ✅ Dependabot for security updates
- ✅ Supply chain security via Trusted Publishers (post-1.0)
- 📋 Regular security audits of dependencies

**Residual Risk**: Low - Multiple supply chain protections

---

### R - Repudiation

#### Threat R-1: Unsigned Report Submission
**Description**: Test reports submitted without signature, sender claims they were signed.

**Attack Scenarios**:
- Skip signature step in plugin
- Disable --jux-publish flag after generating unsigned report
- Manual API submission without signature

**Impact**: Medium - No proof of report authenticity

**Mitigations**:
- ✅ Jux API rejects unsigned reports
- ✅ Plugin always signs when enabled (no bypass)
- 📋 Audit logging on Jux API side (verified/rejected reports)
- 📋 Environment metadata captured in report (hostname, user)

**Residual Risk**: Low - API enforcement prevents unsigned acceptance

---

#### Threat R-2: Lost Signature Chain
**Description**: Signed reports exist but signature verification keys are lost.

**Attack Scenarios**:
- Public key not stored/backed up
- Key rotation without preserving old keys
- Certificate expiration without renewal

**Impact**: Medium - Cannot verify authenticity of historical reports

**Mitigations**:
- ⚠️ Key management documentation required
- 📋 Public key storage recommendations in SECURITY.md
- 📋 Key backup and rotation policy guidance
- 🔮 Future: Certificate-based PKI with key escrow

**Residual Risk**: Medium - Depends on user key management practices

---

### I - Information Disclosure

#### Threat I-1: Private Key Exposure in Logs
**Description**: Private key material written to logs or error messages.

**Attack Scenarios**:
- Exception handler logs private key contents
- Debug logging includes key material
- Error messages display key file contents

**Impact**: Critical - Private key compromise enables signature forgery

**Mitigations**:
- ✅ Private keys never logged (secure coding standard)
- 🔒 Code review required for all key handling (100% coverage)
- 🔒 Automated testing for key exposure in logs
- 📋 Redaction of sensitive data in error messages

**Residual Risk**: Very Low - Multiple preventive controls

---

#### Threat I-2: Sensitive Information in Test Reports
**Description**: JUnit XML reports contain sensitive system information.

**Attack Scenarios**:
- Test names reveal internal system details
- Error messages include passwords or tokens
- Environment variables logged in test output

**Impact**: Medium - Information disclosure via signed reports

**Mitigations**:
- ⚠️ User responsibility to sanitize test output
- 📋 Documentation guidance on sensitive data handling
- 📋 Jux API access controls (separate concern)
- 📋 Consider metadata redaction options (future)

**Residual Risk**: Medium - Primarily user responsibility

---

#### Threat I-3: Network Traffic Interception
**Description**: HTTPS traffic decrypted via certificate compromise or TLS vulnerability.

**Attack Scenarios**:
- TLS downgrade attack
- Compromised certificate authority
- Corporate SSL interception proxy

**Impact**: Medium - Signed reports disclosed to attacker

**Mitigations**:
- ✅ HTTPS enforced (user configuration)
- ✅ Modern TLS via requests library
- ⚠️ Certificate pinning not implemented
- 📋 Guidance on corporate proxy considerations

**Residual Risk**: Low - Standard HTTPS protections

---

### D - Denial of Service

#### Threat D-1: XML Bomb Attack
**Description**: Malicious JUnit XML file causes resource exhaustion during parsing.

**Attack Scenarios**:
- Billion laughs attack (entity expansion)
- Quadratic blowup attack
- Deeply nested XML structures
- Extremely large XML files

**Impact**: High - Plugin crashes, CI/CD pipeline disrupted

**Mitigations**:
- ✅ lxml secure defaults (external entities disabled)
- 🔒 XML size limits required (MAX_XML_SIZE_BYTES)
- 🔒 Entity expansion limits
- 🔒 Parsing timeout enforcement
- 📋 Fuzzing tests for malformed XML

**Residual Risk**: Low - Multiple protective layers

---

#### Threat D-2: Cryptographic Resource Exhaustion
**Description**: Excessive signature operations consume CPU/memory.

**Attack Scenarios**:
- Sign extremely large XML files
- Rapid repeated signing attempts
- Algorithmic complexity attacks on C14N

**Impact**: Medium - Slow CI/CD pipeline, timeout failures

**Mitigations**:
- 🔒 XML size limits prevent oversized files
- ✅ Efficient C14N implementation (lxml)
- 📋 Performance testing for large reports
- 📋 Rate limiting guidance for CI/CD

**Residual Risk**: Low - Size limits provide primary defense

---

#### Threat D-3: API Flooding
**Description**: Plugin sends excessive requests to Jux API.

**Attack Scenarios**:
- Submit same report repeatedly
- Automated test suite generates thousands of reports
- Malicious use of plugin to DDoS Jux API

**Impact**: Medium - Jux API unavailable, impacts all users

**Mitigations**:
- ✅ Canonical hash prevents duplicate acceptance (API side)
- ⚠️ Rate limiting on API side (separate concern)
- 📋 Retry logic with exponential backoff
- 📋 Plugin usage guidance for high-volume scenarios

**Residual Risk**: Low - API-side protections primary defense

---

### E - Elevation of Privilege

#### Threat E-1: Signature Verification Bypass
**Description**: Attacker submits reports that pass signature verification without valid signature.

**Attack Scenarios**:
- Exploit bug in signxml library
- Signature verification logic error
- Algorithm confusion attack (switch from RSA to none)

**Impact**: Critical - Complete bypass of authentication mechanism

**Mitigations**:
- ✅ Use well-audited signxml library (ADR-0003)
- 🔒 100% test coverage for signature verification
- 🔒 Explicit algorithm enforcement (no "none" algorithm)
- 🔒 Security test suite for bypass attempts
- 📋 Regular security audits of crypto code

**Residual Risk**: Very Low - Defense in depth via library choice and testing

---

#### Threat E-2: Dependency Confusion Attack
**Description**: Attacker publishes malicious package with higher version number to internal/public PyPI.

**Attack Scenarios**:
- Internal package repository has pytest-jux, attacker publishes v999.0.0 to PyPI
- Typosquatting with similar name (pytest_jux vs pytest-jux)
- Namespace confusion (pytest-jux vs other-org/pytest-jux)

**Impact**: Critical - Malicious code execution in CI/CD pipeline

**Mitigations**:
- ✅ Exact version pinning in requirements
- ✅ Hash verification (--require-hashes)
- ✅ Trusted Publishers prevents account takeover (post-1.0)
- 📋 Use unique, distinctive package name
- 📋 Monitor for typosquatting attempts

**Residual Risk**: Very Low - Multiple supply chain protections

---

#### Threat E-3: Plugin Hook Exploitation
**Description**: Attacker exploits pytest plugin hooks to execute arbitrary code.

**Attack Scenarios**:
- Hook into pytest lifecycle earlier than pytest-jux
- Override plugin configuration or behavior
- Exploit pytest hook ordering vulnerabilities

**Impact**: High - Compromise test infrastructure

**Mitigations**:
- ✅ pytest-jux uses standard hook patterns
- ✅ Minimal hook surface area (only pytest_sessionfinish)
- ⚠️ Cannot prevent malicious plugins loaded alongside
- 📋 Document safe pytest configuration practices

**Residual Risk**: Medium - pytest security model limitations

---

## Risk Summary

| Threat ID | Threat | Severity | Likelihood | Risk | Status |
|-----------|--------|----------|------------|------|--------|
| S-1 | Fake Report Submission | High | Medium | Medium | Mitigated |
| S-2 | MITM API Impersonation | Medium | Low | Low | Mitigated |
| T-1 | XML Report Modification | High | Low | Low | Mitigated |
| T-2 | Signature Stripping | Medium | Low | Low | Mitigated |
| T-3 | Dependency Tampering | Critical | Low | Low | Mitigated |
| R-1 | Unsigned Report Submission | Medium | Medium | Low | Mitigated |
| R-2 | Lost Signature Chain | Medium | Medium | Medium | User Responsibility |
| I-1 | Private Key in Logs | Critical | Very Low | Very Low | Mitigated |
| I-2 | Sensitive Data in Reports | Medium | Medium | Medium | User Responsibility |
| I-3 | Network Interception | Medium | Low | Low | Mitigated |
| D-1 | XML Bomb Attack | High | Low | Low | In Progress |
| D-2 | Crypto Resource Exhaustion | Medium | Low | Low | In Progress |
| D-3 | API Flooding | Medium | Medium | Low | API-Side |
| E-1 | Signature Bypass | Critical | Very Low | Very Low | In Progress |
| E-2 | Dependency Confusion | Critical | Very Low | Very Low | Mitigated |
| E-3 | Plugin Hook Exploitation | High | Low | Medium | Documented |

**Legend**:
- **Severity**: Potential impact if exploited
- **Likelihood**: Probability of successful exploitation
- **Risk**: Combined severity and likelihood
- **Status**: Mitigated / In Progress / User Responsibility / API-Side / Documented

## Security Requirements

Based on threat analysis, pytest-jux must implement:

### Must Have (Critical)
1. ✅ XML signature generation and verification (signxml)
2. 🔒 XML size limits and bomb protection
3. 🔒 100% test coverage for cryptographic code
4. 🔒 No private key logging under any circumstance
5. ✅ Dependency pinning with cryptographic hashes

### Should Have (High Priority)
6. 🔒 Signature stripping and wrapping attack tests
7. 🔒 Constant-time signature comparison
8. 📋 Comprehensive security documentation
9. 🔒 Fuzzing test suite for XML parsing
10. 📋 Key management and rotation guidance

### Nice to Have (Future Enhancements)
11. 🔮 Certificate-based PKI instead of raw keys
12. 🔮 Hardware security module (HSM) support
13. 🔮 Certificate pinning for API communication
14. 🔮 Automated key rotation tooling
15. 🔮 Report content redaction options

**Legend**: ✅ Complete | 🔒 Sprint 1 | 📋 Documentation | 🔮 Future

## Testing Requirements

### Security Test Categories

1. **Signature Attack Tests** (`tests/security/test_signature_attacks.py`)
   - Signature stripping
   - Signature wrapping
   - Algorithm confusion
   - Key substitution

2. **XML Attack Tests** (`tests/security/test_xml_attacks.py`)
   - XML bomb (billion laughs)
   - XXE injection
   - XPath injection
   - Quadratic blowup

3. **Cryptographic Tests** (`tests/security/test_crypto.py`)
   - Constant-time operations
   - Key format validation
   - Algorithm enforcement
   - Secure random usage

4. **Fuzzing Tests** (`tests/security/test_fuzzing.py`)
   - Malformed XML inputs (Hypothesis)
   - Invalid signature formats
   - Boundary conditions
   - Resource limits

## Monitoring and Detection

### Security Events to Log

1. Signature verification failures
2. XML parsing errors (potential attacks)
3. Oversized XML rejection
4. API communication failures
5. Key file access errors

### Metrics to Track

1. Signature verification success rate
2. XML parsing performance
3. API response times
4. Error rate by category

## Incident Response

### Security Incident Procedure

1. **Detection**: Automated monitoring or user report
2. **Assessment**: Severity and impact analysis
3. **Containment**: Stop exposure, revoke compromised keys
4. **Investigation**: Root cause analysis
5. **Remediation**: Fix vulnerability, update dependencies
6. **Recovery**: Deploy fixed version, verify resolution
7. **Post-Incident**: Update threat model, improve defenses

### Contact Information

- **Security Contact**: jrjsmrtn+security@gmail.com
- **Response Time**: 48 hours acknowledgment
- **Disclosure**: 90-day coordinated disclosure

## Document Maintenance

**Review Schedule**: Quarterly (January, April, July, October)

**Triggers for Update**:
- New threats identified
- Security incidents
- Major feature additions
- Dependency changes
- Security audit findings

**Approval**: Georges Martin (Maintainer)

---

**Document Status**: Active  
**Classification**: Public  
**Version**: 1.0  
**Last Review**: 2025-10-15  
**Next Review**: 2026-01-15
