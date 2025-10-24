# metadata API Reference

**Module**: `pytest_jux.metadata`
**Purpose**: Environment metadata capture for test reports
**Version**: 0.3.0+

---

## Overview

The `metadata` module captures environment metadata (system, Python, pytest, git, CI) and embeds it into JUnit XML test reports via pytest-metadata integration. All metadata is included in XMLDSig signatures for cryptographic provenance.

### Purpose

- **Environment Capture**: System, Python, pytest metadata
- **Project Identification**: Auto-detect project name
- **Git Integration**: Commit, branch, status, remote URL
- **CI Detection**: Auto-detect CI provider and build info
- **Reproducibility**: Enable test result reproduction
- **Auditing**: Track when, where, and how tests were run

### Key Changes in v0.3.0

- ✅ Metadata embedded in JUnit XML `<properties>` elements
- ✅ No separate JSON sidecar files (removed)
- ✅ All metadata included in XMLDSig signature
- ✅ Auto-detects project name (mandatory)
- ✅ Auto-detects git metadata (commit, branch, status, remote)
- ✅ Auto-detects CI provider (GitHub, GitLab, Jenkins, Travis, CircleCI)
- ✅ Semantic namespace prefixes (jux:, git:, ci:, env:)

### Related Modules

- **`plugin`**: Injects metadata into pytest-metadata hook
- **`storage`**: Stores signed reports with embedded metadata

---

## Core Function

### `capture_metadata()`

Capture current environment metadata.

**Signature**:
```python
def capture_metadata(
    include_env_vars: list[str] | None = None,
) -> EnvironmentMetadata
```

**Parameters**:
- `include_env_vars` (optional): List of additional environment variable names to capture

**Returns**: `EnvironmentMetadata` instance with all captured metadata

**Example**:
```python
from pytest_jux.metadata import capture_metadata

# Capture metadata (auto-detects everything)
metadata = capture_metadata()

print(f"Project: {metadata.project_name}")
print(f"Hostname: {metadata.hostname}")
print(f"Git commit: {metadata.git_commit}")
print(f"CI provider: {metadata.ci_provider}")

# Capture with additional env vars
metadata = capture_metadata(include_env_vars=["CUSTOM_VAR", "APP_VERSION"])
```

---

## Data Class

### `EnvironmentMetadata`

Environment metadata model (dataclass).

**Fields**:

#### Core Metadata (always present)
```python
hostname: str                    # System hostname
username: str                    # User running tests
platform: str                    # OS platform (e.g., "Linux-5.15.0")
python_version: str              # Python version
pytest_version: str              # pytest version
pytest_jux_version: str          # pytest-jux version
timestamp: str                   # ISO 8601 timestamp (UTC)
project_name: str                # Project name (mandatory)
```

#### Optional Metadata
```python
env: dict[str, str] | None       # Environment variables
git_commit: str | None           # Git commit SHA
git_branch: str | None           # Git branch name
git_status: str | None           # "clean" or "dirty"
git_remote: str | None           # Git remote URL (sanitized)
ci_provider: str | None          # CI provider name
ci_build_id: str | None          # CI build/pipeline ID
ci_build_url: str | None         # CI build URL
```

**Methods**:

- `to_dict() -> dict`: Convert to dictionary
- `to_json(indent: int | None = None) -> str`: Serialize to JSON

**Example**:
```python
from pytest_jux.metadata import EnvironmentMetadata, capture_metadata

# Capture metadata
metadata = capture_metadata()

# Access fields
print(metadata.project_name)     # "my-project"
print(metadata.hostname)          # "dev-machine"
print(metadata.git_commit)        # "abc123..." or None
print(metadata.ci_provider)       # "github" or None

# Convert to dict
data = metadata.to_dict()
print(data["jux:hostname"])

# Serialize to JSON
json_str = metadata.to_json(indent=2)
```

---

## Project Name Capture

Project name is **mandatory** and captured using multiple fallback strategies:

### Strategy Order

1. **Git Remote URL** - Extracts repository name from git remote
   ```
   https://github.com/owner/my-project.git → "my-project"
   git@github.com:owner/repo.git → "repo"
   ssh://user@host/path/project.git → "project"
   ```

2. **pyproject.toml** - Reads from Python project metadata
   ```toml
   [project]
   name = "my-awesome-project"
   ```
   Or:
   ```toml
   [tool.poetry]
   name = "my-poetry-project"
   ```

3. **Environment Variable** - Checks `JUX_PROJECT_NAME`
   ```bash
   export JUX_PROJECT_NAME="custom-project"
   ```

4. **Directory Basename** - Falls back to current directory name
   ```
   /path/to/my-project → "my-project"
   ```

**Example**:
```python
from pytest_jux.metadata import capture_metadata

# Project name always captured (never None)
metadata = capture_metadata()
assert metadata.project_name is not None
print(f"Project: {metadata.project_name}")
```

---

## Git Metadata Capture

Git metadata is auto-detected when running in a git repository.

### Captured Fields

