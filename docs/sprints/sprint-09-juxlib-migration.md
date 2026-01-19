# Sprint 9: Migrate to py-juxlib

**Target Version**: v0.6.0
**Duration**: 2026-02-03 - 2026-02-17 (2 weeks)
**Status**: 📋 Planned

## Sprint Goal

Migrate pytest-jux to use py-juxlib as its shared library, eliminating code duplication and establishing a unified codebase for Jux Python tools.

## Context

py-juxlib has been created as a shared library containing functionality extracted from pytest-jux:
- `juxlib.metadata` - Environment, Git, and CI/CD metadata detection
- `juxlib.signing` - XML digital signature creation and verification
- `juxlib.api` - HTTP client for Jux API servers
- `juxlib.config` - Configuration management
- `juxlib.storage` - Local filesystem storage
- `juxlib.errors` - User-friendly error handling

This sprint migrates pytest-jux to consume py-juxlib instead of maintaining duplicate implementations.

**Dependencies**:
- py-juxlib v0.3.0+ (all modules implemented)
- py-juxlib published to PyPI or available via path dependency

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 21 |
| Completed | 0 |
| In Progress | 0 |
| Remaining | 21 |

## User Stories

### US-9.1: Add py-juxlib Dependency

**Points**: 2 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to add py-juxlib as a dependency so that pytest-jux can use shared library modules.

**Acceptance Criteria**:
- [ ] py-juxlib added to `[project.dependencies]` in pyproject.toml
- [ ] Version constraint: `py-juxlib>=0.3.0`
- [ ] `uv sync` installs py-juxlib correctly
- [ ] juxlib modules importable in pytest-jux

**Technical Notes**:
- During development, use path dependency: `py-juxlib = { path = "../py-juxlib" }`
- For release, use version constraint from PyPI or git dependency
- Ensure no circular dependencies

**Files Likely Affected**:
- `pyproject.toml`

---

### US-9.2: Migrate Metadata Module

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to replace pytest_jux.metadata with juxlib.metadata so that metadata detection uses the shared library.

**Acceptance Criteria**:
- [ ] `pytest_jux/metadata.py` imports from `juxlib.metadata`
- [ ] All metadata detection tests pass
- [ ] Git metadata (commit, branch, status, remote) works correctly
- [ ] CI metadata (provider, build_id, build_url) works correctly
- [ ] Project name detection works correctly
- [ ] No regression in metadata captured in JUnit XML

**Technical Notes**:
- Replace: `from pytest_jux.metadata import capture_metadata`
- With: `from juxlib.metadata import capture_metadata`
- May need thin wrapper to maintain backward compatibility
- Test with real git repository and CI environment variables

**Files Likely Affected**:
- `pytest_jux/metadata.py` (replace implementation with imports)
- `pytest_jux/plugin.py` (update imports)
- `tests/test_metadata.py` (verify tests still pass)

---

### US-9.3: Migrate Signing Module

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to replace pytest_jux signing modules with juxlib.signing so that XML signing uses the shared library.

**Acceptance Criteria**:
- [ ] `pytest_jux/signer.py` imports from `juxlib.signing`
- [ ] `pytest_jux/verifier.py` imports from `juxlib.signing`
- [ ] `pytest_jux/canonicalizer.py` imports from `juxlib.signing`
- [ ] All signing tests pass
- [ ] All verification tests pass
- [ ] XML canonicalization (C14N) works correctly
- [ ] Key loading (RSA, ECDSA) works correctly

**Technical Notes**:
- Replace multiple modules with imports from juxlib.signing
- Maintain CLI command interfaces
- Test with existing test fixtures

**Files Likely Affected**:
- `pytest_jux/signer.py` (replace with imports)
- `pytest_jux/verifier.py` (replace with imports)
- `pytest_jux/canonicalizer.py` (replace with imports)
- `pytest_jux/commands/sign.py` (update imports)
- `pytest_jux/commands/verify.py` (update imports)
- `pytest_jux/commands/keygen.py` (update imports)
- `tests/test_signer.py`, `tests/test_verifier.py`, `tests/test_canonicalizer.py`

---

### US-9.4: Migrate API Client Module

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to replace pytest_jux.api_client with juxlib.api so that API communication uses the shared library.

**Acceptance Criteria**:
- [ ] `pytest_jux/api_client.py` imports from `juxlib.api`
- [ ] All API client tests pass
- [ ] Bearer token authentication works correctly
- [ ] Retry logic works correctly
- [ ] Response parsing works correctly
- [ ] jux-publish command works correctly

**Technical Notes**:
- Replace: `from pytest_jux.api_client import JuxAPIClient`
- With: `from juxlib.api import JuxAPIClient`
- PublishResponse and TestRun models come from juxlib.api

**Files Likely Affected**:
- `pytest_jux/api_client.py` (replace with imports)
- `pytest_jux/plugin.py` (update imports)
- `pytest_jux/commands/publish.py` (update imports)
- `tests/test_api_client.py`

---

### US-9.5: Migrate Config Module

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to replace pytest_jux.config with juxlib.config so that configuration uses the shared library.

**Acceptance Criteria**:
- [ ] `pytest_jux/config.py` imports from `juxlib.config`
- [ ] All config tests pass
- [ ] Config file loading works correctly
- [ ] Environment variable loading works correctly
- [ ] CLI argument precedence works correctly
- [ ] jux-config command works correctly

