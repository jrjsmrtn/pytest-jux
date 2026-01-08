# Digital Signature Provenance and Trust Models

**Date:** 2025-10-27
**Research Context:** Understanding how digital signatures prove provenance and identity for JUnit XML test reports

---

## Executive Summary

**Digital signatures provide cryptographic guarantees (integrity, authentication, non-repudiation), but provenance—proving WHO signed something—requires additional trust infrastructure.** The strength of provenance claims depends on identity verification mechanisms, not the signature algorithm itself.

### Key Findings

- **Cryptographic Proof**: Signatures prove "holder of private key X signed this"
- **Identity Binding**: Trust models prove "private key X belongs to person/organization Y"
- **Trust Models**: Web of Trust (GPG) vs Certificate Authorities (X.509) vs Direct Distribution
- **Provenance Strength**: Varies from weak (raw keys) to strong (CA-verified certificates)

---

## What Digital Signatures Prove

### Cryptographic Guarantees (Always Provided)

Digital signatures use asymmetric cryptography to provide mathematical guarantees:

| Property | Definition | How It's Achieved |
|----------|------------|-------------------|
| **Integrity** | Data hasn't been modified since signing | Hash comparison: signature contains hash of original data |
| **Authentication** | Signed by holder of specific private key | Only private key can create valid signature for public key |
| **Non-repudiation** | Signer cannot deny having signed | Signature mathematically bound to private key |

### Verification Process

```
Original Data → Hash (SHA-256) → Sign with Private Key → Signature Value
                     ↓
Modified Data → Hash (SHA-256) → Compare ───────────────────┘
                     ↓                                       ↓
              Different Hash                            Same Hash?
                     ↓                                       ↓
              Verification FAILS                    Verification SUCCEEDS
```

**Example** (JUnit XML signing):
```python
# Sign
junit_xml = "<testsuites>...</testsuites>"
hash_value = SHA256(junit_xml)  # e.g., "a3f5b..."
signature = RSA_sign(hash_value, private_key)  # Creates signature

# Verify
received_xml = "<testsuites>...</testsuites>"  # Unmodified
hash_check = SHA256(received_xml)  # Should be "a3f5b..."
RSA_verify(signature, hash_check, public_key)  # Returns TRUE

# Tampered
tampered_xml = "<testsuites modified>...</testsuites>"
hash_tampered = SHA256(tampered_xml)  # Different: "b8c2e..."
RSA_verify(signature, hash_tampered, public_key)  # Returns FALSE
```

---

## The Identity Problem

### What Signatures DON'T Prove Automatically

**Scenario**: Alice creates a key pair and signs a document.

```
Private Key (Alice's secret) → Sign Document → Signature
                                                    ↓
Public Key (distributed) ← Verify Signature ← Recipients
```

**Question**: How do recipients know the public key belongs to Alice?

**Without additional infrastructure:**
- ❌ Anyone can generate a key pair and claim "I am Alice"
- ❌ No cryptographic link between key and real-world identity
- ❌ No proof that "alice@example.com" key belongs to the real Alice

### The Core Challenge

| What Cryptography Proves | What Trust Models Prove |
|--------------------------|-------------------------|
| ✅ "Holder of private key X signed this" | ✅ "Private key X belongs to Alice Smith at Acme Corp" |
| ✅ "Data hasn't changed" | ✅ "Alice's identity was verified by trusted party Y" |
| ✅ "Signature is mathematically valid" | ✅ "I trust party Y to verify identities" |

**Provenance = Cryptographic Proof + Identity Binding**

---

## Trust Models Comparison

### Model 1: Direct Key Distribution (No Infrastructure)

**How It Works**:
1. Generate key pair
2. Share public key directly with recipients (email, USB drive, in-person)
3. Recipients trust key based on distribution channel

**Example**:
```bash
# Generate key pair
openssl genrsa -out team_key.pem 2048
openssl rsa -in team_key.pem -pubout -out team_public.pem

# Share team_public.pem via:
# - Internal Git repository
# - Team wiki
# - Secure file share
# - Email to team members
```