- `git_commit`: Full commit SHA (e.g., "abc123def456...")
- `git_branch`: Current branch name (e.g., "main", "feature/new-feature")
- `git_status`: Working tree status ("clean" or "dirty")
- `git_remote`: Remote URL with credentials sanitized

### Multi-Remote Support

Tries remote names in order: `origin`, `home`, `upstream`, `github`, `gitlab`

### Credential Sanitization

Remote URLs are sanitized to remove credentials:
```
https://user:password@github.com/owner/repo.git
→ https://github.com/owner/repo.git
```

**Example**:
```python
from pytest_jux.metadata import capture_metadata

metadata = capture_metadata()

if metadata.git_commit:
    print(f"Commit: {metadata.git_commit}")
    print(f"Branch: {metadata.git_branch}")
    print(f"Status: {metadata.git_status}")  # "clean" or "dirty"
    print(f"Remote: {metadata.git_remote}")
else:
    print("Not in a git repository")
```

---

## CI Metadata Capture

CI metadata is auto-detected based on environment variables.

### Supported CI Providers

1. **GitHub Actions**
   - Provider: `"github"`
   - Build ID: `$GITHUB_RUN_ID`
   - Build URL: Constructed from `$GITHUB_SERVER_URL`, `$GITHUB_REPOSITORY`, `$GITHUB_RUN_ID`
   - Env vars: `GITHUB_SHA`, `GITHUB_REF`, `GITHUB_ACTOR`, etc.

2. **GitLab CI**
   - Provider: `"gitlab"`
   - Build ID: `$CI_PIPELINE_ID`
   - Build URL: `$CI_PIPELINE_URL`
   - Env vars: `CI_COMMIT_SHA`, `CI_COMMIT_BRANCH`, `CI_PROJECT_PATH`, etc.

3. **Jenkins**
   - Provider: `"jenkins"`
   - Build ID: `$BUILD_ID`
   - Build URL: `$BUILD_URL`
   - Env vars: `GIT_COMMIT`, `GIT_BRANCH`, `JOB_NAME`, `BUILD_NUMBER`

4. **Travis CI**
   - Provider: `"travis"`
   - Build ID: `$TRAVIS_BUILD_ID`
   - Build URL: `$TRAVIS_BUILD_WEB_URL`
   - Env vars: `TRAVIS_COMMIT`, `TRAVIS_BRANCH`, `TRAVIS_JOB_ID`

5. **CircleCI**
   - Provider: `"circleci"`
   - Build ID: `$CIRCLE_BUILD_NUM`
   - Build URL: `$CIRCLE_BUILD_URL`
   - Env vars: `CIRCLE_SHA1`, `CIRCLE_BRANCH`, `CIRCLE_WORKFLOW_ID`

**Example**:
```python
from pytest_jux.metadata import capture_metadata

metadata = capture_metadata()

if metadata.ci_provider:
    print(f"CI Provider: {metadata.ci_provider}")
    print(f"Build ID: {metadata.ci_build_id}")
    print(f"Build URL: {metadata.ci_build_url}")

    # CI env vars automatically captured
    if metadata.env:
        for key, value in metadata.env.items():
            if key.startswith("CI_") or key.startswith("GITHUB_"):
                print(f"{key}: {value}")
else:
    print("Not running in CI")
```

---

## Environment Variables

Environment variables from CI providers are automatically captured. You can also capture custom variables.

### Auto-Captured CI Variables

- **GitHub Actions**: `GITHUB_SHA`, `GITHUB_REF`, `GITHUB_ACTOR`, etc.
- **GitLab CI**: `CI_COMMIT_SHA`, `CI_PIPELINE_ID`, `CI_JOB_ID`, etc.
- **Jenkins**: `GIT_COMMIT`, `BUILD_NUMBER`, `JOB_NAME`, etc.
- **Travis CI**: `TRAVIS_COMMIT`, `TRAVIS_BUILD_NUMBER`, etc.
- **CircleCI**: `CIRCLE_SHA1`, `CIRCLE_WORKFLOW_ID`, etc.

### Custom Variables

```python
from pytest_jux.metadata import capture_metadata

# Capture specific env vars
metadata = capture_metadata(include_env_vars=["APP_VERSION", "CUSTOM_VAR"])

if metadata.env:
    print(f"App Version: {metadata.env.get('APP_VERSION')}")
    print(f"Custom: {metadata.env.get('CUSTOM_VAR')}")
```

### Precedence

User-requested env vars take precedence over auto-detected CI vars if there's a conflict.

---

## Metadata Namespaces

Metadata uses semantic namespace prefixes in JUnit XML:

### Namespace Prefixes

- **jux:** - Core pytest-jux metadata (hostname, username, etc.)
- **git:** - Git metadata (commit, branch, status, remote)
- **ci:** - CI metadata (provider, build_id, build_url)
- **env:** - Environment variables (GITHUB_SHA, CI_COMMIT_SHA, etc.)
- **no prefix** - Project name and user-provided metadata

