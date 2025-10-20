# Architecture Explanation

**Understanding pytest-jux design decisions and architectural patterns**

---

## Overview

This document explains the architectural design of pytest-jux, covering:
- Why specific design patterns were chosen
- How components interact
- Trade-offs in architectural decisions
- Design principles guiding development

For step-by-step usage, see [Tutorials](../tutorials/first-signed-report.md). For API details, see [API Reference](../reference/api/index.md).

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    pytest Test Runner                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │              pytest Plugin Ecosystem                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │ │
│  │  │ pytest-cov   │  │ pytest-xdist │  │  Other   │ │ │
│  │  └──────────────┘  └──────────────┘  │ Plugins  │ │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │          pytest-jux Plugin                    │ │ │
│  │  │  ┌────────────┐  ┌──────────────────────────┐│ │ │
│  │  │  │ pytest     │  │ CLI Commands:            ││ │ │
│  │  │  │ Hooks      │  │ • jux-keygen             ││ │ │
│  │  │  │            │  │ • jux-sign               ││ │ │
│  │  │  └────────────┘  │ • jux-verify             ││ │ │
│  │  │                  │ • jux-inspect            ││ │ │
│  │  │                  │ • jux-cache              ││ │ │
│  │  │                  │ • jux-config             ││ │ │
│  │  │                  └──────────────────────────┘│ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │   JUnit XML Report (unsigned) │
          └───────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │    XML Canonicalization       │
          │    (C14N Exclusive)           │
          └───────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │    XMLDSig Signature          │
          │    (RSA-SHA256/ECDSA-SHA256)  │
          └───────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │   Signed JUnit XML Report     │
          └───────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │   Local Storage (XDG Cache)   │
          │   + Metadata (JSON)           │
          └───────────────────────────────┘
```

---

## Design Principles

### 1. **Client-Side Only**

**Decision**: pytest-jux is a client-side plugin with no server dependencies.

**Rationale**:
- ✅ **Simplicity**: No server setup required for basic usage
- ✅ **Privacy**: Reports stored locally by default
- ✅ **Offline operation**: Works without network access
- ✅ **Gradual adoption**: Use signing without changing infrastructure

**Trade-off**: Future API integration requires separate server component (Jux API Server).

### 2. **Plugin Architecture**

**Decision**: Implemented as a pytest plugin using hook system.

**Rationale**:
- ✅ **Tight integration**: Automatic signing during test runs
- ✅ **No code changes**: Works with existing pytest tests
- ✅ **Composability**: Works alongside other pytest plugins
- ✅ **Standard interface**: Follows pytest plugin conventions

**Alternative Considered**: Standalone tool requiring manual invocation
- ❌ **Rejected**: Too much friction, easy to forget signing step

### 3. **XMLDSig Standard**

**Decision**: Use W3C XMLDSig standard for digital signatures.

**Rationale**:
- ✅ **Industry standard**: Well-established, widely supported
- ✅ **Interoperability**: Compatible with XML security tools
- ✅ **Embedded signatures**: Signature travels with document
- ✅ **Mature libraries**: signxml, lxml provide robust implementation

**Alternative Considered**: JWT/JWS signatures
- ❌ **Rejected**: Requires base64 encoding of XML (breaks readability)

### 4. **Canonical Hashing**

**Decision**: Use C14N (Canonical XML) + SHA-256 for duplicate detection.

**Rationale**:
- ✅ **Semantic equivalence**: Detects duplicates despite formatting differences
- ✅ **Deterministic**: Same content always produces same hash
- ✅ **Standard algorithm**: C14N Exclusive is W3C recommendation
- ✅ **Collision resistance**: SHA-256 provides 256-bit security

**Why Not Simple Hash?**:
```xml
<!-- These are semantically identical but have different byte-level hashes -->
<test name="example" status="passed"/>
<test status="passed" name="example"/>

<!-- C14N normalizes to canonical form before hashing -->
```

### 5. **XDG Base Directory Specification**

**Decision**: Follow XDG Base Directory Specification for storage.

**Rationale**:
- ✅ **Standard compliance**: Follows Linux/macOS conventions
- ✅ **User expectations**: Files in predictable locations
- ✅ **Separation of concerns**: Data/config/cache in separate directories
- ✅ **Clean home directory**: Avoids cluttering `~/`

**Storage Locations**:
```
~/.local/share/pytest-jux/   # XDG_DATA_HOME (reports, metadata)
~/.config/pytest-jux/         # XDG_CONFIG_HOME (config.toml)
~/.cache/pytest-jux/          # XDG_CACHE_HOME (temporary files)
```

---

## Component Architecture

### Core Components

#### 1. **Canonicalizer** (`canonicalizer.py`)

**Purpose**: Normalize XML to canonical form for consistent hashing.

**Key Functions**:
- `canonicalize_xml()`: Transform XML to C14N Exclusive form
- `compute_canonical_hash()`: Generate SHA-256 hash of canonical XML

**Design**:
```python
# Canonical XML ensures deterministic hashing
xml_bytes = canonicalize_xml(tree)
canonical_hash = hashlib.sha256(xml_bytes).hexdigest()
```

**Why C14N Exclusive?**:
- Namespace prefixes normalized
- Attribute order standardized
- Whitespace normalized
- Comments removed

#### 2. **Signer** (`signer.py`)

**Purpose**: Apply XMLDSig signatures to JUnit XML reports.

**Key Functions**:
- `load_private_key()`: Load RSA/ECDSA private keys
- `sign_xml()`: Create enveloped XMLDSig signature

**Design**:
```python
# Enveloped signature (inside XML document)
<testsuites>
  <testsuite ...>
    <!-- Test results -->
  </testsuite>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>...</SignedInfo>
    <SignatureValue>...</SignatureValue>
    <KeyInfo>...</KeyInfo>
  </Signature>
