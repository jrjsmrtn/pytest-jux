# Cryptographic Standards

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Next Review**: 2026-04-15 (Semi-annual)  
**Authority**: Based on NIST, IETF, and industry best practices

## Overview

This document specifies approved cryptographic algorithms, key requirements, and security parameters for pytest-jux. All cryptographic operations must conform to these standards.

## Approved Algorithms

### Digital Signatures (XMLDSig)

**Approved Signature Algorithms**:

| Algorithm | Key Type | Hash | Min Key Size | Status | Notes |
|-----------|----------|------|--------------|--------|-------|
| RSA-SHA256 | RSA | SHA-256 | 2048 bits | ✅ Recommended | Industry standard, broad compatibility |
| RSA-SHA384 | RSA | SHA-384 | 2048 bits | ✅ Approved | Higher security margin |
| RSA-SHA512 | RSA | SHA-512 | 2048 bits | ✅ Approved | Maximum security |
| ECDSA-SHA256 | ECDSA P-256 | SHA-256 | P-256 (256-bit) | ✅ Recommended | Modern, efficient |
| ECDSA-SHA384 | ECDSA P-384 | SHA-384 | P-384 (384-bit) | ✅ Approved | Higher security |
| ECDSA-SHA512 | ECDSA P-521 | SHA-512 | P-521 (521-bit) | ✅ Approved | Maximum security |

**References**:
- NIST FIPS 186-5 (Digital Signature Standard)
- RFC 3275 (XML-Signature Syntax and Processing)
- W3C XML Signature Syntax and Processing Version 1.1

### Hash Functions

**Approved Hash Algorithms**:

| Algorithm | Output Size | Status | Use Case |
|-----------|-------------|--------|----------|
| SHA-256 | 256 bits | ✅ Recommended | Canonical hash, general purpose |
| SHA-384 | 384 bits | ✅ Approved | Higher security requirements |
| SHA-512 | 512 bits | ✅ Approved | Maximum security |
| SHA-3 (256) | 256 bits | ⚠️ Future | Post-quantum consideration |

**References**:
- NIST FIPS 180-4 (Secure Hash Standard)

### XML Canonicalization (C14N)

**Approved C14N Methods**:

| Method | Type | Status | Use Case |
|--------|------|--------|----------|
| C14N 1.0 Exclusive | Exclusive | ✅ Recommended | Default for signatures |
| C14N 1.0 Inclusive | Inclusive | ✅ Approved | Namespace preservation |
| C14N 1.1 | Both | ✅ Approved | Modern applications |

**References**:
- W3C Canonical XML Version 1.0
- W3C Canonical XML Version 1.1

## Forbidden Algorithms

**Never Use These Algorithms**:

| Algorithm | Reason | Replaced By |
|-----------|--------|-------------|
| MD5 | Cryptographically broken | SHA-256 |
| SHA-1 | Collision attacks demonstrated | SHA-256 |
| RSA < 2048 bits | Insufficient key length | RSA 2048+ |
| DSA | Deprecated by NIST | ECDSA or RSA |
| RC4 | Biases in keystream | N/A (not used) |
| DES, 3DES | Insufficient key length | N/A (not used) |

## Key Requirements

### RSA Keys

