# XMLDSig and GPG Compatibility Research

**Date:** 2025-10-27
**Research Context:** Understanding compatibility between GPG (OpenPGP) and XML Digital Signatures for JUnit XML report signing in pytest-jux

---

## Executive Summary

**GPG (GNU Privacy Guard) and XMLDSig (XML Digital Signatures) are NOT directly compatible.** They use different signature formats, data structures, and standards. However, the underlying cryptographic keys (RSA, ECDSA) can be converted between formats with appropriate tools.

### Key Findings

- **Standards**: GPG implements OpenPGP (IETF RFC 4880), XMLDSig implements W3C XML-DSig standard
- **Signature Format**: GPG uses binary/ASCII-armored OpenPGP packets, XMLDSig uses XML structure
- **Interoperability**: Cannot verify a GPG signature with XMLDSig tools or vice versa
- **Key Conversion**: Possible but requires intermediate tools (`openpgp2ssh`, `pem2openpgp`, monkeysphere)

---

## Standards Comparison

### GPG (OpenPGP)

**Standard**: IETF RFC 4880 (OpenPGP Message Format)
**Maintained By**: IETF (Internet Engineering Task Force)
**Primary Use Cases**:
- Email encryption and signing (PGP/MIME)
- File encryption and signing
- Software package signing (Debian, RPM)
- Source code signing (Git commits, tags)

**Signature Structure**: Binary packet format
```
OpenPGP Signature Packet:
- Version
- Signature type
- Public-key algorithm
- Hash algorithm
- Hashed subpacket data
- Unhashed subpacket data
- Left 16 bits of signed hash value
- Signature value (MPI)
```

### XMLDSig (XML Digital Signature)

**Standard**: W3C XML Signature Syntax and Processing
**Maintained By**: W3C (World Wide Web Consortium)
**Primary Use Cases**:
- XML document signing (SOAP, SAML, XML-RPC)
- Web services security (WS-Security)
- Digital document workflows
- Configuration file signing

**Signature Structure**: XML-based format
```xml
<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
  <SignedInfo>
    <CanonicalizationMethod Algorithm="..."/>
    <SignatureMethod Algorithm="..."/>
    <Reference URI="">
      <Transforms>...</Transforms>
      <DigestMethod Algorithm="..."/>
      <DigestValue>...</DigestValue>
    </Reference>
  </SignedInfo>
  <SignatureValue>...</SignatureValue>
  <KeyInfo>...</KeyInfo>
</Signature>
```

---

## Technical Incompatibilities

### 1. Data Format Differences

| Aspect | GPG (OpenPGP) | XMLDSig |
|--------|---------------|---------|
| **Signature Container** | Binary packet or ASCII armor | XML element tree |
| **Canonicalization** | Not applicable | XML C14n (required) |
| **Data Encoding** | Binary or Base64 (armored) | XML with Base64 values |
| **Detached Signatures** | Separate `.sig` file | Embedded `<Signature>` element |
| **Metadata** | OpenPGP subpackets | XML attributes and elements |

### 2. Canonicalization Requirement

**XMLDSig Critical Feature**: XML Canonicalization (C14n)

XML documents can have logically-identical but byte-different representations:
```xml
<!-- These are logically identical but have different bytes -->
<test name="foo" status="passed"/>
<test status="passed" name="foo"/>
```

XMLDSig uses canonical forms to ensure consistent signatures:
- **Exclusive C14n** (exc-c14n): Most common, handles namespace prefixes
- **Inclusive C14n** (c14n): Preserves more namespace context
- **C14n with Comments**: Includes XML comments in signature

**GPG has no equivalent** because it signs binary data directly.

### 3. Key Information Embedding

**GPG Approach**: External key management
- Keys stored in keyrings (`~/.gnupg/`)
- Signatures reference key ID or fingerprint
- Recipients must obtain public key separately

**XMLDSig Approach**: Embedded or referenced key info
```xml
<KeyInfo>
  <!-- Option 1: Embed X.509 certificate -->
  <X509Data>
    <X509Certificate>MIICdTCCAd4...</X509Certificate>
  </X509Data>

  <!-- Option 2: Embed raw public key -->
  <KeyValue>
    <RSAKeyValue>
      <Modulus>xA7SEU+e...</Modulus>
      <Exponent>AQAB</Exponent>
    </RSAKeyValue>
  </KeyValue>

  <!-- Option 3: Reference key by name -->
  <KeyName>signing-key-2025</KeyName>
</KeyInfo>
```

---

## Cryptographic Algorithms

### Shared Primitives (Underlying Compatibility)

