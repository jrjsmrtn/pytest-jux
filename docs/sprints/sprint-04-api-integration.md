# Sprint 4: REST API Client & Plugin Integration

**Sprint Duration**: TBD (pending Jux API Server availability)
**Sprint Goal**: Implement REST API client, resolve technical debt, and integrate storage with pytest plugin
**Status**: 📋 Planned
**Target Release**: v0.2.0 (Beta Milestone)

---

## Overview

Sprint 4 completes the core pytest-jux workflow by implementing:
- **REST API client**: HTTP client for publishing signed reports to Jux API Server
- **Plugin integration**: Automatic storage and publishing after test execution
- **Technical debt resolution**: Fix mypy errors, improve coverage, resolve linting warnings
- **Integration testing**: End-to-end tests with actual pytest execution
- **Beta preparation**: Polish for 0.2.0 release

This sprint transforms pytest-jux from a collection of tools into a **complete end-to-end solution** for signed test report management.

### Sprint Dependencies

**CRITICAL DEPENDENCY**: Jux API Server with REST API endpoints

**Contingency Plan** (if API server not ready):
1. **Phase 1**: Resolve technical debt (mypy, coverage, linting) - 2-3 days
2. **Phase 2**: Plugin integration with local storage only - 2-3 days
3. **Phase 3**: Mock-based API client development - 3-4 days
4. **Phase 4**: Integration testing with local storage - 2 days
5. **Phase 5**: API integration when server ready - 3-4 days

**Total**: 12-16 days (can be split across multiple calendar periods)

---

## Sprint 3 Technical Debt Carryover

From Sprint 3 Retrospective, **must address**:

### High Priority Technical Debt

1. **mypy Type Checking Errors** (26 errors with `rich` imports)
   - Impact: Reduced type safety benefits
   - Estimated effort: 0.5-1 day
   - Action: Install `types-rich` stub package, fix remaining errors

2. **Storage Module Coverage** (80.33%, target >85%)
   - Impact: Potential edge case bugs in security-critical code
   - Estimated effort: 1 day
   - Action: Add tests for filesystem errors, race conditions, XDG fallbacks

3. **ruff Linting Warnings** (5 warnings)
   - Impact: Minor style inconsistencies
   - Estimated effort: 0.5 day
   - Action: Convert Union to X | Y syntax, fix exception chaining

**Total Technical Debt**: 2-2.5 days

---

## User Stories

### US-4.1: REST API Client

**As a** developer
**I want** a REST API client for publishing signed reports
**So that** I can integrate pytest-jux with the Jux backend

**Acceptance Criteria**:
- [ ] HTTP client for POST `/api/v1/reports` endpoint
- [ ] JSON payload construction with signed XML and metadata
- [ ] Support for API authentication (API key header, bearer token)
- [ ] Configurable API endpoint URL via configuration
- [ ] Request timeout configuration (default: 30s)
- [ ] Retry logic for transient failures (max 3 retries with backoff)
- [ ] Proper error handling (network errors, HTTP 4xx/5xx)
- [ ] Response parsing (201 Created, 409 Conflict, 400/401/500)
- [ ] SSL/TLS certificate verification with certifi
- [ ] >85% test coverage for api_client module

**Technical Tasks**:
- [ ] Create `pytest_jux/api_client.py`
- [ ] Implement `JuxAPIClient` class with `publish_report()` method
- [ ] Add authentication support (X-API-Key header, Authorization: Bearer)
- [ ] Add retry logic with exponential backoff (requests.adapters.HTTPAdapter)
- [ ] Write comprehensive unit tests with mocked HTTP responses (responses library)
- [ ] Add integration tests against test API server (optional, if available)
- [ ] Document API client usage in docstrings

**API Request Format**:
```json
{
  "report": "<testsuite>...</testsuite>",
  "canonical_hash": "sha256:abc123...",
  "signature_algorithm": "RSA-SHA256",
  "metadata": {
    "hostname": "ci-runner-01",
    "username": "jenkins",
    "platform": "Linux-5.15.0-x86_64",
    "python_version": "3.11.5",
    "pytest_version": "8.0.0",
    "timestamp": "2025-10-18T12:00:00Z",
    "environment": {}
  }
}
```

**API Response Handling**:
- `201 Created`: Report accepted and stored → Success
- `409 Conflict`: Duplicate report (already exists) → Log warning, continue
- `400 Bad Request`: Invalid XML or signature → Log error, fail
- `401 Unauthorized`: Authentication failed → Log error, fail
- `500 Internal Server Error`: Server error → Retry with backoff
- `503 Service Unavailable`: Server down → Retry, queue locally if cache mode

