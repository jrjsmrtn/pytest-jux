# config API Reference

**Module**: `pytest_jux.config`
**Purpose**: Configuration management with multiple sources (CLI, environment, files)
**Version**: 0.1.9+

---

## Overview

The `config` module provides centralized configuration management for pytest-jux. It supports loading configuration from multiple sources with proper precedence, validation using Pydantic, and environment-specific settings.

### Purpose

- **Multi-Source Configuration**: Load from CLI arguments, environment variables, and config files
- **Validation**: Validate configuration using Pydantic models
- **Environment Support**: Production, staging, development configurations
- **XDG Compliance**: Config files in XDG-compliant locations

### When to Use This Module

- Configuring pytest-jux plugin behavior
- Managing signing keys and API endpoints
- Setting up multi-environment configurations
- Programmatically accessing configuration

### Related Modules

- **`plugin`**: Uses config to configure pytest hooks
- **`storage`**: Uses config for storage mode settings
- **`metadata`**: Uses config for metadata collection settings

---

## Module Documentation

```{eval-rst}
.. automodule:: pytest_jux.config
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

---

## Classes

### `JuxConfig`

Main configuration class (Pydantic model).

```{eval-rst}
.. autoclass:: pytest_jux.config.JuxConfig
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

**Example**:
```python
from pathlib import Path
from pytest_jux.config import JuxConfig

# Create configuration
config = JuxConfig(
    private_key_path=Path("~/.ssh/jux/key.pem").expanduser(),
    certificate_path=Path("~/.ssh/jux/cert.pem").expanduser(),
    environment="production",
    storage_mode="auto"
)

print(f"Environment: {config.environment}")
print(f"Key: {config.private_key_path}")
```

---

### `ConfigManager`

Configuration manager for loading from multiple sources.

```{eval-rst}
.. autoclass:: pytest_jux.config.ConfigManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

**Example**:
```python
from pytest_jux.config import ConfigManager

# Load configuration from all sources
manager = ConfigManager()
config = manager.load()

print(f"Environment: {config.environment}")
print(f"Storage mode: {config.storage_mode}")
```

---

## Configuration Sources

Configuration is loaded from multiple sources with the following precedence (highest to lowest):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`JUX_*` prefix)
3. **Config files** (TOML format)
4. **Default values** (lowest priority)

### Configuration Files

Default locations (searched in order):
1. `$XDG_CONFIG_HOME/pytest-jux/config.toml` (default: `~/.config/pytest-jux/config.toml`)
2. `~/.config/jux/config.toml`
3. `/etc/jux/config.toml`

**Example config.toml**:
```toml
# pytest-jux configuration

[jux]
environment = "production"
storage_mode = "auto"

[jux.signing]
private_key_path = "~/.ssh/jux/jux-signing-key.pem"
certificate_path = "~/.ssh/jux/jux-signing-key.crt"

[jux.api]
# API configuration (future)
# base_url = "https://jux.example.com/api"
# timeout = 30
```

---

## Configuration Options

### Core Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `environment` | `str` | `"production"` | Environment name (production, staging, development) |
| `storage_mode` | `str` | `"auto"` | Storage mode (auto, disabled) |
| `private_key_path` | `Path` | `None` | Path to private key for signing |
| `certificate_path` | `Path` | `None` | Path to X.509 certificate |
| `config_file` | `Path` | `None` | Custom config file path |

### Environment Variables

All options can be set via environment variables with `JUX_` prefix:

| Variable | Option | Example |
|----------|--------|---------|
| `JUX_ENVIRONMENT` | `environment` | `export JUX_ENVIRONMENT=staging` |
| `JUX_STORAGE_MODE` | `storage_mode` | `export JUX_STORAGE_MODE=disabled` |
| `JUX_KEY_PATH` | `private_key_path` | `export JUX_KEY_PATH=~/.ssh/jux/key.pem` |
| `JUX_CERT_PATH` | `certificate_path` | `export JUX_CERT_PATH=~/.ssh/jux/cert.pem` |
| `JUX_CONFIG_FILE` | `config_file` | `export JUX_CONFIG_FILE=/etc/jux/prod.toml` |

---

## Usage Examples

### Loading Configuration

```python
from pytest_jux.config import ConfigManager

# Load from all sources (CLI, env, files, defaults)
manager = ConfigManager()
config = manager.load()

print(f"Environment: {config.environment}")
print(f"Storage: {config.storage_mode}")
```

### Creating Configuration Programmatically

```python
from pathlib import Path
from pytest_jux.config import JuxConfig

# Create configuration object
config = JuxConfig(
    environment="staging",
    private_key_path=Path("~/.ssh/jux-staging/key.pem").expanduser(),
    certificate_path=Path("~/.ssh/jux-staging/cert.pem").expanduser(),
    storage_mode="auto"
)

