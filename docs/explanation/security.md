# Security Explanation

**Understanding pytest-jux security model and cryptographic design**

---

## Overview

This document explains the security architecture of pytest-jux, covering:
- Why digital signatures for test reports
- How cryptographic protection works
- What threats are mitigated
- Security best practices and limitations

For security vulnerability reporting, see [Security Policy](../security/SECURITY.md). For key management procedures, see [How-To Guides](../howto/secure-key-storage.md).

---

## Why Sign Test Reports?

### The Problem: Untrusted Test Results

**Scenario**: You receive a test report showing "All tests passed ✅"

**Questions**:
- Did these tests actually run?
- Were the results modified after testing?
- Can you prove the report is authentic?
- How do you detect duplicate submissions?

**Without signatures**: Trust is based on:
- ❌ File system permissions (easily bypassed)
- ❌ Human review (doesn't scale)
- ❌ Timestamps (can be forged)
- ❌ Honor system (vulnerable to mistakes and malice)

**With signatures**: Cryptographic proof provides:
- ✅ **Authenticity**: Report came from authorized source
- ✅ **Integrity**: Report wasn't modified after signing
- ✅ **Non-repudiation**: Can't deny having signed report
- ✅ **Duplicate detection**: Canonical hashing prevents re-submission

---

## Security Model

### Trust Boundaries

```
┌─────────────────────────────────────────────┐
│           Trusted Environment               │
│  ┌────────────────────────────────────────┐ │
│  │  pytest Test Execution                 │ │
│  │  - Test code                           │ │
│  │  - pytest runner                       │ │
│  │  - JUnit XML generation                │ │
│  └────────────────────────────────────────┘ │
│                    │                         │
│                    ▼                         │
│  ┌────────────────────────────────────────┐ │
│  │  pytest-jux Signing                    │ │
│  │  - Load private key (TRUSTED)          │ │
│  │  - Canonicalize XML                    │ │
│  │  - Compute canonical hash              │ │
│  │  - Apply XMLDSig signature             │ │
│  └────────────────────────────────────────┘ │
│                    │                         │
└────────────────────┼─────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │    Signed Report (portable)    │
    └────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│          Untrusted Environment               │
│  ┌────────────────────────────────────────┐ │
│  │  Report Distribution                   │ │
│  │  - File transfer                       │ │
│  │  - Network transmission                │ │
│  │  - Public storage                      │ │
│  └────────────────────────────────────────┘ │
│                    │                         │
│                    ▼                         │
│  ┌────────────────────────────────────────┐ │
│  │  pytest-jux Verification               │ │
│  │  - Load certificate (PUBLIC)           │ │
│  │  - Verify XMLDSig signature            │ │
│  │  - Check integrity                     │ │
│  │  - Validate authenticity               │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Security Zones

**Zone 1: Trusted (Signing Environment)**
- CI/CD servers with private keys
- Developer workstations (development keys)
- Secure build environments

**Zone 2: Transport (Potentially Hostile)**
- Network transmission
- File system storage
- Email, cloud storage, etc.

**Zone 3: Verification (Semi-Trusted)**
- QA teams verifying reports
- Stakeholders reviewing results
- Compliance auditors
- Public consumers (with certificate)

---

## Cryptographic Design

### Digital Signatures (XMLDSig)

**How It Works**:

1. **Signing**:
   ```
   Report (XML) → C14N → Hash → Encrypt with Private Key → Signature
   ```

2. **Verification**:
   ```
   Report + Signature → Decrypt with Public Key → Hash → Compare → Valid/Invalid
   ```

**Properties**:
- **Authenticity**: Only holder of private key can create valid signature
- **Integrity**: Any modification invalidates signature
- **Non-repudiation**: Signer can't deny signing (private key is secret)

### Supported Algorithms

**RSA-SHA256** (Default, widely compatible):
```
Algorithm: http://www.w3.org/2001/04/xmldsig-more#rsa-sha256
Key Size: 2048, 3072, 4096 bits
Security: 112-128 bits (equivalent to AES-128/256)
Performance: Slower signing, fast verification
```

**ECDSA-SHA256** (Modern, efficient):
```
Algorithm: http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256
Curves: P-256 (secp256r1), P-384, P-521
Security: 128-256 bits
Performance: Fast signing and verification, smaller keys
```

**Algorithm Comparison**:

| Algorithm | Key Size | Signature Size | Signing Speed | Verification Speed | Security Level |
|-----------|----------|----------------|---------------|-------------------|----------------|
| RSA-2048  | 2048 bits | 256 bytes     | Slow          | Fast             | 112 bits       |
| RSA-4096  | 4096 bits | 512 bytes     | Very Slow     | Fast             | 128 bits       |
| ECDSA-P256| 256 bits  | 64-72 bytes   | Fast          | Fast             | 128 bits       |
| ECDSA-P384| 384 bits  | 96-104 bytes  | Fast          | Fast             | 192 bits       |

**Recommendation**:
- **General use**: RSA-4096 (maximum compatibility)
- **Performance-critical**: ECDSA-P256 (smaller, faster)

### Canonical Hashing (C14N + SHA-256)

**Why Canonicalization?**

XML documents can represent the same information in different ways:

```xml
<!-- Semantically identical, different byte representations -->
<test name="example" status="passed"/>
<test status="passed" name="example"/>

<!-- With different whitespace -->
<test name="example" status="passed" />
<test  name="example"  status="passed"/>
```

**C14N (Canonical XML)** transforms XML to standard form:
- Attribute order normalized (alphabetical)
- Namespace prefixes standardized
- Whitespace normalized
- Comments removed
- Encoding standardized (UTF-8)

**Why SHA-256?**:
- ✅ 256-bit security (collision-resistant)
- ✅ Fast computation
- ✅ Industry standard
- ✅ No known practical attacks

**Duplicate Detection**:
```python
# Same content → Same canonical hash
report1 = '<test name="ex" status="passed"/>'
report2 = '<test status="passed" name="ex"/>'

hash1 = canonical_hash(report1)  # abc123...
hash2 = canonical_hash(report2)  # abc123... (identical!)
```

---

## Threat Model

### Threats Mitigated

#### ✅ **Threat 1: Report Tampering**

**Attack**: Attacker modifies test results after tests run

**Example**:
```xml
<!-- Original (2 failures) -->
<testsuite tests="10" failures="2" errors="0" skipped="0">
  ...
</testsuite>

<!-- Tampered (0 failures) -->
<testsuite tests="10" failures="0" errors="0" skipped="0">
  ...
</testsuite>
```

**Mitigation**: XMLDSig signature
- Any modification invalidates signature
- Verification fails immediately
- Tampering is detected

**Protection Level**: ✅ Strong

---

#### ✅ **Threat 2: Forged Reports**

**Attack**: Attacker creates fake test report claiming "all tests passed"

**Example**:
```xml
<!-- Fake report (never ran tests) -->
<testsuite tests="100" failures="0" errors="0">
  <!-- Fabricated test results -->
</testsuite>
```

**Mitigation**: Digital signature with private key
- Only authorized signers have private key
- Forged reports fail signature verification
- Private key storage is protected (file permissions, secrets managers)

**Protection Level**: ✅ Strong (if private key is secure)

---

#### ✅ **Threat 3: Replay Attacks**

**Attack**: Attacker resubmits old passing report instead of new failing report

**Example**:
```
Day 1: All tests pass → Signed report A (hash: abc123)
Day 2: Tests fail → Attacker submits report A again
```

**Mitigation**: Timestamp + canonical hash
- Each report has timestamp in metadata
- Canonical hash includes all content
- Duplicate hash detected by storage system
- API server (future) can enforce uniqueness

**Protection Level**: ✅ Strong (with API server enforcement)

---

#### ✅ **Threat 4: Man-in-the-Middle**

**Attack**: Attacker intercepts report during transmission and replaces it

**Mitigation**: Signature verification
- Replacement report won't have valid signature
- Verification fails
- Integrity protected end-to-end

**Protection Level**: ✅ Strong

---

### Threats Not Mitigated

#### ⚠️ **Threat 5: Compromised Private Key**

**Attack**: Attacker obtains private key and signs malicious reports

**Why Not Mitigated**:
- Private key compromise is outside threat model
- No cryptographic system protects against key theft

**Mitigation Strategy**:
- 🔒 Secure key storage (600 permissions, secrets managers, HSM)
- 🔒 Regular key rotation (90-180 days)
- 🔒 Access controls (least privilege)
- 🔒 Key usage monitoring (audit logs)
- 🔒 Incident response plan (immediate key rotation)

---

#### ⚠️ **Threat 6: System Compromise**

**Attack**: Attacker gains root/admin access to signing system

**Why Not Mitigated**:
- System-level access can bypass all application-level protections
- Can steal private key, modify code, forge reports

**Mitigation Strategy**:
- 🔒 System hardening (minimal attack surface)
- 🔒 Least privilege (don't run as root)
- 🔒 Network segmentation (isolate CI/CD)
- 🔒 Intrusion detection (monitor for suspicious activity)
- 🔒 Regular security audits

---

#### ⚠️ **Threat 7: Malicious Test Code**

**Attack**: Attacker modifies test code to always pass

**Why Not Mitigated**:
- pytest-jux signs whatever pytest produces
- Can't distinguish valid tests from malicious tests

**Mitigation Strategy**:
- 🔒 Code review (review test changes)
- 🔒 Branch protection (require approvals)
- 🔒 Test quality metrics (coverage, assertions)
- 🔒 Test code signing (future consideration)

---

## Security Best Practices

### Key Management

**DO**:
- ✅ Use 4096-bit RSA or P-256 ECDSA
- ✅ Generate keys with strong entropy (`/dev/urandom`, OS crypto APIs)
- ✅ Store private keys with 600 permissions (owner read/write only)
- ✅ Use separate keys per environment (dev, staging, prod)
- ✅ Rotate keys every 90-180 days (production)
- ✅ Back up keys securely (encrypted backups)
- ✅ Use secrets managers in CI/CD (GitHub Secrets, AWS Secrets Manager)

**DON'T**:
- ❌ Commit private keys to version control
- ❌ Share private keys via email/Slack
- ❌ Use same key across environments
- ❌ Store keys unencrypted on network shares
- ❌ Use weak keys (< 2048-bit RSA, non-standard curves)

### Certificate Management

**DO**:
- ✅ Use reasonable validity periods (1-2 years)
- ✅ Include descriptive subject names (CN=Organization CI/CD)
- ✅ Distribute public certificates freely
- ✅ Verify certificates during signature verification

**DON'T**:
- ❌ Use expired certificates
- ❌ Trust self-signed certificates in production (use PKI)
- ❌ Skip certificate verification

### Operational Security

**DO**:
- ✅ Enable audit logging (key access, signing operations)
- ✅ Monitor for anomalies (unusual signing patterns)
- ✅ Use ephemeral keys in CI/CD when possible
- ✅ Implement least privilege access
- ✅ Have incident response plan (key compromise)

**DON'T**:
- ❌ Run signing as root/administrator
- ❌ Expose private keys in logs or error messages
- ❌ Skip security updates (dependencies, OS)

---

## Security Limitations

### What pytest-jux **Does NOT** Protect

1. **Test Code Integrity**:
   - pytest-jux signs results, not test code
   - Malicious tests can produce malicious results
   - Mitigation: Code review, branch protection

2. **Test Environment**:
   - Assumes test environment is trustworthy
   - Compromised test environment → compromised results
   - Mitigation: Isolated build environments, system hardening

3. **Time-of-Check to Time-of-Use**:
   - Report valid at signing time, but environment may change
   - Doesn't prevent future system compromise
   - Mitigation: Regular re-verification, short validity periods

4. **Denial of Service**:
   - Doesn't prevent attacker from flooding with signed reports
   - Mitigation: Rate limiting (future API server feature)

---

## Compliance and Standards

### Standards Compliance

**Cryptographic Standards**:
- ✅ W3C XMLDSig 1.0 (https://www.w3.org/TR/xmldsig-core1/)
- ✅ XML C14N Exclusive (https://www.w3.org/TR/xml-exc-c14n/)
- ✅ NIST FIPS 186-4 (Digital Signature Standard)
- ✅ RFC 3447 (RSA PKCS#1 v2.1)
- ✅ RFC 6979 (Deterministic ECDSA)

**Security Frameworks**:
- ✅ OWASP Top 10 considerations
- ✅ CWE/SANS Top 25 awareness
- ✅ SLSA Build Level 2 compliance (future)

### Audit Requirements

**For Compliance Audits**, pytest-jux provides:
- ✅ Cryptographic proofs of test execution
- ✅ Tamper-evident reports
- ✅ Timestamp and environment metadata
- ✅ Traceable signing keys (X.509 certificates)
- ✅ Reproducible verification

---

## Security Roadmap

### Current (v0.1.x)

- ✅ XMLDSig signatures (RSA, ECDSA)
- ✅ Canonical hashing (C14N + SHA-256)
- ✅ Local storage with duplicate detection
- ✅ File-based key management

### Planned (v0.2.x)

- 📋 API server integration (centralized verification)
- 📋 Certificate chain validation
- 📋 CRL/OCSP certificate revocation checking
- 📋 Key rotation automation

### Future (v1.0+)

- 📋 Hardware Security Module (HSM) support
- 📋 PKCS#11 integration
- 📋 Timestamping Service Protocol (RFC 3161)
- 📋 Long-term signature validation (PAdES)

---

## See Also

- **[Architecture Explanation](architecture.md)**: System architecture
- **[Threat Model](../security/THREAT_MODEL.md)**: Detailed threat analysis
- **[Crypto Standards](../security/CRYPTO_STANDARDS.md)**: Cryptographic specifications
- **[Secure Key Storage](../howto/secure-key-storage.md)**: Key management procedures
- **[Security Policy](../security/SECURITY.md)**: Vulnerability reporting

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
