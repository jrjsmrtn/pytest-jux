# signer API Reference

**Module**: `pytest_jux.signer`
**Purpose**: XML digital signature generation for JUnit XML reports
**Version**: 0.1.9+

---

## Overview

The `signer` module provides functionality to sign JUnit XML reports using **XML Digital Signatures (XMLDSig)** as defined in [W3C XML-Signature](https://www.w3.org/TR/xmldsig-core/). It supports **RSA** and **ECDSA** cryptographic keys for signing.

### Purpose

- **Chain of Trust**: Establish cryptographic proof of report origin
- **Integrity Verification**: Detect tampering or modifications
- **Authentication**: Prove identity of report generator
- **Non-Repudiation**: Signer cannot deny creating the report

### When to Use This Module

- Signing test reports for publication to Jux API
- Creating signed reports for compliance/audit purposes
- Verifying integrity of test reports
- Establishing chain of custody for test results

### Related Modules

- **`canonicalizer`**: Used for C14N before signing
- **`verifier`**: Signature verification (separate module)
- **`plugin`**: Automatic signing during pytest execution

---

## Type Aliases

### `PrivateKey`

Union type for supported private key types.

```python
PrivateKey = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey
```

**Supported Key Types**:
- `cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey` (RSA keys)
- `cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePrivateKey` (ECDSA keys)

---

## Functions

### `load_private_key()`

Load a private key from various source types (file path, string, or bytes).

```python
def load_private_key(source: str | bytes | Path) -> PrivateKey
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `str \| bytes \| Path` | **Required**. Private key source, can be:<br>• `Path` object pointing to PEM key file<br>• PEM key string<br>• PEM key bytes |

#### Supported Key Formats

- **PEM format**: `-----BEGIN PRIVATE KEY-----` or `-----BEGIN RSA PRIVATE KEY-----`
- **Unencrypted keys only** (password-protected keys not supported in current version)
- **RSA keys**: 2048, 3072, or 4096 bits
- **ECDSA keys**: P-256, P-384, or P-521 curves

#### Returns

| Type | Description |
|------|-------------|
| `PrivateKey` | Private key object (either `RSAPrivateKey` or `EllipticCurvePrivateKey`) |

#### Raises

| Exception | When |
|-----------|------|
| `FileNotFoundError` | If `source` is a `Path` and the file doesn't exist |
| `ValueError` | If key data is invalid, malformed, or unsupported format |

#### Examples

**Load from file path:**
```python
from pathlib import Path
from pytest_jux.signer import load_private_key

# Load RSA key from file
key_path = Path("~/.jux/keys/rsa-key.pem").expanduser()
private_key = load_private_key(key_path)

print(f"Key type: {type(private_key).__name__}")
# Output: Key type: RSAPrivateKey

# Check key size
if hasattr(private_key, 'key_size'):
    print(f"Key size: {private_key.key_size} bits")
    # Output: Key size: 2048 bits
```

**Load from string:**
```python
from pytest_jux.signer import load_private_key

pem_string = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"""

private_key = load_private_key(pem_string)
```

**Load from bytes:**
```python
from pytest_jux.signer import load_private_key

pem_bytes = Path("key.pem").read_bytes()
private_key = load_private_key(pem_bytes)
```

**Error handling:**
```python
from pathlib import Path
from pytest_jux.signer import load_private_key

# Handle missing file
try:
    key = load_private_key(Path("nonexistent.pem"))
except FileNotFoundError as e:
    print(f"Key file not found: {e}")

# Handle invalid key data
try:
    key = load_private_key("invalid key data")
except ValueError as e:
    print(f"Invalid key: {e}")
    # Output: Invalid key: Failed to load private key: ...
```

**Detect key type:**
```python
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from pytest_jux.signer import load_private_key

key = load_private_key(Path("key.pem"))

if isinstance(key, rsa.RSAPrivateKey):
    print(f"RSA key: {key.key_size} bits")
elif isinstance(key, ec.EllipticCurvePrivateKey):
    print(f"ECDSA key: {key.curve.name}")
```

---

### `sign_xml()`

Sign XML with XMLDSig enveloped signature.

```python
def sign_xml(
    tree: etree._Element,
    private_key: PrivateKey,
    cert: str | bytes | None = None,
) -> etree._Element
```

#### Description

Adds an **enveloped XMLDSig signature** to the XML document using the provided private key. The signature is placed as a child element of the root element.

The generated signature includes:
- **SignedInfo**: Canonicalization method, signature algorithm, and reference to signed data
- **SignatureValue**: The actual cryptographic signature bytes (base64 encoded)
- **KeyInfo** (optional): X.509 certificate information for verification

#### Signature Methods

| Key Type | Signature Algorithm | Digest Algorithm |
|----------|---------------------|------------------|
| RSA | `rsa-sha256` | SHA-256 |
| ECDSA | `ecdsa-sha256` | SHA-256 |

Both use **C14N (Canonical XML)** for canonicalization before signing.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tree` | `lxml.etree._Element` | **Required** | XML element tree to sign |
| `private_key` | `PrivateKey` | **Required** | RSA or ECDSA private key for signing |
| `cert` | `str \| bytes \| None` | `None` | Optional X.509 certificate in PEM or DER format.<br>If provided, includes certificate in signature's `<KeyInfo>` for verification |

#### Returns

| Type | Description |
|------|-------------|
| `lxml.etree._Element` | Signed XML element tree with `<Signature>` element added as child of root |

#### Raises

| Exception | When |
|-----------|------|
| `TypeError` | If `tree` is not an `lxml.etree._Element` |
| `ValueError` | If signing fails (invalid key, malformed XML, etc.) |

#### Examples

**Basic signing with RSA key:**
```python
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

# Load report and key
report = load_xml(Path("test-results/junit.xml"))
private_key = load_private_key(Path("~/.jux/keys/rsa-key.pem").expanduser())

# Sign the report
signed_report = sign_xml(report, private_key)

# Signature is now embedded in the XML
print(etree.tostring(signed_report, pretty_print=True).decode())
```

**Output structure:**
```xml
<testsuite name="example" tests="10">
    <testcase name="test1" />
    <!-- ... more test cases ... -->

    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
        <SignedInfo>
            <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
            <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
            <Reference URI="">
                <Transforms>
                    <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                </Transforms>
                <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
                <DigestValue>abc123...</DigestValue>
            </Reference>
        </SignedInfo>
        <SignatureValue>xyz789...</SignatureValue>
    </Signature>
</testsuite>
```

**Signing with ECDSA key:**
```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

report = load_xml("report.xml")
ecdsa_key = load_private_key("ecdsa-p256-key.pem")

signed_report = sign_xml(report, ecdsa_key)
# Uses ecdsa-sha256 signature algorithm
```

**Including X.509 certificate:**
```python
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

report = load_xml("report.xml")
private_key = load_private_key("rsa-key.pem")

# Load certificate
cert_pem = Path("cert.pem").read_text()

# Sign with certificate embedded
signed_report = sign_xml(report, private_key, cert=cert_pem)
# Signature now includes <KeyInfo><X509Data> with certificate
```

**Signature with certificate structure:**
```xml
<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>...</SignedInfo>
    <SignatureValue>...</SignatureValue>
    <KeyInfo>
        <X509Data>
            <X509Certificate>MIIDXTCCAkWgAwIBAgI...</X509Certificate>
        </X509Data>
    </KeyInfo>
</Signature>
```

**Save signed report:**
```python
from pathlib import Path
from lxml import etree
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

# Sign report
report = load_xml("report.xml")
key = load_private_key("key.pem")
signed_report = sign_xml(report, key)

# Save to file
output_path = Path("signed_report.xml")
output_path.write_bytes(etree.tostring(signed_report, pretty_print=True))
print(f"Signed report saved to {output_path}")
```

**Error handling:**
```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

report = load_xml("report.xml")
key = load_private_key("key.pem")

try:
    signed_report = sign_xml(report, key)
except TypeError as e:
    print(f"Invalid XML tree: {e}")
except ValueError as e:
    print(f"Signing failed: {e}")
```

---

### `verify_signature()`

Verify XMLDSig signature in signed XML.

```python
def verify_signature(tree: etree._Element) -> bool
```

#### Description

Verifies the XML digital signature embedded in the XML document. Returns `True` if the signature is cryptographically valid, `False` otherwise.

**Note**: This is a basic verification function included in the `signer` module. For more advanced verification features, use the [`verifier` module](verifier.md).

#### Verification Process

1. Locates `<Signature>` element in XML
2. Extracts signature metadata (algorithms, digest values)
3. Recomputes canonical hash of signed content
4. Verifies cryptographic signature using embedded certificate or key

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tree` | `lxml.etree._Element` | Signed XML element tree |

#### Returns

| Type | Description |
|------|-------------|
| `bool` | `True` if signature is valid, `False` otherwise |

#### Examples

**Basic signature verification:**
```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import verify_signature

# Load signed report
signed_report = load_xml("signed_report.xml")

# Verify signature
if verify_signature(signed_report):
    print("✓ Signature is valid")
else:
    print("✗ Signature is invalid or missing")
```

**Complete sign and verify workflow:**
```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml, verify_signature

# Sign report
report = load_xml("report.xml")
key = load_private_key("key.pem")
signed_report = sign_xml(report, key, cert=Path("cert.pem").read_text())

# Verify signature
is_valid = verify_signature(signed_report)
print(f"Signature valid: {is_valid}")  # Output: Signature valid: True
```

**Detect unsigned reports:**
```python
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import verify_signature

# Load unsigned report
report = load_xml("unsigned_report.xml")

# Verification returns False for unsigned reports
if not verify_signature(report):
    print("Report is not signed or signature is invalid")
```

**Detect tampered reports:**
```python
from lxml import etree
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml, verify_signature

# Sign report
report = load_xml("<testsuite><testcase name='tc1'/></testsuite>")
key = load_private_key("key.pem")
signed_report = sign_xml(report, key)

# Verify before tampering
print(f"Before: {verify_signature(signed_report)}")  # True

# Tamper with the report
signed_report.set("tests", "999")  # Modify attribute

# Verify after tampering
print(f"After: {verify_signature(signed_report)}")  # False
```

---

## Complete Example: Sign and Verify Pipeline

This example demonstrates a complete workflow for signing and verifying test reports:

```python
from pathlib import Path
from lxml import etree
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml, verify_signature

def sign_test_report(
    report_path: Path,
    key_path: Path,
    cert_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """
    Sign a JUnit XML test report.

    Args:
        report_path: Path to unsigned JUnit XML report
        key_path: Path to private key (PEM format)
        cert_path: Optional path to X.509 certificate
        output_path: Optional output path (defaults to <report>_signed.xml)

    Returns:
        Path to signed report file
    """
    # Load report and key
    report = load_xml(report_path)
    private_key = load_private_key(key_path)

    # Load certificate if provided
    cert = None
    if cert_path:
        cert = cert_path.read_text()

    # Sign the report
    signed_report = sign_xml(report, private_key, cert=cert)

    # Determine output path
    if output_path is None:
        output_path = report_path.parent / f"{report_path.stem}_signed.xml"

    # Save signed report
    output_path.write_bytes(etree.tostring(signed_report, pretty_print=True))

    print(f"✓ Signed report saved to {output_path}")
    return output_path


def verify_test_report(report_path: Path) -> bool:
    """
    Verify a signed JUnit XML test report.

    Args:
        report_path: Path to signed JUnit XML report

    Returns:
        True if signature is valid, False otherwise
    """
    report = load_xml(report_path)
    is_valid = verify_signature(report)

    if is_valid:
        print(f"✓ Signature is valid: {report_path}")
    else:
        print(f"✗ Signature is invalid or missing: {report_path}")

    return is_valid


# Usage
if __name__ == "__main__":
    # Paths
    report = Path("test-results/junit.xml")
    key = Path("~/.jux/keys/rsa-key.pem").expanduser()
    cert = Path("~/.jux/certs/cert.pem").expanduser()

    # Sign report
    signed_path = sign_test_report(report, key, cert)

    # Verify signature
    verify_test_report(signed_path)
```

---

## Technical Details

### XMLDSig Specification

The signature format follows the [W3C XML Signature](https://www.w3.org/TR/xmldsig-core/) specification:

**Signature Structure**:
```xml
<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>                    <!-- What was signed and how -->
        <CanonicalizationMethod />  <!-- C14N method -->
        <SignatureMethod />         <!-- RSA-SHA256 or ECDSA-SHA256 -->
        <Reference>                 <!-- Reference to signed data -->
            <Transforms />          <!-- Enveloped signature transform -->
            <DigestMethod />        <!-- SHA-256 -->
            <DigestValue />         <!-- Hash of canonical content -->
        </Reference>
    </SignedInfo>
    <SignatureValue />              <!-- Encrypted digest -->
    <KeyInfo>                       <!-- Optional: Key/certificate info -->
        <X509Data>
            <X509Certificate />     <!-- PEM certificate -->
        </X509Data>
    </KeyInfo>
</Signature>
```

### Supported Algorithms

**RSA Keys**:
- Signature algorithm: `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256`
- Digest algorithm: `http://www.w3.org/2001/04/xmlenc#sha256`
- Recommended key sizes: 2048, 3072, 4096 bits

**ECDSA Keys**:
- Signature algorithm: `http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256`
- Digest algorithm: `http://www.w3.org/2001/04/xmlenc#sha256`
- Supported curves: P-256, P-384, P-521

### Security Considerations

**Key Management**:
- ✅ **DO**: Store private keys securely (encrypted, restrictive permissions)
- ✅ **DO**: Use strong keys (RSA ≥2048 bits, ECDSA ≥P-256)
- ✅ **DO**: Rotate keys periodically
- ❌ **DON'T**: Commit private keys to version control
- ❌ **DON'T**: Share private keys between environments

**Certificate Validation**:
- Including certificates enables recipient verification
- Self-signed certificates work for testing but not production
- Production should use certificates from trusted CAs

### Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `load_private_key()` | O(1) | Fast key parsing |
| `sign_xml()` | O(n) | Linear in XML size, dominated by C14N |
| `verify_signature()` | O(n) | Linear in XML size, includes re-canonicalization |

**Typical Performance** (MacBook Pro M1):
- Small reports (<100 tests): <10ms signing
- Medium reports (100-1000 tests): <100ms signing
- Large reports (1000+ tests): <500ms signing

**RSA vs ECDSA**:
- RSA signing: Slower but more widely supported
- ECDSA signing: Faster, smaller signatures, modern standard

### Thread Safety

All functions are **thread-safe** (no shared state). Safe for parallel test execution.

---

## Common Patterns

### Pattern 1: Automated Signing in pytest

```python
import pytest
from pathlib import Path
from lxml import etree
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

def pytest_sessionfinish(session, exitstatus):
    """Hook to automatically sign JUnit XML after test run."""
    xml_path = Path(session.config.getoption("--junit-xml"))
    if not xml_path.exists():
        return

    # Load key from environment or config
    key_path = Path(session.config.getini("jux_key_path"))
    private_key = load_private_key(key_path)

    # Sign report
    report = load_xml(xml_path)
    signed_report = sign_xml(report, private_key)

    # Overwrite with signed version
    xml_path.write_bytes(etree.tostring(signed_report))
```

### Pattern 2: Batch Signing

```python
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

def sign_all_reports(reports_dir: Path, key_path: Path):
    """Sign all XML reports in a directory."""
    key = load_private_key(key_path)

    for report_file in reports_dir.glob("*.xml"):
        report = load_xml(report_file)
        signed_report = sign_xml(report, key)

        # Save as <name>_signed.xml
        output = report_file.parent / f"{report_file.stem}_signed.xml"
        output.write_bytes(etree.tostring(signed_report))
        print(f"Signed: {report_file} → {output}")
```

### Pattern 3: CI/CD Integration

```python
import os
from pathlib import Path
from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

# Load key from environment variable (set in CI secrets)
key_pem = os.environ.get("JUX_SIGNING_KEY")
if not key_pem:
    raise ValueError("JUX_SIGNING_KEY environment variable not set")

key = load_private_key(key_pem)

# Sign report
report = load_xml("test-results/junit.xml")
signed_report = sign_xml(report, key)

# Save for publishing
Path("signed-results/junit.xml").write_bytes(etree.tostring(signed_report))
```

---

## See Also

- **[canonicalizer API](canonicalizer.md)**: XML canonicalization (used before signing)
- **[verifier API](verifier.md)**: Advanced signature verification
- **[plugin API](plugin.md)**: Automated signing during pytest execution
- **[jux-keygen CLI](../cli/jux-keygen.md)**: Generate signing keys
- **[jux-sign CLI](../cli/jux-sign.md)**: Command-line signing tool
- **[W3C XML-Signature](https://www.w3.org/TR/xmldsig-core/)**: XMLDSig specification

---

**Module Path**: `pytest_jux.signer`
**Source Code**: `pytest_jux/signer.py`
**Tests**: `tests/test_signer.py`
**Last Updated**: 2025-10-20
