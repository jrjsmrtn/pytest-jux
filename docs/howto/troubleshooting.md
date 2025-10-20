# Troubleshooting Guide

**Diagnose and fix common pytest-jux issues**

---

## Overview

This guide helps you troubleshoot common pytest-jux issues. It covers:

- Signature verification failures
- Configuration problems
- Storage and caching issues
- Performance problems
- Integration issues
- pytest plugin conflicts

For specific error codes and messages, see the **[Error Code Reference](../reference/error-codes.md)**.

---

## Quick Diagnostic Checklist

Before diving into specific issues, try these quick checks:

### 1. Verify Installation

```bash
# Check pytest-jux is installed
pytest --version

# Expected: pytest-jux should appear in plugins list
# pytest 8.0.0
# setuptools registered plugins:
#   pytest-jux-0.1.9 at /path/to/pytest_jux/plugin.py
```

**If not listed**:
```bash
# Reinstall pytest-jux
uv pip install --force-reinstall pytest-jux
```

### 2. Check Configuration

```bash
# Show current configuration
jux-config show

# Validate configuration
jux-config validate
```

### 3. Enable Debug Logging

```bash
# Enable debug output
export JUX_DEBUG=1

# Run pytest with verbose output
pytest -vv --junitxml=junit.xml
```

### 4. Test with Minimal Setup

```bash
# Generate test key
mkdir -p ~/.ssh/jux
jux-keygen --type rsa --bits 4096 --output ~/.ssh/jux/test-key.pem --cert --subject "CN=Test" --days-valid 30

# Run simple test
echo "def test_example(): assert 1 + 1 == 2" > test_minimal.py
pytest test_minimal.py --junitxml=junit.xml --jux-key ~/.ssh/jux/test-key.pem --jux-cert ~/.ssh/jux/test-key.crt

# Expected: Test passes, report signed successfully
```

---

## Signature Verification Failures

### Symptom: "Signature verification failed"

**Error Message**:
```
ValueError: Signature verification failed
```

**Possible Causes**:
1. ✗ Report was modified after signing (tampering)
2. ✗ Wrong certificate used for verification
3. ✗ Corrupted signature
4. ✗ XML encoding issues

### Diagnosis Steps

#### Step 1: Verify Certificate Matches Private Key

```bash
# Extract public key from private key
openssl rsa -in ~/.ssh/jux/key.pem -pubout -out /tmp/pubkey-from-key.pem 2>/dev/null

# Extract public key from certificate
openssl x509 -in ~/.ssh/jux/cert.pem -pubkey -noout -out /tmp/pubkey-from-cert.pem

# Compare (should be identical)
diff /tmp/pubkey-from-key.pem /tmp/pubkey-from-cert.pem

# Expected: No diff (files are identical)
```

**If different**: You're using wrong certificate. Use the certificate generated with the same private key.

#### Step 2: Check Report Was Not Modified

```bash
# Sign a fresh report
pytest --junitxml=test-report.xml --jux-key ~/.ssh/jux/key.pem --jux-cert ~/.ssh/jux/cert.pem

# Find signed report path (from pytest output)
# Example: /Users/you/.local/share/pytest-jux/reports/abc123...xml

# Verify signature immediately
jux-verify -i ~/.local/share/pytest-jux/reports/abc123*.xml --cert ~/.ssh/jux/cert.pem

# Expected: ✓ Signature is valid
```

**If verification fails immediately**: Problem is not modification, likely certificate mismatch or corrupted key.

**If verification succeeds now**: Original report was modified after signing (compare file hashes).

#### Step 3: Check for XML Encoding Issues

```bash
# Inspect XML encoding
head -1 signed-report.xml

# Expected: <?xml version="1.0" encoding="utf-8"?>
```

**If encoding is not UTF-8**: Re-sign with correct encoding:
```bash
jux-sign -i junit.xml -o signed.xml --key ~/.ssh/jux/key.pem --cert ~/.ssh/jux/cert.pem
```

#### Step 4: Validate Signature Structure

```bash
# Check if signature element exists
grep -c '<Signature xmlns' signed-report.xml

# Expected: 1 (exactly one Signature element)
```

**If 0**: Report is not signed.
**If >1**: Report has multiple signatures (invalid).

### Solutions

| Problem | Solution |
|---------|----------|
| Wrong certificate | Use matching certificate: `jux-verify -i report.xml --cert <correct-cert.pem>` |
| Report modified | Re-sign the report: `jux-sign -i junit.xml -o signed.xml --key key.pem` |
| Corrupted signature | Delete and re-sign: `rm signed.xml && jux-sign -i junit.xml -o signed.xml --key key.pem` |
| Encoding issue | Ensure UTF-8: `file -I signed.xml` (should show utf-8) |

---

## Configuration Problems

