# Sprint 012: pytest-jux API Gap Analysis

**Version**: 1.0
**Status**: Planning Document
**Target pytest-jux version**: v0.3.0+
**Date**: 2025-01-23
**Context**: Jux Sprint 011 deliverable for pytest-jux Sprint 012 planning

## Executive Summary

This document identifies gaps between the **existing pytest-jux v0.2.1 implementation** and the **Jux REST API OpenAPI v1.0.0 contract** finalized in Jux Sprint 011. These gaps must be addressed in pytest-jux Sprint 012 to achieve API contract compliance.

**Critical Finding**: pytest-jux v0.2.1 has **NO API submission functionality implemented**. The current implementation focuses exclusively on XML signing and local storage. Sprint 012 represents a **major architectural refactoring** to introduce HTTP client capabilities, request payload construction, metadata enrichment, retry logic, and error handling.

## Gap Analysis Overview

### Priority Levels

- **CRITICAL**: Functionality required for basic API contract compliance
- **MAJOR**: Significant functionality affecting user experience or reliability
- **MODERATE**: Important but can be deferred to v0.4.0 if needed
- **MINOR**: Nice-to-have enhancements

### Summary of Gaps

| Priority | Count | Examples |
|----------|-------|----------|
| CRITICAL | 8 | HTTP client, request payload, git metadata, retry logic |
| MAJOR | 4 | CI/CD metadata, rate limit handling, authentication errors |
| MODERATE | 3 | Dry run mode, version negotiation, advanced error recovery |
| MINOR | 2 | Webhook notifications, batch submission |

## Detailed Gap Analysis

### 1. HTTP Client Implementation (CRITICAL)

**Current State (v0.2.1)**:
```python
# pytest_jux/plugin.py - NO HTTP client code
def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    xml_path = session.config.getoption("--jux-xml-path")
    if xml_path and os.path.exists(xml_path):
        # Only signs XML locally, no submission
        sign_junit_xml(xml_path, session.config.option.jux_private_key)
```

**Required State (v0.3.0)**:
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def submit_to_jux_api(xml_content, metadata, config):
    """Submit JUnit XML to Jux API with retry logic."""
    api_url = config.getoption("--jux-api-url") or os.getenv("JUX_API_URL")
    api_key = os.getenv("JUX_API_KEY")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "xml_content": xml_content,
        "metadata": metadata
    }

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,  # 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.post(
            f"{api_url}/api/v1/junit/submit",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_submission_error(e, api_url)
        return None
```

**Gap Impact**: Without HTTP client, pytest-jux cannot submit to any Jux instance.

**Dependencies**: requests library, urllib3 for retry logic

---

### 2. Request Payload Construction (CRITICAL)

**Current State (v0.2.1)**:
```python
# pytest_jux/metadata.py - Only basic environment metadata
def collect_metadata():
    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "platform": platform.platform()
    }
```

**Required State (v0.3.0)**:
```python
def construct_submission_payload(xml_content, config):
    """Construct API-compliant submission payload."""
    metadata = {
        "project": get_project_name(config),
        "branch": get_git_branch(),
        "commit_sha": get_git_commit_sha(),
        "tags": get_tags(config),
        "environment": os.getenv("JUX_ENVIRONMENT", "test"),
        "ci_metadata": detect_ci_metadata()
    }

    return {
        "xml_content": xml_content,
        "metadata": metadata
    }

def get_project_name(config):
    """Get project name from config or environment."""
    return (
        config.getoption("--jux-project")
        or os.getenv("JUX_PROJECT")
        or os.path.basename(os.getcwd())
    )

def get_tags(config):
    """Parse comma-separated tags."""
    tags_str = os.getenv("JUX_TAGS", "")
    return [t.strip() for t in tags_str.split(",") if t.strip()]
```

**Gap Impact**: Cannot construct valid API requests per OpenAPI schema.

**OpenAPI Schema Reference**:
```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required:
          - xml_content
          - metadata
        properties:
          xml_content:
            type: string
          metadata:
            type: object
            required:
              - project
```

---

### 3. Git Metadata Detection (CRITICAL)

**Current State (v0.2.1)**:
```python
# pytest_jux/metadata.py - NO git metadata detection
# No functions for branch or commit SHA
```

**Required State (v0.3.0)**:
```python
import subprocess

