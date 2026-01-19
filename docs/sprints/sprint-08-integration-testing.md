# Sprint 8: Integration Testing with jux-mock-server

**Target Version**: v0.5.0
**Duration**: 2026-01-19 - 2026-02-02 (2 weeks)
**Status**: 🔄 In Progress

## Sprint Goal

Validate pytest-jux client compliance against jux-openapi specification using jux-mock-server for integration testing.

## Context

With jux-mock-server v0.4.0 now implementing the full jux-openapi v1 specification, we can perform comprehensive integration testing of pytest-jux's REST API client without requiring a real Jux API server.

**Dependencies**:
- jux-mock-server v0.4.0+ (implements jux-openapi v1)
- jux-openapi specs (single source of truth)

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 21 |
| Completed | 0 |
| In Progress | 0 |
| Remaining | 21 |

## User Stories

### US-8.1: Add jux-mock-server as Development Dependency

**Points**: 2 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a developer, I want jux-mock-server available as a dev dependency so that integration tests can use it.

**Acceptance Criteria**:
- [ ] jux-mock-server added to `[project.optional-dependencies.dev]` in pyproject.toml
- [ ] MockJuxServer importable in test modules
- [ ] `uv sync` installs jux-mock-server correctly
- [ ] Version constraint allows jux-mock-server 0.4.0+

**Technical Notes**:
- Use path dependency for local development: `jux-mock-server = { path = "../jux-mock-server", optional = true }`
- Or use git dependency if published
- Consider making integration tests optional (pytest marker)

**Files Likely Affected**:
- `pyproject.toml`
- `tests/conftest.py`

---

### US-8.2: Create Integration Test Fixtures

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a developer, I want pytest fixtures for MockJuxServer so that integration tests are easy to write.

**Acceptance Criteria**:
- [ ] `mock_jux_server` fixture provides running MockJuxServer instance
- [ ] Fixture handles server lifecycle (start/stop)
- [ ] Server URL accessible via fixture
- [ ] Request recording enabled by default
- [ ] Tests marked with `@pytest.mark.integration`

**Technical Notes**:
- Use MockJuxServer context manager
- Consider session-scoped fixture for performance
- Add `--run-integration` CLI option to opt-in

**Files Likely Affected**:
- `tests/conftest.py`
- `tests/integration/__init__.py` (new)
- `pyproject.toml` (pytest markers)

---

### US-8.3: Test JuxAPIClient Against Mock Server

**Points**: 5 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a developer, I want to test JuxAPIClient against jux-mock-server so that I can verify API compliance.

**Acceptance Criteria**:
- [ ] Test successful report submission (POST /api/v1/junit/submit)
- [ ] Test authentication (Bearer token)
- [ ] Test retry logic with simulated failures
- [ ] Test response parsing matches jux-openapi schema
- [ ] Test error handling (4xx, 5xx responses)
- [ ] Verify request body matches jux-openapi spec

**Technical Notes**:
- Use MockJuxServer's request recording to verify sent data
- Use response configuration for error scenarios
- Use latency simulation for timeout testing

**Files Likely Affected**:
- `tests/integration/test_api_client.py` (new)

---

### US-8.4: Test Plugin Integration with Mock Server

**Points**: 5 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a developer, I want to test the pytest plugin's automatic publishing against jux-mock-server so that I can verify end-to-end workflow.

**Acceptance Criteria**:
- [ ] Test automatic publishing in `pytest_sessionfinish`
- [ ] Test with `--jux-api-url` pointing to mock server
- [ ] Verify signed XML is correctly submitted
- [ ] Verify metadata is included in submission
- [ ] Test storage mode BOTH (local + API)
- [ ] Test storage mode API (API only)

**Technical Notes**:
- Use pytester fixture for running pytest with plugin
- Combine with MockJuxServer fixture
- May need to handle pytester subprocess communication

**Files Likely Affected**:
- `tests/integration/test_plugin_publishing.py` (new)

---

### US-8.5: Test jux-publish Command with Mock Server

