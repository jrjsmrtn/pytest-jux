# metadata API Reference

**Module**: `pytest_jux.metadata`
**Purpose**: Environment metadata capture and persistence
**Version**: 0.1.9+

---

## Overview

The `metadata` module provides functionality to capture environment metadata (system, Python, pytest, dependencies) and persist it alongside test reports. This enables reproducibility, debugging, and auditing of test results.

### Purpose

- **Environment Capture**: Capture system, Python, pytest metadata
- **Dependency Tracking**: Record installed dependencies and versions
- **Git Integration**: Capture git commit, branch, and dirty state
- **Reproducibility**: Enable test result reproduction
- **Auditing**: Track when, where, and how tests were run

### When to Use This Module

- Capturing environment metadata before signing reports
- Storing metadata alongside test reports
- Debugging test failures (environment differences)
- Auditing test execution history

### Related Modules

- **`storage`**: Persists metadata alongside reports
- **`plugin`**: Uses metadata to enrich test reports
- **`config`**: Configuration affects metadata collection

---

## Module Documentation

```{eval-rst}
.. automodule:: pytest_jux.metadata
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

---

## Classes

### `EnvironmentMetadata`

Environment metadata model (Pydantic).

```{eval-rst}
.. autoclass:: pytest_jux.metadata.EnvironmentMetadata
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

**Example**:
```python
from pytest_jux.metadata import EnvironmentMetadata

# Collect current environment metadata
metadata = EnvironmentMetadata.collect()

print(f"Hostname: {metadata.hostname}")
print(f"Platform: {metadata.platform}")
print(f"Python: {metadata.python_version}")
print(f"pytest: {metadata.pytest_version}")
print(f"Git commit: {metadata.git_commit}")
```

---

### `MetadataCollector`

Metadata collection helper class.

```{eval-rst}
.. autoclass:: pytest_jux.metadata.MetadataCollector
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

---

## Metadata Fields

### System Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `hostname` | `str` | System hostname | `"dev-machine.local"` |
| `username` | `str` | Current user | `"alice"` |
| `platform` | `str` | OS platform | `"Darwin-23.5.0-arm64"` |
| `timestamp` | `str` | Capture time (ISO 8601) | `"2025-10-20T14:30:00Z"` |

### Python Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `python_version` | `str` | Python version | `"3.11.14"` |
| `python_implementation` | `str` | Python impl | `"CPython"` |

### pytest Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pytest_version` | `str` | pytest version | `"8.0.0"` |
| `pytest_plugins` | `list[str]` | Active plugins | `["pytest-cov", "pytest-jux"]` |

### Dependency Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dependencies` | `dict` | Installed packages | `{"lxml": "5.0.0", "signxml": "3.2.0"}` |

### Git Metadata (Optional)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `git_commit` | `str \| None` | Git commit SHA | `"abc123..."` |
| `git_branch` | `str \| None` | Git branch | `"main"` |
| `git_dirty` | `bool \| None` | Uncommitted changes | `False` |

### Custom Environment Variables

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `env` | `dict \| None` | Custom env vars | `{"CI": "true", "BUILD_NUMBER": "123"}` |

---

## Usage Examples

### Collecting Metadata

```python
from pytest_jux.metadata import EnvironmentMetadata

# Collect current environment metadata
metadata = EnvironmentMetadata.collect()

# Access metadata fields
print(f"Running on: {metadata.hostname}")
print(f"Platform: {metadata.platform}")
print(f"Python: {metadata.python_version}")
print(f"pytest: {metadata.pytest_version}")
print(f"Timestamp: {metadata.timestamp}")
```

### Storing Metadata with Reports

```python
from pathlib import Path
from pytest_jux.metadata import EnvironmentMetadata
from pytest_jux.storage import ReportStorage

# Collect metadata
metadata = EnvironmentMetadata.collect()

# Store with report
storage = ReportStorage()
report_xml = Path("junit-signed.xml").read_bytes()

report_hash = storage.store_report(
    report_xml=report_xml,
    metadata=metadata
)

print(f"Stored with metadata: {report_hash}")
```