def get_git_branch():
    """Detect current git branch."""
    # Environment variable takes precedence
    branch = os.getenv("JUX_BRANCH")
    if branch:
        return branch

    # Auto-detect from git
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None

def get_git_commit_sha():
    """Detect current git commit SHA."""
    # Environment variable takes precedence
    commit = os.getenv("JUX_COMMIT_SHA")
    if commit:
        return commit

    # Auto-detect from git
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None
```

**Gap Impact**: Cannot provide git context required by API contract.

**API Contract Requirement** (from pytest-jux-integration.md):
```markdown
**Git Metadata** (automatically detected):
- `branch`: Current git branch (from `git rev-parse --abbrev-ref HEAD`)
- `commit_sha`: Current commit SHA (from `git rev-parse HEAD`)

**Manual Override**:
Environment variables always take precedence over auto-detected values.
```

---

### 4. CI/CD Metadata Detection (MAJOR)

**Current State (v0.2.1)**:
```python
# No CI/CD metadata detection
```

**Required State (v0.3.0)**:
```python
def detect_ci_metadata():
    """Detect CI/CD metadata from environment variables."""
    # GitLab CI
    if os.getenv("GITLAB_CI"):
        return {
            "provider": "gitlab",
            "job_id": os.getenv("CI_JOB_ID"),
            "pipeline_url": os.getenv("CI_PIPELINE_URL"),
            "build_number": os.getenv("CI_PIPELINE_IID")
        }

    # GitHub Actions
    if os.getenv("GITHUB_ACTIONS"):
        server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        repo = os.getenv("GITHUB_REPOSITORY")
        run_id = os.getenv("GITHUB_RUN_ID")
        return {
            "provider": "github",
            "job_id": run_id,
            "pipeline_url": f"{server_url}/{repo}/actions/runs/{run_id}",
            "build_number": os.getenv("GITHUB_RUN_NUMBER")
        }

    # Jenkins
    if os.getenv("JENKINS_URL"):
        return {
            "provider": "jenkins",
            "job_id": os.getenv("BUILD_ID"),
            "pipeline_url": os.getenv("BUILD_URL"),
            "build_number": os.getenv("BUILD_NUMBER")
        }

    return None
```

**Gap Impact**: CI/CD submissions lack context metadata.

**API Contract Reference**:
```markdown
| CI/CD System | Detected Variables | Metadata Fields |
|--------------|-------------------|--------------------|
| GitLab CI | CI_JOB_ID, CI_PIPELINE_URL, CI_PIPELINE_IID | job_id, pipeline_url, build_number |
| GitHub Actions | GITHUB_RUN_ID, GITHUB_SERVER_URL, GITHUB_RUN_NUMBER | job_id, pipeline_url, build_number |
| Jenkins | BUILD_ID, BUILD_URL, BUILD_NUMBER | job_id, pipeline_url, build_number |
```

---

### 5. Exponential Backoff Retry Logic (CRITICAL)

**Current State (v0.2.1)**:
```python
# No retry logic implemented
```

**Required State (v0.3.0)**:
```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(retries=3):
    """Create requests session with exponential backoff."""
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,  # 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def submit_with_retry(xml_content, metadata, config):
    """Submit with exponential backoff retry."""
    retries = int(os.getenv("JUX_SUBMIT_RETRIES", "3"))
    session = create_session_with_retries(retries)

    # ... submission logic with session
```

**Gap Impact**: Network failures cause immediate submission failure.

**API Contract Requirement**:
```markdown
**Retry Strategy** (API Contract Requirement):
- **Attempt 1**: Immediate submission
- **Attempt 2**: Retry after 1 second
- **Attempt 3**: Retry after 2 seconds
- **Attempt 4**: Retry after 4 seconds