**Points**: 3 | **Priority**: Medium | **Status**: 📋 Planned

**User Story**:
> As a developer, I want to test the jux-publish CLI command against jux-mock-server so that manual publishing works correctly.

**Acceptance Criteria**:
- [ ] Test `jux-publish <file>` submits to mock server
- [ ] Test `jux-publish --queue` processes cached reports
- [ ] Test `--dry-run` mode (no actual submission)
- [ ] Test `--json` output format
- [ ] Verify authentication header sent correctly

**Technical Notes**:
- Use CliRunner for command testing
- Start MockJuxServer before command execution
- Use environment variables for API URL/token

**Files Likely Affected**:
- `tests/integration/test_publish_command.py` (new)

---

### US-8.6: Test Error Scenarios

**Points**: 3 | **Priority**: Medium | **Status**: 📋 Planned

**User Story**:
> As a developer, I want to test error handling against jux-mock-server so that pytest-jux handles failures gracefully.

**Acceptance Criteria**:
- [ ] Test network timeout handling
- [ ] Test 400 Bad Request (invalid XML)
- [ ] Test 401 Unauthorized (missing/invalid token)
- [ ] Test 422 Validation Error (schema mismatch)
- [ ] Test 500 Internal Server Error
- [ ] Test connection refused (server down)
- [ ] Verify appropriate error messages

**Technical Notes**:
- Use MockJuxServer's `configure_response()` for error scenarios
- Use `configure_latency()` for timeout testing
- Test that errors don't break pytest session

**Files Likely Affected**:
- `tests/integration/test_error_handling.py` (new)

---

## Technical Tasks

### Task 8.1: pytest Marker Configuration

- [ ] Add `integration` marker to pytest.ini/pyproject.toml
- [ ] Configure `--run-integration` CLI option
- [ ] Skip integration tests by default
- [ ] Document how to run integration tests

### Task 8.2: CI Configuration

- [ ] Add integration test job to GitHub Actions
- [ ] Consider separate workflow for integration tests
- [ ] Cache jux-mock-server dependencies

---

## AI Collaboration Strategy

| Task Type | AI Role | Human Role |
|-----------|---------|------------|
| Test generation | Lead | Review |
| Fixture design | Lead | Review |
| Error scenario design | Assist | Lead |
| CI configuration | Lead | Review |

**AI Delegation Guidelines**:
- **AI leads**: Writing integration tests, fixture implementation
- **Human leads**: Verifying API compliance, reviewing edge cases
- **Collaborative**: Designing test scenarios

---

## Dependencies

### External Dependencies
- [x] jux-mock-server v0.4.0 (jux-openapi v1 compliance)
- [x] jux-openapi specs (API contract)

### Internal Dependencies
- US-8.2 depends on US-8.1 (mock server as dependency)
- US-8.3, US-8.4, US-8.5, US-8.6 depend on US-8.2 (fixtures)

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| pytester + MockJuxServer complexity | Medium | Medium | Use subprocess communication if needed |
| Path dependency issues | Low | Medium | Use git dependency as fallback |
| CI environment differences | Low | Low | Test in CI early |

---

## Definition of Done

Sprint is complete when:
- [ ] All user stories meet acceptance criteria
- [ ] All integration tests passing
- [ ] Tests skipped by default, run with `--run-integration`
- [ ] CI runs integration tests
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No critical bugs outstanding
- [ ] Sprint retrospective completed

---

## Success Metrics

- **Integration Test Count**: Target 20+ integration tests
- **API Compliance**: 100% of jux-openapi endpoints tested
- **Error Coverage**: All HTTP error codes tested
- **CI Green**: Integration tests pass in CI

---

## Notes

This sprint addresses the deferred US-4.5 (Integration Testing) from Sprint 4. With jux-mock-server now available as a faithful implementation of jux-openapi, we can finally validate pytest-jux client compliance.

The integration tests are designed to be **optional** - they require jux-mock-server and run only when explicitly requested. This keeps the default test suite fast and dependency-light.