### XML Representation

```xml
<properties>
  <!-- No prefix -->
  <property name="project" value="my-project"/>

  <!-- jux: prefix -->
  <property name="jux:hostname" value="dev-machine"/>
  <property name="jux:timestamp" value="2025-10-24T12:34:56+00:00"/>

  <!-- git: prefix -->
  <property name="git:commit" value="abc123..."/>
  <property name="git:branch" value="main"/>

  <!-- ci: prefix -->
  <property name="ci:provider" value="github"/>
  <property name="ci:build_id" value="123456"/>

  <!-- env: prefix -->
  <property name="env:GITHUB_SHA" value="abc123..."/>
</properties>
```

---

## Usage Examples

### Basic Usage

```python
from pytest_jux.metadata import capture_metadata

# Capture all metadata
metadata = capture_metadata()

# Display summary
print(f"Project: {metadata.project_name}")
print(f"Running on: {metadata.hostname}")
print(f"Platform: {metadata.platform}")
print(f"Python: {metadata.python_version}")
print(f"Timestamp: {metadata.timestamp}")
```

### Git Repository

```python
from pytest_jux.metadata import capture_metadata

metadata = capture_metadata()

# Git metadata only present in git repos
if metadata.git_commit:
    print(f"Git commit: {metadata.git_commit[:7]}")
    print(f"Branch: {metadata.git_branch}")

    if metadata.git_status == "dirty":
        print("⚠️  Warning: Uncommitted changes")
    else:
        print("✓ Clean working tree")
```

### CI Environment

```python
from pytest_jux.metadata import capture_metadata

metadata = capture_metadata()

if metadata.ci_provider:
    print(f"Running in {metadata.ci_provider} CI")
    print(f"Build: {metadata.ci_build_id}")
    print(f"URL: {metadata.ci_build_url}")
else:
    print("Running locally")
```

### Custom Environment Variables

```python
from pytest_jux.metadata import capture_metadata
import os

# Set custom env vars
os.environ["APP_VERSION"] = "1.2.3"
os.environ["DEPLOY_ENV"] = "staging"

# Capture with custom vars
metadata = capture_metadata(
    include_env_vars=["APP_VERSION", "DEPLOY_ENV"]
)

print(f"App: {metadata.env['APP_VERSION']}")
print(f"Env: {metadata.env['DEPLOY_ENV']}")
```

### Serialization

```python
from pytest_jux.metadata import capture_metadata
import json

metadata = capture_metadata()

# Convert to dict
data = metadata.to_dict()
print(f"Fields: {len(data)}")

# Serialize to JSON
json_str = metadata.to_json(indent=2)
print(json_str)

# Pretty print
json_data = json.loads(json_str)
for key, value in json_data.items():
    print(f"{key}: {value}")
```

---

## Integration with pytest-metadata

The `pytest_metadata` hook in `plugin.py` automatically calls `capture_metadata()` and injects all metadata into pytest-metadata's metadata dict:

```python
# In pytest_jux/plugin.py
def pytest_metadata(metadata: dict) -> None:
    jux_meta = capture_metadata()

    # Inject with semantic prefixes
    metadata["project"] = jux_meta.project_name
    metadata["jux:hostname"] = jux_meta.hostname
    metadata["git:commit"] = jux_meta.git_commit
    metadata["ci:provider"] = jux_meta.ci_provider
    # ... etc
```

This metadata is then written to JUnit XML `<properties>` elements and included in XMLDSig signatures.

---

## Security Considerations

### Sensitive Information

Metadata may contain sensitive information:
- ❌ Hostnames (network topology)
- ❌ Usernames (user accounts)
- ❌ Git remotes (private repository URLs)
- ❌ CI build URLs (internal CI systems)

### Best Practices

1. **Review before sharing**: Check metadata before publishing reports
2. **Override sensitive fields**: Use CLI to override hostnames/usernames
3. **Sanitize git remotes**: Credentials are automatically removed from URLs
4. **CI-specific handling**: Use generic identifiers in CI environments

### Example: Sanitizing Metadata

```bash
# Override sensitive fields
pytest --junit-xml=report.xml \
  --metadata jux:hostname "ci-runner" \
  --metadata jux:username "ci-user"
```

---

## Performance

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `capture_metadata()` | O(1) | 10-50ms |
| Git detection | O(1) | 20-100ms |
| CI detection | O(1) | <5ms |
| `to_dict()` | O(1) | <1ms |
| `to_json()` | O(1) | <1ms |

**Note**: Git operations may be slower in large repositories.

---

## See Also

- **[How-To: Add Metadata to Reports](../../howto/add-metadata-to-reports.md)** - User guide
- **[plugin API](plugin.md)** - pytest hook integration
- **[storage API](storage.md)** - Report persistence

---

**Module Path**: `pytest_jux.metadata`
**Source Code**: `pytest_jux/metadata.py`
**Tests**: `tests/test_metadata.py`
**Last Updated**: 2025-10-24 (v0.3.0)