### Symptom: "Private key not found"

**Error Message**:
```
Error: Private key not found: /path/to/key.pem
```

**Diagnosis**:
```bash
# Check if file exists
ls -la /path/to/key.pem

# Check file permissions
ls -l /path/to/key.pem
# Should be: -rw------- (600)
```

**Solutions**:

1. **File doesn't exist**: Generate new key:
   ```bash
   jux-keygen --type rsa --bits 4096 --output /path/to/key.pem --cert --subject "CN=My Key"
   ```

2. **File exists but not readable**: Fix permissions:
   ```bash
   chmod 600 /path/to/key.pem
   ```

3. **Path is relative**: Use absolute path:
   ```bash
   # Instead of: pytest --jux-key ./key.pem
   # Use: pytest --jux-key /absolute/path/to/key.pem
   ```

### Symptom: "Configuration file not found"

**Error Message**:
```
Error: Configuration file not found: ~/.config/pytest-jux/config.toml
```

**Diagnosis**:
```bash
# Check if config directory exists
ls -lad ~/.config/pytest-jux/

# Check if config file exists
ls -la ~/.config/pytest-jux/config.toml
```

**Solutions**:

1. **Create configuration directory**:
   ```bash
   mkdir -p ~/.config/pytest-jux
   ```

2. **Create minimal configuration**:
   ```bash
   cat > ~/.config/pytest-jux/config.toml << 'EOF'
   [jux]
   environment = "development"

   [jux.environments.development]
   private_key_path = "~/.ssh/jux/dev-key.pem"
   certificate_path = "~/.ssh/jux/dev-cert.pem"
   storage_mode = "auto"
   EOF
   ```

3. **Validate configuration**:
   ```bash
   jux-config validate
   ```

### Symptom: "Invalid TOML syntax"

**Error Message**:
```
TOMLDecodeError: Invalid TOML syntax at line 12
```

**Diagnosis**:
```bash
# Validate TOML syntax online
# Copy config file contents to: https://www.toml-lint.com/

# Check for common issues:
# - Missing quotes around strings
# - Invalid escape sequences
# - Mismatched brackets
```

**Common TOML Mistakes**:

| Problem | Wrong | Correct |
|---------|-------|---------|
| Unquoted Windows paths | `path = C:\keys\key.pem` | `path = "C:\\keys\\key.pem"` |
| Single-quoted multi-line | `str = 'line1\nline2'` | `str = "line1\nline2"` or `str = """line1\nline2"""` |
| Invalid table names | `[jux.env.prod-keys]` | `[jux.env."prod-keys"]` (hyphen needs quotes) |

**Solution**:
```bash
# Edit configuration
jux-config edit

# Validate after editing
jux-config validate
```

---

## Storage and Caching Issues

### Symptom: "Storage directory not writable"

**Error Message**:
```
PermissionError: Cannot write to storage directory: ~/.local/share/pytest-jux
```

**Diagnosis**:
```bash
# Check directory permissions
ls -lad ~/.local/share/pytest-jux/

# Check parent directory permissions
ls -lad ~/.local/share/
```

**Solutions**:

1. **Create storage directory**:
   ```bash
   mkdir -p ~/.local/share/pytest-jux/{reports,metadata}
   chmod 755 ~/.local/share/pytest-jux
   ```

2. **Fix permissions**:
   ```bash
   chmod 755 ~/.local/share/pytest-jux
   chmod 755 ~/.local/share/pytest-jux/reports
   chmod 755 ~/.local/share/pytest-jux/metadata
   ```

3. **Use custom storage path**:
   ```bash
   # In config.toml
   [jux]
   storage_base_path = "/custom/storage/path"
   ```

### Symptom: "Report not found" in cache

**Error Message**:
```
StorageError: Report not found: abc123...
```

**Diagnosis**:
```bash
# List all cached reports
jux-cache list

# Check if storage directory exists
ls -la ~/.local/share/pytest-jux/reports/

# Check available disk space
df -h ~/.local/share/pytest-jux/
```

**Solutions**:

1. **Report was purged**: Re-run tests to regenerate:
   ```bash
   pytest --junitxml=junit.xml --jux-key key.pem --jux-cert cert.pem
   ```

2. **Cache was manually cleared**: Check cache statistics:
   ```bash
   jux-cache stats
   ```

3. **Disk full**: Clean old reports:
   ```bash
   # Remove reports older than 30 days
   jux-cache clean --days 30

   # Or purge all reports (destructive!)
   jux-cache purge
   ```

### Symptom: Disk space running out

**Diagnosis**:
```bash
# Check cache size
jux-cache stats

# Expected output:
# Total reports: 1,234
# Total size: 45.2 MB
# Oldest report: 2025-09-01
# Newest report: 2025-10-20
```

**Solutions**:

