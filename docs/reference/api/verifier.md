# verifier API Reference

**Module**: `pytest_jux.verifier`
**Purpose**: XML digital signature verification and validation
**Version**: 0.1.9+

---

## Overview

The `verifier` module provides functionality to verify XMLDSig digital signatures on JUnit XML reports. It validates signatures, extracts signature metadata, and detects tampering.

### Purpose

- **Signature Verification**: Verify XMLDSig signatures are valid
- **Tamper Detection**: Detect if signed reports have been modified
- **Certificate Validation**: Validate X.509 certificate chains
- **Metadata Extraction**: Extract signature information for auditing

### When to Use This Module

- Verifying signed test reports received from external sources
- Validating report authenticity before processing
- Auditing signature metadata (algorithm, timestamp, signer)
- Detecting tampered or corrupted reports

### Related Modules

- **`signer`**: Creates XMLDSig signatures (verified by this module)
- **`canonicalizer`**: Used during signature verification (C14N)
- **`plugin`**: Uses verifier for signature validation (future)

---

## Module Documentation

```{eval-rst}
.. automodule:: pytest_jux.verifier
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

---

## Functions

### `verify_signature()`

Verify XMLDSig signature on signed XML document.

```{eval-rst}
.. autofunction:: pytest_jux.verifier.verify_signature
```

**Example**:
```python
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature

# Load signed report
signed_xml = load_xml("test-results/junit-signed.xml")

# Load public certificate
cert_path = Path("~/.ssh/jux/jux-signing-key.pub").expanduser()
cert = cert_path.read_bytes()

# Verify signature
try:
    is_valid = verify_signature(signed_xml, cert)
    if is_valid:
        print("✓ Signature is valid")
    else:
        print("✗ Signature is invalid")
except ValueError as e:
    print(f"Verification error: {e}")
```

---

## Verification Process

The verification process follows these steps:

1. **Locate Signature**: Find `<Signature>` element in XML
2. **Extract Public Key**: Load public key from certificate
3. **Canonicalize Signed Content**: Apply C14N to signed data
4. **Verify Signature**: Cryptographically verify signature value
5. **Validate Certificate** (if provided): Check certificate validity

### Supported Algorithms

- **RSA-SHA256**: RSA signatures with SHA-256 digest
- **ECDSA-SHA256**: ECDSA signatures with SHA-256 digest

### Error Handling

The verifier raises `ValueError` for:
- Missing or malformed signatures
- Invalid signature values (tampering detected)
- Unsupported signature algorithms
- Expired or invalid certificates

---

## Usage Examples

### Basic Verification

```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature

# Load signed XML and certificate
signed_xml = load_xml("signed-report.xml")
cert = Path("certificate.pem").read_bytes()

# Verify
is_valid = verify_signature(signed_xml, cert)
print(f"Valid: {is_valid}")
```

### Verification with Error Handling

```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature

signed_xml = load_xml("signed-report.xml")
cert = Path("certificate.pem").read_bytes()

try:
    is_valid = verify_signature(signed_xml, cert)
    if is_valid:
        print("✓ Report is authentic and unmodified")
    else:
        print("✗ Report signature is invalid")
except ValueError as e:
    if "No signature found" in str(e):
        print("⚠ Report is not signed")
    elif "Signature verification failed" in str(e):
        print("✗ Report has been tampered with!")
    else:
        print(f"Verification error: {e}")
```

### Batch Verification

```python
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature

def verify_reports(report_dir: Path, cert_path: Path) -> dict[str, bool]:
    """Verify all signed reports in a directory."""
    cert = cert_path.read_bytes()
    results = {}

    for report_file in report_dir.glob("*.xml"):
        try:
            xml = load_xml(report_file)
            is_valid = verify_signature(xml, cert)
            results[report_file.name] = is_valid
        except ValueError:
            results[report_file.name] = False

    return results

# Verify all reports
results = verify_reports(
    Path("test-results/"),
    Path("~/.ssh/jux/jux-signing-key.pub").expanduser()
)

for filename, is_valid in results.items():
    status = "✓" if is_valid else "✗"
    print(f"{status} {filename}")
```

---

## Security Considerations

### Trust Model

- **Public Key Trust**: You must obtain the public key/certificate through a trusted channel
- **Certificate Validation**: The verifier checks certificate validity (expiration, etc.)
- **No PKI Required**: Can work with self-signed certificates (trust on first use)

### Tamper Detection

The verifier detects:
- ✅ Modified XML content (any changes after signing)
- ✅ Modified signature values
- ✅ Changed signature algorithms
- ✅ Corrupted XML structure

The verifier does NOT detect:
- ❌ Use of compromised private keys (assumes key is secure)
- ❌ Time-of-check-time-of-use attacks (verify immediately before use)

### Best Practices

1. **Verify Immediately**: Verify signatures as soon as reports are received
2. **Trusted Certificates**: Obtain certificates through secure channels
3. **Certificate Rotation**: Regularly rotate signing keys
4. **Audit Logs**: Log all verification attempts (pass/fail)
5. **Reject Invalid**: Never process reports with invalid signatures

---

## Error Reference

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `No signature found in XML` | XML is not signed | Sign the XML first with `signer.sign_xml()` |
| `Signature verification failed` | XML was modified after signing | Report is tampered, reject it |
| `Unsupported signature algorithm` | Algorithm not recognized | Re-sign with RSA-SHA256 or ECDSA-SHA256 |
| `Invalid certificate` | Certificate expired or malformed | Obtain valid certificate |
| `Certificate does not match signature` | Wrong certificate for signature | Use matching certificate |

---

## Performance

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `verify_signature()` (RSA) | O(n) | 5-20ms |
| `verify_signature()` (ECDSA) | O(n) | 2-10ms |

**Notes**:
- ECDSA verification is faster than RSA
- Time is linear in XML size
- Certificate validation adds ~1-2ms

---

## See Also

- **[signer API](signer.md)**: XMLDSig signing (creates signatures verified by this module)
- **[canonicalizer API](canonicalizer.md)**: C14N canonicalization (used during verification)
- **[jux-verify CLI](../cli/index.md#jux-verify)**: Command-line signature verification

---

**Module Path**: `pytest_jux.verifier`
**Source Code**: `pytest_jux/verifier.py`
**Tests**: `tests/test_verifier.py`
**Last Updated**: 2025-10-20
