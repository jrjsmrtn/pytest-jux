# Research Documentation

**Purpose**: In-depth technical research on XML digital signatures, cryptographic provenance, and pytest-jux signing implementation.

**Audience**: Contributors, security researchers, and developers seeking deep technical understanding of pytest-jux signing capabilities.

---

## Research Documents

### 1. [XMLDSig and GPG Compatibility](./xmldsig-gpg-compatibility.md)

**Summary**: Comprehensive analysis of compatibility between GPG (OpenPGP) and XML Digital Signatures (XMLDSig).

**Key Topics**:
- Standards comparison (IETF RFC 4880 vs W3C XMLDSig)
- Technical incompatibilities (format, canonicalization, key info)
- Cryptographic algorithm compatibility
- Key conversion workflows (GPG → PEM)
- Use case recommendations

**Key Findings**:
- GPG and XMLDSig are fundamentally incompatible standards
- Underlying cryptographic algorithms (RSA, ECDSA) are compatible
- Key conversion possible but complex (requires monkeysphere tools)
- **Recommendation**: Use native OpenSSL keys for XMLDSig, not converted GPG keys

**Target Readers**: Developers familiar with GPG who want to understand XMLDSig differences and conversion options.

---

### 2. [Digital Signature Provenance and Trust Models](./digital-signature-provenance.md)

**Summary**: Analysis of how digital signatures prove provenance (WHO signed) versus integrity (WHAT was signed).

**Key Topics**:
- Cryptographic guarantees (integrity, authentication, non-repudiation)
- The identity problem (key ownership vs signature validity)
- Trust models comparison:
  - Direct key distribution
  - GPG Web of Trust (decentralized)
  - Certificate Authorities (hierarchical)
- Provenance strength analysis by scenario
- pytest-jux application examples

**Key Findings**:
- Digital signatures alone don't prove identity—trust infrastructure required
- Provenance strength varies: Weak (raw keys) → Medium (Web of Trust) → Strong (CA certificates)
- For internal teams: Shared keys via secure channels provide medium provenance
- For public/commercial use: GPG Web of Trust or CA certificates provide strong provenance

**Target Readers**: Security-conscious developers and teams implementing test report signing for compliance or audit requirements.

---

### 3. [pytest-jux Signing Implementation](./pytest-jux-signing-implementation.md)

**Summary**: Detailed analysis of current pytest-jux XMLDSig signing implementation, configuration, and usage patterns.

**Key Topics**:
- Architecture overview (signer.py, signxml library, lxml integration)
- Implementation details (load_private_key, sign_xml, verify_signature)
- Configuration management (environment variables)
- Signed XML output structure
- Usage workflows (team keys, CI/CD, GPG conversion)
- Verification methods
- Security considerations
- Performance benchmarks

**Key Findings**:
- pytest-jux uses `signxml` library for W3C XMLDSig compliance
- Supports RSA-SHA256 and ECDSA-SHA256 algorithms
- Enveloped signatures (embedded in XML document)
- Configuration via `JUX_SIGN` and `JUX_SIGNING_KEY` environment variables
- Signing overhead <100ms (negligible for typical test suites)
- Optional X.509 certificate embedding for identity binding

**Target Readers**: pytest-jux contributors, users implementing signing workflows, developers debugging signing issues.

---

## Quick Navigation

### By Topic