1. **Clean old reports**:
   ```bash
   # Remove reports older than 30 days
   jux-cache clean --days 30
   ```

2. **Disable caching** (if not needed):
   ```bash
   # In config.toml
   [jux]
   storage_mode = "disabled"
   ```

3. **Use custom storage path** (different partition):
   ```bash
   # In config.toml
   [jux]
   storage_base_path = "/mnt/large-disk/pytest-jux-cache"
   ```

---

## Performance Problems

### Symptom: pytest runs very slowly

**Diagnosis**:
```bash
# Run pytest with profiling
pytest --junitxml=junit.xml --profile

# Check if signing is the bottleneck
time pytest --junitxml=junit.xml --jux-key key.pem  # With signing
time pytest --junitxml=junit.xml                    # Without signing

# Compare execution times
```

**Expected Overhead**: pytest-jux adds ~50-200ms per test run (depending on report size).

**If overhead is >1 second**:

1. **Large XML reports**: Optimize test collection:
   ```bash
   # Reduce test output verbosity
   pytest --junitxml=junit.xml --jux-key key.pem -q

   # Limit captured output
   pytest --junitxml=junit.xml --jux-key key.pem --capture=no
   ```

2. **Slow I/O**: Use faster storage:
   ```bash
   # Use RAM disk for cache (Linux)
   sudo mount -t tmpfs -o size=512M tmpfs /tmp/pytest-jux-cache

   # Configure pytest-jux to use it
   export JUX_STORAGE_BASE_PATH=/tmp/pytest-jux-cache
   ```

3. **Slow key loading**: Cache keys in environment:
   ```bash
   # Load key once per session (not per test)
   # This is automatic - if slow, key file may be on network drive
   ```

### Symptom: Verification takes too long

**Diagnosis**:
```bash
# Time verification
time jux-verify -i signed-report.xml --cert cert.pem
```

**Expected**: <100ms for reports <1MB

**If >500ms**:

1. **Large report**: Split into smaller files:
   ```bash
   # Use pytest-xdist to split tests across multiple files
   pytest --junitxml-prefix=report -n 4 --jux-key key.pem
   ```

2. **Complex signatures**: Use faster algorithm (ECDSA instead of RSA):
   ```bash
   # Generate ECDSA key (faster verification)
   jux-keygen --type ecdsa --curve P-256 --output ecdsa-key.pem --cert
   ```

---

## Integration Issues

### Symptom: pytest-jux conflicts with other plugins

**Error Message**:
```
PluginValidationError: pytest-jux conflicts with pytest-<other-plugin>
```

**Diagnosis**:
```bash
# List all pytest plugins
pytest --version

# Expected: List of all plugins
# pytest 8.0.0
# setuptools registered plugins:
#   pytest-jux-0.1.9
#   pytest-xdist-3.3.1
#   pytest-cov-4.1.0
#   ... (other plugins)
```

**Common Conflicts**:

| Plugin | Issue | Solution |
|--------|-------|----------|
| pytest-metadata | Duplicate metadata collection | Disable pytest-jux metadata: `--jux-metadata disabled` |
| pytest-html | JUnit XML interference | Use separate output files: `--junitxml=junit.xml --html=report.html` |
| pytest-xdist | Parallel execution issues | Use `--jux-storage-mode disabled` with xdist |

**Solutions**:

1. **Disable conflicting plugin temporarily**:
   ```bash
   pytest -p no:<plugin-name> --junitxml=junit.xml --jux-key key.pem
   ```

2. **Update pytest-jux and other plugins**:
   ```bash
   uv pip install --upgrade pytest-jux pytest-<other-plugin>
   ```