**Estimated Effort**: 3-4 days

---

### US-4.2: Plugin Integration with Storage

**As a** pytest user
**I want** reports automatically stored/published after test execution
**So that** I don't need manual intervention

**Acceptance Criteria**:
- [ ] pytest hook integration: `pytest_sessionfinish` stores/publishes reports
- [ ] Respect `jux_enabled` configuration (default: false)
- [ ] Respect `jux_storage_mode` configuration (LOCAL, API, BOTH, CACHE)
- [ ] LOCAL mode: Store signed reports in XDG-compliant directory
- [ ] API mode: Publish signed reports to Jux API (fail if network error)
- [ ] BOTH mode: Store locally AND publish to API
- [ ] CACHE mode: Store locally, publish to API with offline queue fallback
- [ ] Graceful degradation: Network failures don't block test execution
- [ ] Capture environment metadata automatically
- [ ] Log storage/publishing status to pytest output
- [ ] >85% test coverage for plugin integration

**Technical Tasks**:
- [ ] Update `pytest_jux/plugin.py` with storage integration
- [ ] Add configuration options to `pytest_addoption` hook
- [ ] Implement storage mode handling in `pytest_sessionfinish`
- [ ] Integrate metadata capture from `pytest_jux.metadata`
- [ ] Integrate API client from `pytest_jux.api_client`
- [ ] Add error handling and logging (warnings for failures)
- [ ] Update tests: `tests/test_plugin.py` with storage scenarios
- [ ] Test all storage modes (LOCAL, API, BOTH, CACHE)
- [ ] Test graceful degradation (network failures, permission errors)

**Configuration Example**:
```ini
# ~/.jux/config
[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = cache
storage_path = ~/.local/share/jux/reports
api_url = https://jux.example.com/api/v1/reports
api_key = <from environment variable>
```

**Estimated Effort**: 2-3 days

---

### US-4.3: Manual Publishing Command

**As a** system administrator
**I want** to manually publish cached reports
**So that** I can retry failed uploads or publish offline-generated reports

**Acceptance Criteria**:
- [ ] `jux-publish` command publishes single report or all queued reports
- [ ] Publish specific report: `jux-publish --file report.xml`
- [ ] Publish all queued: `jux-publish --queue`
- [ ] Process offline queue: `jux-publish --process-queue`
- [ ] Dry-run mode: `jux-publish --dry-run` (show what would be published)
- [ ] JSON output for scripting: `jux-publish --json`
- [ ] Exit codes: 0 = success, 1 = failure, 2 = partial success
- [ ] Verbose logging option: `--verbose`
- [ ] >85% test coverage for publish command