**Minimum Requirements**:
- **Key Length**: 2048 bits (minimum), 3072 bits (recommended for long-term)
- **Public Exponent**: 65537 (0x10001) - standard value
- **Private Key Protection**: File permissions 0600, encrypted at rest recommended
- **Key Format**: PEM encoding (PKCS#1 or PKCS#8)

**Key Generation**:
```bash
# RSA 2048-bit key generation
openssl genrsa -out private_key.pem 2048

# RSA 3072-bit key generation (recommended)
openssl genrsa -out private_key.pem 3072

# Extract public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Verify key
openssl rsa -in private_key.pem -text -noout
```

**Security Considerations**:
- RSA 2048-bit: Secure until ~2030 (NIST guidance)
- RSA 3072-bit: Secure until ~2050 (NIST guidance)
- RSA 4096-bit: Long-term security, but slower performance

### ECDSA Keys

**Approved Curves**:

| Curve | Bit Security | Status | NIST Name |
|-------|--------------|--------|-----------|
| P-256 | 128-bit | ✅ Recommended | secp256r1, prime256v1 |
| P-384 | 192-bit | ✅ Approved | secp384r1 |
| P-521 | 256-bit | ✅ Approved | secp521r1 |

**Key Generation**:
```bash
# ECDSA P-256 key generation (recommended)
openssl ecparam -genkey -name prime256v1 -out private_key.pem

# ECDSA P-384 key generation
openssl ecparam -genkey -name secp384r1 -out private_key.pem

# Extract public key
openssl ec -in private_key.pem -pubout -out public_key.pem

# Verify key
openssl ec -in private_key.pem -text -noout
```

**Security Considerations**:
- P-256: Equivalent to RSA 3072-bit security
- P-384: Equivalent to RSA 7680-bit security
- Faster signature generation than RSA
- Smaller signature sizes

**Forbidden Curves**:
- secp256k1 (Bitcoin curve) - not NIST-approved for government use
- Proprietary or non-standard curves
- Curves with known weaknesses

### Key Storage

**File System Protection**:
```bash
# Set restrictive permissions (Unix/Linux/macOS)
chmod 600 private_key.pem
chown $USER:$USER private_key.pem

# Verify permissions
ls -la private_key.pem
# Should show: -rw------- (600)
```

**Encryption at Rest** (Recommended):
```bash
# Encrypt private key with passphrase
openssl rsa -in private_key.pem -aes256 -out private_key_encrypted.pem

# Use encrypted key (will prompt for passphrase)
pytest --jux-key=private_key_encrypted.pem
```

**Environment Considerations**:
- Store keys outside version control (add `*.pem` to .gitignore)
- Use environment-specific keys (dev, staging, production)
- Consider hardware security modules (HSM) for production
- Use secrets management systems (HashiCorp Vault, AWS Secrets Manager)

### Key Rotation Policy

**Rotation Schedule**:

| Key Type | Environment | Rotation Frequency | Trigger Events |
|----------|-------------|-------------------|----------------|
| RSA 2048 | Development | Annual | None (best effort) |
| RSA 2048 | Production | Annual | Compromise suspected |
| RSA 3072+ | Production | 2 years | Compromise suspected |
| ECDSA P-256 | Production | 2 years | Compromise suspected |
| ECDSA P-384+ | Production | 3 years | Compromise suspected |

**Immediate Rotation Required If**:
- Private key compromised or suspected compromise
- Key accidentally committed to version control
- Employee with key access terminated
- Security audit recommends rotation
- Algorithm or key length deprecated

**Rotation Procedure**:
1. Generate new key pair
2. Update configuration with new private key
3. Publish new public key to Jux API
4. Maintain old public key for historical verification (90 days minimum)
5. Monitor for any issues with new key
6. Securely destroy old private key after grace period

## Implementation Requirements

### signxml Library Configuration

**Approved Configuration**:
```python
from signxml import XMLSigner, XMLVerifier, methods

# Signature generation
signer = XMLSigner(
    method=methods.enveloped,          # Signature inside signed element
    signature_algorithm='rsa-sha256',  # or 'ecdsa-sha256'
    digest_algorithm='sha256',
    c14n_algorithm='http://www.w3.org/2001/10/xml-exc-c14n#'  # Exclusive C14N
)

# Signature verification
verifier = XMLVerifier()
# Verification automatically validates algorithm used
```

**Forbidden Configurations**:
```python
# NEVER use these
signature_algorithm='none'           # No signature!
signature_algorithm='hmac-sha1'      # SHA-1 forbidden
digest_algorithm='md5'               # MD5 forbidden
digest_algorithm='sha1'              # SHA-1 forbidden
```

### lxml Configuration

**Secure Defaults**:
```python
from lxml import etree

# Secure parser configuration
parser = etree.XMLParser(
    resolve_entities=False,    # Disable XXE
    no_network=True,           # Prevent network access
    dtd_validation=False,      # Disable DTD
    load_dtd=False,            # Don't load external DTDs
    huge_tree=False,           # Prevent billion laughs
    remove_blank_text=False    # Preserve formatting for C14N
)

# Parse XML securely
tree = etree.parse(xml_file, parser=parser)
```

### cryptography Library

**Key Loading**:
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load RSA private key
with open('private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,  # or bytes password
        backend=default_backend()
    )

# Validate key type and size
from cryptography.hazmat.primitives.asymmetric import rsa, ec

if isinstance(private_key, rsa.RSAPrivateKey):
    key_size = private_key.key_size
    if key_size < 2048:
        raise ValueError(f"RSA key too small: {key_size} < 2048")
elif isinstance(private_key, ec.EllipticCurvePrivateKey):
    curve_name = private_key.curve.name
    if curve_name not in ['secp256r1', 'secp384r1', 'secp521r1']:
        raise ValueError(f"Unsupported curve: {curve_name}")
else:
    raise TypeError(f"Unsupported key type: {type(private_key)}")
```

## Security Parameters

### XML Processing Limits

```python
# pytest_jux/security.py constants
from typing import Final

# XML size limits (prevent DoS)
MAX_XML_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
MAX_XML_DEPTH: Final[int] = 100                     # Maximum nesting
MAX_XML_NODES: Final[int] = 100_000                 # Maximum elements

# Signature limits
MAX_SIGNATURE_SIZE_BYTES: Final[int] = 4096        # 4 KB
MIN_SIGNATURE_SIZE_BYTES: Final[int] = 128         # 128 bytes

# Parsing timeouts
XML_PARSE_TIMEOUT_SECONDS: Final[int] = 30
SIGNATURE_VERIFY_TIMEOUT_SECONDS: Final[int] = 10
```

### Constant-Time Operations

**Critical Requirement**: Signature comparison must be constant-time to prevent timing attacks.

```python
import secrets

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Constant-time comparison prevents timing attacks.
    
    SECURITY: Never use == or != for signature comparison!
    """
    return secrets.compare_digest(a, b)

# Usage
if constant_time_compare(computed_signature, expected_signature):
    # Signature valid
    pass
```

**Forbidden**:
```python
# NEVER do this - vulnerable to timing attacks!
if computed_signature == expected_signature:  # ❌ WRONG
    pass
```

## Compliance

### Standards Compliance

pytest-jux cryptographic operations comply with:

- **NIST FIPS 140-2**: Cryptographic Module Validation Program
- **NIST FIPS 186-5**: Digital Signature Standard (DSS)
- **NIST FIPS 180-4**: Secure Hash Standard (SHS)
- **NIST SP 800-57**: Key Management Recommendations
- **RFC 3275**: XML-Signature Syntax and Processing
- **W3C XML Signature**: XML Signature Syntax and Processing Version 1.1

### Algorithm Deprecation Timeline

| Algorithm | Current Status | Deprecation Date | Removal Date |
|-----------|----------------|------------------|--------------|
| RSA-SHA256 (2048-bit) | ✅ Approved | 2030 (projected) | 2035 (projected) |
| RSA-SHA256 (3072-bit) | ✅ Recommended | 2050+ | N/A |
| ECDSA-SHA256 (P-256) | ✅ Recommended | 2040+ | N/A |
| SHA-256 | ✅ Recommended | No plans | N/A |

**Note**: Dates are projections based on current NIST guidance. Monitor NIST publications for updates.

## Testing Requirements

### Cryptographic Test Coverage

**Required Tests**:
1. ✅ Algorithm enforcement (reject forbidden algorithms)
2. ✅ Key length validation (minimum requirements)
3. ✅ Signature generation and verification
4. ✅ Constant-time comparison validation
5. ✅ Key format validation
6. ✅ Curve validation (ECDSA)
7. ✅ Error handling for invalid keys
8. ✅ Performance benchmarks

### Test Vectors

Use standard test vectors from:
- NIST Cryptographic Algorithm Validation Program (CAVP)
- RFC test vectors for XML-Signature
- OpenSSL test suite

## References

### Standards Documents

1. **NIST FIPS 186-5**: Digital Signature Standard  
   https://csrc.nist.gov/publications/detail/fips/186/5/final

2. **NIST FIPS 180-4**: Secure Hash Standard  
   https://csrc.nist.gov/publications/detail/fips/180/4/final

3. **NIST SP 800-57**: Key Management Recommendations  
   https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final

4. **RFC 3275**: XML-Signature Syntax and Processing  
   https://www.ietf.org/rfc/rfc3275.txt

5. **W3C XML Signature**: Syntax and Processing Version 1.1  
   https://www.w3.org/TR/xmldsig-core1/

### Libraries

1. **signxml**: https://github.com/XML-Security/signxml
2. **cryptography**: https://cryptography.io/
3. **lxml**: https://lxml.de/

### Security Advisories

Monitor these sources for cryptographic vulnerabilities:
- CVE Database: https://cve.mitre.org/
- NVD: https://nvd.nist.gov/
- GitHub Security Advisories
- signxml security advisories
- cryptography library security advisories

## Document Maintenance

**Review Triggers**:
- NIST algorithm updates
- New cryptographic attacks discovered
- Library security advisories
- Industry best practice changes
- Semi-annual scheduled review

**Approval**: Georges Martin (Maintainer)

---

**Document Status**: Active  
**Classification**: Public  
**Version**: 1.0  
**Last Review**: 2025-10-15  
**Next Review**: 2026-04-15