### Custom Environment Variables

```python
import os
from pytest_jux.metadata import EnvironmentMetadata

# Set custom environment variables
os.environ["CI"] = "true"
os.environ["BUILD_NUMBER"] = "456"
os.environ["BRANCH_NAME"] = "feature/new-feature"

# Collect metadata (includes JUX_* env vars)
metadata = EnvironmentMetadata.collect()

# Access custom env vars
if metadata.env:
    print(f"CI: {metadata.env.get('CI')}")
    print(f"Build: {metadata.env.get('BUILD_NUMBER')}")
    print(f"Branch: {metadata.env.get('BRANCH_NAME')}")
```

### Git Metadata

```python
from pytest_jux.metadata import EnvironmentMetadata

# Collect metadata (auto-detects git)
metadata = EnvironmentMetadata.collect()

if metadata.git_commit:
    print(f"Git commit: {metadata.git_commit}")
    print(f"Git branch: {metadata.git_branch}")

    if metadata.git_dirty:
        print("⚠ Warning: Uncommitted changes present")
    else:
        print("✓ Clean git state")
else:
    print("Not a git repository")
```

### Serialization

```python
from pytest_jux.metadata import EnvironmentMetadata
import json

# Collect metadata
metadata = EnvironmentMetadata.collect()

# Convert to dict
metadata_dict = metadata.to_dict()

# Serialize to JSON
metadata_json = json.dumps(metadata_dict, indent=2)
print(metadata_json)

# Deserialize from dict
metadata_loaded = EnvironmentMetadata.from_dict(metadata_dict)
assert metadata_loaded.hostname == metadata.hostname
```

---

## Metadata Collection Process

### 1. System Metadata

Collected using Python standard library:
```python
import socket
import platform
import getpass
from datetime import datetime, UTC

hostname = socket.gethostname()
username = getpass.getuser()
platform_info = platform.platform()
timestamp = datetime.now(UTC).isoformat()
```

### 2. Python Metadata

```python
import sys

python_version = sys.version.split()[0]
python_implementation = sys.implementation.name
```

### 3. pytest Metadata

```python
import pytest

pytest_version = pytest.__version__
pytest_plugins = [p for p in sys.modules if p.startswith('pytest_')]
```

### 4. Dependency Metadata

```python
import importlib.metadata

dependencies = {
    dist.name: dist.version
    for dist in importlib.metadata.distributions()
}
```

### 5. Git Metadata (Optional)

```python
import subprocess

git_commit = subprocess.check_output(
    ["git", "rev-parse", "HEAD"],
    text=True
).strip()

git_branch = subprocess.check_output(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    text=True
).strip()

git_dirty = subprocess.call(["git", "diff-index", "--quiet", "HEAD"]) != 0
```

---

## Environment Variable Filtering

Only environment variables with specific prefixes are included:

**Included Prefixes**:
- `CI_*` (CI/CD variables)
- `BUILD_*` (Build system variables)
- `GITHUB_*` (GitHub Actions)
- `GITLAB_*` (GitLab CI)
- `JENKINS_*` (Jenkins)
- `JUX_*` (pytest-jux configuration)

**Example**:
```python
import os
from pytest_jux.metadata import EnvironmentMetadata

# These will be included
os.environ["CI_PIPELINE_ID"] = "123"
os.environ["BUILD_NUMBER"] = "456"
os.environ["GITHUB_RUN_ID"] = "789"
os.environ["JUX_ENVIRONMENT"] = "production"

# This will NOT be included (no matching prefix)
os.environ["RANDOM_VAR"] = "value"

metadata = EnvironmentMetadata.collect()

# Only CI_*, BUILD_*, GITHUB_*, JUX_* are in metadata.env
assert "CI_PIPELINE_ID" in metadata.env
assert "RANDOM_VAR" not in metadata.env
```

---