**Error Handling** (API Contract Requirement):
- **Network errors**: Retry with exponential backoff
- **Rate limit (429)**: Wait for `Retry-After` header duration
- **Authentication errors (401, 403)**: Log error, no retry
- **Invalid XML (400)**: Log detailed error, no retry
- **Server errors (5xx)**: Retry with exponential backoff
```

---

### 6. Rate Limit Handling (MAJOR)

**Current State (v0.2.1)**:
```python
# No rate limit handling
```

**Required State (v0.3.0)**:
```python
def handle_rate_limit(response):
    """Handle 429 Too Many Requests response."""
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "60")
        try:
            wait_seconds = int(retry_after)
        except ValueError:
            # Retry-After might be HTTP-date, default to 60 seconds
            wait_seconds = 60

        sys.stderr.write(
            f"Rate limit exceeded. Waiting {wait_seconds} seconds before retry...\n"
        )
        time.sleep(wait_seconds)
        return True
    return False
```

**Gap Impact**: Rate limiting causes submission failures without proper backoff.

**API Contract Requirement**:
```markdown
**Issue**: "429 Too Many Requests" rate limit exceeded

**Solution**:
1. Wait for `Retry-After` duration (pytest-jux handles this automatically)
2. Reduce submission frequency in CI/CD pipelines
3. Contact system administrator to increase rate limits
```

---

### 7. Authentication Error Handling (MAJOR)

**Current State (v0.2.1)**:
```python
# No authentication error handling
```

**Required State (v0.3.0)**:
```python
def handle_authentication_error(response, api_url):
    """Handle 401/403 authentication errors with actionable guidance."""
    if response.status_code in [401, 403]:
        sys.stderr.write(
            f"Authentication failed for {api_url}\n"
            f"Status: {response.status_code}\n\n"
            f"Suggestions:\n"
            f"1. Verify JUX_API_KEY environment variable is set\n"
            f"2. Check API key is valid in team server admin interface\n"
            f"3. Ensure API key has not expired\n"
            f"4. For team server submissions, confirm Authorization header format\n"
            f"5. For localhost submissions, API key should NOT be required\n\n"
        )

        try:
            error_details = response.json()
            if "suggestions" in error_details:
                sys.stderr.write("API Response Suggestions:\n")
                for suggestion in error_details["suggestions"]:
                    sys.stderr.write(f"  - {suggestion}\n")
        except ValueError:
            pass

        # Do NOT retry authentication errors
        return False
    return True
```

**Gap Impact**: Authentication failures provide no troubleshooting guidance.

**API Contract Requirement**:
```markdown
**Issue**: "401 Unauthorized" when submitting to team server

**Solution**:
1. Verify `JUX_API_KEY` environment variable is set
2. Check API key is valid in team server admin interface
3. Rotate API key if compromised
```

---

### 8. Validation Error Handling (MAJOR)

**Current State (v0.2.1)**:
```python
# No validation error handling
```

**Required State (v0.3.0)**:
```python
def handle_validation_error(response):
    """Handle 400 Bad Request validation errors."""
    if response.status_code == 400:
        sys.stderr.write("JUnit XML validation failed\n\n")

        try:
            error_details = response.json()

            if "message" in error_details:
                sys.stderr.write(f"Error: {error_details['message']}\n\n")

            if "suggestions" in error_details:
                sys.stderr.write("Suggestions:\n")
                for suggestion in error_details["suggestions"]:
                    sys.stderr.write(f"  - {suggestion}\n")
                sys.stderr.write("\n")

            if "details" in error_details:
                sys.stderr.write("Validation Details:\n")
                sys.stderr.write(f"{error_details['details']}\n\n")
        except ValueError:
            sys.stderr.write(f"Response: {response.text}\n\n")

        sys.stderr.write(
            "Troubleshooting:\n"
            "1. Run pytest --jux-dry-run to validate XML locally\n"
            "2. Check for special characters that need XML escaping\n"
            "3. Verify XML structure matches JUnit XML specification\n"
        )

        # Do NOT retry validation errors
        return False
    return True
```

**Gap Impact**: XML validation failures provide no actionable feedback.

---

### 9. Configuration Management (CRITICAL)

**Current State (v0.2.1)**:
```python
# pytest_jux/config.py - Schema exists but not fully utilized
def pytest_addoption(parser):
    group = parser.getgroup("jux")
    group.addoption("--jux-api-url", help="Jux API endpoint URL")
    # Schema exists but no implementation using these options