**Technical Tasks**:
- [ ] Create `pytest_jux/commands/publish.py`
- [ ] Implement CLI argument parsing (argparse or configargparse)
- [ ] Integrate API client for publishing
- [ ] Add queue processing logic (iterate offline queue)
- [ ] Add dry-run mode (read queue, don't publish)
- [ ] Write comprehensive tests: `tests/commands/test_publish.py`
- [ ] Test single file publishing
- [ ] Test queue processing
- [ ] Test error handling (network errors, authentication failures)

**CLI Examples**:
```bash
# Publish single report
jux-publish --file /path/to/report.xml

# Publish all queued reports
jux-publish --queue

# Dry-run (show what would be published)
jux-publish --queue --dry-run

# Process queue with verbose logging
jux-publish --process-queue --verbose

# JSON output for scripting
jux-publish --queue --json
```

**Estimated Effort**: 2 days

---

### US-4.4: Resolve Technical Debt

**As a** maintainer
**I want** to resolve Sprint 3 technical debt
**So that** code quality meets project standards

**Acceptance Criteria**:
- [ ] mypy passes with 0 errors (strict mode)
- [ ] All modules achieve >85% code coverage
- [ ] ruff linting passes with 0 warnings
- [ ] All tests pass (260+ tests)
- [ ] Documentation updated for any API changes

**Technical Tasks**:

**1. Fix mypy Type Checking Errors** (26 errors)
- [ ] Install `types-rich` stub package: `uv pip install types-rich`
- [ ] Add `rich` to `[tool.mypy]` ignore if needed
- [ ] Fix remaining import-not-found errors
- [ ] Run `uv run mypy --strict pytest_jux` and verify 0 errors

**2. Improve Storage Module Coverage** (80.33% → >85%)
- [ ] Add tests for filesystem permission errors (read-only dirs)
- [ ] Test atomic write race conditions (concurrent writes)
- [ ] Test XDG fallback behavior (missing env vars)
- [ ] Test secure file permissions (Unix 0600 validation)
- [ ] Run `uv run pytest --cov=pytest_jux.storage` and verify >85%

**3. Fix ruff Linting Warnings** (5 warnings)
- [ ] UP007: Convert `Union[X, Y]` to `X | Y` syntax (keygen.py, verifier.py)
- [ ] B904: Add `raise ... from err` for exception chaining (verifier.py)
- [ ] S110: Add logging to try-except-pass blocks (test_plugin.py)
- [ ] Run `uv run ruff check .` and verify 0 warnings

**Estimated Effort**: 2-2.5 days

---

### US-4.5: Integration Testing

**As a** developer
**I want** end-to-end integration tests
**So that** I can verify the complete workflow

**Acceptance Criteria**:
- [ ] End-to-end pytest execution tests (sign + store)
- [ ] Test configuration loading in real pytest sessions
- [ ] Test storage persistence across multiple test runs
- [ ] Test API publishing (if test server available)
- [ ] Test graceful degradation (network failures, permission errors)
- [ ] Integration tests run in CI/CD pipeline
- [ ] >85% coverage for integration test suite

**Technical Tasks**:
- [ ] Create `tests/integration/` directory
- [ ] Write `test_e2e_signing.py` (pytest execution → signed report)
- [ ] Write `test_e2e_storage.py` (storage modes → file system)
- [ ] Write `test_e2e_api.py` (API publishing, if server available)
- [ ] Write `test_e2e_config.py` (configuration loading in pytest)
- [ ] Add integration test target to Makefile
- [ ] Document integration test setup in CONTRIBUTING.md

**Test Scenarios**:
1. **Sign and store locally**: `pytest --jux-sign --jux-key <key> --jux-storage-mode local`
2. **Sign and publish**: `pytest --jux-sign --jux-key <key> --jux-storage-mode api`
3. **Cache mode with network failure**: Verify offline queue creation
4. **Configuration precedence**: CLI > env > file > defaults
5. **Multiple test runs**: Verify no duplicate storage

**Estimated Effort**: 2 days

---

## Technical Design

### REST API Client Architecture

```python
# pytest_jux/api_client.py

from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel

class PublishRequest(BaseModel):
    """API request payload for publishing reports."""
    report: str  # Signed JUnit XML
    canonical_hash: str  # sha256:...
    signature_algorithm: str  # RSA-SHA256, ECDSA-SHA256
    metadata: Dict[str, Any]  # Environment metadata

class PublishResponse(BaseModel):
    """API response from publishing endpoint."""
    status: str  # created, duplicate, error
    id: Optional[str] = None  # Report ID
    canonical_hash: Optional[str] = None
    message: str

class JuxAPIClient:
    """HTTP client for Jux REST API."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize API client with configuration."""
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

        # Session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Authentication headers
        if api_key:
            self.session.headers["X-API-Key"] = api_key
        elif bearer_token:
            self.session.headers["Authorization"] = f"Bearer {bearer_token}"

    def publish_report(
        self,
        signed_xml: str,
        canonical_hash: str,
        signature_algorithm: str,
        metadata: Dict[str, Any],
    ) -> PublishResponse:
        """
        Publish signed report to Jux API.

        Args:
            signed_xml: Signed JUnit XML report
            canonical_hash: Canonical SHA-256 hash (sha256:...)
            signature_algorithm: Signature algorithm used
            metadata: Environment metadata

        Returns:
            PublishResponse with status and details

        Raises:
            requests.exceptions.RequestException: Network/HTTP errors
            ValueError: Invalid response format
        """
        request = PublishRequest(
            report=signed_xml,
            canonical_hash=canonical_hash,
            signature_algorithm=signature_algorithm,
            metadata=metadata,
        )

        try:
            response = self.session.post(
                f"{self.api_url}/reports",
                json=request.model_dump(),
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            return PublishResponse(**data)

        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"Request timeout after {self.timeout}s"
            )
        except requests.exceptions.HTTPError as e:
            # Parse error response if available
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    return PublishResponse(**error_data)
                except Exception:
                    pass
            raise
```

### Plugin Integration Flow

```
pytest execution
    ↓
pytest_sessionfinish hook
    ↓
Check: jux_enabled = true?
    ↓ (yes)
Load configuration (CLI > env > file > defaults)
    ↓
Check: JUnit XML file exists?
    ↓ (yes)
Check: jux_sign = true?
    ↓ (yes)
Sign XML with key (existing functionality)
    ↓
Capture environment metadata
    ↓
Check storage_mode:
    ├─ LOCAL: store_locally() only
    ├─ API: publish_to_api() only (fail if error)
    ├─ BOTH: store_locally() + publish_to_api()
    └─ CACHE: store_locally() + try publish_to_api()
                 (queue if network error)
    ↓
Log results (warnings if failures)
    ↓
Complete (don't block pytest)
```

---

## Implementation Order (TDD)

### Phase 1: Technical Debt Resolution (2-2.5 days)

**Goal**: Clean code foundation before new features

1. **Fix mypy errors** (0.5-1 day)
   - Install `types-rich`
   - Fix import-not-found errors
   - Verify `uv run mypy --strict pytest_jux` passes

2. **Improve storage coverage** (1 day)
   - Write tests: filesystem errors, race conditions, XDG fallbacks
   - Target: >85% coverage for storage.py

3. **Fix ruff warnings** (0.5 day)
   - Convert Union → X | Y syntax
   - Add exception chaining
   - Add logging to try-except-pass

**Deliverable**: Clean codebase (0 mypy errors, 0 ruff warnings, >85% coverage)

---

### Phase 2: REST API Client (3-4 days)

**Goal**: HTTP client for publishing reports (if API server ready)

**Day 1-2**: Core API Client
- [ ] Write tests: `tests/test_api_client.py`
  - Test request payload construction
  - Test authentication (API key, bearer token)
  - Test response parsing (201, 409, 400, 401, 500)
  - Mock HTTP responses with `responses` library
- [ ] Implement: `pytest_jux/api_client.py`
  - `JuxAPIClient` class
  - `publish_report()` method
  - Pydantic request/response schemas
  - Authentication headers

**Day 3**: Retry Logic & Error Handling
- [ ] Write tests: retry scenarios, network errors, timeouts
- [ ] Implement: retry with exponential backoff (HTTPAdapter)
- [ ] Implement: error handling and logging
- [ ] Test: timeout configuration

**Day 4**: Integration Testing (optional)
- [ ] If test API server available: integration tests
- [ ] If not: additional unit tests with edge cases
- [ ] Documentation: API client usage in docstrings

**Deliverable**: `api_client.py` (>85% coverage)

---

### Phase 3: Plugin Integration (2-3 days)

**Goal**: Automatic storage/publishing after pytest execution

**Day 1**: Storage Integration
- [ ] Write tests: `tests/test_plugin.py` (storage scenarios)
  - Test LOCAL mode (store only)
  - Test CACHE mode (store + queue)
  - Test graceful degradation (permission errors)
- [ ] Update: `pytest_jux/plugin.py`
  - Import storage module
  - Add storage mode handling in `pytest_sessionfinish`
  - Integrate environment metadata capture

**Day 2**: API Integration
- [ ] Write tests: API publishing scenarios
  - Test API mode (publish only)
  - Test BOTH mode (store + publish)
  - Test CACHE mode with network failure (offline queue)
- [ ] Update: `pytest_jux/plugin.py`
  - Import API client
  - Add API publishing logic
  - Handle authentication from configuration

**Day 3**: Configuration & Polish
- [ ] Write tests: configuration loading, precedence
- [ ] Add: logging and user-facing messages
- [ ] Test: all storage modes end-to-end
- [ ] Documentation: plugin usage examples

**Deliverable**: Integrated plugin (>85% coverage)

---

### Phase 4: Publishing Command (2 days)

**Goal**: Manual publishing CLI tool

**Day 1**: Core Command
- [ ] Write tests: `tests/commands/test_publish.py`
  - Test single file publishing
  - Test queue processing
  - Test dry-run mode
- [ ] Implement: `pytest_jux/commands/publish.py`
  - CLI argument parsing
  - Single file publishing
  - Queue iteration

**Day 2**: Advanced Features & Polish
- [ ] Write tests: error handling, JSON output
- [ ] Implement: verbose logging, JSON output
- [ ] Add: CLI entry point to `pyproject.toml`
- [ ] Documentation: command usage and examples

**Deliverable**: `jux-publish` command (>85% coverage)

---

### Phase 5: Integration Testing & Polish (2 days)

**Goal**: End-to-end validation

**Day 1**: Integration Tests
- [ ] Create: `tests/integration/` directory
- [ ] Write: `test_e2e_signing.py` (pytest execution → signed report)
- [ ] Write: `test_e2e_storage.py` (storage modes → filesystem)
- [ ] Write: `test_e2e_config.py` (configuration loading)

**Day 2**: Documentation & Release Prep
- [ ] Update: README.md with complete workflow examples
- [ ] Update: CHANGELOG.md for 0.2.0 release
- [ ] Create: Sprint 4 retrospective
- [ ] Verify: all quality checks pass (mypy, ruff, pytest, coverage)

**Deliverable**: v0.2.0 release candidate

---

## Test Strategy

### Unit Tests

**API Client Tests** (`tests/test_api_client.py`):
- Mock HTTP responses using `responses` library
- Test authentication (API key, bearer token, none)
- Test error handling (network errors, timeouts, HTTP 4xx/5xx)
- Test retry logic (transient failures, max retries)
- Test response parsing (201 Created, 409 Conflict, 400/401/500)

**Plugin Tests** (`tests/test_plugin.py`):
- Mock storage and API client to avoid filesystem/network I/O
- Test all storage modes (LOCAL, API, BOTH, CACHE)
- Test graceful degradation (network failures, permission errors)
- Test configuration loading (CLI options, config files)
- Test environment metadata capture

**Publish Command Tests** (`tests/commands/test_publish.py`):
- Mock API client for predictable responses
- Test single file publishing
- Test queue processing (multiple reports)
- Test dry-run mode (no actual publishing)
- Test JSON output format
- Test exit codes (0, 1, 2)

### Integration Tests

**End-to-End Tests** (`tests/integration/`):
- Run actual pytest execution in subprocess
- Verify signed reports created in filesystem
- Verify storage modes work as expected
- Test configuration loading from files
- Test API publishing (if test server available)

**Coverage Target**: >85% for all new modules, >90% for security-critical code

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
  "report": "<testsuite name=\"tests\">...</testsuite>",
  "canonical_hash": "sha256:abc123...",
  "signature_algorithm": "RSA-SHA256",
  "metadata": {
    "hostname": "ci-runner-01",
    "username": "jenkins",
    "platform": "Linux-5.15.0-x86_64",
    "python_version": "3.11.5",
    "pytest_version": "8.0.0",
    "timestamp": "2025-10-18T12:00:00Z",
    "environment": {
      "CI": "true",
      "BUILD_NUMBER": "42"
    }
  }
}
```

**Response (201 Created - Success):**
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
  "message": "Report already exists (duplicate detected by canonical hash)"
}
```

