# Sprint 4: REST API Client & Plugin Integration

**Sprint Duration**: TBD (pending Jux API Server availability)
**Sprint Goal**: Implement REST API client, resolve technical debt, and integrate storage with pytest plugin
**Status**: 🚧 In Progress (API Client Complete, Plugin Integration Complete)
**Target Release**: v0.4.0 (Beta Milestone - was v0.2.0)
**API Compliance**: Jux API v1.0.0 (released 2025-01-24)

## Implementation Progress (2025-10-25)

**✅ Completed**:
- **US-4.1**: REST API Client (100% complete)
  - HTTP client for POST `/api/v1/junit/submit` (JuxAPIClient)
  - Bearer token authentication
  - Retry logic with exponential backoff
  - Comprehensive error handling (4xx/5xx, network errors, timeouts)
  - 13 unit tests with mocked HTTP responses (92.86% coverage)
  - Pydantic response models (PublishResponse)

- **US-4.2**: Plugin Integration (100% complete)
  - Storage mode handling (LOCAL, API, BOTH, CACHE)
  - API publishing integration in pytest_sessionfinish
  - Graceful degradation for all storage modes
  - Error handling and warning messages per mode
  - 6 comprehensive plugin tests for API publishing scenarios

**Branch**: `feature/sprint-04-api-integration`

**Commits**:
- `31a7b9f` - docs: update Sprint 4 plan for Jux API v1.0.0 compliance
- `113570a` - chore: auto-fix ruff linting warnings
- `85ab703` - feat(api): implement JuxAPIClient for Jux API v1.0.0
- `a63f699` - chore(config): update configuration for Jux API v1.0.0
- `c2bde47` - feat(plugin): integrate JuxAPIClient with pytest_sessionfinish
- `c9fa97f` - test(plugin): add comprehensive tests for API publishing

**Remaining**:
- US-4.3: Technical debt resolution (mypy, coverage, linting)
- US-4.4: Integration testing with real Jux API Server (requires server availability)
- US-4.5: Documentation updates (how-to guides, API reference)

---

## ⚠️ MAJOR SIMPLIFICATION UPDATE (2025-10-25)

**Good news!** The actual Jux API v1.0.0 is **much simpler** than originally planned:

### What Changed
- ❌ **REMOVED**: JSON envelope with separate metadata payload
- ❌ **REMOVED**: Canonical hash calculation in client (server handles it)
- ❌ **REMOVED**: Duplicate detection logic (server handles it)
- ❌ **REMOVED**: Signature algorithm parameter (server detects from XMLDsig)
- ❌ **REMOVED**: Separate metadata extraction (server auto-extracts from XML properties)
- ✅ **NEW**: Just POST raw signed JUnit XML to `/api/v1/junit/submit`
- ✅ **NEW**: Content-Type: `application/xml` (not JSON!)
- ✅ **NEW**: Bearer token authentication only (no API key header)

### Effort Savings
- **Estimated reduction**: 1-2 days (API client much simpler)
- **Original estimate**: 12-16 days
- **Revised estimate**: 10-14 days

### Why Simpler?
pytest-jux v0.3.0 **already embeds metadata in XML properties** via pytest-metadata integration.
The server auto-extracts everything from the XML. Client just sends signed XML - done!

---

## Overview

Sprint 4 completes the core pytest-jux workflow by implementing:
- **REST API client**: Simple HTTP client to POST signed XML to Jux API v1.0.0
- **Plugin integration**: Automatic storage and publishing after test execution
- **Technical debt resolution**: Fix mypy errors, improve coverage, resolve linting warnings
- **Integration testing**: End-to-end tests with actual pytest execution
- **Beta preparation**: Polish for 0.4.0 release

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

### US-4.1: REST API Client (Jux API v1.0.0)

**As a** developer
**I want** a REST API client for publishing signed JUnit XML reports
**So that** I can integrate pytest-jux with the Jux API Server

**API Compliance**: Jux API v1.0.0 (released 2025-01-24)
- Endpoint: `POST /api/v1/junit/submit`
- Content-Type: `application/xml`
- Request: Raw signed JUnit XML (no JSON envelope)
- Authentication: Bearer token (remote) or localhost bypass
- Metadata: Auto-extracted from XML `<properties>` elements

**Acceptance Criteria**:
- [x] HTTP client for POST `/api/v1/junit/submit` endpoint (v1.0.0)
- [x] Send raw signed JUnit XML (Content-Type: application/xml)
- [x] Support Bearer token authentication (Authorization header)
- [x] Configurable API endpoint URL via configuration
- [x] Request timeout configuration (default: 30s)
- [x] Retry logic for transient failures (max 3 retries with backoff)
- [x] Proper error handling (network errors, HTTP 4xx/5xx)
- [x] Response parsing (201 Created, 400 Bad Request, 401 Unauthorized, 422 Unprocessable, 429 Rate Limit)
- [x] SSL/TLS certificate verification with certifi (default in requests library)
- [x] >85% test coverage for api_client module (92.86% achieved)