**Understanding XMLDSig**:
- [XMLDSig vs GPG](./xmldsig-gpg-compatibility.md#standards-comparison)
- [XML Canonicalization](./xmldsig-gpg-compatibility.md#2-canonicalization-requirement)
- [Signature Structure](./pytest-jux-signing-implementation.md#signed-xml-output)

**Cryptographic Provenance**:
- [What Signatures Prove](./digital-signature-provenance.md#what-digital-signatures-prove)
- [Trust Models](./digital-signature-provenance.md#trust-models-comparison)
- [Provenance Strength](./digital-signature-provenance.md#provenance-strength-analysis)

**pytest-jux Usage**:
- [Configuration](./pytest-jux-signing-implementation.md#configuration)
- [Basic Signing Workflow](./pytest-jux-signing-implementation.md#workflow-1-basic-signing-team-key)
- [CI/CD Integration](./pytest-jux-signing-implementation.md#workflow-2-cicd-signing-github-actions)
- [GPG Key Conversion](./pytest-jux-signing-implementation.md#workflow-3-gpg-key-conversion-advanced)

### By Audience

**For New Users**:
1. Start with [pytest-jux Implementation Overview](./pytest-jux-signing-implementation.md#architecture-overview)
2. Read [Basic Signing Workflow](./pytest-jux-signing-implementation.md#workflow-1-basic-signing-team-key)
3. Understand [Provenance Basics](./digital-signature-provenance.md#what-digital-signatures-prove)

**For Security Professionals**:
1. Review [Digital Signature Provenance](./digital-signature-provenance.md)
2. Examine [Trust Models Comparison](./digital-signature-provenance.md#trust-models-comparison)
3. Assess [Provenance Strength](./digital-signature-provenance.md#provenance-strength-analysis)

**For GPG Users**:
1. Understand [GPG vs XMLDSig Incompatibility](./xmldsig-gpg-compatibility.md#technical-incompatibilities)
2. Review [Key Conversion Options](./xmldsig-gpg-compatibility.md#key-conversion-workflows)
3. Consider [Recommendation: Separate Keys](./xmldsig-gpg-compatibility.md#recommendations)

**For Contributors**:
1. Study [Implementation Architecture](./pytest-jux-signing-implementation.md#architecture-overview)
2. Review [Core Signing Module](./pytest-jux-signing-implementation.md#implementation-details)
3. Check [Future Enhancements](./pytest-jux-signing-implementation.md#future-enhancements)

---

## Research Methodology

### Data Sources

**Standards Documents**:
- [W3C XML Signature Syntax and Processing Version 2.0](https://www.w3.org/TR/xmldsig-core2/)
- [IETF RFC 4880: OpenPGP Message Format](https://datatracker.ietf.org/doc/html/rfc4880)
- [NIST FIPS 186-5: Digital Signature Standard](https://csrc.nist.gov/publications/detail/fips/186/5/final)

**Web Research**:
- GPG/OpenPGP documentation and tutorials
- XML security best practices
- Digital signature verification workflows
- Trust model comparisons

**Code Analysis**:
- pytest-jux source code (`pytest_jux/signer.py`, `pytest_jux/config.py`)
- signxml library implementation
- lxml and cryptography library APIs

### Validation

All research findings were validated through:
- Code inspection of pytest-jux implementation
- Standards document verification
- Practical testing with GPG and OpenSSL tools
- Performance benchmarks on real test suites

---

## Related Documentation

### pytest-jux User Documentation (Diátaxis Framework)

**Tutorials** (Learning-oriented):
- [Getting Started with Signing](../tutorials/getting-started-signing.md) *(Coming soon)*

**How-To Guides** (Task-oriented):
- [How to Sign Test Reports](../howto/sign-test-reports.md)
- [How to Configure CI/CD Signing](../howto/cicd-signing-setup.md) *(Coming soon)*
- [How to Verify Signatures](../howto/verify-signatures.md) *(Coming soon)*

**Reference** (Information-oriented):
- [Configuration Reference](../reference/configuration.md#signing-options)
- [API Reference: Signer Module](../reference/api/signer.md) *(Coming soon)*

**Explanation** (Understanding-oriented):
- [Why XMLDSig for JUnit XML?](../explanation/why-xmldsig.md) *(Coming soon)*
- [Security Model](../security/digital-signatures.md)

---

## Contributing

### Updating Research Documents

1. **Verify Changes**: Research updates require verification from standards documents or tested implementations
2. **Cite Sources**: Include references to authoritative sources
3. **Practical Examples**: Provide working code examples and command-line demonstrations
4. **Version Updates**: Update "Last Updated" date and increment document version

### Requesting New Research

File an issue with the "research" label describing:
- Topic area (cryptography, standards, implementation)
- Specific questions to be answered
- Use case or motivation

---

## Maintenance

**Document Versions**: All research documents follow semantic versioning (1.0, 1.1, 2.0, etc.)

**Update Schedule**:
- **Quarterly Review**: Check for outdated information, broken links, deprecated approaches
- **Standards Changes**: Update immediately when W3C/IETF standards are revised
- **Implementation Changes**: Update when pytest-jux signing implementation changes

**Last Full Review**: 2025-10-27

---

## Summary Table

| Document | Purpose | Audience | Complexity |
|----------|---------|----------|------------|
| **XMLDSig-GPG Compatibility** | Compare standards, explain incompatibility | GPG users transitioning to XMLDSig | Medium |
| **Digital Signature Provenance** | Explain trust models and provenance strength | Security professionals, compliance teams | Medium-High |
| **pytest-jux Implementation** | Document current implementation details | Contributors, advanced users | High |

---

## Questions or Feedback

For questions about this research:
- **General questions**: Use [pytest-jux Discussions](https://github.com/jux-tools/pytest-jux/discussions)
- **Technical corrections**: File an issue with "documentation" label
- **Research requests**: File an issue with "research" label

---

**Research Collection Version**: 1.0
**Last Updated**: 2025-10-27
**Maintained By**: pytest-jux contributors
