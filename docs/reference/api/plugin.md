# plugin API Reference

**Module**: `pytest_jux.plugin`
**Purpose**: pytest plugin hooks and integration
**Version**: 0.1.9+

---

## Overview

The `plugin` module implements pytest hooks for seamless integration with pytest test execution. It automatically signs JUnit XML reports, captures metadata, and stores reports locally.

### Purpose

- **pytest Integration**: Hook-based integration with pytest lifecycle
- **Automatic Signing**: Sign test reports automatically after test runs
- **Metadata Capture**: Capture environment metadata during test execution
- **Local Storage**: Store signed reports in XDG-compliant locations
- **Configuration**: pytest.ini and CLI argument support

### When to Use This Module

- Running pytest with automatic report signing
- Integrating pytest-jux into CI/CD pipelines
- Configuring pytest-jux via pytest.ini
- Programmatically triggering plugin functionality

### Related Modules

- **`signer`**: Signs reports (called by plugin hooks)
- **`metadata`**: Captures metadata (called by plugin hooks)
- **`storage`**: Stores reports (called by plugin hooks)
- **`config`**: Provides configuration (loaded by plugin)

---

## Module Documentation

```{eval-rst}
.. automodule:: pytest_jux.plugin
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## pytest Hooks

### `pytest_addoption()`

Add pytest-jux command-line options.

```{eval-rst}
.. autofunction:: pytest_jux.plugin.pytest_addoption
```

**Added Options**:
- `--jux-key` - Path to private key for signing
- `--jux-cert` - Path to X.509 certificate
- `--jux-environment` - Environment name (production, staging, development)
- `--jux-storage-mode` - Storage mode (auto, disabled)
- `--jux-no-sign` - Skip signing (disable plugin)

---

### `pytest_configure()`

Configure pytest-jux plugin on startup.

```{eval-rst}
.. autofunction:: pytest_jux.plugin.pytest_configure
```

**Actions**:
1. Load configuration from CLI, env, and config files
2. Validate signing key and certificate paths
3. Initialize storage manager
4. Register plugin with pytest

---

### `pytest_terminal_summary()`

Sign and store test reports after test execution.

```{eval-rst}
.. autofunction:: pytest_jux.plugin.pytest_terminal_summary
```

**Actions**:
1. Locate JUnit XML report (from `--junitxml` option)
2. Sign report with XMLDSig signature
3. Capture environment metadata
4. Store signed report locally
5. Display summary to user

---

## Usage Examples

### Basic Usage

```bash
# Run pytest with automatic signing
pytest \
  --junitxml=test-results/junit.xml \
  --jux-key ~/.ssh/jux/key.pem \
  --jux-cert ~/.ssh/jux/cert.pem
```

**Output**:
```
======================== test session starts =========================
...
======================== 10 passed in 2.34s ==========================

pytest-jux: Report signed and stored
  Hash: abc123def456...
  Signed report: /Users/alice/.local/share/pytest-jux/reports/abc123...xml
```

---

### pytest.ini Configuration

```ini
# pytest.ini

[pytest]
# JUnit XML report
junit_family = xunit2
addopts = --junitxml=test-results/junit.xml

# pytest-jux configuration
jux_key_path = ~/.ssh/jux/jux-signing-key.pem
jux_cert_path = ~/.ssh/jux/jux-signing-key.crt
jux_environment = production
jux_storage_mode = auto
```

**Usage**:
```bash
# Configuration loaded from pytest.ini
pytest
```

---

### Environment Variables

```bash
# Set configuration via environment variables
export JUX_KEY_PATH=~/.ssh/jux/key.pem
export JUX_CERT_PATH=~/.ssh/jux/cert.pem
export JUX_ENVIRONMENT=staging

# Run pytest
pytest --junitxml=junit.xml
```

---

### Disabling Plugin

```bash
# Skip signing (don't use plugin)
pytest --junitxml=junit.xml --jux-no-sign

