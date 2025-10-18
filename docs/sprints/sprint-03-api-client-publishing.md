# Sprint 3: Configuration, Storage & Caching

**Sprint Duration**: 2025-10-15 to 2025-10-18
**Sprint Goal**: Implement configuration management, local storage/caching, and CLI tools for report management
**Status**: ✅ Complete (REST API client postponed to Sprint 4)

## Overview

Sprint 3 adds REST API integration, local filesystem storage, and comprehensive configuration management to pytest-jux, enabling:
- **Configuration management**: Full-featured config system with validation, debugging, and initialization
- **Local filesystem storage**: Cache/store signed reports in XDG-compliant directories
- **Flexible storage modes**: Local-only, API-only, or both (with offline fallback)
- **REST API publishing**: Publish signed reports to the Jux REST API
- **Automatic publishing**: After test execution (via pytest hook)
- **Manual publishing**: Via standalone CLI command (`jux-publish`)
- **Cache management**: CLI tools to inspect and manage cached reports (`jux-cache`)
- **Config inspection**: Debug and validate configuration (`jux-config`)
- **Environment metadata**: Capture execution context (hostname, user, platform)
- **Offline resilience**: Queue reports locally when API unavailable

This sprint completes the core workflow: **sign → store locally and/or publish → server storage** (server storage handled by Jux API server).

**Configuration philosophy**: Signing and publishing are **disabled by default** and must be explicitly enabled via configuration.

## Architecture Clarification

**pytest-jux (this project) - Client responsibilities:**
- Sign JUnit XML reports with XMLDSig (opt-in via configuration)
- Store signed reports locally in XDG-compliant directories
- Publish signed reports to Jux REST API via HTTP POST
- Cache reports when API unavailable (offline queue)
- CLI tools for offline signing, publishing, and cache management
- Environment metadata capture

**Jux API Server (separate project) - Server responsibilities:**
- Receive signed reports via REST API endpoints
- Store reports in database (SQLite/PostgreSQL)
- Detect duplicate reports using canonical hash
- Verify XML signatures
- Provide query/browse interfaces
- Web UI for report visualization

This sprint focuses **exclusively on the client-side** API integration and local storage.

---

## User Stories

### US-3.1: REST API Client

**As a** developer
**I want** a REST API client for publishing signed reports
**So that** I can integrate with the Jux backend

**Acceptance Criteria**:
- [ ] HTTP client for POST requests to Jux API
- [ ] JSON payload construction with signed XML and metadata
- [ ] Support for API authentication (API keys, bearer tokens)
- [ ] Configurable API endpoint URL
- [ ] Request timeout configuration
- [ ] Proper error handling (network errors, HTTP status codes)
- [ ] >85% test coverage for api_client module

**Technical Tasks**:
- [ ] Create `pytest_jux/api_client.py`
- [ ] Implement `JuxAPIClient` class
- [ ] Add authentication support (API key, token)
- [ ] Add retry logic for transient failures
- [ ] Write comprehensive tests (mocked HTTP responses)
- [ ] Add integration tests (optional: against test API server)

**API Request Format**:
```json
{
  "report": "<signed-junit-xml>",
  "canonical_hash": "sha256:abc123...",
  "metadata": {
    "hostname": "ci-runner-01",
    "username": "jenkins",
    "platform": "Linux-5.15.0-x86_64",
    "python_version": "3.11.5",
    "pytest_version": "8.0.0",
    "timestamp": "2025-10-17T10:30:00Z"
  }
}
```

**API Response Handling**:
- `201 Created`: Report accepted and stored
- `409 Conflict`: Duplicate report (already exists)
- `400 Bad Request`: Invalid XML or signature
- `401 Unauthorized`: Authentication failed
- `500 Internal Server Error`: Server error (retry)

---

### US-3.2: Environment Metadata Capture

**As a** system administrator
**I want** test environment metadata captured with reports
**So that** I can correlate test results with execution context

**Acceptance Criteria**:
- [ ] Capture hostname (`socket.gethostname()`)
- [ ] Capture username (`getpass.getuser()`)
- [ ] Capture platform information (`platform.platform()`)
- [ ] Capture Python version (`sys.version`)
- [ ] Capture pytest version
- [ ] Capture timestamp (ISO 8601 format, UTC)
- [ ] Optional: environment variables (CI/CD context)
- [ ] >85% test coverage for metadata module

**Technical Tasks**:
- [ ] Create `pytest_jux/metadata.py`
- [ ] Implement `capture_metadata()` function
- [ ] Add configuration for optional metadata fields
- [ ] Write comprehensive tests
- [ ] Test on multiple platforms (Linux, macOS, Windows)

**Metadata Example**:
```python
{
    "hostname": "ci-runner-01",
    "username": "jenkins",
    "platform": "Linux-5.15.0-x86_64-with-glibc2.35",
    "python_version": "3.11.5 (main, Sep 11 2023, 13:54:46) [GCC 11.2.0]",
    "pytest_version": "8.0.0",
    "timestamp": "2025-10-17T10:30:00+00:00",
    "env": {
        "CI": "true",
        "CI_JOB_ID": "12345",
        "CI_COMMIT_SHA": "abc123..."
    }
}
```

---

### US-3.3: Automatic Publishing via pytest Hook

**As a** developer
**I want** signed reports automatically published after test execution
**So that** results are immediately available in the Jux backend