Both GPG and XMLDSig support common cryptographic algorithms:

| Algorithm Type | GPG Support | XMLDSig Support | Notes |
|----------------|-------------|-----------------|-------|
| **RSA** | ✅ RSA (1024-4096 bits) | ✅ RSA-SHA256, RSA-SHA512 | Compatible key material |
| **ECDSA** | ✅ NIST curves, Ed25519 | ✅ ECDSA-SHA256, ECDSA-SHA512 | Compatible EC keys |
| **DSA** | ✅ DSA (legacy) | ✅ DSA-SHA256 | Legacy, not recommended |
| **SHA-2 Hashes** | ✅ SHA-256, SHA-384, SHA-512 | ✅ SHA-256, SHA-384, SHA-512 | Identical |
| **SHA-1** | ✅ (deprecated) | ✅ (deprecated) | Avoid for new signatures |

**Key Insight**: The cryptographic algorithms are compatible, but the packaging formats are not.

---

## Key Conversion Workflows

### Approach 1: GPG → PEM (for XMLDSig use)

**Tool**: `openpgp2ssh` (from monkeysphere package)

```bash
# Install monkeysphere
# macOS: sudo port install monkeysphere
# Debian/Ubuntu: sudo apt install monkeysphere

# Find GPG key ID
gpg --list-secret-keys --keyid-format=long

# Export GPG secret key to OpenSSH format
gpg --export-secret-key KEY_ID | openpgp2ssh KEY_ID > private_key_openssh

# Convert OpenSSH to PEM format (if needed)
ssh-keygen -p -m PEM -f private_key_openssh

# Export public key for XMLDSig
gpg --export KEY_ID | openpgp2pem > public_key.pem
```

**Limitations**:
- Only works for RSA and DSA keys (not ECC/Ed25519)
- Private key passphrase must be removed or handled
- Metadata (user ID, signatures) is lost in conversion

### Approach 2: X.509 → GPG (reverse direction)

**Tool**: `pem2openpgp` (from monkeysphere package)

```bash
# Convert PEM private key to OpenPGP format
cat private_key.pem | \
  PEM2OPENPGP_USAGE_FLAGS=sign,auth \
  pem2openpgp "User Name <user@example.com>" > openpgp_key.pgp

# Import to GPG keyring
gpg --import openpgp_key.pgp
```

**Limitations**:
- Identity binding is manual (must specify name/email)
- No certificate chain preserved
- Trust must be established separately

### Approach 3: Generate Separate Keys (Recommended)

**For XMLDSig**: Use OpenSSL directly
```bash
# Generate RSA key pair for XMLDSig
openssl genrsa -out xmldsig_private.pem 2048
openssl rsa -in xmldsig_private.pem -pubout -out xmldsig_public.pem

# Or ECDSA (smaller, faster)
openssl ecparam -name secp256r1 -genkey -noout -out xmldsig_ecdsa_private.pem
openssl ec -in xmldsig_ecdsa_private.pem -pubout -out xmldsig_ecdsa_public.pem
```

**For GPG**: Use `gpg --generate-key`

**Rationale**:
- Avoids conversion complexity
- Each tool uses native key format
- Clearer separation of use cases
- No metadata loss

---

## Use Case Analysis

### When to Use GPG

**Ideal Scenarios**:
- Email encryption and signing
- Software package signing (apt, yum)
- Git commit/tag signing
- General file signing with detached signatures
- Web of Trust identity verification
- Cross-platform file encryption

**Advantages**:
- Mature ecosystem and tooling
- Built-in key management (keyrings)
- Web of Trust for decentralized identity
- Widely supported in developer workflows

**Disadvantages** (for XML signing):
- Requires conversion to work with XMLDSig
- No XML-specific features (C14n, XPath transforms)
- Detached signatures require separate file management

### When to Use XMLDSig

**Ideal Scenarios**:
- XML document signing (SOAP, SAML, XML-RPC)
- JUnit XML test report signing
- Configuration file signing (XML-based)
- Web services security (WS-Security)
- Embedded signatures (no separate file)

**Advantages**:
- Native XML integration
- Canonical form handling (C14n)
- Embedded or referenced key info
- XPath filtering (sign parts of XML)
- Enveloped, enveloping, or detached signatures

**Disadvantages**:
- XML-only (not general-purpose)
- More complex than simple file signatures
- Requires XML-aware tools for verification

---

## Compatibility Matrix

