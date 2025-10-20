# Configuration Reference

**Complete reference for pytest-jux configuration options**

---

## Overview

pytest-jux supports configuration from multiple sources with a well-defined precedence order. This document provides a complete reference of all configuration options, their types, defaults, and usage.

### Configuration Sources

Configuration is loaded from multiple sources in the following precedence order (highest to lowest):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`JUX_*` prefix)
3. **Configuration files** (TOML format)
4. **pytest.ini** (pytest configuration)
5. **Default values** (lowest priority)

---

## Quick Reference Table

| Option | Type | Default | CLI | Env Var | Config File | pytest.ini |
|--------|------|---------|-----|---------|-------------|------------|
| `environment` | `str` | `"production"` | `--jux-environment` | `JUX_ENVIRONMENT` | `environment` | `jux_environment` |
| `storage_mode` | `str` | `"auto"` | `--jux-storage-mode` | `JUX_STORAGE_MODE` | `storage_mode` | `jux_storage_mode` |
| `private_key_path` | `Path` | `None` | `--jux-key` | `JUX_KEY_PATH` | `private_key_path` | `jux_key_path` |
| `certificate_path` | `Path` | `None` | `--jux-cert` | `JUX_CERT_PATH` | `certificate_path` | `jux_cert_path` |
| `config_file` | `Path` | `None` | `--jux-config` | `JUX_CONFIG_FILE` | N/A | `jux_config_file` |
| `no_sign` | `bool` | `False` | `--jux-no-sign` | `JUX_NO_SIGN` | `no_sign` | `jux_no_sign` |

---

## Configuration Options

### `environment`

**Description**: Environment name for multi-environment configurations.

**Type**: `str`

**Default**: `"production"`

**Valid Values**: Any string (common: `"production"`, `"staging"`, `"development"`, `"ci"`)

**Usage**:
```bash
# CLI
pytest --jux-environment staging

# Environment variable
export JUX_ENVIRONMENT=staging

# Config file (config.toml)
[jux]
environment = "staging"

# pytest.ini
[pytest]
jux_environment = staging
```

**Example**:
```python
from pytest_jux.config import JuxConfig

config = JuxConfig(environment="staging")
assert config.environment == "staging"
```

---

### `storage_mode`

**Description**: Local storage mode for signed reports.

**Type**: `str`

**Default**: `"auto"`

**Valid Values**:
- `"auto"` - Automatic storage with duplicate detection
- `"disabled"` - Disable local storage (reports not cached)

**Usage**:
```bash
# CLI
pytest --jux-storage-mode disabled

# Environment variable
export JUX_STORAGE_MODE=disabled

# Config file (config.toml)
[jux]
storage_mode = "disabled"

# pytest.ini
[pytest]
jux_storage_mode = disabled
```

**When to Use**:
- **`auto`**: Local development, testing, persistent storage needed
- **`disabled`**: CI/CD pipelines where reports are published immediately

---

### `private_key_path`

**Description**: Path to private key file for XMLDSig signing (PEM format).

**Type**: `Path`

**Default**: `None` (required for signing)

**Supported Key Types**:
- RSA (2048, 3072, 4096 bits)
- ECDSA (P-256, P-384, P-521 curves)

**Usage**:
```bash
# CLI
pytest --jux-key ~/.ssh/jux/signing-key.pem

# Environment variable
export JUX_KEY_PATH=~/.ssh/jux/signing-key.pem

# Config file (config.toml)
[jux.signing]
private_key_path = "~/.ssh/jux/signing-key.pem"

# pytest.ini
[pytest]
jux_key_path = ~/.ssh/jux/signing-key.pem
```

**File Permissions**: Should be `600` (owner read/write only)

**Generation**:
```bash
# Generate RSA key
jux-keygen --type rsa --bits 4096 --output ~/.ssh/jux/key.pem

# Generate ECDSA key
jux-keygen --type ecdsa --curve P-256 --output ~/.ssh/jux/key.pem
```