**Response (400 Bad Request - Invalid):**
```json
{
  "status": "error",
  "error": "InvalidSignature",
  "message": "XMLDSig signature verification failed"
}
```

**Response (401 Unauthorized - Auth Failure):**
```json
{
  "status": "error",
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

**Response (500 Internal Server Error):**
```json
{
  "status": "error",
  "error": "InternalServerError",
  "message": "Database connection failed"
}
```

---

## Configuration Updates

### New Configuration Options

Add to `pytest_jux/config.py`:

```python
class ConfigSchema(BaseModel):
    # ... existing options ...

    # API configuration (new)
    jux_api_url: Optional[str] = Field(
        default=None,
        description="Jux API endpoint URL (e.g., https://jux.example.com/api/v1)",
    )
    jux_api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (X-API-Key header)",
    )
    jux_bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token for authentication (Authorization header)",
    )
    jux_api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds",
    )
    jux_api_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts for failed API requests",
    )
```

### Example Configuration

```ini
# ~/.jux/config
[jux]
# Core settings
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
cert_path = ~/.jux/signing_key.crt

# Storage settings
storage_mode = cache
storage_path = ~/.local/share/jux/reports

# API settings (new in Sprint 4)
api_url = https://jux.example.com/api/v1
# api_key set via environment variable: JUX_API_KEY
api_timeout = 30
api_max_retries = 3
```

---

## Definition of Done

### Sprint 4 Completion Criteria

**Code Quality**:
- [ ] All tests pass (300+ tests expected)
- [ ] Test coverage >85% overall (>90% for security-critical modules)
- [ ] mypy strict mode passes with 0 errors
- [ ] ruff linting passes with 0 warnings
- [ ] No regressions in existing functionality

**Features**:
- [ ] REST API client implemented (`api_client.py`)
- [ ] Plugin integration with storage and API (`plugin.py`)
- [ ] Manual publishing command (`jux-publish`)
- [ ] All storage modes work (LOCAL, API, BOTH, CACHE)
- [ ] Graceful degradation on network failures

**Technical Debt**:
- [ ] mypy errors resolved (0 errors)
- [ ] Storage coverage >85%
- [ ] ruff warnings resolved (0 warnings)

**Documentation**:
- [ ] API client documented (docstrings, examples)
- [ ] Plugin integration documented (README.md)
- [ ] Publishing command documented (CLI help, examples)
- [ ] CHANGELOG.md updated for 0.2.0
- [ ] Sprint 4 retrospective completed

**Release**:
- [ ] Version bumped to 0.2.0
- [ ] Git tag: v0.2.0
- [ ] Release notes prepared

---

## Risks and Mitigations

### High-Risk Items

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Jux API Server not ready** | High | High | Develop with mocks, integrate later when ready |
| **API contract changes** | Medium | High | Version API endpoints, maintain compatibility |
| **Network timeout issues** | Medium | Medium | Implement robust retry logic, cache mode default |
| **Certificate validation failures** | Low | High | Use certifi CA bundle, document self-signed setup |
| **Performance degradation** | Low | Medium | Profile pytest overhead, optimize if >5% slowdown |

### Medium-Risk Items

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Storage race conditions** | Low | Medium | Atomic writes (already implemented), add tests |
| **Configuration complexity** | Medium | Low | Provide templates, improve validation errors |
| **Integration test flakiness** | Medium | Low | Retry flaky tests, improve isolation |
| **Type checking regressions** | Low | Low | Run mypy in CI/CD, enforce strict mode |

---

## Success Metrics

### Sprint Velocity

**Estimated Duration**: 12-16 days (can span multiple calendar periods)

**Phase Breakdown**:
- Phase 1: Technical debt (2-2.5 days)
- Phase 2: API client (3-4 days)
- Phase 3: Plugin integration (2-3 days)
- Phase 4: Publishing command (2 days)
- Phase 5: Integration testing & polish (2 days)

### Quality Metrics

**Code Coverage**:
- Target: >85% overall
- Security-critical (api_client.py): >90%
- Plugin (plugin.py): >85%

**Test Count**:
- Expected: 300+ tests (current: 260)
- New tests: ~40-50

**Code Quality**:
- mypy errors: 0 (current: 26)
- ruff warnings: 0 (current: 5)
- Test failures: 0

### Feature Completeness

**Must-Have** (Sprint 4 MVP):
- [ ] REST API client with retry logic
- [ ] Plugin integration with LOCAL and CACHE modes
- [ ] Technical debt resolved (mypy, coverage, ruff)

**Should-Have** (Sprint 4 Complete):
- [ ] All storage modes (LOCAL, API, BOTH, CACHE)
- [ ] Manual publishing command (jux-publish)
- [ ] Integration tests

**Nice-to-Have** (Sprint 4 Polish):
- [ ] API integration tests (if test server ready)
- [ ] Performance profiling and optimization
- [ ] Additional documentation (tutorials, how-tos)

---

## Sprint 4 Retrospective Template

At completion, address:
- What went well?
- What could be improved?
- Lessons learned?
- Technical debt incurred?
- Technical debt resolved?
- Sprint grade (A-F)?
- Recommendations for future sprints?

---

## Notes

### Development Principles

- **TDD Approach**: Write tests first, then implement
- **Client-Side Focus**: This sprint completes client-side functionality
- **Graceful Degradation**: Network failures must not block pytest execution
- **Security First**: API keys never logged or printed
- **Type Safety**: Maintain strict mypy compliance
- **Documentation**: Every public function needs comprehensive docstrings
- **Performance**: Pytest overhead should be <5% of test execution time

### API Server Integration

**If API Server Ready**:
- Develop against real API endpoints
- Integration tests with test server
- Validate API contract matches documentation

**If API Server Not Ready**:
- Develop with mocked HTTP responses
- Document API contract assumptions
- Plan integration testing for future sprint

### Beta Release (0.2.0)

**Significance**: First feature-complete version
- All core workflows implemented (sign → store → publish)
- Production-ready for early adopters
- Comprehensive documentation
- High test coverage (>85%)
- Clean codebase (0 mypy/ruff errors)

**Post-Beta**:
- Gather user feedback
- Plan 1.0.0 release with production hardening
- Consider HSM support (future)
- Consider API v2 features (future)

---

**Sprint Lead**: AI-Assisted Development
**Reviewed By**: Georges Martin
**Created**: 2025-10-18
**Status**: 📋 Planned (awaiting Jux API Server)
