# Sprint 7: Metadata Integration with pytest-metadata

**Sprint Goal**: Integrate environment metadata with pytest-metadata and remove JSON sidecar storage
**Duration**: 1-2 weeks
**Sprint Type**: Architecture Improvement & Security Enhancement
**Target Version**: v0.3.0 (breaking change)
**Status**: 🚧 In Progress
**Start Date**: 2025-10-24
**End Date**: TBD

---

## Sprint Overview

### Context

pytest-jux currently maintains two separate metadata systems:
1. **pytest-metadata** (external): User-provided metadata via CLI, stored in XML `<properties>`, cryptographically signed
2. **pytest_jux.metadata** (internal): Environment metadata (hostname, username, timestamp), stored in separate JSON files, NOT signed

This creates security and architectural issues:
- Environment metadata not cryptographically bound to reports
- Two storage mechanisms (XML + JSON)
- Files can become separated
- Inconsistent trust model

### Decision

**ADR-0011** proposes integrating all metadata into pytest-metadata, ensuring everything is stored in JUnit XML `<properties>` and included in the XMLDSig signature.

### Goals

**Primary Objectives**:
1. Add `pytest_metadata` hook to inject environment metadata into JUnit XML
2. Remove JSON sidecar storage entirely
3. Update all commands to read metadata from XML properties
4. Ensure all metadata is cryptographically signed
5. Maintain backward compatibility where possible

**Success Metrics**:
- All metadata stored in XML `<properties>` elements
- All metadata cryptographically signed
- No JSON sidecar files created
- All tests pass (>88% coverage maintained)
- Documentation updated
- Migration guide provided

---

## User Stories

### US-7.1: Integrate Environment Metadata with pytest-metadata

**As a** pytest-jux user
**I want** environment metadata automatically included in JUnit XML properties
**So that** all metadata is cryptographically signed and cannot be tampered with

**Acceptance Criteria**:
- `pytest_metadata` hook implemented in `plugin.py`
- Environment metadata (hostname, username, platform, etc.) added to XML `<properties>`
- Uses "jux:" namespace prefix to avoid conflicts
- User-provided metadata (CLI) takes precedence
- Metadata included in XMLDSig signature

**Implementation Tasks**:
- [ ] Add `pytest_metadata()` hook to `pytest_jux/plugin.py`
- [ ] Test hook integration with pytest-metadata
- [ ] Verify metadata appears in JUnit XML
- [ ] Verify metadata is included in signature

**Estimated Effort**: 0.5 days

---

### US-7.2: Remove JSON Sidecar Storage

**As a** pytest-jux developer
**I want** to remove JSON sidecar file storage
**So that** we have a single source of truth for report metadata

**Acceptance Criteria**:
- `storage.store_report()` no longer accepts metadata parameter
- `storage.get_metadata()` method removed
- `metadata/` directory no longer created
- `queue/` metadata JSON files no longer created
- Storage simplified to XML-only

**Implementation Tasks**:
- [ ] Update `storage.py` to remove metadata parameter from `store_report()`
- [ ] Remove `get_metadata()` method
- [ ] Remove `metadata/` directory handling
- [ ] Update `queue_report()` to not store metadata JSON
- [ ] Update `dequeue_report()` to not read metadata JSON

**Estimated Effort**: 0.5 days

---

### US-7.3: Update pytest_sessionfinish Hook

**As a** pytest-jux developer
**I want** to simplify the `pytest_sessionfinish` hook
**So that** it no longer captures or stores separate metadata

**Acceptance Criteria**:
- `pytest_sessionfinish` no longer calls `capture_metadata()`
- `pytest_sessionfinish` no longer passes metadata to `store_report()`
- Hook still signs XML (which now includes metadata)
- Hook still stores XML reports

**Implementation Tasks**:
- [ ] Remove `capture_metadata()` call from `pytest_sessionfinish`
- [ ] Remove metadata parameter from `storage.store_report()` call
- [ ] Verify signing still works correctly
- [ ] Verify storage still works correctly

**Estimated Effort**: 0.25 days

---

### US-7.4: Update jux-cache Command

**As a** pytest-jux user
**I want** jux-cache to read metadata from XML properties
**So that** I can view report metadata without JSON sidecars

**Acceptance Criteria**:
- `jux-cache list` reads metadata from XML `<properties>`
- `jux-cache show` displays metadata from XML
- No errors when JSON sidecar files are missing
- Metadata displayed with "jux:" prefix

**Implementation Tasks**:
- [ ] Update `commands/cache.py` to read metadata from XML
- [ ] Add XML property parsing helper function
- [ ] Remove JSON metadata reading code
- [ ] Update output formatting for "jux:" prefixed keys

**Estimated Effort**: 0.5 days

---

### US-7.5: Update Tests

**As a** pytest-jux developer
**I want** comprehensive tests for the new metadata integration
**So that** I can ensure correctness and prevent regressions

