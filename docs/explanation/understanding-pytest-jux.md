# Understanding pytest-jux

_Why XML signatures matter for test reports_

**Audience:** Infrastructure Engineers, Integrators, Developers, System Administrators

## What is pytest-jux?

pytest-jux is a pytest plugin that adds cryptographic signatures to JUnit XML test reports, creating a verifiable chain-of-trust for your test results.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   pytest    │ --> │  pytest-jux  │ --> │   Signed    │
│  Test Run   │     │   Sign +     │     │   Report    │
│             │     │   Store      │     │   (Trusted) │
└─────────────┘     └──────────────┘     └─────────────┘
```

## The Problem: Test Report Trust

### Scenario 1: CI/CD Pipeline Compromise

Imagine your CI/CD pipeline produces test results:
```
✓ All 500 tests passed
✓ Code coverage: 95%
✓ Ready to deploy
```

**Question:** How do you know these results are real?

**Risks:**
- Pipeline could be compromised
- Test results could be modified after execution
- Malicious actor could fake passing tests
- No way to prove test results are authentic

### Scenario 2: Distributed Testing

You run tests across multiple environments:
- Developer laptops
- CI/CD servers
- Staging environments
- Production smoke tests

**Question:** How do you verify which environment produced which results?

**Risks:**
- Results could be misattributed
- No audit trail for test execution
- Can't prove test ran in correct environment
- Difficult to detect duplicate or replayed results

### Scenario 3: Compliance and Auditing

Your organization requires:
- Audit trails for all test executions
- Proof of test integrity
- Traceability from code to deployment

**Question:** How do you prove your test results haven't been tampered with?

**Risks:**
- No cryptographic proof of integrity
- Can't detect modifications after the fact
- Difficult to maintain compliance
- Manual auditing is error-prone

## The Solution: Cryptographic Signatures

pytest-jux solves these problems by:

### 1. Signing Test Reports

Every test report gets a cryptographic signature:

```xml
<testsuites>
  <testsuite name="tests" ...>
    <!-- Your test results -->
  </testsuite>

  <!-- Digital signature -->
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="">
        <DigestValue>abc123...</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>xyz789...</SignatureValue>
  </Signature>
</testsuites>
```

**What this means:**
- **Tampering is detectable**: Any modification breaks the signature
- **Authenticity is provable**: Only the private key holder can create valid signatures
- **Integrity is guaranteed**: You can verify the report hasn't changed

### 2. Capturing Environment Metadata

Every report includes context:

```json
{
  "hostname": "ci-runner-03",
  "username": "jenkins",
  "platform": "Linux-5.15.0-x86_64",
  "python_version": "3.11.4",
  "pytest_version": "8.0.0",
  "timestamp": "2025-10-17T14:30:00Z",
  "env": {
    "CI": "true",
    "BUILD_ID": "12345"
  }
}
```

**What this provides:**
- **Traceability**: Know exactly where and when tests ran
- **Environment verification**: Ensure tests ran in correct environment
- **Audit trail**: Complete history of test executions
- **Debugging context**: Reproduce issues with environment details

### 3. Local Storage and Caching

Reports are stored locally with queue support:

```
~/.local/share/jux/reports/
├── sha256:abc123.../
│   ├── report.xml           # Signed test report
│   └── metadata.json        # Environment context
└── queue/                   # Offline queue for API publishing
    └── sha256:def456.../
```

**What this enables:**
- **Offline operation**: No API server required
- **Network resilience**: Queue reports when API unavailable
- **Local inspection**: Verify reports without server access
- **Cache management**: Control storage and retention

## How pytest-jux Works

### Integration with pytest

pytest-jux hooks into pytest's session lifecycle:

```python
# 1. pytest runs your tests
pytest.main(['tests/'])

# 2. pytest generates JUnit XML report
# report.xml created

