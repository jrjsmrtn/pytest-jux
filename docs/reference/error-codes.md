# Error Code Reference

**Complete catalog of pytest-jux error messages, causes, and solutions**

---

## Overview

This reference catalogs all error messages, exceptions, and exit codes in pytest-jux. Use this guide to troubleshoot issues and understand error messages.

### Error Categories

- **[Configuration Errors](#configuration-errors)**: Invalid configuration or missing settings
- **[File Errors](#file-errors)**: File not found, permission denied
- **[Cryptographic Errors](#cryptographic-errors)**: Key/certificate issues, signing failures
- **[Validation Errors](#validation-errors)**: Invalid XML, schema violations
- **[Storage Errors](#storage-errors)**: Storage/caching failures
- **[CLI Errors](#cli-errors)**: Command-line usage errors

---

## Exit Codes

All pytest-jux CLI commands use standard exit codes:

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| `0` | Success | Command completed successfully |
| `1` | General Error | Generic error (file not found, invalid input, etc.) |
| `2` | Verification Failed | Signature verification failed (tampered report) |
| `3` | Configuration Error | Invalid configuration or missing required settings |

---

## Configuration Errors

### CONFIG-001: Private key not found

**Error Message**:
```
Error: Private key not found: /path/to/key.pem
```

**Cause**: The specified private key file does not exist.

**Solution**:
1. Check the path is correct
2. Verify the file exists: `ls -la /path/to/key.pem`
3. Generate a new key if missing: `jux-keygen --type rsa --bits 4096 --output key.pem`

**Command**: All signing commands (`jux-sign`, `pytest --jux-key`, etc.)

**Exit Code**: `1`

---

### CONFIG-002: Certificate not found

**Error Message**:
```
Error: Certificate file not found: /path/to/cert.pem
```

**Cause**: The specified certificate file does not exist.

**Solution**:
1. Check the path is correct
2. Verify the file exists: `ls -la /path/to/cert.pem`
3. Generate a new certificate: `jux-keygen --cert --output key.pem`

**Command**: All signing commands (`jux-sign`, `pytest --jux-cert`, etc.)

**Exit Code**: `1`

---

### CONFIG-003: Invalid storage mode

**Error Message**:
```
ValidationError: storage_mode must be 'auto' or 'disabled'
```

**Cause**: Storage mode set to invalid value.

**Solution**: Use valid storage mode:
```bash
# Valid options
pytest --jux-storage-mode auto
pytest --jux-storage-mode disabled
```

**Command**: `pytest`, `jux-config`

**Exit Code**: `3`

---

### CONFIG-004: Configuration file not found

**Error Message**:
```
Error: Configuration file not found: /path/to/config.toml
```

**Cause**: Specified configuration file does not exist.

**Solution**:
1. Check the path is correct
2. Create configuration file: `jux-config edit`
3. Use default location: `~/.config/pytest-jux/config.toml`

**Command**: `pytest --jux-config`, `jux-config`

**Exit Code**: `1`

---

### CONFIG-005: Invalid TOML syntax

**Error Message**:
```
TOMLDecodeError: Invalid TOML syntax at line X
```

**Cause**: Configuration file has syntax errors.

**Solution**:
1. Validate TOML syntax: https://www.toml-lint.com/
2. Check for common issues:
   - Missing quotes around strings
   - Invalid escape sequences
   - Mismatched brackets
3. Edit configuration: `jux-config edit`

**Command**: All commands reading configuration

**Exit Code**: `3`

---

## File Errors

### FILE-001: Input file not found

**Error Message**:
```
Error: Input file not found: /path/to/junit.xml
```

**Cause**: The specified input XML file does not exist.

**Solution**:
1. Verify the file exists: `ls -la /path/to/junit.xml`
2. Check pytest created the file: `pytest --junitxml=junit.xml`
3. Verify the path is correct

**Command**: `jux-sign`, `jux-verify`, `jux-inspect`

**Exit Code**: `1`

---

### FILE-002: Permission denied (read)

**Error Message**:
```
PermissionError: Permission denied: /path/to/file
```

**Cause**: Insufficient permissions to read file.

**Solution**:
1. Check file permissions: `ls -la /path/to/file`
2. Grant read permission: `chmod 644 /path/to/file`
3. Or run with appropriate user

**Command**: All commands reading files

**Exit Code**: `1`

---

### FILE-003: Permission denied (write)

**Error Message**:
```
PermissionError: Permission denied: /path/to/output
```

**Cause**: Insufficient permissions to write file.

**Solution**:
1. Check directory permissions: `ls -lad /path/to/`
2. Grant write permission: `chmod 755 /path/to/`
3. Or use different output directory

**Command**: All commands writing files

**Exit Code**: `1`

---

### FILE-004: Disk full

**Error Message**:
```
OSError: No space left on device
```

**Cause**: Insufficient disk space.

**Solution**:
1. Check disk space: `df -h`
2. Free up space or use different partition
3. Clean up cache: `jux-cache clean --days 30`

**Command**: All commands writing files

**Exit Code**: `1`

---

## Cryptographic Errors

### CRYPTO-001: Invalid private key format

**Error Message**:
```
ValueError: Invalid private key format
```

**Cause**: Private key file is not valid PEM format or is corrupted.

**Solution**:
1. Verify key format: `openssl rsa -in key.pem -check`
2. Regenerate key: `jux-keygen --type rsa --bits 4096 --output key.pem`
3. Ensure file wasn't corrupted during transfer

**Command**: `jux-sign`, `pytest`

**Exit Code**: `1`

---

### CRYPTO-002: Unsupported key type

**Error Message**:
```
ValueError: Unsupported key type: DSA
```

**Cause**: Key type not supported (only RSA and ECDSA are supported).

**Solution**: Generate supported key type:
```bash
# RSA (recommended)
jux-keygen --type rsa --bits 4096 --output key.pem

# ECDSA
jux-keygen --type ecdsa --curve P-256 --output key.pem
```

**Supported**:
- ✅ RSA (2048, 3072, 4096 bits)
- ✅ ECDSA (P-256, P-384, P-521)
- ❌ DSA
- ❌ Ed25519 (not yet supported)

**Command**: `jux-sign`, `pytest`

**Exit Code**: `1`

---

### CRYPTO-003: Signature verification failed

**Error Message**:
```
ValueError: Signature verification failed
```

**Cause**: XML was modified after signing (tampered) or signature is invalid.

**Solution**:
1. **If expected**: Report is tampered, reject it
2. **If unexpected**:
   - Verify using correct certificate
   - Check XML wasn't modified
   - Re-sign the report

**Command**: `jux-verify`

**Exit Code**: `2` (verification failed)

---

### CRYPTO-004: Certificate expired

**Error Message**:
```
ValueError: Certificate has expired
```

**Cause**: X.509 certificate validity period has ended.

**Solution**:
1. Generate new certificate: `jux-keygen --cert --days-valid 365`
2. Or obtain valid certificate from CA
3. Re-sign reports with new certificate

**Command**: `jux-verify`

**Exit Code**: `2`

---

### CRYPTO-005: Certificate does not match signature

**Error Message**:
```
ValueError: Certificate does not match signature
```

**Cause**: Wrong certificate used for verification (doesn't match private key used for signing).

**Solution**:
1. Use matching certificate (public key corresponding to private key used for signing)
2. Verify certificate fingerprint
3. Check certificate was not replaced

**Command**: `jux-verify`

**Exit Code**: `2`

---

## Validation Errors

### VALID-001: Invalid XML syntax

**Error Message**:
```
XMLSyntaxError: XML syntax error at line X: <error details>
```

**Cause**: Input file is not valid XML.

**Solution**:
1. Validate XML syntax: `xmllint --noout file.xml`
2. Check for common issues:
   - Unclosed tags
   - Invalid characters
   - Encoding issues
3. Regenerate report: `pytest --junitxml=junit.xml`

**Command**: All commands processing XML

**Exit Code**: `1`

---

### VALID-002: Not a JUnit XML file

**Error Message**:
```
ValueError: Not a valid JUnit XML file
```

**Cause**: XML file doesn't match JUnit XML schema.

**Solution**:
1. Verify file is JUnit XML (should have `<testsuite>` or `<testsuites>` root)
2. Check pytest generated the file correctly
3. Validate schema: https://github.com/windyroad/JUnit-Schema

**Command**: All commands expecting JUnit XML

**Exit Code**: `1`

---

### VALID-003: No signature found

**Error Message**:
```
ValueError: No signature found in XML
```

**Cause**: XML file is not signed (no `<Signature>` element).

**Solution**:
1. Sign the report first: `jux-sign -i junit.xml -o signed.xml --key key.pem`
2. Or use signed report for verification

**Command**: `jux-verify`

**Exit Code**: `1`

---

### VALID-004: Malformed signature

**Error Message**:
```
ValueError: Malformed XMLDSig signature
```

**Cause**: Signature element exists but is invalid or corrupted.

**Solution**:
1. Re-sign the report: `jux-sign -i junit.xml -o signed.xml --key key.pem`
2. Verify signature wasn't corrupted during transfer
3. Check XML wasn't manually edited

**Command**: `jux-verify`

**Exit Code**: `2`

---

## Storage Errors

### STORAGE-001: Report not found

**Error Message**:
```
StorageError: Report not found: <hash>
```

**Cause**: Requested report does not exist in storage.

**Solution**:
1. Verify report hash is correct
2. List available reports: `jux-cache list`
3. Check report was stored: Storage may have been purged

**Command**: `jux-cache show`

**Exit Code**: `1`

---

### STORAGE-002: Metadata not found

**Error Message**:
```
StorageError: Metadata not found: <hash>
```

**Cause**: Report exists but metadata file is missing.

**Solution**:
1. Report storage is inconsistent
2. Check metadata file: `~/.local/share/pytest-jux/metadata/<hash>.json`
3. May need to re-generate report

**Command**: `jux-cache show`

**Exit Code**: `1`

---

### STORAGE-003: Storage directory not writable

**Error Message**:
```
PermissionError: Cannot write to storage directory
```

**Cause**: Insufficient permissions for storage directory.

**Solution**:
1. Check directory permissions: `ls -lad ~/.local/share/pytest-jux/`
2. Create directory: `mkdir -p ~/.local/share/pytest-jux/reports`
3. Grant permissions: `chmod 755 ~/.local/share/pytest-jux/`

**Command**: All commands storing reports

**Exit Code**: `1`

---

## CLI Errors

### CLI-001: Missing required argument

**Error Message**:
```
error: the following arguments are required: --key
```

**Cause**: Required command-line argument not provided.

**Solution**: Provide required argument:
```bash
# Example: Missing --key
jux-sign -i junit.xml -o signed.xml --key key.pem
```

**Command**: All CLI commands

**Exit Code**: `2` (usage error)

---

### CLI-002: Invalid argument value

**Error Message**:
```
error: argument --type: invalid choice: 'dsa' (choose from 'rsa', 'ecdsa')
```

**Cause**: Invalid value for argument.

**Solution**: Use valid value:
```bash
# Valid key types
jux-keygen --type rsa --output key.pem
jux-keygen --type ecdsa --output key.pem
```

**Command**: All CLI commands

**Exit Code**: `2` (usage error)

---

### CLI-003: Conflicting arguments

**Error Message**:
```
error: argument --input: not allowed with argument <stdin>
```

**Cause**: Conflicting command-line arguments provided.

**Solution**: Use either file input OR stdin, not both:
```bash
# File input
jux-sign -i junit.xml -o signed.xml --key key.pem

# Stdin input
cat junit.xml | jux-sign -o signed.xml --key key.pem
```

**Command**: Commands accepting stdin

**Exit Code**: `2` (usage error)

---

### CLI-004: No JUnit XML report found

**Error Message**:
```
Error: No JUnit XML report found. Use --junitxml option.
```

**Cause**: pytest-jux plugin activated but no `--junitxml` option specified.

**Solution**: Add `--junitxml` to pytest command:
```bash
pytest --junitxml=test-results/junit.xml
```

Or add to pytest.ini:
```ini
[pytest]
addopts = --junitxml=test-results/junit.xml
```

**Command**: `pytest`

**Exit Code**: `1`

---

## Error Message Patterns

### Pattern: "No such file or directory"

**Common Causes**:
1. File path typo
2. File doesn't exist
3. Relative vs absolute path confusion

**Solution**: Use absolute paths or verify working directory

---

### Pattern: "Permission denied"

**Common Causes**:
1. Insufficient file permissions
2. Insufficient directory permissions
3. File owned by different user

**Solution**: Check permissions with `ls -la`, use `chmod` to fix

---

### Pattern: "Invalid format"

**Common Causes**:
1. Wrong file format (e.g., providing certificate when key expected)
2. Corrupted file
3. Encoding issues

**Solution**: Verify file format, regenerate if corrupted

---

## Debugging Tips

### Enable Debug Logging

```bash
# Enable debug output
export JUX_DEBUG=1
pytest --junitxml=junit.xml --jux-key key.pem
```

### Verbose Output

```bash
# pytest verbose
pytest -v --junitxml=junit.xml

# CLI command verbose (where supported)
jux-verify -i signed.xml --cert cert.pem -v
```

### Validate Configuration

```bash
# Check current configuration
jux-config show

# Validate configuration
jux-config validate
```

### Check File Permissions

```bash
# Check key file permissions
ls -la ~/.ssh/jux/

# Should be 600 for private keys
chmod 600 ~/.ssh/jux/key.pem
```

---

## Getting Help

If you encounter an error not listed here:

1. **Check GitHub Issues**: https://github.com/jux-tools/pytest-jux/issues
2. **Review Documentation**: See [Troubleshooting Guide](../howto/troubleshooting.md)
3. **Report Bug**: Include error message, command, and pytest-jux version

**Collect Debug Information**:
```bash
# pytest-jux version
pytest --version | grep pytest-jux

# Python version
python --version

# Full error output
pytest --junitxml=junit.xml --jux-key key.pem 2>&1 | tee error.log
```

---

## See Also

- **[Configuration Reference](configuration.md)**: Complete configuration documentation
- **[Troubleshooting Guide](../howto/troubleshooting.md)**: How-to guide for troubleshooting
- **[Security Policy](../security/SECURITY.md)**: Security vulnerability reporting

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