| Use Case | GPG | XMLDSig | Recommendation |
|----------|-----|---------|----------------|
| **Email signing** | ✅ Native | ❌ Not applicable | Use GPG (OpenPGP/MIME) |
| **Git commits** | ✅ Native | ❌ Not applicable | Use GPG |
| **JUnit XML signing** | ⚠️ Via conversion | ✅ Native | Use XMLDSig (pytest-jux) |
| **SOAP/SAML** | ❌ Not applicable | ✅ Native | Use XMLDSig |
| **General files** | ✅ Native | ❌ Wrong tool | Use GPG |
| **XML configs** | ⚠️ Detached sig | ✅ Native | Use XMLDSig |
| **Web of Trust** | ✅ Built-in | ❌ Use X.509 CA | Use GPG |
| **CA hierarchy** | ⚠️ X.509 support | ✅ Native | Use XMLDSig + X.509 |

---

## pytest-jux Context

### Current Implementation

pytest-jux uses **XMLDSig via the `signxml` Python library**:

```python
# pytest_jux/signer.py
from signxml import XMLSigner
from cryptography.hazmat.primitives import serialization

def load_private_key(source):
    """Load private key from PEM format."""
    key_data = # ... load from file/string/bytes
    private_key = serialization.load_pem_private_key(
        key_data,
        password=None,
    )
    return private_key

def sign_xml(tree, private_key, cert=None):
    """Sign XML with XMLDSig enveloped signature."""
    signer = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm="rsa-sha256" if RSA else "ecdsa-sha256",
        digest_algorithm="sha256",
    )
    signed_root = signer.sign(tree, key=private_key, cert=cert)
    return signed_root
```

### Configuration

```bash
# Enable signing
export JUX_SIGN=true

# Provide PEM-format private key
export JUX_SIGNING_KEY=./signing_key.pem

# Run pytest - JUnit XML will be signed
pytest
```

### Signed Output Example

```xml
<testsuites>
  <testsuite name="tests" tests="10" failures="0">
    <!-- test cases -->
  </testsuite>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>k5O3h1...</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>ZG5vdGU...</SignatureValue>
  </Signature>
</testsuites>
```

---

## Recommendations

### For pytest-jux Users

**✅ Recommended: Generate Dedicated XMLDSig Keys**
```bash
# Simple RSA key generation
openssl genrsa -out pytest_signing_key.pem 2048
export JUX_SIGNING_KEY=./pytest_signing_key.pem
```

**⚠️ Not Recommended: Convert Existing GPG Keys**
- Adds complexity
- Requires monkeysphere tools
- Metadata loss
- Passphrase handling issues

### For GPG Users Who Must Use XMLDSig

**If you have a strong reason to use existing GPG keys:**

1. Install monkeysphere: `sudo port install monkeysphere`
2. Export GPG key to PEM: `gpg --export-secret-key KEY_ID | openpgp2ssh KEY_ID > key.pem`
3. Configure pytest-jux: `export JUX_SIGNING_KEY=./key.pem`

**Better approach:** Maintain separate key pairs for separate purposes.

---

## References

### Standards Documents

- **OpenPGP**: [RFC 4880 - OpenPGP Message Format](https://datatracker.ietf.org/doc/html/rfc4880)
- **XMLDSig**: [W3C XML Signature Syntax and Processing Version 2.0](https://www.w3.org/TR/xmldsig-core2/)
- **XML C14n**: [W3C Canonical XML Version 1.1](https://www.w3.org/TR/xml-c14n11/)

### Tools

- **GPG**: [GNU Privacy Guard](https://gnupg.org/)
- **Monkeysphere**: [OpenPGP ↔ SSH/X.509 conversion](http://web.monkeysphere.info/)
- **signxml**: [Python XMLDSig library](https://github.com/XML-Security/signxml)
- **OpenSSL**: [Cryptography toolkit](https://www.openssl.org/)

### pytest-jux Documentation

- [Security: Digital Signatures](../security/digital-signatures.md)
- [How-To: Sign Test Reports](../howto/sign-test-reports.md)
- [Reference: Signing Configuration](../reference/configuration.md#signing-options)

---

## Conclusion

GPG and XMLDSig are **fundamentally incompatible standards** serving different purposes. While the underlying cryptographic algorithms are compatible, the signature formats and workflows are not interchangeable.

**For pytest-jux JUnit XML signing**, use **native XMLDSig with OpenSSL-generated PEM keys** rather than attempting GPG key conversion. This provides:

- ✅ Simpler workflow
- ✅ Native XMLDSig features (C14n, enveloped signatures)
- ✅ Better tool support (signxml library)
- ✅ Clearer separation of concerns

Reserve GPG for its strengths (email, git, packages) and XMLDSig for XML-specific signing needs.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Maintained By**: pytest-jux contributors