```

**Required State (v0.3.0)**:
```python
def pytest_addoption(parser):
    """Add pytest-jux command-line options."""
    group = parser.getgroup("jux")

    # Core options
    group.addoption(
        "--jux-submit",
        action="store_true",
        help="Enable automatic submission to Jux API"
    )

    group.addoption(
        "--jux-dry-run",
        action="store_true",
        help="Generate XML and validate but don't submit"
    )

    group.addoption(
        "--jux-api-url",
        help="Jux API endpoint URL (default: from JUX_API_URL env var)"
    )

    group.addoption(
        "--jux-project",
        help="Project name override (default: from JUX_PROJECT env var or cwd)"
    )

    group.addoption(
        "--jux-verbose",
        action="store_true",
        help="Enable verbose output for debugging"
    )

# pytest.ini support
def pytest_configure(config):
    """Register pytest.ini options."""
    config.addinivalue_line(
        "markers",
        "jux_submit: mark test for automatic Jux submission"
    )
```

**pytest.ini Configuration**:
```ini
[pytest]
# pytest-jux options
jux_submit = true
jux_submit_timeout = 30
jux_submit_retries = 3
jux_verbose = false
```

**Gap Impact**: Cannot configure pytest-jux behavior without implementation.

---

### 10. Dry Run Mode (MODERATE)

**Current State (v0.2.1)**:
```python
# No dry run mode
```

**Required State (v0.3.0)**:
```python
def dry_run_submission(xml_content, metadata, config):
    """Display what would be submitted without sending HTTP request."""
    print("\n" + "="*60)
    print("pytest-jux DRY RUN MODE")
    print("="*60)
    print("\nConfiguration:")
    print(f"  API URL: {config.getoption('--jux-api-url')}")
    print(f"  Project: {metadata.get('project')}")
    print(f"  Branch: {metadata.get('branch')}")
    print(f"  Commit: {metadata.get('commit_sha')}")
    print(f"  Tags: {metadata.get('tags')}")

    if metadata.get('ci_metadata'):
        print(f"\nCI/CD Metadata:")
        for key, value in metadata['ci_metadata'].items():
            print(f"  {key}: {value}")

    print(f"\nJUnit XML Content Length: {len(xml_content)} bytes")
    print("\nValidating XML structure...")

    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(xml_content)
        print("✓ XML structure is valid")
    except ET.ParseError as e:
        print(f"✗ XML validation failed: {e}")

    print("\nNOTE: No HTTP request sent (dry run mode)")
    print("="*60 + "\n")
```

**Gap Impact**: Cannot test configuration without actual API submission.

**API Contract Requirement**:
```markdown
Scenario: pytest-jux dry run mode for testing configuration
  Given I want to test pytest-jux configuration without submitting results
  When I run pytest --jux-dry-run
  Then pytest-jux should generate JUnit XML from test execution
  And pytest-jux should validate the XML structure locally
  And pytest-jux should display what would be submitted
  But pytest-jux should NOT send any HTTP requests to Jux API
```

---

### 11. Command-Line Interface (CRITICAL)

**Current State (v0.2.1)**:
```python
# Limited command-line options
def pytest_addoption(parser):
    group.addoption("--jux-xml-path", help="Path to signed JUnit XML")
```

**Required State (v0.3.0)**:
```bash
# Enable automatic submission
pytest --jux-submit

# Dry run (generate XML but don't submit)
pytest --jux-dry-run

# Verbose output
pytest --jux-verbose

# Override project name
pytest --jux-submit --jux-project=my-application

# Combine with standard pytest options
pytest --jux-submit -v tests/integration/
```

**Gap Impact**: Cannot control pytest-jux behavior from command line.

---

### 12. Environment Variable Support (CRITICAL)

**Current State (v0.2.1)**:
```python
# Limited environment variable support
```

**Required State (v0.3.0)**:
```python
# Configuration priority: CLI args > Environment vars > Defaults

def get_api_url(config):
    """Get API URL with priority: CLI > ENV > Default."""
    return (
        config.getoption("--jux-api-url")
        or os.getenv("JUX_API_URL")
        or "http://localhost:4000"
    )

def get_api_key():
    """Get API key from environment."""
    return os.getenv("JUX_API_KEY")