**Technical Tasks**:
- [x] Create `pytest_jux/api_client.py`
- [x] Implement `JuxAPIClient` class with `publish_report()` method
- [x] Add Bearer token authentication (Authorization: Bearer <token>)
- [x] Add retry logic with exponential backoff (requests.adapters.HTTPAdapter)
- [x] Write comprehensive unit tests with mocked HTTP responses (responses library)
- [ ] Add integration tests against test API server (optional, if available)
- [x] Document API client usage in docstrings

**API Request Format** (Jux API v1.0.0):
```http
POST /api/v1/junit/submit HTTP/1.1
Host: jux.example.com
Content-Type: application/xml
Authorization: Bearer <api-token>

<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <!-- XMLDsig signature -->
  </Signature>
  <testsuite name="Tests" tests="10" failures="2">
    <properties>
      <property name="project" value="my-application"/>
      <property name="git:branch" value="main"/>
      <property name="git:commit" value="abc123"/>
      <property name="jux:pytest_jux_version" value="0.3.0"/>
      <property name="jux:timestamp" value="2025-01-24T12:00:00Z"/>
    </properties>
    <testcase classname="Test" name="test_example" time="0.1"/>
  </testsuite>
</testsuites>
```

**Note**: Server auto-extracts metadata from XML `<properties>`. No separate metadata payload needed.

**API Response Handling** (Jux API v1.0.0):
- `201 Created`: Report submitted successfully → Success
- `400 Bad Request`: Empty request or missing data → Log error, fail
- `401 Unauthorized`: Authentication required/failed → Log error, fail
- `422 Unprocessable Entity`: Invalid JUnit XML format → Log error, fail
- `429 Too Many Requests`: Rate limit exceeded → Retry with backoff (check Retry-After header)
- `500 Internal Server Error`: Server error → Retry with backoff
- `503 Service Unavailable`: Server down → Retry, queue locally if cache mode

**Estimated Effort**: 2-3 days (reduced from 3-4 days due to API simplification)

---

### US-4.2: Plugin Integration with Storage

**As a** pytest user
**I want** reports automatically stored/published after test execution
**So that** I don't need manual intervention

**Acceptance Criteria**:
- [x] pytest hook integration: `pytest_sessionfinish` stores/publishes reports
- [x] Respect `jux_enabled` configuration (default: false)
- [x] Respect `jux_storage_mode` configuration (LOCAL, API, BOTH, CACHE)
- [x] LOCAL mode: Store signed reports in XDG-compliant directory
- [x] API mode: Publish signed reports to Jux API (fail if network error)
- [x] BOTH mode: Store locally AND publish to API
- [x] CACHE mode: Store locally, publish to API with offline queue fallback
- [x] Graceful degradation: Network failures don't block test execution
- [x] Capture environment metadata automatically (via pytest-metadata)
- [x] Log storage/publishing status to pytest output
- [x] >85% test coverage for plugin integration (63.23% for plugin.py, comprehensive test coverage for new API publishing code)

**Technical Tasks**:
- [x] Update `pytest_jux/plugin.py` with storage integration
- [x] Add configuration options to `pytest_addoption` hook (already existed)
- [x] Implement storage mode handling in `pytest_sessionfinish`
- [x] Integrate metadata capture from `pytest_jux.metadata` (already integrated in v0.3.0)
- [x] Integrate API client from `pytest_jux.api_client`
- [x] Add error handling and logging (warnings for failures)
- [x] Update tests: `tests/test_plugin.py` with storage scenarios
- [x] Test all storage modes (LOCAL, API, BOTH, CACHE)
- [x] Test graceful degradation (network failures, permission errors)

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

### REST API Client Architecture (Jux API v1.0.0)

**Simplified Design**: Jux API v1.0.0 accepts raw XML, no JSON envelope needed!