# Or disable via environment
export JUX_NO_SIGN=1
pytest --junitxml=junit.xml
```

---

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/test.yml

name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Generate signing key
        run: |
          jux-keygen \
            --type rsa \
            --bits 4096 \
            --output ~/.ssh/jux/key.pem \
            --cert \
            --subject "CN=GitHub Actions CI"

      - name: Run tests with signing
        run: |
          pytest \
            --junitxml=test-results/junit.xml \
            --jux-key ~/.ssh/jux/key.pem \
            --jux-cert ~/.ssh/jux/key.crt \
            --jux-environment ci

      - name: Upload signed report
        uses: actions/upload-artifact@v4
        with:
          name: signed-test-report
          path: ~/.local/share/pytest-jux/reports/*.xml
```

#### GitLab CI

```yaml
# .gitlab-ci.yml

test:
  stage: test
  image: python:3.11

  before_script:
    - pip install -e ".[dev]"
    - jux-keygen --type rsa --bits 4096 --output key.pem --cert

  script:
    - |
      pytest \
        --junitxml=junit.xml \
        --jux-key key.pem \
        --jux-cert key.crt \
        --jux-environment ci

  artifacts:
    reports:
      junit: junit.xml
    paths:
      - ~/.local/share/pytest-jux/reports/
```

---

## Plugin Lifecycle

### 1. Plugin Registration

pytest discovers pytest-jux via entry point:

```python
# pyproject.toml

[project.entry-points.pytest11]
jux_publisher = "pytest_jux.plugin"
```

### 2. Configuration Phase

`pytest_configure()` hook is called:

```
pytest startup
  ↓
pytest_configure()
  ↓
Load configuration (CLI + env + files)
  ↓
Validate signing key/cert
  ↓
Initialize storage
  ↓
Register plugin
```

### 3. Test Execution

Tests run normally (plugin does not interfere).

### 4. Report Signing Phase

`pytest_terminal_summary()` hook is called after tests complete:

```
Tests complete
  ↓
pytest_terminal_summary()
  ↓
Locate JUnit XML report (--junitxml path)
  ↓
Load XML
  ↓
Sign with XMLDSig (signer module)
  ↓
Capture metadata (metadata module)
  ↓
Store locally (storage module)
  ↓
Display summary
```

---

## Configuration Options

### Command-Line Options

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `--jux-key` | `Path` | Private key path | `--jux-key ~/.ssh/jux/key.pem` |
| `--jux-cert` | `Path` | Certificate path | `--jux-cert ~/.ssh/jux/cert.pem` |
| `--jux-environment` | `str` | Environment name | `--jux-environment production` |
| `--jux-storage-mode` | `str` | Storage mode | `--jux-storage-mode auto` |
| `--jux-no-sign` | `bool` | Disable signing | `--jux-no-sign` |

### pytest.ini Options

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `jux_key_path` | `Path` | Private key path | `jux_key_path = ~/.ssh/jux/key.pem` |
| `jux_cert_path` | `Path` | Certificate path | `jux_cert_path = ~/.ssh/jux/cert.pem` |
| `jux_environment` | `str` | Environment name | `jux_environment = production` |
| `jux_storage_mode` | `str` | Storage mode | `jux_storage_mode = auto` |
| `jux_no_sign` | `bool` | Disable signing | `jux_no_sign = false` |

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No JUnit XML report found` | Missing `--junitxml` option | Add `--junitxml=path/to/junit.xml` |
| `Private key not found` | Invalid key path | Check `--jux-key` path |
| `Certificate not found` | Invalid cert path | Check `--jux-cert` path |
| `Permission denied` | Cannot write to storage | Check storage directory permissions |
| `Invalid signature algorithm` | Unsupported key type | Use RSA or ECDSA keys |

### Example Error Output

```bash
$ pytest --junitxml=junit.xml --jux-key /nonexistent/key.pem