**Acceptance Criteria**:
- New test file `test_metadata_integration.py` created
- Tests verify `pytest_metadata` hook injection
- Tests verify metadata in XML properties
- Tests verify metadata included in signature
- Tests verify CLI precedence (user metadata not overridden)
- Tests verify storage works without JSON sidecars
- All existing tests updated or removed as needed

**Implementation Tasks**:
- [ ] Create `tests/test_metadata_integration.py`
- [ ] Add test for `pytest_metadata` hook
- [ ] Add test for metadata in signed XML
- [ ] Add test for CLI precedence
- [ ] Update `test_storage.py` (remove JSON tests)
- [ ] Update `test_plugin.py` (remove JSON verification)
- [ ] Update `test_cache.py` (test XML property reading)

**Estimated Effort**: 1 day

---

### US-7.6: Update Documentation

**As a** pytest-jux user
**I want** updated documentation explaining the new metadata system
**So that** I understand how metadata works and is stored

**Acceptance Criteria**:
- `docs/howto/add-metadata-to-reports.md` updated (remove JSON references)
- `docs/reference/storage.md` updated (single file structure)
- `CLAUDE.md` metadata section updated
- `README.md` updated if needed
- ADR-0011 referenced in documentation

**Implementation Tasks**:
- [ ] Update `docs/howto/add-metadata-to-reports.md`
- [ ] Update `docs/reference/storage.md`
- [ ] Update `CLAUDE.md` metadata architecture section
- [ ] Update `README.md` if needed
- [ ] Add migration guide for existing users

**Estimated Effort**: 1 day

---

### US-7.7: Provide Migration Support

**As a** pytest-jux user upgrading from v0.2.x
**I want** guidance on migrating existing JSON sidecar files
**So that** I can safely upgrade without losing metadata

**Acceptance Criteria**:
- Migration guide created
- Migration script provided (optional)
- Explains what changed and why
- Explains how to handle existing JSON files
- Notes that JSON files are no longer needed

**Implementation Tasks**:
- [ ] Create migration guide document
- [ ] Provide optional migration script (informational)
- [ ] Document breaking changes
- [ ] Update CHANGELOG.md with migration notes

**Estimated Effort**: 0.5 days

---

## Epic Breakdown

### Epic 1: Core Implementation (US-7.1, US-7.2, US-7.3)

**Goal**: Implement pytest_metadata hook and remove JSON sidecar storage

**Tasks**:
1. Add `pytest_metadata()` hook to `plugin.py` ✅
2. Update `storage.py` to remove metadata handling
3. Update `plugin.py` to simplify `pytest_sessionfinish`
4. Manual testing of metadata integration

**Duration**: 1-2 days
**Status**: 🚧 In Progress

---

### Epic 2: Command Updates (US-7.4)

**Goal**: Update CLI commands to work without JSON sidecars

**Tasks**:
1. Update `jux-cache` to read from XML properties
2. Verify `jux-inspect` works correctly (already reads XML)
3. Verify other commands work correctly

**Duration**: 0.5 days
**Status**: 📋 Pending

---

### Epic 3: Testing (US-7.5)

**Goal**: Comprehensive test coverage for new architecture

**Tasks**:
1. Create `test_metadata_integration.py`
2. Update existing tests
3. Remove obsolete tests
4. Verify coverage maintained (>88%)

**Duration**: 1 day
**Status**: 📋 Pending

---

### Epic 4: Documentation (US-7.6, US-7.7)

**Goal**: Update all documentation and provide migration guidance

**Tasks**:
1. Update how-to guides
2. Update reference documentation
3. Update CLAUDE.md
4. Create migration guide
5. Update CHANGELOG.md

**Duration**: 1 day
**Status**: 📋 Pending

---

## Technical Details

### Metadata Mapping

**From `pytest_jux.metadata` → XML properties**:

```python
# Before (v0.2.1): Stored in JSON
{
  "hostname": "ci-runner-01",
  "username": "gitlab-runner",
  "platform": "Linux-5.15.0",
  "python_version": "3.11.4",
  "pytest_version": "8.4.2",
  "pytest_jux_version": "0.2.1",
  "timestamp": "2025-10-24T12:34:56+00:00"
}

# After (v0.3.0): Stored in XML properties
<properties>
  <property name="jux:hostname" value="ci-runner-01"/>
  <property name="jux:username" value="gitlab-runner"/>
  <property name="jux:platform" value="Linux-5.15.0"/>
  <property name="jux:python_version" value="3.11.4"/>
  <property name="jux:pytest_version" value="8.4.2"/>
  <property name="jux:pytest_jux_version" value="0.2.1"/>
  <property name="jux:timestamp" value="2025-10-24T12:34:56+00:00"/>
</properties>
```

### Storage Structure Change