def get_submit_timeout():
    """Get submission timeout with default."""
    return int(os.getenv("JUX_SUBMIT_TIMEOUT", "30"))

def get_submit_retries():
    """Get retry count with default."""
    return int(os.getenv("JUX_SUBMIT_RETRIES", "3"))
```

**Environment Variables**:
| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `JUX_API_URL` | **Yes** | Jux API endpoint URL | None | `http://localhost:4000` |
| `JUX_API_KEY` | No | API key for team server | None | `your-secret-api-key` |
| `JUX_PROJECT` | No | Project name override | Inferred from git | `my-application` |
| `JUX_BRANCH` | No | Branch name override | Inferred from git | `feature/new-login` |
| `JUX_COMMIT_SHA` | No | Commit SHA override | Inferred from git | `abc123def456` |
| `JUX_TAGS` | No | Comma-separated tags | None | `smoke-tests,nightly` |
| `JUX_ENVIRONMENT` | No | Test environment | `test` | `staging` |
| `JUX_SUBMIT_TIMEOUT` | No | Submission timeout (sec) | `30` | `60` |
| `JUX_SUBMIT_RETRIES` | No | Number of retry attempts | `3` | `5` |

---

### 13. pytest Exit Behavior (CRITICAL)

**Current State (v0.2.1)**:
```python
# Unclear exit behavior
```

**Required State (v0.3.0)**:
```python
def pytest_sessionfinish(session, exitstatus):
    """Handle submission after test run, preserve test exit status."""
    if not session.config.getoption("--jux-submit"):
        return

    # Preserve original test exit status
    original_exitstatus = exitstatus

    try:
        # Generate JUnit XML
        xml_content = generate_junit_xml(session)

        # Construct metadata
        metadata = construct_submission_payload(xml_content, session.config)

        # Submit to API
        if session.config.getoption("--jux-dry-run"):
            dry_run_submission(xml_content, metadata, session.config)
        else:
            submit_to_jux_api(xml_content, metadata, session.config)

    except Exception as e:
        # Log submission error but don't change test exit status
        sys.stderr.write(f"\npytest-jux submission error: {e}\n")
        sys.stderr.write("Test results were NOT submitted to Jux\n")
        sys.stderr.write("Tests themselves may have passed or failed independently\n\n")

    # ALWAYS preserve original test exit status
    # Submission errors do NOT cause pytest to fail
    return original_exitstatus
```

**Gap Impact**: Unclear whether submission errors should fail pytest.

**API Contract Requirement**:
```markdown
**pytest Exit Behavior** (API Contract Requirement):
- pytest test failures **always** cause non-zero exit (test suite failed)
- Submission errors **do not** cause pytest to fail (unless `--jux-strict` flag used)
- Submission errors logged to stderr with actionable suggestions
```

---

### 14. API Version Negotiation (MODERATE)

**Current State (v0.2.1)**:
```python
# No API version negotiation
```

**Required State (v0.3.0)**:
```python
def check_api_version(api_url):
    """Check API version compatibility."""
    try:
        response = requests.get(
            f"{api_url}/api/version",
            timeout=5
        )

        if response.status_code == 200:
            version_info = response.json()
            server_version = version_info.get("version", "unknown")

            # pytest-jux v0.3.0 supports API v1.0.0
            if not server_version.startswith("1."):
                sys.stderr.write(
                    f"WARNING: API version mismatch\n"
                    f"  pytest-jux supports: API v1.x\n"
                    f"  Server version: API {server_version}\n"
                    f"  Upgrade guidance: https://docs.jux.io/upgrade\n\n"
                )
    except requests.RequestException:
        # Version check failure doesn't prevent submission attempt
        pass
```

**Gap Impact**: No warning when API versions are incompatible.

**API Contract Requirement**:
```markdown
Scenario: pytest-jux API version negotiation (future proofing)
  Given Jux API evolves to v2.0.0 with breaking changes
  And pytest-jux v1.x supports only API v1.0.0
  When pytest-jux submits to a Jux server running API v2.0.0
  Then pytest-jux should detect API version mismatch
  And pytest-jux should log a warning about version incompatibility
  And pytest-jux should provide upgrade guidance
```