---

### `certificate_path`

**Description**: Path to X.509 certificate file (PEM format, optional).

**Type**: `Path`

**Default**: `None` (optional)

**Usage**:
```bash
# CLI
pytest --jux-cert ~/.ssh/jux/signing-cert.pem

# Environment variable
export JUX_CERT_PATH=~/.ssh/jux/signing-cert.pem

# Config file (config.toml)
[jux.signing]
certificate_path = "~/.ssh/jux/signing-cert.pem"

# pytest.ini
[pytest]
jux_cert_path = ~/.ssh/jux/signing-cert.pem
```

**Purpose**: Include certificate in XMLDSig signature for verification

**Generation**:
```bash
# Generate self-signed certificate with key
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output ~/.ssh/jux/key.pem \
  --cert \
  --subject "CN=My Organization"
```

---

### `config_file`

**Description**: Path to custom configuration file (TOML format).

**Type**: `Path`

**Default**: `None` (searches default locations if not specified)

**Default Search Locations** (XDG Base Directory compliant):
1. `$XDG_CONFIG_HOME/jux/config` (default: `~/.config/jux/config`)
2. Project directory: `.jux.conf`
3. Project directory: `pytest.ini` (in `[jux]` section)

**Usage**:
```bash
# CLI
pytest --jux-config /etc/jux/production.toml

# Environment variable
export JUX_CONFIG_FILE=/etc/jux/production.toml

# pytest.ini
[pytest]
jux_config_file = /etc/jux/production.toml
```

---

### `no_sign`

**Description**: Disable signing (skip pytest-jux plugin execution).

**Type**: `bool`

**Default**: `False`

**Usage**:
```bash
# CLI
pytest --jux-no-sign

# Environment variable
export JUX_NO_SIGN=1

# Config file (config.toml)
[jux]
no_sign = true

# pytest.ini
[pytest]
jux_no_sign = true
```

**When to Use**: Disable signing for specific test runs without removing configuration

---

## Configuration Files

### TOML Format

pytest-jux uses TOML configuration files for persistent configuration.

**Example** (`~/.config/pytest-jux/config.toml`):
```toml
# pytest-jux configuration

[jux]
environment = "production"
storage_mode = "auto"
no_sign = false

[jux.signing]
private_key_path = "~/.ssh/jux/jux-signing-key.pem"
certificate_path = "~/.ssh/jux/jux-signing-key.crt"
```

### Multi-Environment Configuration

**Example** (multi-environment `config.toml`):
```toml
# Default environment
[jux]
environment = "production"

# Production environment
[jux.environments.production]
private_key_path = "~/.ssh/jux/prod-key.pem"
certificate_path = "~/.ssh/jux/prod-cert.pem"
storage_mode = "auto"

# Staging environment
[jux.environments.staging]
private_key_path = "~/.ssh/jux/staging-key.pem"
certificate_path = "~/.ssh/jux/staging-cert.pem"
storage_mode = "auto"

# Development environment
[jux.environments.development]
private_key_path = "~/.ssh/jux/dev-key.pem"
certificate_path = "~/.ssh/jux/dev-cert.pem"
storage_mode = "disabled"  # Don't cache in dev

# CI environment
[jux.environments.ci]
private_key_path = "/tmp/ci-key.pem"
certificate_path = "/tmp/ci-cert.pem"
storage_mode = "disabled"  # Don't cache in CI
```

**Usage**:
```bash
# Switch environments
pytest --jux-environment production
pytest --jux-environment staging
pytest --jux-environment development
```

---

## pytest.ini Configuration

pytest-jux options can be configured in `pytest.ini` for pytest integration.

**Example** (`pytest.ini`):
```ini
[pytest]
# JUnit XML configuration
junit_family = xunit2
addopts = --junitxml=test-results/junit.xml

# pytest-jux configuration
jux_environment = production
jux_storage_mode = auto
jux_key_path = ~/.ssh/jux/jux-signing-key.pem
jux_cert_path = ~/.ssh/jux/jux-signing-key.crt
```