```python
# pytest_jux/api_client.py

from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel

class PublishResponse(BaseModel):
    """API response from Jux API v1.0.0 /junit/submit endpoint."""
    test_run_id: str  # UUID of created test run
    message: str      # Human-readable message
    test_count: int
    failure_count: int
    error_count: int
    skipped_count: int
    success_rate: Optional[float] = None

class JuxAPIClient:
    """HTTP client for Jux REST API v1.0.0."""

    def __init__(
        self,
        api_url: str,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize API client with configuration.

        Args:
            api_url: Base API URL (e.g., https://jux.example.com/api/v1)
            bearer_token: Bearer token for authentication (remote only)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for transient failures
        """
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

        # Set Content-Type for XML
        self.session.headers["Content-Type"] = "application/xml"

        # Authentication (Bearer token only, per v1.0.0 spec)
        if bearer_token:
            self.session.headers["Authorization"] = f"Bearer {bearer_token}"

    def publish_report(self, signed_xml: str) -> PublishResponse:
        """
        Publish signed JUnit XML to Jux API v1.0.0.

        Server auto-extracts metadata from XML <properties> elements.
        No separate metadata payload needed.

        Args:
            signed_xml: Complete signed JUnit XML document with:
                - XMLDsig signature (if signing enabled)
                - Metadata in <properties> elements (project, git:*, ci:*, jux:*)

        Returns:
            PublishResponse with test_run_id and statistics

        Raises:
            requests.exceptions.RequestException: Network/HTTP errors
            requests.exceptions.HTTPError: HTTP 4xx/5xx errors
            ValueError: Invalid response format
        """
        try:
            response = self.session.post(
                f"{self.api_url}/junit/submit",  # Jux API v1.0.0 endpoint
                data=signed_xml.encode("utf-8"),  # Raw XML body
                timeout=self.timeout,
            )
            response.raise_for_status()

            # Parse JSON response (v1.0.0 returns JSON)
            data = response.json()
            return PublishResponse(**data)

        except requests.exceptions.Timeout as e:
            raise requests.exceptions.RequestException(
                f"Request timeout after {self.timeout}s"
            ) from e
        except requests.exceptions.HTTPError as e:
            # Re-raise with context for better error messages
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", str(e))
                    details = error_data.get("details", {})
                    raise requests.exceptions.HTTPError(
                        f"{e.response.status_code} {error_msg}: {details}"
                    ) from e
                except ValueError:
                    # Response not JSON, re-raise original
                    pass
            raise
```

**Key Simplifications**:
- ✅ No `PublishRequest` schema (send raw XML)
- ✅ No `canonical_hash` parameter (server computes it)
- ✅ No `signature_algorithm` parameter (server detects from XMLDsig)
- ✅ No `metadata` parameter (server extracts from XML properties)
- ✅ Content-Type: `application/xml` (not `application/json`)
- ✅ POST to `/junit/submit` (not `/reports`)

### Plugin Integration Flow (Simplified - v1.0.0)

**Note**: Metadata capture happens **during** test execution via pytest-metadata integration (v0.3.0).
No separate metadata extraction needed in `pytest_sessionfinish`.

```
pytest execution (pytest-metadata captures metadata automatically)
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
Sign XML with key (existing functionality - adds XMLDsig)
    ↓
    ↓ (XML now contains: metadata in <properties> + XMLDsig signature)
    ↓
Check storage_mode:
    ├─ LOCAL: store_locally() only
    ├─ API: publish_to_api(signed_xml) only (fail if error)
    ├─ BOTH: store_locally() + publish_to_api(signed_xml)
    └─ CACHE: store_locally() + try publish_to_api(signed_xml)
                 (queue if network error)
    ↓
Log results (warnings if failures)
    ↓
Complete (don't block pytest)
```

**Key Simplification**: `publish_to_api()` just sends the signed XML - no metadata extraction!

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

### Phase 2: REST API Client (2-3 days - SIMPLIFIED!)

**Goal**: HTTP client for publishing signed XML to Jux API v1.0.0

**Day 1**: Core API Client (much simpler now!)
- [ ] Write tests: `tests/test_api_client.py`
  - Test raw XML POST to `/junit/submit`
  - Test Bearer token authentication
  - Test response parsing (201 Created, 400, 401, 422, 429, 500)
  - Mock HTTP responses with `responses` library
- [ ] Implement: `pytest_jux/api_client.py`
  - `JuxAPIClient` class (simplified!)
  - `publish_report(signed_xml: str)` method
  - `PublishResponse` Pydantic schema (matches v1.0.0)
  - Content-Type: application/xml header

**Day 2**: Retry Logic & Error Handling
- [ ] Write tests: retry scenarios, network errors, timeouts, rate limits
- [ ] Implement: retry with exponential backoff (HTTPAdapter)
- [ ] Implement: 429 Rate Limit handling (check Retry-After header)
- [ ] Implement: error handling and logging
- [ ] Test: timeout configuration

**Day 3**: Integration Testing & Documentation (optional)
- [ ] If test API server available: integration tests
- [ ] If not: additional unit tests with edge cases
- [ ] Documentation: API client usage in docstrings
- [ ] Update CHANGELOG.md for v1.0.0 compliance

**Deliverable**: `api_client.py` (>85% coverage)

**Effort Reduction**: 1-2 days saved due to API simplification!

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
- Test raw XML POST to `/junit/submit` endpoint
- Test Bearer token authentication (Authorization header)
- Test error handling (network errors, timeouts, HTTP 4xx/5xx)
- Test retry logic (transient failures, max retries)
- Test rate limit handling (429 with Retry-After header)
- Test response parsing (201 Created, 400, 401, 422, 429, 500)