# 3. pytest-jux session hook fires
def pytest_sessionfinish(session, exitstatus):
    # 4. Load the JUnit XML report
    report = load_xml(session.config.option.xmlpath)

    # 5. Canonicalize (normalize) the XML
    canonical_xml = canonicalize_xml(report)

    # 6. Compute canonical hash (for duplicate detection)
    canonical_hash = sha256(canonical_xml)

    # 7. Sign the report with private key
    signed_report = sign_xml(report, private_key)

    # 8. Capture environment metadata
    metadata = capture_metadata()

    # 9. Store locally and/or publish to API
    storage.store_report(signed_report, canonical_hash, metadata)
```

### Key Components

**1. Canonicalization (C14N)**
- Normalizes XML to a standard form
- Ensures same content always produces same hash
- Eliminates whitespace and formatting differences
- Enables duplicate detection

**2. Digital Signatures (XMLDSig)**
- Industry-standard XML signature format
- Supports RSA and ECDSA algorithms
- Enveloped signatures (inside the XML document)
- Compatible with standard verification tools

**3. Storage Modes**
- **LOCAL**: Store reports locally only (no server)
- **API**: Publish to Jux API server only (no local storage)
- **BOTH**: Store locally AND publish to API
- **CACHE**: Store locally, publish when API available (offline queue)

## When to Use pytest-jux

### ✅ Good Use Cases

**High-Trust Environments**
- Financial services testing
- Healthcare compliance testing
- Security-critical applications
- Regulated industries

**Distributed Testing**
- Multiple CI/CD pipelines
- Developer and production testing
- Cross-environment verification
- Centralized test result aggregation

**Audit Requirements**
- Compliance auditing
- Test result provenance
- Long-term test history
- Regulatory reporting

**CI/CD Security**
- Prevent test result tampering
- Verify test authenticity
- Detect compromised pipelines
- Maintain chain-of-trust from code to deploy

### ❌ Not Ideal For

**Simple Projects**
- Small personal projects
- No compliance requirements
- Single developer
- Low security needs

**Rapid Prototyping**
- Experimental code
- Throwaway tests
- No long-term test history needed

**Performance-Critical Testing**
- Microsecond-level performance tests
- Signing adds small overhead (~100ms)
- May not be worth it for trivial test suites

## Chain-of-Trust Concept

pytest-jux creates an **unbroken chain of trust**:

```
┌─────────────┐
│ Private Key │  (Kept secure, never shared)
└──────┬──────┘
       │
       v
┌─────────────┐
│  Test Run   │  (pytest executes tests)
└──────┬──────┘
       │
       v
┌─────────────┐
│ Sign Report │  (pytest-jux signs with private key)
└──────┬──────┘
       │
       v
┌─────────────┐
│   Storage   │  (Report stored with metadata)
└──────┬──────┘
       │
       v