**Benefits**:
- Configuration committed to repository
- Consistent settings across team
- pytest integration

**Note**: Sensitive values (keys, certificates) should use environment variables, not committed files.

---

## Environment Variables

All configuration options support environment variables with `JUX_` prefix.

### Environment Variable Reference

| Variable | Option | Type | Example |
|----------|--------|------|---------|
| `JUX_ENVIRONMENT` | `environment` | `str` | `export JUX_ENVIRONMENT=staging` |
| `JUX_STORAGE_MODE` | `storage_mode` | `str` | `export JUX_STORAGE_MODE=disabled` |
| `JUX_KEY_PATH` | `private_key_path` | `Path` | `export JUX_KEY_PATH=~/.ssh/jux/key.pem` |
| `JUX_CERT_PATH` | `certificate_path` | `Path` | `export JUX_CERT_PATH=~/.ssh/jux/cert.pem` |
| `JUX_CONFIG_FILE` | `config_file` | `Path` | `export JUX_CONFIG_FILE=/etc/jux/config.toml` |
| `JUX_NO_SIGN` | `no_sign` | `bool` | `export JUX_NO_SIGN=1` |

### CI/CD Environment Variables

**GitHub Actions**:
```yaml
env:
  JUX_ENVIRONMENT: ci
  JUX_KEY_PATH: /tmp/ci-key.pem
  JUX_CERT_PATH: /tmp/ci-cert.pem
  JUX_STORAGE_MODE: disabled
```

**GitLab CI**:
```yaml
variables:
  JUX_ENVIRONMENT: ci
  JUX_KEY_PATH: /tmp/ci-key.pem
  JUX_CERT_PATH: /tmp/ci-cert.pem
  JUX_STORAGE_MODE: disabled
```

---

## Configuration Precedence

Configuration sources are merged with the following precedence (highest to lowest):

1. **CLI arguments** (highest)
2. **Environment variables**
3. **Configuration files**
4. **pytest.ini**
5. **Default values** (lowest)

### Precedence Example

Given:
```toml
# config.toml
[jux]
environment = "production"
```

```bash
# Environment variable
export JUX_ENVIRONMENT=staging
```

```bash
# CLI argument
pytest --jux-environment development
```

**Result**: `environment = "development"` (CLI wins)

---

## Validation Rules

Configuration is validated using Pydantic models.

### Validation Errors

| Field | Validation | Error |
|-------|------------|-------|
| `storage_mode` | Must be `"auto"` or `"disabled"` | `ValidationError: storage_mode must be 'auto' or 'disabled'` |
| `private_key_path` | Must be valid Path (if provided) | `ValidationError: Invalid path` |
| `certificate_path` | Must be valid Path (if provided) | `ValidationError: Invalid path` |
| `environment` | Must be string | `ValidationError: environment must be string` |

### File Existence Checks

**Note**: Configuration validates path *types* but does NOT check file existence during loading. File existence is checked when signing operations are performed.

---

## Complete Configuration Examples

### Example 1: Local Development

**pytest.ini**:
```ini
[pytest]
jux_environment = development
jux_key_path = ~/.ssh/jux/dev-key.pem
jux_cert_path = ~/.ssh/jux/dev-cert.pem
jux_storage_mode = auto
```

**Command**:
```bash
pytest --junitxml=junit.xml
```

---

### Example 2: CI/CD Pipeline

**No configuration files** (ephemeral environment).

**Command**:
```bash
# Generate ephemeral key
jux-keygen --type rsa --bits 4096 --output /tmp/ci-key.pem --cert

# Run tests with signing
pytest \
  --junitxml=junit.xml \
  --jux-environment ci \
  --jux-key /tmp/ci-key.pem \
  --jux-cert /tmp/ci-key.crt \
  --jux-storage-mode disabled
```