---

### 15. Error Message Quality (MAJOR)

**Current State (v0.2.1)**:
```python
# Generic error messages
```

**Required State (v0.3.0)**:
```python
def handle_submission_error(error, api_url):
    """Provide actionable error messages for submission failures."""
    sys.stderr.write("\n" + "="*60 + "\n")
    sys.stderr.write("pytest-jux submission failed\n")
    sys.stderr.write("="*60 + "\n\n")

    if isinstance(error, requests.exceptions.ConnectionError):
        sys.stderr.write(
            f"Connection Error: Could not connect to {api_url}\n\n"
            f"Suggestions:\n"
            f"1. Verify Jux server is running: curl {api_url}\n"
            f"2. Check JUX_API_URL environment variable is correct\n"
            f"3. Ensure firewall allows connections to Jux server\n"
            f"4. For localhost: verify port {extract_port(api_url)} is not blocked\n"
            f"5. For team server: check VPN/network connectivity\n\n"
        )

    elif isinstance(error, requests.exceptions.Timeout):
        sys.stderr.write(
            f"Timeout Error: Request to {api_url} timed out\n\n"
            f"Suggestions:\n"
            f"1. Increase JUX_SUBMIT_TIMEOUT (current: {get_submit_timeout()}s)\n"
            f"2. Check server performance and load\n"
            f"3. Verify network connectivity is stable\n\n"
        )

    elif isinstance(error, requests.exceptions.HTTPError):
        handle_http_error(error.response, api_url)

    else:
        sys.stderr.write(f"Unexpected Error: {error}\n\n")

    sys.stderr.write("="*60 + "\n\n")
```

**Gap Impact**: Generic error messages make troubleshooting difficult.

---

## Jux Server-Side Gaps

### 16. API Key Validation (CRITICAL - Jux Side)

**Current State (Jux v0.1.20)**:
```elixir
# lib/jux_web/controllers/api/junit_controller.ex:174-178
# TODO: Validate API key for team server deployments
# For now, allow all submissions (trust-based local development)
api_key = get_req_header(conn, "authorization")
if api_key && !valid_api_key?(api_key) do
  # TODO: Return 401 Unauthorized
end
```

**Required State (Jux Sprint 012)**:
```elixir
defp authenticate_api_request(conn, _opts) do
  # Skip authentication for localhost submissions
  if conn.remote_ip == {127, 0, 0, 1} do
    conn
  else
    # Team server requires valid API key
    case get_req_header(conn, "authorization") do
      ["Bearer " <> api_key] ->
        if valid_api_key?(api_key) do
          assign(conn, :api_key, api_key)
        else
          conn
          |> put_status(:unauthorized)
          |> json(%{
            "error" => "Invalid API key",
            "suggestions" => [
              "Verify JUX_API_KEY environment variable is set correctly",
              "Check API key has not expired in admin interface",
              "Generate new API key if needed"
            ]
          })
          |> halt()
        end

      _ ->
        conn
        |> put_status(:unauthorized)
        |> json(%{
          "error" => "Missing Authorization header",
          "suggestions" => [
            "Set JUX_API_KEY environment variable in CI/CD configuration",
            "Include Authorization: Bearer <key> header in requests"
          ]
        })
        |> halt()
    end
  end
end
```

**Gap Impact**: Team server submissions cannot be authenticated.

---

### 17. Rate Limiting (CRITICAL - Jux Side)

**Current State (Jux v0.1.20)**:
```elixir
# No rate limiting implemented
```

**Required State (Jux Sprint 012)**:
```elixir
# Use PlugAttack or custom rate limiter
defmodule JuxWeb.RateLimiter do
  use PlugAttack

  rule "rate_limit_submit", conn do
    # Allow 100 submissions per minute per API key
    api_key = conn.assigns[:api_key] || "anonymous"
    throttle(api_key, by: :submissions, limit: 100, period: 60_000)
  end

  def handle_rate_limit(conn) do
    conn
    |> put_resp_header("retry-after", "60")
    |> put_status(:too_many_requests)
    |> Phoenix.Controller.json(%{
      "error" => "Rate limit exceeded",
      "suggestions" => [
        "Wait 60 seconds before retrying",
        "Reduce submission frequency in CI/CD pipeline",
        "Contact administrator to increase rate limits"
      ]
    })
    |> halt()
  end
end
```