======================== test session starts =========================
...
======================== 10 passed in 2.34s ==========================

pytest-jux: Error signing report
  Error: Private key not found: /nonexistent/key.pem
```

---

## Programmatic Usage

### Triggering Plugin Manually

```python
from pathlib import Path
from pytest_jux.plugin import sign_and_store_report
from pytest_jux.config import JuxConfig

# Configure
config = JuxConfig(
    private_key_path=Path("~/.ssh/jux/key.pem").expanduser(),
    certificate_path=Path("~/.ssh/jux/cert.pem").expanduser(),
    environment="production",
    storage_mode="auto"
)

# Sign and store report
report_path = Path("test-results/junit.xml")
report_hash = sign_and_store_report(report_path, config)

print(f"Report stored: {report_hash}")
```

---

## Plugin Configuration Precedence

Configuration sources (highest to lowest priority):

1. **CLI arguments**: `--jux-key`, `--jux-cert`, etc.
2. **Environment variables**: `JUX_KEY_PATH`, `JUX_CERT_PATH`, etc.
3. **pytest.ini**: `jux_key_path`, `jux_cert_path`, etc.
4. **Config files**: `~/.config/pytest-jux/config.toml`
5. **Default values**

---

## Debugging

### Verbose Output

```bash
# Enable pytest verbose output
pytest -v --junitxml=junit.xml --jux-key key.pem --jux-cert cert.pem

# Enable pytest-jux debug logging
export JUX_DEBUG=1
pytest --junitxml=junit.xml --jux-key key.pem --jux-cert cert.pem
```

### Checking Plugin Status

```bash
# List active pytest plugins
pytest --version --version

# Should show:
# pytest 8.0.0
# setuptools registered plugins:
#   pytest-jux-0.1.9 at /path/to/pytest_jux/plugin.py
```

---

## Performance Impact

The plugin has minimal performance impact:

| Phase | Time Added | Notes |
|-------|------------|-------|
| Configuration | <5ms | One-time startup cost |
| Test execution | 0ms | No impact during tests |
| Report signing | 10-50ms | After tests complete |
| Metadata capture | 5-20ms | Parallel with signing |
| Storage | 5-10ms | Parallel with signing |

**Total overhead**: ~20-80ms (after test execution completes)

---

## Security Considerations

### Private Key Security

**Warning**: Private keys must be protected:

1. **Never commit keys** to version control
2. **Restrict permissions**: `chmod 600 key.pem`
3. **Use environment variables** or secure vaults in CI/CD
4. **Rotate keys regularly** (recommended: every 90 days)

### CI/CD Key Management

**Best Practices**:
- Generate ephemeral keys for CI builds
- Store long-term keys in secret vaults (GitHub Secrets, GitLab CI Variables)
- Use different keys for different environments

**Example** (GitHub Actions):
```yaml
- name: Generate ephemeral signing key
  run: |
    jux-keygen \
      --type rsa \
      --bits 4096 \
      --output ~/.ssh/jux/ci-key.pem \
      --cert \
      --subject "CN=GitHub Actions CI"

- name: Run tests
  run: |
    pytest \
      --junitxml=junit.xml \
      --jux-key ~/.ssh/jux/ci-key.pem \
      --jux-cert ~/.ssh/jux/ci-key.crt
```

---

## See Also

- **[signer API](signer.md)**: XMLDSig signing (used by plugin)
- **[metadata API](metadata.md)**: Metadata capture (used by plugin)
- **[storage API](storage.md)**: Local storage (used by plugin)
- **[config API](config.md)**: Configuration management (used by plugin)
- **[CI/CD Deployment How-To](../../howto/ci-cd-deployment.md)**: Guide for CI/CD integration

---

**Module Path**: `pytest_jux.plugin`
**Source Code**: `pytest_jux/plugin.py`
**Tests**: `tests/test_plugin.py`
**Last Updated**: 2025-10-20