**Before (v0.2.1)**:
```
~/.local/share/jux/
├── reports/
│   └── sha256_abc123.xml
├── metadata/
│   └── sha256_abc123.json  # ← Removed
└── queue/
    ├── sha256_abc123.xml
    └── sha256_abc123.json  # ← Removed
```

**After (v0.3.0)**:
```
~/.local/share/jux/
├── reports/
│   └── sha256_abc123.xml  # Contains metadata in <properties>
└── queue/
    └── sha256_abc123.xml  # Contains metadata in <properties>
```

### Code Changes Summary

**Modified Files**:
- `pytest_jux/plugin.py` - Add `pytest_metadata()` hook
- `pytest_jux/storage.py` - Remove metadata methods and parameters
- `pytest_jux/commands/cache.py` - Read metadata from XML properties
- `pytest_jux/metadata.py` - Update documentation only

**New Files**:
- `tests/test_metadata_integration.py` - New test suite

**Removed Functionality**:
- JSON sidecar file creation
- `storage.get_metadata()` method
- Metadata directory handling

---

## Definition of Done

Sprint 7 is complete when:

- [x] ADR-0011 approved and documented
- [ ] `pytest_metadata` hook implemented and tested
- [ ] JSON sidecar storage removed
- [ ] All commands work without JSON files
- [ ] All tests pass (>88% coverage)
- [ ] Documentation updated
- [ ] Migration guide provided
- [ ] CHANGELOG.md updated
- [ ] Feature branch merged to develop
- [ ] Version bumped to 0.3.0

---

## Risks and Mitigations

### Risk 1: Breaking Change Impact

**Risk**: Users with existing JSON sidecar files may be surprised by removal

**Likelihood**: Low (JSON files were informational, not critical)

**Mitigation**:
- Provide clear migration guide
- Document breaking change prominently in CHANGELOG
- Use semantic versioning (0.3.0 = minor version bump)

### Risk 2: pytest-metadata Compatibility

**Risk**: pytest-metadata behavior may change or have edge cases

**Likelihood**: Low (pytest-metadata is mature and stable)

**Mitigation**:
- Pin pytest-metadata to known working version (>=3.0, <4.0)
- Test with multiple pytest versions
- Add integration tests

### Risk 3: XML Property Namespace Conflicts

**Risk**: "jux:" prefix may conflict with other plugins

**Likelihood**: Very Low (descriptive prefix, unlikely collision)

**Mitigation**:
- Use clear "jux:" prefix
- Document namespace usage
- Test with common pytest plugins

---

## Success Metrics

### Code Quality
- ✅ All tests pass
- ✅ Test coverage ≥88%
- ✅ No regressions in existing functionality
- ✅ Type checking passes (mypy)
- ✅ Linting passes (ruff)

### Architecture
- ✅ Single source of truth for metadata (XML)
- ✅ All metadata cryptographically signed
- ✅ Simpler storage model (XML only)
- ✅ Reduced code complexity in storage.py

### Documentation
- ✅ All docs updated
- ✅ Migration guide provided
- ✅ ADR-0011 approved
- ✅ CHANGELOG.md updated

### Security
- ✅ All metadata cryptographically bound
- ✅ Improved provenance tracking
- ✅ No security regressions

---

## Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| Week 1, Day 1-2 | Core Implementation | `pytest_metadata` hook, storage updates |
| Week 1, Day 3 | Command Updates | `jux-cache` XML reading |
| Week 1, Day 4 | Testing | `test_metadata_integration.py`, update existing tests |
| Week 1, Day 5 | Documentation | Update guides, create migration docs |
| Week 2, Day 1 | Testing & Refinement | Integration testing, edge cases |
| Week 2, Day 2 | Code Review & Merge | Final review, merge to develop |

**Target Completion**: End of Week 1 (aggressive) or Mid Week 2 (realistic)

---

## Post-Sprint Activities

After Sprint 7 completion:

1. **Tag v0.3.0 Release**
   - Update version in `pyproject.toml`
   - Update CHANGELOG.md
   - Create git tag
   - Push to GitHub

2. **Monitor for Issues**
   - Watch for user feedback on breaking changes
   - Be prepared to create hotfix if needed

3. **Plan Sprint 8**
   - Consider additional enhancements
   - Or proceed to Sprint 4 (API integration) if server ready

---

## Related Documents

- **ADR-0011**: Integrate Environment Metadata with pytest-metadata
- **Sprint 6 Retrospective**: Previous sprint outcomes
- **ROADMAP.md**: Long-term project vision

---

## Sprint Retrospective (TBD)

To be completed at end of sprint:
- What went well?
- What could be improved?
- Lessons learned
- Action items for next sprint

---

**Created**: 2025-10-24
**Author**: Georges Martin
**Sprint Type**: Architecture Improvement
**Priority**: High (security improvement, architectural simplification)