3. **Report incompatibility**: [Open an issue](https://github.com/jrjsmrtn/pytest-jux/issues)

### Symptom: CI/CD integration failing

**Common CI/CD Issues**:

#### GitHub Actions

**Problem**: "Private key not found in CI"

**Solution**: Use ephemeral keys:
```yaml
- name: Generate ephemeral signing key
  run: |
    mkdir -p ~/.ssh/jux
    jux-keygen \
      --type rsa \
      --bits 4096 \
      --output ~/.ssh/jux/ci-key.pem \
      --cert \
      --subject "CN=GitHub Actions CI" \
      --days-valid 1

- name: Run tests with signing
  env:
    JUX_KEY_PATH: ~/.ssh/jux/ci-key.pem
    JUX_CERT_PATH: ~/.ssh/jux/ci-key.crt
  run: pytest --junitxml=junit.xml
```

#### GitLab CI

**Problem**: "Permission denied" on key file

**Solution**: Fix file permissions in CI:
```yaml
before_script:
  - chmod 600 ${CI_PROJECT_DIR}/keys/ci-key.pem
  - chmod 644 ${CI_PROJECT_DIR}/keys/ci-cert.pem

test:
  script:
    - pytest --junitxml=junit.xml --jux-key ${CI_PROJECT_DIR}/keys/ci-key.pem
```

#### Jenkins

**Problem**: "Storage directory not writable"

**Solution**: Use workspace-relative storage:
```groovy
environment {
  JUX_STORAGE_BASE_PATH = "${WORKSPACE}/.pytest-jux-cache"
}

steps {
  sh 'mkdir -p ${JUX_STORAGE_BASE_PATH}'
  sh 'pytest --junitxml=junit.xml --jux-key keys/ci-key.pem'
}
```

---

## Advanced Debugging

### Enable Verbose Logging

```bash
# Maximum verbosity
export JUX_DEBUG=1
export PYTEST_DEBUG=1

pytest -vv -s --junitxml=junit.xml --jux-key key.pem 2>&1 | tee debug.log

# Review debug.log for detailed plugin execution
```

### Inspect Signed XML Structure

```bash
# View signature element
xmllint --xpath '//*[local-name()="Signature"]' signed-report.xml | xmllint --format -

# Expected: Well-formed Signature element with SignedInfo, SignatureValue, KeyInfo
```

### Validate XML Against JUnit Schema

```bash
# Download JUnit XSD schema
curl -O https://raw.githubusercontent.com/windyroad/JUnit-Schema/master/JUnit.xsd

# Validate report (ignore signature elements)
xmllint --noout --schema JUnit.xsd junit.xml

# Expected: junit.xml validates
```

### Test Signing Manually

```bash
# Sign report without pytest
jux-sign -i junit.xml -o signed.xml --key ~/.ssh/jux/key.pem --cert ~/.ssh/jux/cert.pem

# Verify signature
jux-verify -i signed.xml --cert ~/.ssh/jux/cert.pem

# Inspect report
jux-inspect -i signed.xml
```

### Check Certificate Validity

```bash
# View certificate details
openssl x509 -in ~/.ssh/jux/cert.pem -text -noout

# Check expiration
openssl x509 -in ~/.ssh/jux/cert.pem -noout -enddate

# Expected: notAfter=... (future date)
```

**If expired**:
```bash
# Generate new certificate
jux-keygen --type rsa --bits 4096 --output new-key.pem --cert --subject "CN=My New Key" --days-valid 365

# Re-sign reports
jux-sign -i junit.xml -o signed.xml --key new-key.pem --cert new-key.crt
```

---

## Getting Help

### 1. Check Documentation

- **[Error Code Reference](../reference/error-codes.md)**: Specific error messages and solutions
- **[Configuration Reference](../reference/configuration.md)**: All configuration options
- **[API Reference](../reference/api/index.md)**: Programmatic usage
- **[CLI Reference](../reference/cli/index.md)**: Command-line tools

### 2. Search Existing Issues

- **[GitHub Issues](https://github.com/jrjsmrtn/pytest-jux/issues)**: Search for similar problems

### 3. Report a Bug

**Before reporting**, collect diagnostic information:

```bash
# pytest-jux version
pytest --version | grep pytest-jux

# Python version
python --version

# OS information
uname -a  # Linux/macOS
systeminfo | findstr /C:"OS"  # Windows

# Configuration
jux-config show

# Full error output
pytest --junitxml=junit.xml --jux-key key.pem 2>&1 | tee error.log
```

**Submit bug report**: https://github.com/jrjsmrtn/pytest-jux/issues/new

Include:
- pytest-jux version
- Python version
- Operating system
- Full error message (from error.log)
- Configuration (redact sensitive paths/keys)
- Steps to reproduce

---

## Common Error Patterns

### Pattern: "No such file or directory"

**Quick Fix**:
1. Use absolute paths (not relative)
2. Expand `~` in paths: Use `/Users/you/...` not `~/.ssh/...`
3. Check file actually exists: `ls -la <path>`

### Pattern: "Permission denied"

**Quick Fix**:
1. Private key: `chmod 600 <key.pem>`
2. Certificate: `chmod 644 <cert.pem>`
3. Storage directory: `chmod 755 ~/.local/share/pytest-jux`

### Pattern: "Invalid format"

**Quick Fix**:
1. Verify PEM format: `openssl rsa -in key.pem -check`
2. Re-generate key: `jux-keygen --type rsa --bits 4096 --output new-key.pem`
3. Check file encoding: `file -I <file>`

---

## See Also

- **[Error Code Reference](../reference/error-codes.md)**: Complete error catalog
- **[Configuration Reference](../reference/configuration.md)**: Configuration options
- **[CI/CD Deployment Guide](ci-cd-deployment.md)**: CI/CD integration
- **[Multi-Environment Configuration](multi-environment-config.md)**: Environment-specific setup

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