</testsuites>
```

**Why Enveloped?**:
- ✅ Self-contained: Signature embedded in document
- ✅ No separate files: Single file for distribution
- ✅ Standard pattern: Common in SAML, SOAP, XML documents

#### 3. **Verifier** (`verifier.py`)

**Purpose**: Verify XMLDSig signatures and report authenticity.

**Key Functions**:
- `load_certificate()`: Load X.509 certificates
- `verify_signature()`: Validate XMLDSig signature

**Verification Steps**:
1. Extract signature from XML
2. Verify certificate (if provided)
3. Validate signature cryptographically
4. Check signature covers entire document

#### 4. **Storage** (`storage.py`)

**Purpose**: Local caching and duplicate detection.

**Key Functions**:
- `store_report()`: Save signed report to cache
- `get_report()`: Retrieve report by canonical hash
- `list_reports()`: Enumerate cached reports

**Design**:
```
~/.local/share/pytest-jux/
├── reports/
│   └── <canonical-hash>.xml      # Signed XML report
├── metadata/
│   └── <canonical-hash>.json     # Report metadata
└── storage.db                     # Index (future)
```

**Why Hash-Based Storage?**:
- ✅ Content-addressable: Hash is unique identifier
- ✅ Duplicate detection: Same content = same hash
- ✅ Deduplication: Only store unique reports

#### 5. **Configuration** (`config.py`)

**Purpose**: Multi-source configuration management.

**Configuration Precedence** (highest to lowest):
1. CLI arguments (`--jux-key`)
2. Environment variables (`JUX_KEY_PATH`)
3. Configuration file (`~/.config/pytest-jux/config.toml`)
4. pytest.ini (`[pytest]` section)
5. Defaults

**Design**:
```python
# Configuration cascade
config = ConfigManager.load()
key_path = (
    cli_args.key_path or          # 1. CLI
    os.getenv('JUX_KEY_PATH') or  # 2. Environment
    config.get('key_path') or     # 3. Config file
    pytest_ini.get('jux_key') or  # 4. pytest.ini
    DEFAULT_KEY_PATH              # 5. Default
)
```

#### 6. **Metadata** (`metadata.py`)

**Purpose**: Capture environment metadata for reproducibility.

**Collected Data**:
- Hostname, username, platform
- Python version, pytest version
- Timestamp (ISO 8601)
- Optional: Git commit, branch, environment variables

**Why Metadata?**:
- ✅ **Reproducibility**: Know exact environment that produced results
- ✅ **Debugging**: Identify environmental differences
- ✅ **Auditing**: Track when/where tests ran

---

## Plugin Lifecycle

### pytest Hook Integration

```python
# Plugin initialization
def pytest_addoption(parser):
    """Add pytest-jux CLI options."""
    parser.addoption('--jux-key', ...)
    parser.addoption('--jux-cert', ...)

def pytest_configure(config):
    """Configure plugin at startup."""
    if config.getoption('--junitxml'):
        # Initialize signer, storage, etc.
        pass

def pytest_sessionfinish(session, exitstatus):
    """Sign report after tests complete."""
    if junit_xml_path:
        # 1. Load JUnit XML report
        # 2. Sign report
        # 3. Store signed report
        pass
```

### Execution Flow

```
pytest startup
    │
    ▼
pytest_addoption() ─────► Add CLI options
    │
    ▼
pytest_configure() ─────► Initialize plugin
    │
    ▼
Test execution ─────────► pytest runs tests
    │
    ▼
pytest writes JUnit XML ► Unsigned report created
    │
    ▼
pytest_sessionfinish() ─► Sign report
    │                      │
    │                      ▼
    │                  Canonicalize XML
    │                      │
    │                      ▼
    │                  Compute hash
    │                      │
    │                      ▼
    │                  Apply signature
    │                      │
    │                      ▼
    │                  Store report
    │
    ▼