**Trust Basis**: "I trust this key because I got it from a trusted channel"

**Provenance Strength**: ⚠️ **Weak to Medium**
- Depends entirely on channel security
- Vulnerable to channel compromise
- No formal identity verification
- Works for small, closed groups

**Use Cases**:
- Internal team testing
- Personal projects
- Development environments
- Small organizations with secure channels

---

### Model 2: GPG Web of Trust (Decentralized)

**How It Works**:
1. Create GPG key with identity (name, email)
2. Publish to key servers
3. Others verify your identity (in person, phone, government ID)
4. They sign your public key with their keys
5. Recipients check: "Do I trust any signers of this key?"

**Trust Chain Example**:
```
Bob receives a file signed by Alice

Bob's Keyring:
  ✅ Trusts Carol (verified in person)
  ✅ Carol signed Alice's key (Carol verified Alice)
     ↓
  ✅ Therefore: Bob trusts Alice's key
```

**Verification Workflow**:
```bash
# Alice creates key
gpg --generate-key  # Name: Alice Smith, Email: alice@example.com

# Alice meets Carol in person, shows ID
# Carol verifies Alice's key fingerprint over phone
gpg --fingerprint alice@example.com
# "3A4B 5C6D 7E8F 9A0B 1C2D 3E4F 5A6B 7C8D 9E0F A1B2"

# Carol signs Alice's key (after verification)
gpg --sign-key alice@example.com

# Bob imports Alice's key
gpg --import alice_public_key.asc

# Bob sees Carol signed it (Bob trusts Carol)
gpg --check-sigs alice@example.com
# Shows: sig! Carol <carol@example.com>

# Bob can now trust Alice's signatures
gpg --verify signed_file.xml.sig signed_file.xml
```

**Trust Basis**: "I trust Alice because Carol verified her, and I trust Carol"

**Provenance Strength**: ✅ **Medium to Strong**
- Depends on number and quality of signatures
- Stronger with more trusted signers
- Social network of trust
- Requires manual verification work

**Advantages**:
- Decentralized (no central authority)
- Flexible trust relationships
- No cost
- Privacy-preserving (no CA tracking)

**Disadvantages**:
- Doesn't scale to strangers well
- Requires in-person or verified communication
- Trust is subjective and transitive
- Complexity for non-technical users

**Use Cases**:
- Open source software signing
- Debian package maintainers
- PGP/GPG email encryption
- Developer community trust networks

---

### Model 3: Certificate Authorities (Hierarchical)

**How It Works**:
1. Generate key pair and Certificate Signing Request (CSR)
2. Submit CSR to Certificate Authority (CA)
3. CA verifies your identity (varies by CA type)
4. CA signs your certificate with their trusted key
5. Recipients trust CA, therefore trust your certificate

**CA Hierarchy**:
```
Root CA (Trusted by OS/Browser)
  ↓ signs
Intermediate CA
  ↓ signs
End-Entity Certificate (Your Identity)
  ↓ contains
Public Key
```

**Verification Workflow**:
```bash
# Generate private key and CSR
openssl req -new -newkey rsa:2048 -nodes \
  -keyout mykey.pem -out mycsr.csr \
  -subj "/C=US/ST=CA/O=Acme Corp/CN=Alice Smith"

# Submit to CA (e.g., DigiCert, Let's Encrypt)
# CA verifies:
# - Domain ownership (for DV certificates)
# - Organization existence (for OV certificates)
# - Legal identity (for EV certificates)

# CA issues signed certificate
# Certificate contains:
# - Public key
# - Identity information (CN, O, OU)
# - CA signature
# - Validity period

# Recipients verify certificate chain
openssl verify -CAfile ca-bundle.crt alice-cert.pem
# alice-cert.pem: OK
```

**Trust Basis**: "I trust this CA to verify identities, therefore I trust this certificate"

**Provenance Strength**: ✅✅ **Strong**
- CA performs formal identity verification
- Widely accepted trust model
- Scalable to internet-scale use
- Legal backing in many jurisdictions

**CA Verification Levels**:

| Level | Verification | Use Case | Cost |
|-------|-------------|----------|------|
| **Domain Validated (DV)** | Domain ownership only | HTTPS websites | $ (or free with Let's Encrypt) |
| **Organization Validated (OV)** | Domain + legal entity verification | Corporate websites | $$ |
| **Extended Validation (EV)** | Stringent legal and operational verification | Financial services, high-security | $$$ |
| **Code Signing** | Organization + developer identity | Software signing | $$$ |

**Advantages**:
- Works with strangers (no prior relationship needed)
- Formal identity verification
- Hierarchical trust model (easy to understand)
- Revocation infrastructure (CRL, OCSP)

**Disadvantages**:
- Centralized (must trust CAs)
- Costs money (except Let's Encrypt for DV)
- CA compromise affects all certificates
- Privacy concerns (CA knows all certificates issued)

**Use Cases**:
- HTTPS/TLS (web servers)
- Code signing (Windows, macOS applications)
- Email encryption (S/MIME)
- Document signing (Adobe, DocuSign)

---

## Provenance Strength Analysis

### Scenario-Based Comparison

| Scenario | Key Type | Identity Verification | Provenance Strength | Trust Basis |
|----------|----------|----------------------|---------------------|-------------|
| **Personal dev testing** | Raw OpenSSL key | None | N/A | Self-trust |
| **Internal team (Git repo)** | Shared key in private repo | Team knows key location | ⚠️ Medium | Secure channel trust |
| **Internal team (secure file share)** | Shared key distributed securely | Admin controls distribution | ⚠️ Medium | Access control trust |
| **Open source project (unsigned GPG)** | GPG key, no signatures | Self-asserted | ⚠️ Weak | "Anyone can claim identity" |
| **Open source project (2-3 GPG signatures)** | GPG key with signatures | Manual verification by signers | ✅ Medium | Web of Trust |
| **Open source project (10+ GPG signatures)** | GPG key with many signatures | Multiple trusted verifiers | ✅ Strong | Strong Web of Trust |
| **Commercial software (code signing cert)** | CA-signed certificate | CA legal verification (OV/EV) | ✅✅ Strong | CA hierarchy |
| **Financial/Legal documents** | EV certificate | Stringent CA verification | ✅✅✅ Very Strong | Legal + CA hierarchy |

### Attack Resistance

| Attack | Direct Distribution | GPG Web of Trust | CA Certificate |
|--------|---------------------|------------------|----------------|
| **Key substitution** (attacker replaces public key) | ⚠️ Vulnerable if channel compromised | ✅ Requires compromising multiple signers | ✅ Requires CA compromise |
| **Impersonation** (attacker claims to be signer) | ⚠️ Easy if key not verified | ✅ Difficult (requires fooling verifiers) | ✅ Very difficult (CA verification) |
| **Man-in-the-middle** (intercept distribution) | ⚠️ Vulnerable without secure channel | ✅ Multiple paths make MITM harder | ✅ Certificate pinning prevents MITM |
| **Revocation** (key compromised) | ❌ No revocation mechanism | ⚠️ Manual revocation certificate | ✅ Automated CRL/OCSP |

---

## pytest-jux Application

### Use Case Analysis for JUnit XML Signing

#### Scenario 1: Individual Developer (Personal Testing)

**Setup**:
```bash
# Generate personal signing key
openssl genrsa -out ~/.pytest-jux/signing_key.pem 2048
export JUX_SIGNING_KEY=~/.pytest-jux/signing_key.pem
export JUX_SIGN=true
pytest
```

**Provenance Claim**: "This test report was created on my machine"
**Trust Model**: Self-trust (no external verification needed)
**Strength**: N/A (self-verification)
**Use Case**: Local integrity checks, personal audit trails

---

#### Scenario 2: Internal Development Team

**Setup**:
```bash
# Team lead generates shared key
openssl genrsa -out team_signing_key.pem 2048
openssl rsa -in team_signing_key.pem -pubout -out team_public_key.pem

# Store in private Git repository
git add team_signing_key.pem team_public_key.pem
git commit -m "Add team XMLDSig signing keys"

# Team members configure
export JUX_SIGNING_KEY=./team_signing_key.pem
export JUX_SIGN=true
```

**Provenance Claim**: "This test report was signed by our team's key"
**Trust Model**: Direct distribution via Git repository
**Strength**: ⚠️ Medium
- Trust basis: Git repository access control
- Assumes repository is secure
- Team knows key location and access policy

**Recommendations**:
- Store private key in protected Git repository (limited access)
- Use Git LFS or encrypted storage for sensitive keys
- Rotate keys periodically
- Document key ownership and access policy

---

#### Scenario 3: Open Source Project (Public Distribution)

**Option A: GPG Key with Web of Trust**

```bash
# Project maintainer creates GPG key
gpg --full-generate-key
# Name: Acme Test Framework
# Email: maintainers@acme-test.org

# Get key signed by known developers
# Attend conferences, key signing parties
# Publish fingerprint on website, GitHub profile

# Convert to PEM for pytest-jux
gpg --export-secret-key KEY_ID | openpgp2ssh KEY_ID > signing_key.pem

# Configure pytest-jux
export JUX_SIGNING_KEY=./signing_key.pem
export JUX_SIGN=true

# Publish public key
gpg --armor --export KEY_ID > PUBLIC_KEY.asc
# Add to repository README
```

**Provenance Claim**: "This test report was signed by Acme Test Framework maintainers (verified by X, Y, Z developers)"
**Trust Model**: GPG Web of Trust
**Strength**: ✅ Medium to Strong (depends on number of signatures)

**Trust Verification** (by report recipients):
```bash
# Import maintainer's GPG public key
gpg --import PUBLIC_KEY.asc

# Check key signatures
gpg --check-sigs maintainers@acme-test.org
# Look for trusted developers who signed the key

# If trust is established, verify report signature
# (Assuming xmldsig verification tool with GPG-converted key)
```

---

**Option B: Code Signing Certificate (Commercial)**

```bash
# Purchase code signing certificate from DigiCert, Sectigo, etc.
# CA verifies:
# - Organization legal existence
# - Domain ownership (acme-test.org)
# - Authorized representative identity

# Receive certificate and private key
# certificate.pem (public certificate + CA chain)
# private_key.pem (protected private key)

# Configure pytest-jux
export JUX_SIGNING_KEY=./private_key.pem
export JUX_SIGN=true

# Include certificate in XMLDSig signature
# (pytest-jux supports X.509 certificate embedding)
```

**Provenance Claim**: "This test report was signed by Acme Test Framework (verified by DigiCert CA)"
**Trust Model**: Certificate Authority hierarchy
**Strength**: ✅✅ Strong
- CA performed legal verification
- Recipients trust CA (pre-installed root certificates)
- Formal identity binding

**Cost**: $$$ (code signing certificates typically $200-500/year)

---

#### Scenario 4: CI/CD Pipeline Signing

**Challenge**: CI/CD systems need automated signing without human interaction

**Solution: Key Management Service (KMS)**

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests with signing
        env:
          # Private key stored in GitHub Secrets
          JUX_SIGNING_KEY_BASE64: ${{ secrets.PYTEST_JUX_SIGNING_KEY }}
          JUX_SIGN: true
        run: |
          # Decode key from secret
          echo "$JUX_SIGNING_KEY_BASE64" | base64 -d > signing_key.pem
          export JUX_SIGNING_KEY=./signing_key.pem

          # Run tests
          pytest

          # Clean up key
          rm signing_key.pem
```

**Provenance Claim**: "This test report was signed by our CI/CD pipeline"
**Trust Model**: Direct distribution + access control
**Strength**: ⚠️ Medium
- Trust basis: GitHub repository access control
- Secret management by CI/CD platform
- Audit trail of who modified secrets

**Recommendations**:
- Use dedicated CI/CD signing key (not personal key)
- Rotate keys quarterly
- Monitor secret access logs
- Use hardware security modules (HSM) for high-security needs

---

## Recommendations by Use Case

| Use Case | Recommended Approach | Provenance Strength | Complexity | Cost |
|----------|---------------------|---------------------|------------|------|
| **Personal development** | Raw OpenSSL key | N/A (self-trust) | Low | Free |
| **Internal team (2-5 people)** | Shared key in private Git | Medium | Low | Free |
| **Internal team (6-50 people)** | Shared key + access control policy | Medium | Medium | Free |
| **Open source project** | GPG key with Web of Trust | Medium-Strong | Medium | Free |
| **Commercial product** | Code signing certificate (OV) | Strong | Medium | $$ |
| **Financial/Legal software** | Code signing certificate (EV) | Very Strong | High | $$$ |
| **CI/CD automation** | Dedicated key in secrets manager | Medium | Medium | $ (KMS costs) |

---

## Best Practices

### For All Scenarios

1. **Key Protection**
   - Store private keys securely (encrypted, access-controlled)
   - Never commit private keys to public repositories
   - Use strong passphrases for key encryption

2. **Key Rotation**
   - Rotate signing keys periodically (annually for low-risk, quarterly for high-risk)
   - Maintain old public keys for historical verification
   - Document rotation schedule

3. **Documentation**
   - Document key ownership and access policy
   - Publish public keys in multiple channels (website, README, key servers)
   - Provide verification instructions

4. **Revocation**
   - Plan for key compromise scenarios
   - GPG: Generate and publish revocation certificate
   - X.509: Contact CA for revocation
   - Document revocation procedures

### For pytest-jux Specifically

1. **Configuration Management**
   - Store `JUX_SIGNING_KEY` path in team documentation
   - Use environment variables (not hardcoded paths)
   - Provide clear setup instructions in README

2. **Verification**
   - Include public key in repository (if shared team key)
   - Document how recipients verify signatures
   - Provide example verification scripts

3. **Metadata**
   - Include signer identity in test metadata
   - Document which key was used for which reports
   - Maintain audit trail of signed reports

---

## Conclusion

**Can we prove provenance with OpenSSL or GPG keys?**

**Answer**: **Yes, but provenance strength depends on the trust model, not the signature algorithm.**

| Component | What It Provides |
|-----------|------------------|
| **Digital Signature (Cryptography)** | ✅ Integrity, Authentication, Non-repudiation |
| **Identity Binding (Trust Model)** | ✅ Provenance (WHO signed it) |
| **Both Together** | ✅ Complete provenance story |

**For pytest-jux**:

- **Internal team use**: Direct key distribution (medium provenance)
- **Open source use**: GPG Web of Trust (medium-strong provenance)
- **Commercial use**: Code signing certificate (strong provenance)

The choice of trust model should match your security requirements and audience.

---

## References

### Academic Sources

- **"A Practical Guide to Cryptography"**: [Applied Cryptography by Bruce Schneier](https://www.schneier.com/books/applied-cryptography/)
- **Digital Signature Standard (DSS)**: [FIPS PUB 186-5](https://csrc.nist.gov/publications/detail/fips/186/5/final)

### Standards

- **GPG/OpenPGP**: [RFC 4880 - OpenPGP Message Format](https://datatracker.ietf.org/doc/html/rfc4880)
- **X.509 Certificates**: [RFC 5280 - Internet X.509 PKI Certificate](https://datatracker.ietf.org/doc/html/rfc5280)
- **XML Digital Signatures**: [W3C XML-DSig Core](https://www.w3.org/TR/xmldsig-core/)

### Practical Guides

- **GPG Handbook**: [The GNU Privacy Handbook](https://www.gnupg.org/gph/en/manual.html)
- **OpenSSL Cookbook**: [OpenSSL Documentation](https://www.openssl.org/docs/)
- **CA/Browser Forum**: [Certificate Authority Standards](https://cabforum.org/)

### pytest-jux Documentation

- [Research: XMLDSig and GPG Compatibility](./xmldsig-gpg-compatibility.md)
- [How-To: Sign Test Reports](../howto/sign-test-reports.md)
- [Security: Digital Signatures](../security/digital-signatures.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Maintained By**: pytest-jux contributors