**Gap Impact**: No protection against submission abuse.

---

### 18. Versioned API Endpoints (MODERATE - Jux Side)

**Current State (Jux v0.1.20)**:
```elixir
# lib/jux_web/router.ex
scope "/api", JuxWeb.Api do
  post "/junit/submit", JunitController, :submit  # No version in path
end
```

**Required State (Jux Sprint 012)**:
```elixir
# lib/jux_web/router.ex
scope "/api/v1", JuxWeb.Api do
  post "/junit/submit", JunitController, :submit
  get "/test_runs", TestRunController, :index
end

# Support both /api/junit/submit (legacy) and /api/v1/junit/submit (versioned)
# for backward compatibility during migration
```

**Gap Impact**: Cannot evolve API without breaking changes.

---

## Sprint 012 Recommended Scope

### Phase 1: Core API Integration (Week 1)

**Priority**: CRITICAL gaps only

1. HTTP client implementation with requests library
2. Request payload construction per OpenAPI schema
3. Git metadata detection (branch, commit SHA)
4. Basic error handling (connection, timeout, HTTP errors)
5. Configuration management (environment variables, CLI options)
6. pytest exit behavior (preserve test status)

**Deliverable**: pytest-jux v0.3.0-alpha can submit to localhost

**Test Coverage**: Individual developer scenarios from test_runner_plugin.feature

---

### Phase 2: Reliability & Resilience (Week 2)

**Priority**: CRITICAL + MAJOR gaps

7. Exponential backoff retry logic (1s, 2s, 4s)
8. Rate limit handling (429 with Retry-After)
9. Authentication error handling (401/403)
10. Validation error handling (400)
11. CI/CD metadata detection (GitLab, GitHub Actions, Jenkins)

**Deliverable**: pytest-jux v0.3.0-beta for CI/CD testing

**Test Coverage**: CI/CD submission scenarios from test_runner_plugin.feature

---

### Phase 3: Enhanced User Experience (Week 3)

**Priority**: MODERATE gaps

12. Dry run mode (--jux-dry-run)
13. API version negotiation
14. Enhanced error messages with suggestions
15. pytest.ini configuration support

**Deliverable**: pytest-jux v0.3.0-rc1

**Test Coverage**: All test_runner_plugin.feature scenarios pass

---

### Phase 4: Jux Server Updates (Week 4)

**Priority**: Server-side CRITICAL gaps

16. API key validation in Jux (lib/jux_web/controllers/api/junit_controller.ex)
17. Rate limiting implementation
18. Versioned API endpoints (/api/v1/)

**Deliverable**: pytest-jux v0.3.0 + Jux v0.2.1 (Sprint 012 aligned)

**Test Coverage**: Integration tests with real Jux server

---

### Phase 5: Validation & Release (Week 5)

**Priorities**: Testing, documentation, release preparation

19. Comprehensive integration testing against Jux server
20. BDD scenario validation (all 18 scenarios pass)
21. Update pytest-jux documentation
22. Migration guide from v0.2.1 to v0.3.0
23. Release notes and changelog

**Deliverable**: pytest-jux v1.0.0 (API contract compliant)

---

## Testing Strategy

### Unit Tests

```python
# test_metadata.py
def test_get_git_branch():
    """Test git branch detection."""
    branch = get_git_branch()
    assert branch is not None
    assert isinstance(branch, str)

def test_detect_gitlab_ci_metadata():
    """Test GitLab CI metadata detection."""
    os.environ["GITLAB_CI"] = "true"
    os.environ["CI_JOB_ID"] = "12345"
    metadata = detect_ci_metadata()
    assert metadata["provider"] == "gitlab"
    assert metadata["job_id"] == "12345"
```

### Integration Tests

```python
# test_submission.py
def test_submit_to_localhost():
    """Test submission to local Jux instance."""
    xml_content = "<testsuites>...</testsuites>"
    metadata = {"project": "test-project"}

    response = submit_to_jux_api(
        xml_content, metadata,
        api_url="http://localhost:4000"
    )

    assert response is not None
    assert "test_run_id" in response
```