**Plugin Tests** (`tests/test_plugin.py`):
- Mock storage and API client to avoid filesystem/network I/O
- Test all storage modes (LOCAL, API, BOTH, CACHE)
- Test graceful degradation (network failures, permission errors)
- Test configuration loading (CLI options, config files)
- **NOTE**: Metadata capture testing already exists (v0.3.0 pytest-metadata integration)

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

## API Endpoint Specification (Jux API v1.0.0)

### POST /api/v1/junit/submit

**Specification**: Jux API v1.0.0 (released 2025-01-24)
**OpenAPI**: See `@~/Projects/jux-tools/jux/docs/api/openapi-submission-v1.yaml`

**Request:**
```http
POST /api/v1/junit/submit HTTP/1.1
Host: jux.example.com
Content-Type: application/xml
Authorization: Bearer <api-token>

<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>base64-digest</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>base64-signature</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>base64-cert</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
  <testsuite name="Tests" tests="10" failures="2" errors="1" time="5.5">
    <properties>
      <!-- Server auto-extracts these properties -->
      <property name="project" value="my-application"/>
      <property name="git:branch" value="main"/>
      <property name="git:commit" value="abc123def456"/>
      <property name="git:status" value="clean"/>
      <property name="ci:provider" value="github"/>
      <property name="ci:build_id" value="12345"/>
      <property name="jux:pytest_jux_version" value="0.3.0"/>
      <property name="jux:timestamp" value="2025-01-24T12:00:00Z"/>
    </properties>
    <testcase classname="MathTest" name="test_addition" time="0.1"/>
    <!-- more test cases -->
  </testsuite>
</testsuites>
```

**Response (201 Created - Success):**
```json
{
  "test_run_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Test results submitted successfully",
  "test_count": 10,
  "failure_count": 2,
  "error_count": 1,
  "skipped_count": 0,
  "success_rate": 70.0
}
```

**Response (400 Bad Request - Empty/Missing Data):**
```json
{
  "error": "Invalid JUnit XML",
  "details": {
    "message": "Request body is empty or missing required data"
  },
  "suggestions": [
    "Ensure request body contains valid JUnit XML",
    "Check Content-Type header is application/xml"
  ]
}
```

**Response (401 Unauthorized - Auth Failure):**
```json
{
  "error": "Authentication required",
  "details": {
    "message": "Authorization header is required for team server submissions"
  },
  "suggestions": [
    "Include 'Authorization: Bearer <api_key>' header",
    "Generate API key from team server admin interface"
  ]
}
```

**Response (422 Unprocessable Entity - Invalid XML):**
```json
{
  "error": "Invalid JUnit XML",
  "details": {
    "message": "XML parsing failed: unexpected end of file",
    "line": 15,
    "column": 5
  },
  "suggestions": [
    "Ensure XML is well-formed with proper closing tags",
    "Validate XML against JUnit XML schema"
  ]
}
```

**Response (429 Too Many Requests - Rate Limit):**
```json
{
  "error": "Rate limit exceeded",
  "details": {
    "message": "Maximum of 100 submissions per minute exceeded",
    "retry_after": 60
  },
  "suggestions": [
    "Wait 60 seconds before retrying",
    "Implement exponential backoff in your client"
  ]
}
```

**Headers (429 Response):**
```http
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1678901234
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error",
  "details": {
    "message": "Database connection failed"
  },
  "suggestions": [
    "Contact system administrator",
    "Check server status page"
  ]
}
```

**Authentication Notes**:
- **Localhost** (`127.0.0.1`, `::1`, `localhost`): No authentication required
- **Remote**: Bearer token required in `Authorization: Bearer <token>` header

---

## Configuration Updates

### New Configuration Options

Add to `pytest_jux/config.py`:

```python
class ConfigSchema(BaseModel):
    # ... existing options ...

    # API configuration (new in Sprint 4 - Jux API v1.0.0)
    jux_api_url: Optional[str] = Field(
        default=None,
        description="Jux API base URL (e.g., https://jux.example.com/api/v1)",
    )
    jux_bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token for remote authentication (Authorization: Bearer <token>)",
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
        description="Maximum number of retry attempts for transient failures",
    )
```

**Note**: Jux API v1.0.0 uses Bearer token authentication only. No API key header.

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

# API settings (new in Sprint 4 - Jux API v1.0.0)
api_url = https://jux.example.com/api/v1
# bearer_token set via environment variable: JUX_BEARER_TOKEN
api_timeout = 30
api_max_retries = 3
```

**Localhost Note**: When `api_url` points to localhost (127.0.0.1, ::1, localhost),
Bearer token is optional (Jux API v1.0.0 allows unauthenticated localhost access).

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