┌─────────────┐
│   Verify    │  (Anyone with public key/certificate)
└─────────────┘
```

**Trust Properties:**

1. **Authenticity**: Only holder of private key can create valid signatures
2. **Integrity**: Any tampering invalidates the signature
3. **Non-repudiation**: Signer cannot deny signing (private key is proof)
4. **Traceability**: Metadata ties report to specific execution context

## Security Model

### What pytest-jux Protects Against

✅ **Report Modification**
- Changing test results after execution
- Adding/removing test cases
- Modifying timestamps or metadata

✅ **Report Forgery**
- Creating fake test reports
- Impersonating test runs
- Replaying old test reports

✅ **Attribution Attacks**
- Misattributing test results to wrong environment
- Claiming tests ran when they didn't
- False compliance claims

### What pytest-jux Does NOT Protect Against

❌ **Compromised Test Code**
- If tests are modified before execution
- Use code signing and version control

❌ **Compromised Private Keys**
- If private key is stolen, attacker can sign reports
- Protect keys with proper access controls

❌ **Test Environment Compromise**
- If entire test environment is compromised
- Use infrastructure security best practices

❌ **Time-of-Check vs Time-of-Use**
- Report is valid at signing time only
- Code could change after tests run

## Integration with Jux API Server

pytest-jux is the **client component** in a larger system:

```
┌──────────────────┐         ┌──────────────────┐
│   pytest-jux     │         │  Jux API Server  │
│   (Client)       │         │  (Server)        │
│                  │         │                  │
│  • Sign reports  │  HTTP   │  • Store reports │
│  • Store local   │ ─────>  │  • Verify sigs   │
│  • Publish       │  POST   │  • Deduplicate   │
│  • Cache queue   │         │  • Query API     │
│                  │         │  • Web UI        │
└──────────────────┘         └──────────────────┘
```

**Client Responsibilities (pytest-jux):**
- Test report signing
- Environment metadata capture
- Local storage and caching
- API publishing (when available)

**Server Responsibilities (Jux API Server):**
- Report storage (PostgreSQL/SQLite)
- Signature verification
- Duplicate detection (canonical hash)
- Query and aggregation
- Web UI for visualization

**Note:** pytest-jux works standalone without the server. You can use local storage mode for complete offline operation.

## Performance Impact

Typical overhead for signing a test report:

| Operation            | Time     |
|---------------------|----------|
| Load XML report     | ~5ms     |
| Canonicalize XML    | ~10ms    |
| Compute hash        | ~2ms     |
| Sign report (RSA)   | ~50ms    |
| Sign report (ECDSA) | ~20ms    |
| Store locally       | ~10ms    |
| **Total**           | **~100ms** |

**Relative to test execution:**
- 100ms is negligible for most test suites
- Tests typically take seconds to minutes
- <1% overhead for test runs >10 seconds

## Comparison with Other Approaches

### vs. Simple File Hashing

**File Hashing (e.g., SHA-256 of report.xml):**
```bash
sha256sum report.xml > report.xml.sha256
```

**Limitations:**
- ❌ No authenticity (anyone can compute hash)
- ❌ No non-repudiation (can't prove who created it)
- ❌ Hash must be stored separately (can be swapped)

**pytest-jux:**
- ✅ Signature proves authenticity
- ✅ Non-repudiation (private key holder is accountable)
- ✅ Signature embedded in report (can't be separated)

### vs. External Logging

**External Logging (e.g., send results to logging service):**
```python
logging.info(f"Tests passed: {results}")
```

**Limitations:**
- ❌ Logs can be modified or deleted
- ❌ No cryptographic proof
- ❌ Difficult to verify integrity

**pytest-jux:**
- ✅ Cryptographic proof of integrity
- ✅ Self-contained reports (don't depend on external service)
- ✅ Verifiable offline

### vs. Manual Verification

**Manual Verification (human review):**
```
1. Developer looks at test output
2. Developer approves deployment
```

**Limitations:**
- ❌ Human error
- ❌ Not scalable
- ❌ No audit trail
- ❌ Can't detect subtle modifications

**pytest-jux:**
- ✅ Automated verification
- ✅ Scales to thousands of reports
- ✅ Complete audit trail
- ✅ Detects any modification (even single byte)

## Next Steps

Now that you understand pytest-jux, explore:

- **[Quick Start](../tutorials/quick-start.md)** - Get up and running in 10 minutes
- **[Choosing Storage Modes](../howto/choosing-storage-modes.md)** - Select the right mode for your needs
- **[Setting Up Signing Keys](../tutorials/setting-up-signing-keys.md)** - Production key management
- **[CI/CD Deployment](../howto/ci-cd-deployment.md)** - Integrate with your pipeline

## Further Reading

**Cryptography Concepts:**
- [XML Digital Signatures (XMLDSig)](https://www.w3.org/TR/xmldsig-core/)
- [Canonical XML (C14N)](https://www.w3.org/TR/xml-c14n)
- [Public Key Infrastructure (PKI)](https://en.wikipedia.org/wiki/Public_key_infrastructure)

**Security Documentation:**
- [Security Policy](../security/SECURITY.md)
- [Threat Model](../security/THREAT_MODEL.md)
- [Cryptographic Standards](../security/CRYPTO_STANDARDS.md)

**Architecture:**
- [Architecture Decision Records](../adr/)
- [C4 Architecture Models](../architecture/)