---

### Example 3: Multi-Environment Production

**config.toml**:
```toml
[jux]
environment = "production"

[jux.environments.production]
private_key_path = "/secure/keys/prod-key.pem"
certificate_path = "/secure/keys/prod-cert.pem"
storage_mode = "auto"

[jux.environments.staging]
private_key_path = "/secure/keys/staging-key.pem"
certificate_path = "/secure/keys/staging-cert.pem"
storage_mode = "auto"
```

**Command**:
```bash
# Production
pytest --junitxml=junit.xml --jux-environment production

# Staging
pytest --junitxml=junit.xml --jux-environment staging
```

---

### Example 4: Disable Signing for Specific Run

**Preserve configuration but skip signing**:

```bash
# Temporary disable
pytest --junitxml=junit.xml --jux-no-sign
```

---

## Configuration Management

### View Current Configuration

```bash
# Show current configuration
jux-config show

# Show as JSON
jux-config show --json
```

**Output**:
```
Current Configuration:
  Environment:       production
  Storage Mode:      auto
  Private Key Path:  /Users/alice/.ssh/jux/key.pem
  Certificate Path:  /Users/alice/.ssh/jux/cert.pem
  Config File:       /Users/alice/.config/pytest-jux/config.toml
```

### Edit Configuration

```bash
# Edit configuration file
jux-config edit
```

Opens configuration file in `$EDITOR` (default: vim).

### Validate Configuration

```bash
# Validate configuration
jux-config validate
```

**Output**:
```
✓ Configuration is valid

Validation Results:
  Environment:       production (valid)
  Storage Mode:      auto (valid)
  Private Key Path:  /Users/alice/.ssh/jux/key.pem (exists)
  Certificate Path:  /Users/alice/.ssh/jux/cert.pem (exists)
```

---

## Security Considerations

### Sensitive Configuration

**DO NOT** commit sensitive configuration to version control:
- ❌ Private keys
- ❌ Certificates (if not public)
- ❌ API tokens (future)

### Best Practices

1. **Use environment variables** for sensitive values in CI/CD
2. **Store config files outside repository** (use `~/.config/pytest-jux/`)
3. **Restrict file permissions**:
   ```bash
   chmod 600 ~/.ssh/jux/key.pem
   chmod 644 ~/.config/pytest-jux/config.toml
   ```
4. **Use `.gitignore`**:
   ```gitignore
   # Exclude sensitive configuration
   config.toml
   *.pem
   *.key
   *.crt
   .env
   ```

---

## Troubleshooting

### Common Configuration Issues

**Issue**: `Private key not found`
```bash
pytest --junitxml=junit.xml --jux-key /nonexistent/key.pem
# Error: Private key not found: /nonexistent/key.pem
```
**Solution**: Check key path, verify file exists

---

**Issue**: `Invalid storage mode`
```bash
pytest --jux-storage-mode invalid
# Error: storage_mode must be 'auto' or 'disabled'
```
**Solution**: Use valid storage mode (`auto` or `disabled`)

---

**Issue**: `Configuration file not found`
```bash
pytest --jux-config /nonexistent/config.toml
# Error: Configuration file not found
```
**Solution**: Check config file path, verify file exists

---

**Issue**: `Conflicting configuration sources`
```bash
# pytest.ini has: jux_environment = production
# But CLI specifies: --jux-environment staging
# Which wins?
```
**Solution**: CLI wins (highest precedence). See [Configuration Precedence](#configuration-precedence)

---

## See Also

- **[config API Reference](api/config.md)**: Configuration API documentation
- **[jux-config CLI Reference](cli/index.md#jux-config)**: Configuration management command
- **[Multi-Environment Configuration Guide](../howto/multi-environment-config.md)**: How-to guide for multi-environment setup
- **[CI/CD Deployment Guide](../howto/ci-cd-deployment.md)**: How-to guide for CI/CD integration

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