**Technical Notes**:
- ConfigurationManager from juxlib.config
- ConfigSchema and StorageMode from juxlib.config
- May need pytest-specific configuration extensions

**Files Likely Affected**:
- `pytest_jux/config.py` (replace with imports)
- `pytest_jux/plugin.py` (update imports)
- `pytest_jux/commands/config_cmd.py` (update imports)
- `tests/test_config.py`

---

### US-9.6: Migrate Storage Module

**Points**: 3 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to replace pytest_jux.storage with juxlib.storage so that local storage uses the shared library.

**Acceptance Criteria**:
- [ ] `pytest_jux/storage.py` imports from `juxlib.storage`
- [ ] All storage tests pass
- [ ] Report storage works correctly
- [ ] Cache management works correctly
- [ ] XDG paths work correctly
- [ ] jux-cache command works correctly

**Technical Notes**:
- ReportStorage from juxlib.storage
- get_default_path() from juxlib.storage
- Atomic file operations maintained

**Files Likely Affected**:
- `pytest_jux/storage.py` (replace with imports)
- `pytest_jux/plugin.py` (update imports)
- `pytest_jux/commands/cache.py` (update imports)
- `tests/test_storage.py`

---

### US-9.7: Remove Duplicate Code

**Points**: 2 | **Priority**: Medium | **Status**: 📋 Planned

**User Story**:
> As a maintainer, I want to remove duplicate implementations so that pytest-jux only contains plugin-specific code.

**Acceptance Criteria**:
- [ ] Local implementations removed or reduced to thin wrappers
- [ ] No dead code remaining
- [ ] Code coverage maintained >85%
- [ ] Package size reduced

**Technical Notes**:
- After migration, assess what remains in each module
- Keep only pytest-specific logic (plugin hooks, CLI commands)
- Remove utility functions now provided by juxlib

**Files Likely Affected**:
- All migrated modules (reduce to imports/wrappers)

---

### US-9.8: Update Documentation

**Points**: 2 | **Priority**: Medium | **Status**: 📋 Planned

**User Story**:
> As a user, I want updated documentation reflecting the juxlib migration so that I understand the new architecture.

**Acceptance Criteria**:
- [ ] CHANGELOG.md documents migration
- [ ] README.md updated with new dependency
- [ ] CLAUDE.md updated to reference juxlib
- [ ] API reference updated if public interfaces changed
- [ ] Migration notes for any breaking changes

**Technical Notes**:
- This is a major internal refactoring
- Public API should remain unchanged
- Document any subtle behavior differences

**Files Likely Affected**:
- `CHANGELOG.md`
- `README.md`
- `CLAUDE.md`
- `docs/` (various)

---

## Technical Tasks

### Task 9.1: Verify Test Coverage

- [ ] Run full test suite after each module migration
- [ ] Maintain >85% coverage
- [ ] Add tests for edge cases discovered during migration

### Task 9.2: Version Bump

- [ ] Bump pytest-jux version to 0.6.0
- [ ] Update CHANGELOG with all changes
- [ ] Prepare release notes

### Task 9.3: CI Verification

- [ ] Verify all CI checks pass
- [ ] Test with py-juxlib path dependency
- [ ] Prepare for PyPI release coordination

---

## AI Collaboration Strategy

| Task Type | AI Role | Human Role |
|-----------|---------|------------|
| Import migration | Lead | Review |
| Test verification | Lead | Review |
| Dead code removal | Assist | Approve |
| Documentation | Lead | Review |

**AI Delegation Guidelines**:
- **AI leads**: Import replacements, test running, documentation updates
- **Human leads**: Verifying no regressions, release decisions
- **Collaborative**: Identifying subtle compatibility issues

---

## Dependencies

### External Dependencies
- [ ] py-juxlib v0.3.0 released or available
- [ ] All py-juxlib modules tested

### Internal Dependencies
- US-9.2 through US-9.6 depend on US-9.1 (dependency added)
- US-9.7 depends on US-9.2 through US-9.6 (migrations complete)
- US-9.8 can run in parallel with US-9.7

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Subtle behavior differences | Medium | Medium | Comprehensive testing |
| Import path issues | Low | Low | Careful import updates |
| Missing juxlib features | Low | High | Gap analysis before starting |
| Version compatibility | Low | Medium | Pin juxlib version |

---

## Definition of Done

Sprint is complete when:
- [ ] All user stories meet acceptance criteria
- [ ] All tests passing (420+ tests)
- [ ] Coverage >85%
- [ ] No duplicate code (or minimal wrappers only)
- [ ] CI green
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version 0.6.0 ready for release
- [ ] Sprint retrospective completed

---

## Success Metrics

- **Test Pass Rate**: 100% (420+ tests)
- **Coverage**: >85%
- **Code Reduction**: ~500+ lines removed
- **Dependency Count**: +1 (py-juxlib)
- **CI Green**: All workflows passing

---

## Notes

This sprint represents a significant architectural improvement:
- **Unified codebase**: pytest-jux and behave-jux share the same library
- **Easier maintenance**: Bug fixes and improvements apply to all tools
- **Cleaner separation**: pytest-jux focuses on pytest-specific logic
- **Foundation for future tools**: Any new Jux client can use py-juxlib

The migration should be transparent to end users - the public API remains unchanged.