### BDD Scenario Tests

```bash
# Run all Test Runner Plugin scenarios
pytest test/features/test_runner_plugin.feature

# Verify all 18 scenarios pass
```

---

## Migration Guide (v0.2.1 → v0.3.0)

### Breaking Changes

**XML Signing Removal**:
- v0.2.1: `pytest --jux-xml-path=output.xml` with signing
- v0.3.0: `pytest --jux-submit` with API submission

**Configuration Changes**:
- v0.2.1: `--jux-xml-path`, `--jux-private-key`
- v0.3.0: `--jux-submit`, `--jux-api-url`, `JUX_API_URL` environment variable

### Migration Steps

1. **Uninstall v0.2.1**:
   ```bash
   pip uninstall pytest-jux
   ```

2. **Install v0.3.0**:
   ```bash
   pip install pytest-jux>=0.3.0
   ```

3. **Update Configuration**:
   ```bash
   # Old (v0.2.1)
   pytest --jux-xml-path=output.xml --jux-private-key=key.pem

   # New (v0.3.0)
   export JUX_API_URL=http://localhost:4000
   pytest --jux-submit
   ```

4. **Update CI/CD Pipelines**:
   ```yaml
   # .gitlab-ci.yml
   variables:
     JUX_API_URL: https://team-jux.company.com

   test:
     script:
       - export JUX_API_KEY=$JUX_API_KEY
       - pytest --jux-submit
   ```

---

## Success Criteria

### Sprint 012 Definition of Done

1. ✅ All 15 pytest-jux gaps resolved (CRITICAL, MAJOR priorities)
2. ✅ All 18 Test Runner Plugin BDD scenarios pass
3. ✅ HTTP client submits to Jux API successfully
4. ✅ Git metadata automatically detected and included
5. ✅ CI/CD metadata detected for GitLab, GitHub Actions, Jenkins
6. ✅ Exponential backoff retry logic implemented (1s, 2s, 4s)
7. ✅ Rate limit handling with Retry-After header respect
8. ✅ Authentication errors return actionable suggestions
9. ✅ Validation errors display detailed API feedback
10. ✅ Dry run mode validates XML without submission
11. ✅ pytest exit status preserves test results (submission errors don't fail tests)
12. ✅ API key validation implemented in Jux server
13. ✅ Rate limiting implemented in Jux server (100 req/min default)
14. ✅ Versioned API endpoints (/api/v1/) in Jux
15. ✅ Integration tests pass against real Jux server
16. ✅ Documentation updated (README, API guide, migration guide)
17. ✅ pytest-jux v1.0.0 released (API contract compliant)

---

## References

### Jux Sprint 011 Deliverables

- **OpenAPI Submission API**: `jux/docs/api/openapi-submission-v1.yaml`
- **OpenAPI Query API**: `jux/docs/api/openapi-query-v1.yaml`
- **pytest-jux Integration Guide**: `jux/docs/guides/pytest-jux-integration.md`
- **BDD Features**: `jux/test/features/test_runner_plugin.feature`

### pytest-jux Repository

- **Current Implementation**: `pytest-jux/pytest_jux/` (v0.2.1)
- **Target Version**: v0.3.0 (API contract compliant)
- **Future Version**: v1.0.0 (production ready)

### External Dependencies

- **requests**: HTTP client library
- **urllib3**: Retry logic with exponential backoff
- **pytest**: Test framework integration

---

## Conclusion

pytest-jux v0.2.1 requires **major architectural refactoring** to comply with the Jux REST API OpenAPI v1.0.0 contract. The current implementation has **zero API submission functionality** and focuses exclusively on XML signing and local storage.

Sprint 012 represents a **5-week effort** to introduce HTTP client capabilities, request payload construction, metadata enrichment, retry logic, error handling, and comprehensive testing. Upon completion, pytest-jux v1.0.0 will be fully compliant with the API contract and ready for production use across individual developers, team members, and CI/CD pipelines.

**Next Steps**:
1. Review and approve this gap analysis
2. Create Sprint 012 project board in pytest-jux repository
3. Break down phases into GitHub issues
4. Begin Phase 1: Core API Integration