## Metadata Persistence

Metadata is stored as JSON alongside test reports:

### Storage Format

```
~/.local/share/pytest-jux/
├── reports/
│   └── abc123...xml      # Test report
└── metadata/
    └── abc123...json     # Metadata (same hash)
```

### JSON Structure

```json
{
  "hostname": "dev-machine.local",
  "username": "alice",
  "platform": "Darwin-23.5.0-arm64",
  "python_version": "3.11.14",
  "python_implementation": "CPython",
  "pytest_version": "8.0.0",
  "pytest_plugins": ["pytest-cov", "pytest-jux"],
  "timestamp": "2025-10-20T14:30:00Z",
  "git_commit": "abc123...",
  "git_branch": "main",
  "git_dirty": false,
  "dependencies": {
    "lxml": "5.0.0",
    "signxml": "3.2.0",
    "cryptography": "41.0.0"
  },
  "env": {
    "CI": "true",
    "BUILD_NUMBER": "456"
  }
}
```

---

## Use Cases

### 1. Debugging Test Failures

```python
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# Get metadata for failed test report
metadata = storage.get_metadata("failed-test-hash")

print(f"Failed on: {metadata.hostname}")
print(f"Platform: {metadata.platform}")
print(f"Python: {metadata.python_version}")
print(f"pytest: {metadata.pytest_version}")
print(f"Git commit: {metadata.git_commit}")

# Compare with successful run metadata
success_metadata = storage.get_metadata("success-test-hash")
if metadata.python_version != success_metadata.python_version:
    print("⚠ Different Python versions!")
```

### 2. Reproducibility

```python
from pytest_jux.metadata import EnvironmentMetadata
from pytest_jux.storage import ReportStorage

# Store current test run
metadata = EnvironmentMetadata.collect()
storage = ReportStorage()

# Later: reproduce environment
historical_metadata = storage.get_metadata("historical-hash")

print("To reproduce:")
print(f"  Python: {historical_metadata.python_version}")
print(f"  pytest: {historical_metadata.pytest_version}")
print(f"  Git commit: {historical_metadata.git_commit}")
for dep, version in historical_metadata.dependencies.items():
    print(f"  {dep}=={version}")
```

### 3. Audit Trail

```python
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# Audit all test runs
for report_hash in storage.list_reports():
    metadata = storage.get_metadata(report_hash)
    print(f"{metadata.timestamp} | {metadata.username}@{metadata.hostname} | {metadata.git_commit[:7]}")
```

---

## Security Considerations

### Sensitive Information

**Warning**: Metadata may contain sensitive information:
- Hostnames (reveals network topology)
- Usernames (reveals user accounts)
- Environment variables (may contain secrets)
- Git commits (may expose private repos)

**Best Practices**:
1. Review metadata before sharing reports
2. Filter sensitive environment variables
3. Sanitize hostnames/usernames in CI/CD
4. Use metadata encryption for public storage

### Environment Variable Filtering

The module only captures environment variables with specific prefixes to avoid accidentally capturing secrets:

```python
# SAFE: Only CI_*, BUILD_*, GITHUB_*, GITLAB_*, JENKINS_*, JUX_* are captured
# Secrets in other env vars (like AWS_SECRET_KEY) are NOT captured
```

---

## Performance

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `collect()` | O(n) | 5-20ms |
| `to_dict()` | O(1) | <1ms |
| `from_dict()` | O(1) | <1ms |

Where n = number of installed packages

**Note**: Git metadata collection may take longer (~50-100ms) if repository is large.

---

## See Also

- **[storage API](storage.md)**: Persists metadata alongside reports
- **[config API](config.md)**: Configuration affects metadata collection
- **[Reproducibility How-To](../../howto/reproducible-tests.md)**: Guide for reproducible test environments

---

**Module Path**: `pytest_jux.metadata`
**Source Code**: `pytest_jux/metadata.py`
**Tests**: `tests/test_metadata.py`
**Last Updated**: 2025-10-20
