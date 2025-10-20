# API Reference

Complete API reference for all pytest-jux modules.

## Core Modules

```{toctree}
:maxdepth: 2

canonicalizer
signer
verifier
storage
config
metadata
plugin
```

## Module Overview

### canonicalizer

XML canonicalization (C14N) and canonical hashing for duplicate detection.

**Key Functions**:
- `load_xml()` - Load XML from file, string, or bytes
- `canonicalize_xml()` - Canonicalize XML using C14N algorithm
- `compute_canonical_hash()` - Compute SHA-256 hash of canonical XML

**Use Cases**: Duplicate detection, content verification, signature preparation

---

### signer

XMLDSig digital signature generation and verification.

**Key Functions**:
- `load_private_key()` - Load RSA/ECDSA private key from file
- `sign_xml()` - Sign XML with XMLDSig enveloped signature
- `verify_signature()` - Verify XMLDSig signature

**Algorithms**: RSA-SHA256, ECDSA-SHA256

---

### verifier

Signature verification and tamper detection.

**Key Functions**:
- `verify_xml_signature()` - Verify XMLDSig signatures
- `extract_signature_info()` - Extract signature metadata

**Validations**: Certificate chain, signature algorithm, timestamp validity

---

### storage

XDG-compliant local storage and caching.

**Key Classes**:
- `ReportStorage` - Store and retrieve signed reports
- `CacheManager` - Cache management (stats, cleanup, purge)

**Storage Locations**:
- Reports: `~/.local/share/pytest-jux/reports/`
- Cache: `~/.cache/pytest-jux/`
- Config: `~/.config/pytest-jux/`

---

### config

Configuration management (CLI, environment, files).

**Key Classes**:
- `JuxConfig` - Main configuration (Pydantic model)
- `ConfigManager` - Load/merge configurations from multiple sources

**Sources**: Command-line arguments, environment variables (`JUX_*`), config files

---

### metadata

Environment metadata capture.

**Key Classes**:
- `EnvironmentMetadata` - System, Python, pytest metadata
- `MetadataCollector` - Collect metadata from current environment

**Metadata**: OS, Python version, pytest version, dependencies, git commit

---

### plugin

pytest hook integration.

**Hooks**:
- `pytest_configure()` - Plugin initialization
- `pytest_terminal_summary()` - Report signing and publishing

**Entry Point**: `pytest11` plugin discovery

---

## Auto-Generated API Documentation

```{eval-rst}
.. autosummary::
   :toctree: _autosummary
   :recursive:

   pytest_jux.canonicalizer
   pytest_jux.signer
   pytest_jux.verifier
   pytest_jux.storage
   pytest_jux.config
   pytest_jux.metadata
   pytest_jux.plugin
```