pytest exit
```

---

## Security Architecture

### Cryptographic Choices

**Supported Algorithms**:
- **RSA-SHA256**: Industry standard, widely compatible
- **ECDSA-SHA256**: Smaller keys, faster verification

**Why Not Ed25519?**:
- ❌ Limited XMLDSig support
- ❌ Not in W3C XMLDSig standard

**Key Sizes**:
- RSA: 2048/3072/4096 bits (4096 recommended)
- ECDSA: P-256/P-384/P-521 curves (P-256 recommended)

### Threat Model

**Protected Against**:
- ✅ Report tampering (XMLDSig signature)
- ✅ Replay attacks (timestamp in metadata)
- ✅ Duplicate reports (canonical hash)

**Not Protected Against** (by design):
- ⚠️ Key compromise (rotate keys regularly)
- ⚠️ System compromise (secure your systems)
- ⚠️ Social engineering (security awareness)

**Defense in Depth**:
1. Strong cryptography (RSA-4096, ECDSA-P256)
2. Secure key storage (file permissions, secrets managers)
3. Regular key rotation (90-180 days)
4. Access controls (least privilege)
5. Audit logging (key access, report generation)

---

## Scalability and Performance

### Performance Characteristics

**Signing Overhead**:
- Small reports (<10 KB): ~50-100ms
- Medium reports (~100 KB): ~100-200ms
- Large reports (>1 MB): ~200-500ms

**Bottlenecks**:
1. **C14N transformation**: O(n) where n = XML size
2. **Cryptographic signing**: O(1) but constant is large
3. **File I/O**: Disk write speed

**Optimization Strategies**:
- ✅ C14N caching: Cache canonical form for repeated hashing
- ✅ Parallel signing: Sign multiple reports concurrently
- ✅ Fast storage: Use SSD for cache
- ⚠️ Storage disabled mode: Skip caching for performance-critical scenarios

### Scalability Limits

**Single Machine**:
- Tested: 10,000 reports/day (typical CI workload)
- Theoretical: Limited by disk I/O and CPU

**Storage Growth**:
- Average report: ~50-100 KB
- 10,000 reports: ~500 MB - 1 GB
- Mitigation: Automated cache cleanup, archival

---

## Design Trade-offs

### 1. Local Storage vs. Immediate Upload

**Chosen**: Local storage with optional future upload

**Rationale**:
- ✅ Works offline
- ✅ No server dependency
- ✅ Privacy-preserving
- ⚠️ Manual archival required

### 2. pytest Plugin vs. Standalone CLI

**Chosen**: Both (plugin for automation, CLI for manual)

**Rationale**:
- ✅ Plugin: Seamless integration
- ✅ CLI: Flexibility for manual operations
- ⚠️ More code to maintain

### 3. Enveloped vs. Detached Signatures

**Chosen**: Enveloped signatures

**Rationale**:
- ✅ Self-contained
- ✅ Single file distribution
- ⚠️ Slightly larger file size

### 4. C14N vs. Simple Byte Hash

**Chosen**: C14N + SHA-256

**Rationale**:
- ✅ Semantic duplicate detection
- ✅ Format-agnostic
- ⚠️ Slightly slower

---

## Future Architecture Considerations

### Planned: API Server Integration

```
pytest-jux (client) ────► Jux API Server
    │                         │
    │                         ▼
    │                   Verify signature
    │                         │
    │                         ▼
    │                   Store in database
    │                         │
    │                         ▼
    │                   Deduplicate
    │                         │
    │                         ▼
    │                   Web UI / API
```

**Design Considerations**:
- RESTful API for report submission
- Server-side signature verification
- Centralized storage and querying
- Web UI for report browsing

### Planned: Hardware Security Module (HSM) Support

**Use Case**: Enterprise environments requiring hardware key storage

**Integration Points**:
- PKCS#11 interface for HSM access
- Key generation within HSM
- Signing operations delegated to HSM

---

## Lessons Learned

### What Worked Well

1. **pytest Hook System**: Clean integration with existing workflows
2. **XMLDSig Standard**: Mature, well-supported specification
3. **XDG Compliance**: Users find files where expected
4. **Dual Interface**: Plugin + CLI covers all use cases

### What Could Be Improved

1. **Parallel Execution**: pytest-xdist requires `storage_mode=disabled`
   - Future: Per-worker storage or lock-free storage
2. **Large Reports**: Performance degrades with >1 MB reports
   - Future: Streaming C14N, incremental signing
3. **Windows Support**: Limited testing on Windows
   - Future: Enhanced Windows compatibility testing

---

## See Also

- **[Security Explanation](security.md)**: Deep dive into security design
- **[Performance Explanation](performance.md)**: Performance characteristics
- **[API Reference](../reference/api/index.md)**: Component documentation
- **[ADRs](../adr/README.md)**: Architecture Decision Records

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