# Use configuration
if config.private_key_path.exists():
    print(f"Key found: {config.private_key_path}")
```

### Environment-Specific Configuration

```python
from pytest_jux.config import ConfigManager
import os

# Set environment via environment variable
os.environ["JUX_ENVIRONMENT"] = "development"

manager = ConfigManager()
config = manager.load()

if config.environment == "development":
    print("Development mode - using test keys")
elif config.environment == "production":
    print("Production mode - using production keys")
```

### Multi-Environment Config File

```toml
# config.toml

[jux]
environment = "production"  # Default environment

[jux.environments.production]
private_key_path = "~/.ssh/jux/prod-key.pem"
certificate_path = "~/.ssh/jux/prod-cert.pem"
storage_mode = "auto"

[jux.environments.staging]
private_key_path = "~/.ssh/jux/staging-key.pem"
certificate_path = "~/.ssh/jux/staging-cert.pem"
storage_mode = "auto"

[jux.environments.development]
private_key_path = "~/.ssh/jux/dev-key.pem"
certificate_path = "~/.ssh/jux/dev-cert.pem"
storage_mode = "disabled"  # Don't cache in dev
```

---

## Validation

Configuration is validated using Pydantic:

### Validation Rules

- **private_key_path**: Must be a valid Path object (if provided)
- **certificate_path**: Must be a valid Path object (if provided)
- **environment**: Must be a string
- **storage_mode**: Must be "auto" or "disabled"

### Validation Errors

```python
from pytest_jux.config import JuxConfig
from pydantic import ValidationError

try:
    config = JuxConfig(
        storage_mode="invalid"  # Invalid value
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # Output: Input should be 'auto' or 'disabled'
```

---

## CLI Integration

The config module is used by the `jux-config` CLI command:

```bash
# Show current configuration
jux-config show

# Show configuration in JSON format
jux-config show --json

# Edit configuration file
jux-config edit

# Validate configuration
jux-config validate

# Use custom config file
jux-config show --config /etc/jux/custom.toml
```

See [jux-config CLI reference](../cli/index.md#jux-config) for details.

---

## Configuration Precedence Example

Given:
- **Config file**: `environment = "production"`
- **Environment variable**: `export JUX_ENVIRONMENT=staging`
- **CLI argument**: `--environment development`

Result:
```python
# CLI wins (highest precedence)
config.environment == "development"
```

---

## Default Configuration

When no configuration is provided:

```python
from pytest_jux.config import JuxConfig

# Default configuration
config = JuxConfig()

assert config.environment == "production"
assert config.storage_mode == "auto"
assert config.private_key_path is None
assert config.certificate_path is None
```

---

## Pytest Integration

Configuration is automatically loaded when pytest-jux plugin is activated:

```bash
# Via pytest command line
pytest --jux-key ~/.ssh/jux/key.pem --jux-cert ~/.ssh/jux/cert.pem

# Via environment variables
export JUX_KEY_PATH=~/.ssh/jux/key.pem
export JUX_CERT_PATH=~/.ssh/jux/cert.pem
pytest

# Via pytest.ini
# [pytest]
# jux_key_path = ~/.ssh/jux/key.pem
# jux_cert_path = ~/.ssh/jux/cert.pem
pytest
```

---

## Security Considerations

### Sensitive Configuration

**DO NOT** commit sensitive configuration to version control:
- ❌ Private keys
- ❌ API tokens
- ❌ Passwords

**Best Practices**:
1. Use environment variables for sensitive values
2. Store config files outside repository
3. Use `.gitignore` to exclude config files
4. Restrict file permissions (`chmod 600 config.toml`)

### Example `.gitignore`

```gitignore
# Exclude sensitive configuration
config.toml
*.pem
*.key
.env
```

---

## Error Handling

### Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Config file not found | Check file path or create config file |
| `ValidationError` | Invalid configuration value | Fix configuration value |
| `PermissionError` | Cannot read config file | Check file permissions |
| `TOMLDecodeError` | Invalid TOML syntax | Fix TOML syntax errors |

**Example**:
```python
from pytest_jux.config import ConfigManager
from pydantic import ValidationError

try:
    manager = ConfigManager(config_file="/nonexistent.toml")
    config = manager.load()
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except ValidationError as e:
    print(f"Invalid configuration: {e}")
```

---

## See Also

- **[jux-config CLI](../cli/index.md#jux-config)**: Configuration management command
- **[Multi-Environment Configuration Guide](../../howto/multi-environment-config.md)**: How-to guide for multi-environment setup
- **[Pydantic Documentation](https://docs.pydantic.dev/)**: Pydantic validation library

---

**Module Path**: `pytest_jux.config`
**Source Code**: `pytest_jux/config.py`
**Tests**: `tests/test_config.py`
**Last Updated**: 2025-10-20