**Acceptance Criteria**:
- [ ] Integrate API client with `pytest_sessionfinish` hook
- [ ] Publish after signing (if `--jux-publish` enabled)
- [ ] Configuration via pytest options or config file
- [ ] Graceful degradation if API unreachable (log error, don't fail tests)
- [ ] Log publishing status (success, failure, duplicate)
- [ ] >85% test coverage for plugin publishing integration

**Technical Tasks**:
- [ ] Update `pytest_jux/plugin.py` to integrate API client
- [ ] Add `--jux-api-url`, `--jux-api-key` options
- [ ] Implement publishing logic in `pytest_sessionfinish`
- [ ] Add error handling (network failures, timeouts)
- [ ] Write integration tests
- [ ] Test with actual pytest execution

**pytest Configuration**:
```ini
[pytest]
jux_publish = true
jux_api_url = https://jux.example.com/api/v1/reports
jux_api_key = secret-api-key-here
jux_key_path = ~/.jux/signing_key.pem
jux_cert_path = ~/.jux/signing_key.crt
```

**Command-line Usage**:
```bash
pytest --junit-xml=report.xml \
       --jux-sign \
       --jux-publish \
       --jux-api-url=https://jux.example.com/api/v1/reports \
       --jux-api-key=secret-api-key
```

---

### US-3.4: Manual Publishing CLI Command

**As a** CI/CD engineer
**I want** to manually publish signed reports via CLI
**So that** I can control publishing separately from test execution

**Acceptance Criteria**:
- [ ] `jux-publish` CLI command for manual publishing
- [ ] Support for publishing previously signed XML files
- [ ] Configuration via command-line, config file, or environment variables
- [ ] JSON output for scripting (published, duplicate, error)
- [ ] Exit codes: 0 = success, 1 = error, 2 = duplicate
- [ ] >85% test coverage for publish command

**Technical Tasks**:
- [ ] Create `pytest_jux/commands/publish.py`
- [ ] Integrate with `api_client.py`
- [ ] Add stdin support for pipelines
- [ ] Implement JSON output mode
- [ ] Write comprehensive tests
- [ ] Test with mocked API responses

**CLI Interface**:
```bash
# Publish a signed report
jux-publish --input signed-report.xml \
  --api-url https://jux.example.com/api/v1/reports \
  --api-key secret-api-key

# Publish with JSON output
jux-publish --input signed-report.xml --json
# Output: {"status": "published", "id": "report-123", "canonical_hash": "sha256:abc..."}

# Publish from stdin (pipeline)
cat signed-report.xml | jux-publish --api-url https://jux.example.com/api/v1/reports
```

---

### US-3.5: Local Filesystem Storage & Caching

**As a** developer
**I want** signed reports stored locally on the filesystem
**So that** I have a local copy and can work offline when the API is unavailable

**Acceptance Criteria**:
- [ ] Store signed reports in XDG-compliant directories
  - `~/.local/share/jux/reports/` (Linux/Unix)
  - `~/Library/Application Support/jux/reports/` (macOS)
  - `%LOCALAPPDATA%\jux\reports\` (Windows)
- [ ] Configurable storage modes:
  - `local`: Store locally only (no API publishing)
  - `api`: Publish to API only (no local storage)
  - `both`: Store locally AND publish to API (default when API configured)
  - `cache`: Store locally, publish to API if available (offline queue)
- [ ] Store reports with canonical hash as filename: `{hash}.xml`
- [ ] Store metadata alongside reports: `{hash}.json`
- [ ] Automatic directory creation with appropriate permissions
- [ ] Graceful handling of filesystem errors (disk full, permissions)
- [ ] >85% test coverage for storage module

**Technical Tasks**:
- [ ] Create `pytest_jux/storage.py`
- [ ] Implement `ReportStorage` class with XDG directory support
- [ ] Add storage mode configuration
- [ ] Implement atomic write operations (temp file + rename)
- [ ] Add file permission management (0600 for sensitive data)
- [ ] Write comprehensive tests (mocked filesystem)
- [ ] Test on multiple platforms (Linux, macOS, Windows)

**Storage Structure**:
```
~/.local/share/jux/
├── reports/                    # Signed XML reports
│   ├── sha256-abc123...xml     # Report file (canonical hash as name)
│   └── sha256-def456...xml
├── metadata/                   # Metadata JSON files
│   ├── sha256-abc123...json    # Metadata for corresponding report
│   └── sha256-def456...json
└── queue/                      # Offline queue (failed API publishes)
    ├── sha256-ghi789...xml
    └── sha256-ghi789...json
```

**Configuration Examples**:
```ini
[jux]
# Store locally only (no API)
storage_mode = local
storage_path = ~/.local/share/jux/reports

# Publish to API only (no local storage)
storage_mode = api

# Store locally AND publish to API
storage_mode = both

# Cache locally, publish to API when available
storage_mode = cache
```

---

### US-3.6: Cache Management CLI Command

**As a** developer
**I want** to inspect and manage locally cached reports
**So that** I can see what's stored and clean up old reports

**Acceptance Criteria**:
- [ ] `jux-cache` CLI command for cache management
- [ ] Subcommands:
  - `jux-cache list`: List cached reports
  - `jux-cache show <hash>`: Display report details
  - `jux-cache clean`: Remove old/expired reports
  - `jux-cache push`: Publish cached reports to API (retry failed publishes)
  - `jux-cache stats`: Show cache statistics (size, count, oldest)
- [ ] Support for filtering (date range, status)
- [ ] JSON output for scripting
- [ ] Dry-run mode for destructive operations
- [ ] >85% test coverage for cache command

**Technical Tasks**:
- [ ] Create `pytest_jux/commands/cache.py`
- [ ] Implement cache listing and statistics
- [ ] Implement cache cleaning with age/size limits
- [ ] Implement offline queue retry (publish cached reports)
- [ ] Add JSON output mode
- [ ] Write comprehensive tests
- [ ] Test with various cache states

**CLI Interface**:
```bash
# List cached reports
jux-cache list
# Output:
#   sha256:abc123... | 2025-10-17 10:30:00 | 42 tests, 2 failed | published
#   sha256:def456... | 2025-10-17 11:45:00 | 35 tests, 0 failed | queued

# Show report details
jux-cache show sha256:abc123...
# Output: Full report with metadata

# Clean old reports (older than 30 days)
jux-cache clean --days 30 --dry-run
jux-cache clean --days 30  # Actually delete

# Publish queued reports (retry offline queue)
jux-cache push
# Output: Published 3 reports, 1 failed

# Cache statistics
jux-cache stats
# Output:
#   Total reports: 127
#   Total size: 2.4 MB
#   Oldest: 2025-09-01
#   Queued (not published): 5
```

---

### US-3.7: Configuration Management CLI Command

**As a** developer
**I want** to manage and inspect pytest-jux configuration
**So that** I can debug configuration issues and understand effective settings

**Acceptance Criteria**:
- [ ] `jux-config` CLI command for configuration management
- [ ] Subcommands (similar to `ansible-config`):
  - `jux-config list`: List all available configuration options with descriptions
  - `jux-config dump`: Show current effective configuration (merged from all sources)
  - `jux-config view`: View configuration file contents (with source precedence)
  - `jux-config init`: Initialize/create configuration files with defaults
  - `jux-config validate`: Validate configuration syntax and values
- [ ] Show configuration source (CLI, env, file) for each setting
- [ ] Support for different output formats (text, JSON, YAML)
- [ ] Highlight configuration conflicts or warnings
- [ ] >85% test coverage for config command

**Technical Tasks**:
- [ ] Create `pytest_jux/commands/config.py`
- [ ] Implement configuration discovery and merging logic
- [ ] Add configuration schema/validation
- [ ] Implement all subcommands
- [ ] Add JSON/YAML output formats
- [ ] Write comprehensive tests
- [ ] Test with various configuration scenarios

**CLI Interface**:
```bash
# List all configuration options
jux-config list
# Output:
#   jux_enabled          (bool)   Enable pytest-jux plugin [default: false]
#   jux_sign             (bool)   Enable report signing [default: false]
#   jux_publish          (bool)   Enable API publishing [default: false]
#   jux_storage_mode     (enum)   Storage mode: local|api|both|cache [default: local]
#   jux_api_url          (str)    API endpoint URL
#   jux_api_key          (str)    API authentication key
#   ...

# Dump current effective configuration
jux-config dump
# Output:
#   Configuration from multiple sources:
#
#   jux_enabled = true                    (source: pytest.ini)
#   jux_sign = true                       (source: pytest.ini)
#   jux_key_path = ~/.jux/signing_key.pem (source: ~/.jux/config)
#   jux_storage_mode = cache              (source: environment variable JUX_STORAGE_MODE)
#   jux_api_url = https://jux.example.com (source: pytest.ini)
#   jux_api_key = ***********             (source: environment variable JUX_API_KEY)

# Dump configuration as JSON
jux-config dump --format json
# Output: {"jux_enabled": true, "jux_sign": true, ...}

# View configuration file
jux-config view ~/.jux/config
# Output: [Shows file contents with syntax highlighting]

# View all configuration files with precedence
jux-config view --all
# Output:
#   Configuration files (in precedence order):
#
#   1. ~/.jux/config (user-level)
#      [jux]
#      enabled = true
#      sign = true
#
#   2. pytest.ini (project-level)
#      [pytest]
#      jux_api_url = https://jux.example.com

# Initialize configuration file
jux-config init
# Output: Created configuration file: ~/.jux/config

jux-config init --path .jux.conf
# Output: Created configuration file: .jux.conf

jux-config init --path .jux.conf --template full
# Output: Created configuration file with all options: .jux.conf

# Validate configuration
jux-config validate
# Output: ✓ Configuration is valid

jux-config validate --strict
# Output:
#   ⚠ Warning: jux_sign enabled but jux_key_path not set
#   ⚠ Warning: jux_publish enabled but jux_api_url not set
#   ✗ Error: jux_storage_mode has invalid value 'invalid' (expected: local|api|both|cache)
```

**Configuration Schema**:
```python
# Configuration options with types and defaults
CONFIG_SCHEMA = {
    "jux_enabled": {
        "type": "bool",
        "default": False,
        "description": "Enable pytest-jux plugin"
    },
    "jux_sign": {
        "type": "bool",
        "default": False,
        "description": "Enable report signing",
        "requires": ["jux_key_path"]
    },
    "jux_key_path": {
        "type": "path",
        "default": None,
        "description": "Path to signing key (PEM format)"
    },
    "jux_storage_mode": {
        "type": "enum",
        "default": "local",
        "choices": ["local", "api", "both", "cache"],
        "description": "Storage mode"
    },
    # ... more options
}
```

---

## Technical Architecture

### Module Structure

```
pytest_jux/
├── storage.py              # (new) Local filesystem storage (XDG directories)
├── api_client.py           # (new) REST API client
├── metadata.py             # (new) Environment metadata capture
├── config.py               # (new) Configuration management (schema, validation, merging)
├── plugin.py               # (updated) Add storage + publishing to pytest hook
├── commands/
│   ├── config.py           # (new) Configuration management command
│   ├── cache.py            # (new) Cache management command
│   ├── publish.py          # (new) Manual publishing command
│   ├── keygen.py           # (existing)
│   ├── sign.py             # (existing)
│   ├── verify.py           # (existing)
│   └── inspect.py          # (existing)
├── signer.py               # (existing) XML signing
├── verifier.py             # (existing) Signature verification
└── canonicalizer.py        # (existing) C14N and hashing
```

### HTTP Client Library

Using **requests** library (already in dependencies):
- Simple, well-tested HTTP client
- Session management for connection pooling
- Built-in retry support (via urllib3.Retry)
- Timeout configuration
- SSL/TLS certificate verification

### Authentication Methods

Support multiple authentication methods:
1. **API Key** (HTTP header: `X-API-Key: <key>`)
2. **Bearer Token** (HTTP header: `Authorization: Bearer <token>`)
3. **Basic Auth** (optional, for testing)

Configuration priority:
1. Command-line options (`--jux-api-key`)
2. Environment variables (`JUX_API_KEY`)
3. Config file (`~/.jux/config`)

---

### Implementation Order (TDD)

Following TDD principles, implement in this order:

1. **Configuration Management** (foundational, used by all modules)
   - Write tests: `tests/test_config.py`
   - Implement: `pytest_jux/config.py`
   - Define configuration schema with types and validation
   - Implement configuration merging (CLI, env, files)
   - Validate: >85% coverage

2. **Environment Metadata** (foundational, no dependencies)
   - Write tests: `tests/test_metadata.py`
   - Implement: `pytest_jux/metadata.py`
   - Validate: >85% coverage

3. **Local Filesystem Storage** (foundational, uses metadata + config)
   - Write tests: `tests/test_storage.py`
   - Implement: `pytest_jux/storage.py`
   - Test XDG directory support on multiple platforms
   - Validate: >85% coverage

4. **REST API Client** (uses metadata + config)
   - Write tests: `tests/test_api_client.py`
   - Implement: `pytest_jux/api_client.py`
   - Validate: >85% coverage

5. **Plugin Storage & Publishing Integration** (uses storage + API client + config)
   - Update tests: `tests/test_plugin.py`
   - Update: `pytest_jux/plugin.py`
   - Add configuration for signing enabled/disabled
   - Add configuration for storage modes
   - Validate: >85% coverage

6. **Manual Publishing Command** (uses API client + storage)
   - Write tests: `tests/commands/test_publish.py`
   - Implement: `pytest_jux/commands/publish.py`
   - Validate: >85% coverage

7. **Cache Management Command** (uses storage)
   - Write tests: `tests/commands/test_cache.py`
   - Implement: `pytest_jux/commands/cache.py`
   - Test all subcommands (list, show, clean, push, stats)
   - Validate: >85% coverage

8. **Configuration Management Command** (uses config module)
   - Write tests: `tests/commands/test_config.py`
   - Implement: `pytest_jux/commands/config.py`
   - Test all subcommands (list, dump, view, init, validate)
   - Test multiple output formats (text, JSON, YAML)
   - Validate: >85% coverage

---

## API Endpoint Specification

### POST /api/v1/reports

**Request:**
```http
POST /api/v1/reports HTTP/1.1
Host: jux.example.com
Content-Type: application/json
X-API-Key: secret-api-key-here

{
  "report": "<testsuite>...</testsuite>",
  "canonical_hash": "sha256:abc123...",
  "metadata": {
    "hostname": "ci-runner-01",
    "username": "jenkins",
    "platform": "Linux-5.15.0-x86_64",
    "timestamp": "2025-10-17T10:30:00Z"
  }
}
```

**Response (201 Created):**
```json
{
  "status": "created",
  "id": "report-12345",
  "canonical_hash": "sha256:abc123...",
  "message": "Report published successfully"
}
```

**Response (409 Conflict - Duplicate):**
```json
{
  "status": "duplicate",
  "id": "report-12345",
  "canonical_hash": "sha256:abc123...",
  "message": "Report already exists"
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "error": "Invalid XML signature",
  "message": "XMLDSig signature verification failed"
}
```

---

## Test Strategy

### Unit Tests

**API Client Tests** (`tests/test_api_client.py`):
- Mock HTTP responses using `responses` library or `requests-mock`
- Test authentication (API key, bearer token)
- Test error handling (network errors, timeouts, HTTP errors)
- Test retry logic (transient failures)
- Test response parsing (201, 409, 400, 500)

**Metadata Tests** (`tests/test_metadata.py`):
- Test metadata capture on multiple platforms
- Test optional environment variable capture
- Test timestamp formatting (ISO 8601, UTC)
- Mock system calls for consistent testing

**Plugin Tests** (`tests/test_plugin.py`):
- Test publishing integration with pytest hook
- Test graceful degradation (API unreachable)
- Test configuration loading (options, config file)
- Mock API client to avoid network calls

**Publish Command Tests** (`tests/commands/test_publish.py`):
- Test CLI argument parsing
- Test stdin/stdout handling
- Test JSON output format
- Test exit codes (0, 1, 2)
- Mock API client for predictable responses

### Integration Tests (Optional)

**Against Test API Server**:
- Spin up local Jux API server (Docker/Podman)
- Test full workflow: sign → publish → verify stored
- Test duplicate detection
- Test authentication failures

---

## CLI Entry Points

Update `pyproject.toml` to add new console scripts:

```toml
[project.scripts]
jux-keygen = "pytest_jux.commands.keygen:main"      # (existing)
jux-sign = "pytest_jux.commands.sign:main"          # (existing)
jux-verify = "pytest_jux.commands.verify:main"      # (existing)
jux-inspect = "pytest_jux.commands.inspect:main"    # (existing)
jux-publish = "pytest_jux.commands.publish:main"    # NEW
jux-cache = "pytest_jux.commands.cache:main"        # NEW
jux-config = "pytest_jux.commands.config:main"      # NEW
```

---

## Configuration Management

### Default Behavior

**IMPORTANT**: Signing and publishing are **disabled by default**. Users must explicitly enable them via configuration.

**Default configuration:**
- `jux_enabled = false` - Plugin disabled by default
- `jux_sign = false` - Signing disabled by default
- `jux_publish = false` - Publishing disabled by default
- `storage_mode = local` - Local storage only when enabled

Users must opt-in to enable any pytest-jux functionality.

### Configuration File Support

Support configuration files using **configargparse**:
- `~/.jux/config` (user-level)
- `/etc/jux/config` (system-level)
- `.jux.conf` (project-level)
- `pytest.ini` or `pyproject.toml` (pytest configuration)

**Example Config File** (`~/.jux/config`):
```ini
[jux]
# Enable pytest-jux plugin
enabled = true

# Enable report signing (REQUIRED for publishing)
sign = true
key_path = ~/.jux/signing_key.pem
cert_path = ~/.jux/signing_key.crt

# Storage configuration
storage_mode = both                                  # local, api, both, cache
storage_path = ~/.local/share/jux/reports           # Optional: custom path

# API configuration (for publishing)
publish = true
api_url = https://jux.example.com/api/v1/reports
api_key = secret-api-key-here
```

**Example pytest.ini**:
```ini
[pytest]
# Enable pytest-jux and signing
jux_enabled = true
jux_sign = true
jux_key_path = ~/.jux/signing_key.pem

# Enable local storage only (no API)
jux_storage_mode = local

# OR: Enable API publishing with local caching
jux_storage_mode = cache
jux_publish = true
jux_api_url = https://jux.example.com/api/v1/reports
jux_api_key_env = JUX_API_KEY  # Read from environment variable
```

### Environment Variables

Support environment variables for sensitive data:
- `JUX_ENABLED`: Enable/disable plugin (true/false)
- `JUX_SIGN`: Enable/disable signing (true/false)
- `JUX_PUBLISH`: Enable/disable publishing (true/false)
- `JUX_API_URL`: API endpoint URL
- `JUX_API_KEY`: API authentication key
- `JUX_KEY_PATH`: Path to signing key
- `JUX_CERT_PATH`: Path to certificate
- `JUX_STORAGE_MODE`: Storage mode (local/api/both/cache)
- `JUX_STORAGE_PATH`: Custom storage directory path

### Configuration Priority

1. Command-line options (highest priority)
2. Environment variables
3. Project-level config file (`.jux.conf`, `pytest.ini`)
4. User-level config file (`~/.jux/config`)
5. System-level config file (`/etc/jux/config`)
6. Default values (lowest priority - signing/publishing DISABLED)

### Configuration Examples

**Local storage only (no signing, no API):**
```bash
pytest --jux-enabled --jux-storage-mode=local
```

**Sign and store locally (no API):**
```bash
pytest --jux-enabled --jux-sign --jux-key=~/.jux/key.pem --jux-storage-mode=local
```

**Sign, store locally, and publish to API:**
```bash
pytest --jux-enabled --jux-sign --jux-publish \
       --jux-api-url=https://jux.example.com/api/v1/reports \
       --jux-storage-mode=both
```

**Cache locally, publish to API when available:**
```bash
pytest --jux-enabled --jux-sign --jux-publish \
       --jux-storage-mode=cache
# If API unavailable, reports are queued locally for later publishing
```

---

## Definition of Done

Sprint 3 is complete when:

- [ ] All user stories meet acceptance criteria
- [ ] All tests pass (`pytest`)
- [ ] Code coverage >85% for all new modules
- [ ] Type checking passes (`mypy pytest_jux`)
- [ ] Linting clean (`ruff check .`)
- [ ] Formatting clean (`ruff format --check .`)
- [ ] Security scans clean (`make security-scan`)
- [ ] Documentation updated (docstrings, type hints)
- [ ] README.md updated with publishing examples
- [ ] CLAUDE.md updated with client/server architecture clarification
- [ ] Manual smoke tests: full workflow (sign → publish) works end-to-end
- [ ] Changes committed to `develop` branch

---

## Risks & Mitigations

### Risk 1: API Server Unavailability
**Impact**: High (blocks publishing)
**Probability**: Medium
**Mitigation**:
- Graceful degradation (log error, don't fail tests)
- Retry logic with exponential backoff
- Clear error messages for troubleshooting

### Risk 2: API Authentication Complexity
**Impact**: Medium
**Probability**: Low
**Mitigation**:
- Support multiple auth methods (API key, bearer token)
- Clear documentation on authentication setup
- Test with different auth configurations

### Risk 3: Network Timeout Configuration
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- Configurable timeouts (connect, read)
- Sensible defaults (10s connect, 30s read)
- Document timeout configuration

### Risk 4: Metadata Privacy Concerns
**Impact**: Medium (sensitive environment data)
**Probability**: Low
**Mitigation**:
- Document what metadata is captured
- Optional metadata fields (env vars)
- Allow metadata filtering/redaction

### Risk 5: Filesystem Storage Errors
**Impact**: High (data loss, disk full)
**Probability**: Medium
**Mitigation**:
- Graceful error handling for disk full, permissions errors
- Atomic writes (temp file + rename)
- Configurable storage path with fallback
- File size limits and cleanup policies
- Comprehensive logging of storage errors

### Risk 6: XDG Directory Portability
**Impact**: Medium (platform compatibility)
**Probability**: Low
**Mitigation**:
- Test on Linux, macOS, Windows
- Use appropriate XDG directories per platform
- Allow custom storage path override
- Document platform-specific paths

### Risk 7: Cache Growth & Management
**Impact**: Medium (disk space consumption)
**Probability**: High
**Mitigation**:
- Implement cache size limits
- Automatic cleanup of old reports
- `jux-cache clean` command for manual cleanup
- Document cache management best practices
- Warn users when cache size exceeds threshold

---

## Success Metrics

- **Code Coverage**: >85% for all new modules
- **Type Safety**: 0 mypy errors in strict mode
- **Security**: 0 findings from Bandit/Safety
- **Performance**: Publishing <1 second per report
- **Reliability**: >99% success rate with retry logic
- **Usability**: Clear error messages, comprehensive CLI help

---

## Sprint Backlog

### Week 1: Foundation & Configuration

**Day 1-2: Configuration Management Module**
- [ ] Write tests: `tests/test_config.py`
- [ ] Implement: `pytest_jux/config.py`
- [ ] Define configuration schema with types
- [ ] Implement configuration merging (CLI, env, files)
- [ ] Add validation logic
- [ ] Achieve >85% coverage

**Day 3: Environment Metadata**
- [ ] Write tests: `tests/test_metadata.py`
- [ ] Implement: `pytest_jux/metadata.py`
- [ ] Test on multiple platforms
- [ ] Achieve >85% coverage

**Day 4-5: Local Filesystem Storage**
- [ ] Write tests: `tests/test_storage.py`
- [ ] Implement: `pytest_jux/storage.py`
- [ ] Add XDG directory support (Linux, macOS, Windows)
- [ ] Implement storage modes (local, api, both, cache)
- [ ] Test atomic writes and permissions
- [ ] Achieve >85% coverage

**Day 6-7: REST API Client**
- [ ] Write tests: `tests/test_api_client.py`
- [ ] Implement: `pytest_jux/api_client.py`
- [ ] Add authentication support
- [ ] Add retry logic
- [ ] Test error handling
- [ ] Achieve >85% coverage

### Week 2: Publishing Integration & CLI

**Day 8-9: pytest Plugin Storage & Publishing**
- [ ] Update tests: `tests/test_plugin.py`
- [ ] Update: `pytest_jux/plugin.py`
- [ ] Add configuration for signing enabled/disabled
- [ ] Add storage + publishing logic to `pytest_sessionfinish`
- [ ] Test graceful degradation
- [ ] Achieve >85% coverage

**Day 10: Manual Publishing Command**
- [ ] Write tests: `tests/commands/test_publish.py`
- [ ] Implement: `pytest_jux/commands/publish.py`
- [ ] Add stdin/stdout support
- [ ] Add JSON output mode
- [ ] Test exit codes
- [ ] Achieve >85% coverage

**Day 11: Cache Management Command**
- [ ] Write tests: `tests/commands/test_cache.py`
- [ ] Implement: `pytest_jux/commands/cache.py`
- [ ] Implement subcommands (list, show, clean, push, stats)
- [ ] Add JSON output mode
- [ ] Test dry-run mode for destructive operations
- [ ] Achieve >85% coverage

### Week 3: Configuration CLI & Polish

**Day 12-13: Configuration Management Command**
- [ ] Write tests: `tests/commands/test_config.py`
- [ ] Implement: `pytest_jux/commands/config.py`
- [ ] Implement subcommands (list, dump, view, init, validate)
- [ ] Add JSON/YAML output formats
- [ ] Test configuration precedence and merging
- [ ] Achieve >85% coverage

**Day 14: Polish & Documentation**
- [ ] Update README.md with storage and publishing examples
- [ ] Update CLAUDE.md with architecture clarification
- [ ] Write usage documentation for cache and config management
- [ ] Update CHANGELOG.md
- [ ] End-to-end smoke testing (all storage modes, all commands)
- [ ] Sprint review
- [ ] Merge to `develop`

---

## Out of Scope (Handled by Jux API Server)

The following are explicitly **NOT** in Sprint 3 (handled by the Jux API server):

- ❌ SQLAlchemy models
- ❌ Database integration (SQLite/PostgreSQL)
- ❌ Duplicate detection logic (canonical hash comparison)
- ❌ Report storage and persistence
- ❌ Report querying and browsing
- ❌ Web UI for report visualization
- ❌ Signature verification server-side
- ❌ User authentication and authorization
- ❌ Multi-tenancy support

## Out of Scope (Future Enhancements)

The following are **NOT** in Sprint 3 but may be considered for future sprints:

- ❌ Batch publishing of multiple reports
- ❌ Advanced retry strategies (circuit breaker, exponential backoff with jitter)
- ❌ Webhook notifications (publish success/failure)
- ❌ Report analytics client-side
- ❌ Hardware security module (HSM) integration
- ❌ Certificate Authority (CA) integration
- ❌ Automatic cache size management with rotation policies
- ❌ Compression of stored reports (gzip)

---

## Complete Workflow Examples

### Example 1: Local Storage Only

```bash
# 1. Generate signing key
jux-keygen --type rsa --bits 2048 --cert --output ~/.jux/signing_key.pem

# 2. Configure pytest for local storage only
cat > pytest.ini << EOF
[pytest]
jux_enabled = true
jux_sign = true
jux_key_path = ~/.jux/signing_key.pem
jux_storage_mode = local
EOF

# 3. Run tests (automatic signing + local storage)
pytest --junit-xml=report.xml

# Output:
#   ✓ Tests completed: 42 passed, 2 failed
#   ✓ Report signed: report.xml
#   ✓ Stored locally: ~/.local/share/jux/reports/sha256-abc123...xml

# 4. List cached reports
jux-cache list
# Output:
#   sha256:abc123... | 2025-10-17 10:30:00 | 42 tests, 2 failed | local

# 5. View cache statistics
jux-cache stats
# Output:
#   Total reports: 15
#   Total size: 1.2 MB
#   Oldest: 2025-09-15
```

### Example 2: Cache Mode with Offline Fallback

```bash
# 1. Configure pytest with cache mode (API + local fallback)
cat > pytest.ini << EOF
[pytest]
jux_enabled = true
jux_sign = true
jux_publish = true
jux_storage_mode = cache
jux_api_url = https://jux.example.com/api/v1/reports
jux_api_key_env = JUX_API_KEY
jux_key_path = ~/.jux/signing_key.pem
EOF

# 2. Run tests (online - publishes to API and stores locally)
pytest --junit-xml=report.xml

# Output:
#   ✓ Tests completed: 42 passed, 2 failed
#   ✓ Report signed: report.xml
#   ✓ Stored locally: ~/.local/share/jux/reports/sha256-abc123...xml
#   ✓ Published to API: https://jux.example.com/reports/report-12345

# 3. Run tests again (offline - API unavailable, stores locally)
# Simulate offline by setting invalid API URL temporarily
pytest --junit-xml=report2.xml

# Output:
#   ✓ Tests completed: 35 passed, 1 failed
#   ✓ Report signed: report2.xml
#   ✓ Stored locally: ~/.local/share/jux/reports/sha256-def456...xml
#   ⚠ API unavailable, queued for retry

# 4. List cached reports (shows queued report)
jux-cache list
# Output:
#   sha256:abc123... | 2025-10-17 10:30:00 | 42 tests, 2 failed | published
#   sha256:def456... | 2025-10-17 11:45:00 | 35 tests, 1 failed | queued

# 5. Retry publishing queued reports (when back online)
jux-cache push
# Output:
#   Publishing queued reports...
#   ✓ sha256:def456... published successfully
#   Published 1 report(s), 0 failed
```

### Example 3: Store Locally AND Publish to API

```bash
# 1. Configure pytest to both store locally and publish
cat > ~/.jux/config << EOF
[jux]
enabled = true
sign = true
publish = true
storage_mode = both
api_url = https://jux.example.com/api/v1/reports
api_key = secret-api-key-here
key_path = ~/.jux/signing_key.pem
EOF

# 2. Run tests (stores locally AND publishes)
pytest --junit-xml=report.xml

# Output:
#   ✓ Tests completed: 42 passed, 2 failed
#   ✓ Report signed: report.xml
#   ✓ Stored locally: ~/.local/share/jux/reports/sha256-abc123...xml
#   ✓ Published to API: https://jux.example.com/reports/report-12345

# 3. Inspect local cached report
jux-cache show sha256:abc123...
# Output: [Full report with metadata]

# 4. Clean old reports (older than 30 days)
jux-cache clean --days 30
# Output: Removed 5 reports (1.2 MB freed)
```

### Example 4: Manual Workflow with CLI Commands

```bash
# 1. Generate key
jux-keygen --type rsa --bits 2048 --cert --output ~/.jux/signing_key.pem

# 2. Sign report manually
jux-sign --input report.xml --output signed-report.xml \
  --key ~/.jux/signing_key.pem --cert ~/.jux/signing_key.crt

# 3. Inspect signed report
jux-inspect signed-report.xml
# Output:
#   Tests: 42
#   Failures: 2
#   Canonical Hash: sha256:abc123...
#   Signature: RSA-SHA256 (valid)

# 4. Verify signature
jux-verify --input signed-report.xml --cert ~/.jux/signing_key.crt
# Output: ✓ Signature valid

# 5. Publish manually
jux-publish --input signed-report.xml \
  --api-url https://jux.example.com/api/v1/reports \
  --api-key secret-api-key
# Output: ✓ Published successfully (report-12345)
```

### Example 5: Configuration Management and Debugging

```bash
# 1. Initialize configuration file with defaults
jux-config init
# Output: Created configuration file: ~/.jux/config

# 2. List all available configuration options
jux-config list
# Output:
#   jux_enabled          (bool)   Enable pytest-jux plugin [default: false]
#   jux_sign             (bool)   Enable report signing [default: false]
#   jux_publish          (bool)   Enable API publishing [default: false]
#   jux_storage_mode     (enum)   Storage mode: local|api|both|cache [default: local]
#   jux_api_url          (str)    API endpoint URL
#   jux_key_path         (path)   Path to signing key (PEM format)
#   ... (more options)

# 3. Edit configuration file
vim ~/.jux/config
# Add your settings:
#   [jux]
#   enabled = true
#   sign = true
#   key_path = ~/.jux/signing_key.pem
#   storage_mode = cache

# 4. Dump current effective configuration (debug)
jux-config dump
# Output:
#   Configuration from multiple sources:
#
#   jux_enabled = true                    (source: ~/.jux/config)
#   jux_sign = true                       (source: ~/.jux/config)
#   jux_key_path = ~/.jux/signing_key.pem (source: ~/.jux/config)
#   jux_storage_mode = cache              (source: ~/.jux/config)
#   jux_api_url = <not set>

# 5. Validate configuration
jux-config validate --strict
# Output:
#   ⚠ Warning: jux_sign enabled but jux_cert_path not set
#   ⚠ Warning: jux_storage_mode is 'cache' but jux_api_url not configured
#   Configuration has warnings but is valid

# 6. View all configuration files with precedence
jux-config view --all
# Output:
#   Configuration files (in precedence order):
#
#   1. ~/.jux/config (user-level) ✓ exists
#      [jux]
#      enabled = true
#      sign = true
#      ...
#
#   2. pytest.ini (project-level) ✗ not found
#
#   3. /etc/jux/config (system-level) ✗ not found

# 7. Export configuration as JSON (for scripting)
jux-config dump --format json
# Output: {"jux_enabled": true, "jux_sign": true, ...}

# 8. Validate configuration before running tests
jux-config validate && pytest
# Output: ✓ Configuration is valid
#         (pytest runs...)
```

---

## Sprint 3 Completion Status

### ✅ Completed (2025-10-18)

**Modules Implemented** (5 modules, 118 tests, >85% average coverage):
1. **Configuration Management** (`pytest_jux/config.py`):
   - ✅ Multi-source configuration (CLI, environment, files)
   - ✅ ConfigSchema with all configuration options
   - ✅ ConfigurationManager with load/validate/dump methods
   - ✅ Configuration precedence: CLI > env > files > defaults
   - ✅ Strict validation mode for dependency checking
   - ✅ 25 comprehensive tests, 85.05% code coverage

2. **Environment Metadata** (`pytest_jux/metadata.py`):
   - ✅ EnvironmentMetadata dataclass for test context
   - ✅ capture_metadata() function for automatic collection
   - ✅ System information (hostname, username, platform)
   - ✅ Python and pytest version tracking
   - ✅ ISO 8601 timestamps with UTC timezone
   - ✅ Environment variable capture
   - ✅ 19 comprehensive tests, 92.98% code coverage

3. **Local Storage & Caching** (`pytest_jux/storage.py`):
   - ✅ XDG-compliant storage paths (macOS, Linux, Windows)
   - ✅ Four storage modes: LOCAL, API, BOTH, CACHE
   - ✅ ReportStorage class with atomic file writes
   - ✅ Offline queue for network-resilient operation
   - ✅ Secure file permissions (0600 on Unix)
   - ✅ get_default_storage_path() for platform detection
   - ✅ 33 comprehensive tests, 80.33% code coverage

4. **Cache Management CLI** (`pytest_jux/commands/cache.py`):
   - ✅ `jux-cache list`: List all cached reports
   - ✅ `jux-cache show`: Show report details by hash
   - ✅ `jux-cache stats`: View cache statistics
   - ✅ `jux-cache clean`: Remove old reports with dry-run mode
   - ✅ JSON output support for all subcommands
   - ✅ Custom storage path support
   - ✅ 16 comprehensive tests, 84.13% code coverage

5. **Configuration Management CLI** (`pytest_jux/commands/config_cmd.py`):
   - ✅ `jux-config list`: List all configuration options
   - ✅ `jux-config dump`: Show effective configuration with sources
   - ✅ `jux-config view`: View configuration files
   - ✅ `jux-config init`: Initialize configuration file (minimal/full templates)
   - ✅ `jux-config validate`: Validate configuration with strict mode
   - ✅ JSON output support for all subcommands
   - ✅ 25 comprehensive tests, 91.32% code coverage

**Documentation Completed**:
- ✅ Multi-environment configuration guide (docs/howto/multi-environment-config.md)
- ✅ CLAUDE.md updated with uv run best practices
- ✅ CHANGELOG.md updated for v0.1.4 release
- ✅ Sprint 3 retrospective (docs/sprints/sprint-03-retrospective.md)

### ⏸️ Postponed to Sprint 4

**Reason**: No Jux API Server available yet for testing/integration

**Deferred Items**:
1. **REST API Client** (`pytest_jux/api_client.py`):
   - ⏸️ HTTP client for POST requests to Jux API
   - ⏸️ JSON payload construction with signed XML and metadata
   - ⏸️ API authentication (API keys, bearer tokens)
   - ⏸️ Request timeout and retry logic

2. **Manual Publishing Command** (`pytest_jux/commands/publish.py`):
   - ⏸️ `jux-publish`: Manual report publishing to API
   - ⏸️ Queue processing and retry logic

3. **Plugin Integration**:
   - ⏸️ Automatic publishing after test execution
   - ⏸️ Integration with storage and API client

**Next Steps**: Sprint 4 will implement API client and publishing when Jux API Server is available.

---

## Notes

- **TDD Approach**: Write tests first, then implement
- **Client-Side Focus**: This sprint is exclusively client-side (no server implementation)
- **Disabled by Default**: Signing and publishing are opt-in via configuration
- **Graceful Degradation**: Publishing failures should not block test execution
- **Offline Resilience**: Cache mode enables offline work with automatic retry
- **XDG Compliance**: Use platform-appropriate storage directories
- **Security**: API keys should never be logged or printed
- **Type Hints**: Use strict type checking for all functions
- **Documentation**: Every public function needs comprehensive docstrings
- **Storage Modes**: Support local-only, API-only, both, and cache (offline fallback)

---

**Sprint Lead**: AI-Assisted Development
**Reviewed By**: Georges Martin
**Last Updated**: 2025-10-18
**Status**: ✅ Complete (v0.1.3, v0.1.4)
