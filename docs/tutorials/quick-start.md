# Quick Start Guide

_Get started with pytest-jux in 10 minutes_

**Audience:** Infrastructure Engineers, Integrators, Developers
**Prerequisites:** Python 3.11+, pytest installed in your project
**Time:** ~10 minutes

## What You'll Learn

By the end of this tutorial, you will:
- Install pytest-jux in your project
- Generate cryptographic signing keys
- Configure pytest-jux for local storage
- Run tests and produce signed XML reports
- Inspect and verify your signed reports

## What is pytest-jux?

pytest-jux is a pytest plugin that:
1. **Signs** your JUnit XML test reports with cryptographic signatures
2. **Stores** reports locally (or publishes to an API server)
3. **Provides** CLI tools for key management and report inspection

This creates a **chain-of-trust** for your test results, ensuring they haven't been tampered with.

## Step 1: Install pytest-jux

In your project's virtual environment:

```bash
# Using uv (recommended)
uv pip install pytest-jux

# Or using pip
pip install pytest-jux
```

Verify installation:

```bash
pytest --version
# Should show pytest-jux in the list of installed plugins
```

## Step 2: Generate Signing Keys

Generate a private key for signing your test reports:

```bash
# Generate RSA key (recommended for most use cases)
jux-keygen --output ~/.jux/signing_key.pem --type rsa --bits 2048

# Generate with self-signed certificate (optional)
jux-keygen --output ~/.jux/signing_key.pem --type rsa --bits 2048 --cert
```

**Output:**
```
✓ Generated RSA private key (2048 bits)
✓ Key saved: /Users/you/.jux/signing_key.pem
✓ File permissions set to 0600 (read/write for owner only)
✓ Certificate saved: /Users/you/.jux/signing_key.crt
⚠ Self-signed certificate - NOT suitable for production use
```

**Important:** Keep your private key secure! It's like a password for your test reports.

## Step 3: Configure pytest-jux

Create a configuration file in your project:

```bash
jux-config init --path .jux.conf --template minimal
```

Edit `.jux.conf`:

```ini
[jux]
# Enable pytest-jux plugin
enabled = true

# Enable report signing
sign = true

# Path to signing key
key_path = ~/.jux/signing_key.pem

# Storage mode: local (no API server needed)
storage_mode = local
```

**Alternatively**, add to your `pytest.ini`:

```ini
[pytest]
# Your existing pytest config...
junit_family = xunit2

[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = local
```

## Step 4: Run Tests

Run your existing pytest tests with JUnit XML output:

```bash
pytest --junit-xml=report.xml
```

**What happens:**
1. pytest runs your tests as normal
2. JUnit XML report is generated
3. pytest-jux automatically signs the report
4. Signed report is stored locally in `~/.local/share/jux/reports/` (macOS/Linux)
5. Original `report.xml` contains the signature

**Expected output:**
```
======================== test session starts =========================
collected 10 items

tests/test_example.py::test_one PASSED                         [ 10%]
tests/test_example.py::test_two PASSED                         [ 20%]
...

======================== 10 passed in 0.50s ==========================
generated xml file: /path/to/report.xml
pytest-jux: Report signed and stored (sha256:abc123...)
```

## Step 5: Inspect Your Signed Report

View report details:

```bash
jux-inspect report.xml
```

**Output:**
```
JUnit XML Report Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Results:
  Tests:     10
  Failures:  0
  Errors:    0
  Skipped:   0

Report Details:
  Canonical Hash: sha256:abc123def456...
  Signature:      ✓ Present (XMLDSig)
  Test Suites:    1
```

Verify the signature:

```bash
jux-verify report.xml --cert ~/.jux/signing_key.crt
```

**Output:**
```
✓ Signature is VALID
  Algorithm: RSA-SHA256
  Certificate: CN=pytest-jux
```

## Step 6: View Cached Reports

List all cached reports:

```bash
jux-cache list
```

**Output:**
```
Cached Reports (1 total):

  sha256:abc123def456...
    Timestamp: 2025-10-17T14:30:00Z
    Hostname:  dev-laptop
    Username:  developer

```

View cache statistics:

```bash
jux-cache stats
```

**Output:**
```
Cache Statistics:

  Total Reports:  1
  Queued Reports: 0
  Total Size:     2.5 KB
  Oldest Report:  2025-10-17 14:30:00
```

## What You've Accomplished

You now have:
- ✅ pytest-jux installed and configured
- ✅ Cryptographic signing keys generated
- ✅ Signed test reports from your test suite
- ✅ Local storage with cached reports
- ✅ Verification capability for report integrity

## Next Steps

### Learn More

- **[Understanding pytest-jux](../explanation/understanding-pytest-jux.md)** - Why XML signatures matter
- **[Choosing Storage Modes](../howto/choosing-storage-modes.md)** - When to use local/api/both/cache
- **[Setting Up Signing Keys](setting-up-signing-keys.md)** - Production key management

### Common Tasks

- **Configure for CI/CD:** See [CI/CD Deployment Guide](../howto/ci-cd-deployment.md)
- **Multiple Environments:** See [Multi-Environment Configuration](../howto/multi-environment-config.md)
- **Troubleshooting:** See [Troubleshooting Guide](../howto/troubleshooting.md)

### Advanced Features

- **API Publishing:** When your Jux API Server is available, change `storage_mode = api` or `storage_mode = both`
- **Offline Queue:** Use `storage_mode = cache` for unreliable network connections
- **Certificate Management:** Generate production certificates with proper CA signing

## Troubleshooting

### Plugin Not Running

**Problem:** pytest-jux doesn't seem to do anything.

**Solution:** Check that `enabled = true` in your config file.

```bash
# Verify current configuration
jux-config dump
```

### Signature Verification Fails

**Problem:** `jux-verify` reports invalid signature.

**Solution:** Ensure you're using the matching certificate:

```bash
# The certificate must match the private key used for signing
jux-verify report.xml --cert ~/.jux/signing_key.crt
```

### Permission Denied

**Problem:** Cannot write to storage directory.

**Solution:** Check storage path permissions:

```bash
# View storage location
jux-config dump | grep storage_path

# Create directory if needed
mkdir -p ~/.local/share/jux/reports
chmod 700 ~/.local/share/jux
```

## Getting Help

- **Documentation:** [docs/](../../)
- **Issues:** [GitHub Issues](https://github.com/jux-tools/pytest-jux/issues)
- **Security:** [Security Policy](../../security/SECURITY.md)

---

**Next Tutorial:** [Setting Up Signing Keys](setting-up-signing-keys.md) - Production key management and certificate authorities
