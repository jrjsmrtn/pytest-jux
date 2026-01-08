# CLI Reference

Complete command-line reference for all pytest-jux CLI tools.

## Available Commands

pytest-jux provides 8 CLI commands for offline signing, verification, publishing, and management:

```{toctree}
:maxdepth: 2

keygen
sign
verify
inspect
cache
config
publish
```

## Command Overview

### jux-keygen

Generate RSA or ECDSA key pairs for XMLDSig signing.

**Purpose**: Create signing keys for test report signing

**Algorithms**: RSA (2048/4096-bit), ECDSA (P-256/P-384)

**Output**: PEM-encoded private/public key files

---

### jux-sign

Sign JUnit XML reports offline with XMLDSig signatures.

**Purpose**: Add cryptographic signatures to test reports

**Features**: Enveloped signatures, canonical hashing, metadata embedding

**Algorithms**: RSA-SHA256, ECDSA-SHA256

---

### jux-verify

Verify XMLDSig signatures on signed test reports.

**Purpose**: Validate report authenticity and detect tampering

**Checks**: Signature validity, certificate chain, timestamp

**Output**: Verification status (valid/invalid), signature metadata

---

### jux-inspect

Inspect signed test report metadata and signatures.

**Purpose**: Extract and display report information without verification

**Output**: XML structure, signature details, metadata, test results

**Format**: JSON or human-readable text

---

### jux-cache

Manage local report cache (stats, cleanup, purge).

**Purpose**: Maintain XDG-compliant cache storage

**Operations**: Show stats, list cached reports, cleanup old reports, purge all

**Storage**: `~/.cache/pytest-jux/`

---

### jux-config

Manage pytest-jux configuration (show, edit, validate).

**Purpose**: Configure signing keys, API endpoints, environments

**Operations**: Show current config, edit config file, validate settings

**Storage**: `~/.config/pytest-jux/config.toml`

---

### jux-publish

Publish signed test reports to Jux API server.

**Purpose**: Manual publishing of cached or single reports to Jux API

**Modes**: Single file (`--file`), queue processing (`--queue`)

**Features**: Dry-run mode, JSON output, retry with backoff

**Exit Codes**: 0 (success), 1 (all failed), 2 (partial success)

---

## Auto-Generated CLI Documentation

The sections below are auto-generated from the command-line parsers using sphinx-argparse-cli.

### jux-keygen

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.keygen
   :func: create_parser
   :prog: jux-keygen
   :title:
```

### jux-sign

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.sign
   :func: create_parser
   :prog: jux-sign
   :title:
```

### jux-verify

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.verify
   :func: create_parser
   :prog: jux-verify
   :title:
```

### jux-inspect

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.inspect
   :func: create_parser
   :prog: jux-inspect
   :title:
```

### jux-cache

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.cache
   :func: create_parser
   :prog: jux-cache
   :title:
```

### jux-config

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.config_cmd
   :func: create_parser
   :prog: jux-config
   :title:
```

### jux-publish

```{eval-rst}
.. sphinx_argparse_cli::
   :module: pytest_jux.commands.publish
   :func: create_parser
   :prog: jux-publish
   :title:
```

## Examples

### Generate RSA Key Pair

```bash
# Generate 4096-bit RSA key pair
jux-keygen --algorithm rsa --key-size 4096 --output-dir ~/.ssh/jux

# Output:
# Private key: ~/.ssh/jux/jux-signing-key.pem
# Public key: ~/.ssh/jux/jux-signing-key.pub
```

### Sign Test Report

```bash
# Sign report with RSA private key
jux-sign \
  --input test-results/junit.xml \
  --output test-results/junit-signed.xml \
  --private-key ~/.ssh/jux/jux-signing-key.pem

# Output: test-results/junit-signed.xml (with XMLDSig signature)
```

### Verify Signature

```bash
# Verify signed report
jux-verify --input test-results/junit-signed.xml

# Output:
# ✓ Signature valid
# Algorithm: RSA-SHA256
# Signed: 2025-10-20T10:30:45Z
```

### Inspect Report

```bash
# Inspect signed report (JSON output)
jux-inspect --input test-results/junit-signed.xml --format json

# Output: JSON with test results, signature, metadata
```

### Cache Management

```bash
# Show cache statistics
jux-cache stats

# List cached reports
jux-cache list

# Cleanup reports older than 30 days
jux-cache cleanup --days 30

# Purge all cached reports
jux-cache purge --force
```

### Configuration

```bash
# Show current configuration
jux-config show

# Edit configuration file
jux-config edit

# Validate configuration
jux-config validate
```

### Publishing

```bash
# Publish single signed report to Jux API
jux-publish --file test-results/junit-signed.xml --api-url https://jux.example.com/api/v1

# Publish all queued reports
jux-publish --queue --api-url https://jux.example.com/api/v1

# Dry-run (preview without publishing)
jux-publish --queue --api-url https://jux.example.com/api/v1 --dry-run

# Publish with authentication
export JUX_BEARER_TOKEN=your-token
jux-publish --queue --api-url https://jux.example.com/api/v1

# JSON output for scripting
jux-publish --queue --api-url https://jux.example.com/api/v1 --json
```

## Exit Codes

All commands use standard exit codes:

- **0**: Success
- **1**: General error (invalid arguments, file not found)
- **2**: Verification failed (invalid signature, tampered report)
- **3**: Configuration error (invalid config file, missing keys)
