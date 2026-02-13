# Sprint 5: SLSA Build Level 2 Compliance

**Sprint Duration**: TBD (5 weeks estimated)
**Sprint Goal**: Implement SLSA Build Level 2 compliance with provenance generation, signing, and verification
**Status**: 📋 Planned

## Overview

Sprint 5 implements supply chain security for pytest-jux by achieving SLSA Build Level 2 compliance. This sprint adds cryptographic provenance to all releases, enabling consumers to verify that packages were built from audited source code on trusted infrastructure.

**Why SLSA L2 for pytest-jux:**
- pytest-jux handles cryptographic keys (signing keys for test reports)
- Integrates into CI/CD pipelines (trusted environments)
- Claims to provide security guarantees (signed test reports)
- Must practice what it preaches: verifiable supply chain

**SLSA L2 Benefits:**
- Cryptographic proof packages match source code
- Protection against compromised developer workstations
- Protection against malicious build script injection
- Independent verification by any consumer
- Industry-standard supply chain security

## User Stories

### US-5.1: Automated Build Provenance Generation
**As a** package consumer
**I want** cryptographic build provenance for every pytest-jux release
**So that** I can verify the package was built from the public source repository

**Acceptance Criteria**:
- [ ] SLSA Provenance v1.0 generated for every release
- [ ] Provenance includes source commit SHA, build parameters, timestamps
- [ ] Provenance signed by GitHub Actions (not developer workstation)
- [ ] Provenance uploaded to GitHub Releases
- [ ] Provenance uploaded to PyPI with package
- [ ] Automated generation (no manual steps)

**Technical Tasks**:
- [ ] Create `.github/workflows/build.yml` workflow
- [ ] Configure build job with artifact hashing
- [ ] Add SLSA provenance generation job using `slsa-github-generator`
- [ ] Configure GitHub OIDC permissions
- [ ] Test provenance generation with pre-release
- [ ] Add provenance upload to GitHub Releases
- [ ] Configure PyPI Trusted Publishing (OIDC)
- [ ] Add provenance upload to PyPI

**Definition of Done**:
- Build workflow generates provenance for tagged releases
- Provenance verifiable with `slsa-verifier`
- Provenance accessible on GitHub Releases and PyPI
- No manual secrets required (GitHub OIDC only)

---

### US-5.2: Consumer Verification Capability
**As a** security-conscious consumer
**I want** to verify pytest-jux package authenticity
**So that** I can trust the package wasn't tampered with

**Acceptance Criteria**:
- [ ] Verification guide published in documentation
- [ ] Verification examples using `slsa-verifier` tool
- [ ] Verification process tested by external party
- [ ] README includes SLSA L2 badge
- [ ] Verification command provided for each release

**Technical Tasks**:
- [ ] Create `docs/security/SLSA_VERIFICATION.md`
- [ ] Document verification process with examples
- [ ] Add troubleshooting section
- [ ] Create verification test script
- [ ] Add SLSA badge to README.md
- [ ] Update security documentation index

**Definition of Done**:
- External party successfully verifies package
- Documentation includes working examples
- SLSA badge displayed on README
- Verification process takes < 5 minutes

---

### US-5.3: Build Reproducibility
**As a** release manager
**I want** reproducible builds
**So that** provenance hashes are consistent and verifiable

**Acceptance Criteria**:
- [ ] Builds produce identical artifacts for same source
- [ ] Build environment variables documented
- [ ] Dependency versions pinned
- [ ] Build process documented
- [ ] Reproducibility verified by CI

**Technical Tasks**:
- [ ] Create `requirements.lock` using `uv pip compile`
- [ ] Update build workflow to use lock file
- [ ] Add reproducibility test to CI
- [ ] Document build environment
- [ ] Add build instructions to README

**Definition of Done**:
- Two builds of same commit produce identical hashes
- Lock file committed to repository
- Build instructions documented
- Reproducibility test in CI passes

---

### US-5.4: SLSA Compliance Documentation
**As a** project maintainer
**I want** comprehensive SLSA documentation
**So that** the implementation is maintainable and auditable

**Acceptance Criteria**:
- [ ] ADR-0006 documented (SLSA adoption decision)
- [ ] Sprint 5 plan documented (this document)
- [ ] Security documentation updated
- [ ] README security section enhanced
- [ ] Release process updated with SLSA steps

**Technical Tasks**:
- [ ] Complete ADR-0006 (already done ✅)
- [ ] Complete Sprint 5 plan (this document)
- [ ] Update `docs/security/SECURITY.md`
- [ ] Update README security section
- [ ] Document release process with SLSA
- [ ] Add SLSA to CHANGELOG

**Definition of Done**:
- ADR-0006 accepted and merged
- All SLSA documentation complete
- Security documentation references SLSA
- Release process includes SLSA verification

---

## Sprint Timeline (5 Weeks)

### Week 1: Build Infrastructure Foundation
**Goal**: Create build workflow with artifact generation

**Tasks**:
- [ ] Create `.github/workflows/build.yml`
- [ ] Add build job (python -m build)
- [ ] Add artifact hash generation
- [ ] Add artifact upload
- [ ] Test workflow with manual trigger
- [ ] Verify artifacts are correct

**Deliverables**:
- Working build workflow
- Artifacts generated and hashed
- Manual build process documented

**Success Criteria**:
- Workflow runs successfully
- Artifacts uploaded to workflow runs
- Hashes computed correctly

---

### Week 2: SLSA Provenance Generation
**Goal**: Add provenance generation and signing

**Tasks**:
- [ ] Add SLSA provenance job to workflow
- [ ] Configure `slsa-github-generator` workflow
- [ ] Configure GitHub OIDC permissions
- [ ] Test provenance generation
- [ ] Verify provenance signature
- [ ] Upload provenance to workflow artifacts

**Deliverables**:
- SLSA provenance generated
- Provenance signed by GitHub Actions
- Provenance structure validated

**Success Criteria**:
- Provenance generated for every build
- Provenance verifiable with `slsa-verifier`
- Provenance includes correct source info

---

### Week 3: Distribution Integration
**Goal**: Distribute provenance to consumers

**Tasks**:
- [ ] Configure PyPI Trusted Publishing (OIDC)
- [ ] Add PyPI publish job to workflow
- [ ] Upload provenance to GitHub Releases
- [ ] Upload provenance to PyPI
- [ ] Test with pre-release (v0.1.5-alpha1)
- [ ] Verify provenance accessibility

**Deliverables**:
- PyPI Trusted Publishing configured
- Provenance on GitHub Releases
- Provenance on PyPI
- Pre-release tested

**Success Criteria**:
- Provenance accessible on both platforms
- PyPI attestations working
- Pre-release verifiable

---

### Week 4: Documentation and Verification
**Goal**: Enable consumer verification

**Tasks**:
- [ ] Create `docs/security/SLSA_VERIFICATION.md`
- [ ] Add verification examples
- [ ] Add troubleshooting guide
- [ ] Add SLSA badge to README
- [ ] Update security documentation
- [ ] Create verification test script
- [ ] External verification testing

**Deliverables**:
- Complete verification guide
- README updated with SLSA info
- Verification script
- External verification confirmed

**Success Criteria**:
- External party verifies package
- Documentation complete and clear
- Verification takes < 5 minutes

---

### Week 5: Validation and Release
**Goal**: Validate implementation and release

**Tasks**:
- [ ] Security review of SLSA implementation
- [ ] Test full release process with v0.1.5
- [ ] Verify OpenSSF Scorecard improvement
- [ ] Update CHANGELOG with SLSA
- [ ] Announce SLSA L2 compliance
- [ ] Monitor for issues
- [ ] Document lessons learned

**Deliverables**:
- SLSA L2 compliant release (v0.1.5)
- Security review complete
- Announcement published
- Retrospective documented

**Success Criteria**:
- v0.1.5 released with provenance
- OpenSSF Scorecard score improved
- No critical issues found
- Community feedback positive

---

## Technical Architecture

### Build Workflow Structure

```yaml
# .github/workflows/build.yml

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  # 1. Build Python package
  build:
    runs-on: ubuntu-latest
    outputs:
      hashes: ${{ steps.hash.outputs.hashes }}
    steps:
      - checkout code
      - setup Python
      - build package
      - compute hashes
      - upload artifacts

  # 2. Generate SLSA provenance (official generator)
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.0.0
    with:
      base64-subjects: "${{ needs.build.outputs.hashes }}"
      upload-assets: true

  # 3. Publish to PyPI with attestations
  publish-pypi:
    needs: [build, provenance]
    environment: pypi
    permissions:
      id-token: write
    steps:
      - download artifacts
      - download provenance
      - publish to PyPI with attestations
```

### SLSA Provenance Structure

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "pytest_jux-0.1.5-py3-none-any.whl",
      "digest": {
        "sha256": "abcdef123456..."
      }
    }
  ],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://slsa-framework.github.io/github-actions-buildtypes/workflow/v1",
      "externalParameters": {
        "workflow": {
          "ref": "refs/tags/v0.1.5",
          "repository": "https://github.com/jux-tools/pytest-jux"
        }
      },
      "internalParameters": {
        "github": {
          "event_name": "push",
          "actor_id": "1234567"
        }
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/jux-tools/pytest-jux@refs/tags/v0.1.5",
          "digest": {
            "gitCommit": "abc123..."
          }
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v2.0.0"
      },
      "metadata": {
        "invocationId": "https://github.com/jux-tools/pytest-jux/actions/runs/123456",
        "startedOn": "2025-10-26T12:00:00Z",
        "finishedOn": "2025-10-26T12:05:00Z"
      }
    }
  }
}
```

### Verification Process

```bash
# Consumer verification steps

# 1. Install verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# 2. Download package
pip download pytest-jux==0.1.5 --no-deps

# 3. Download provenance (from GitHub Releases)
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.1.5/pytest-jux-0.1.5.intoto.jsonl

# 4. Verify provenance
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  pytest_jux-0.1.5-py3-none-any.whl

# Expected output:
# Verified signature against tlog entry index 12345...
# Verified build using builder "https://github.com/slsa-framework/slsa-github-generator/..."
# PASSED: Verified SLSA provenance
```

---

## Dependencies

### External Services
- **GitHub Actions**: Hosted build platform (already in use)
- **GitHub OIDC**: Signing identity (no additional setup)
- **PyPI Trusted Publishing**: OIDC authentication (requires PyPI config)
- **SLSA GitHub Generator**: Official provenance generator (maintained by SLSA team)

### Tools and Libraries
- **slsa-framework/slsa-github-generator**: Official SLSA provenance generator
- **slsa-verifier**: Official verification tool (Go binary)
- **python-build**: Package build tool (already in use)
- **uv**: Fast Python package manager (already in use)

### Documentation References
- [SLSA Specification v1.0](https://slsa.dev/spec/v1.0/)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)
- [PyPI Attestations](https://docs.pypi.org/attestations/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)

---

## Risk Assessment

### High Risk
**Build Workflow Complexity**
- **Risk**: GitHub Actions workflow misconfiguration
- **Impact**: Provenance not generated or invalid
- **Mitigation**: Test with pre-releases, use official SLSA generator, peer review

**PyPI Integration Issues**
- **Risk**: PyPI attestation upload fails
- **Impact**: Provenance not available to pip users
- **Mitigation**: Test with PyPI test server first, fallback to manual upload

### Medium Risk
**Consumer Adoption**
- **Risk**: Users don't verify provenance
- **Impact**: Security benefit not realized
- **Mitigation**: Clear documentation, verification examples, automation tools

**SLSA Generator Updates**
- **Risk**: Breaking changes in SLSA generator
- **Impact**: Workflow breaks on updates
- **Mitigation**: Pin generator version, monitor changelog, test updates

### Low Risk
**Verification Tool Availability**
- **Risk**: slsa-verifier not available on all platforms
- **Impact**: Some users can't verify
- **Mitigation**: Document alternative verification methods, provide web UI

---

## Success Metrics

### Technical Metrics
- [ ] 100% of releases have SLSA provenance
- [ ] 100% of provenance signatures verify successfully
- [ ] 100% of releases verifiable with `slsa-verifier`
- [ ] 0 manual steps in release process
- [ ] < 5 minutes added to release workflow time

### Quality Metrics
- [ ] OpenSSF Scorecard score improvement (target: 8.5+)
- [ ] SLSA badge displayed on README
- [ ] External verification successful (3rd party)
- [ ] Documentation complete score (all sections)

### Security Metrics
- [ ] Build provenance includes source commit
- [ ] Provenance signed by GitHub Actions (not tenant)
- [ ] Provenance distributed on 2+ platforms
- [ ] Verification process documented
- [ ] Zero build secrets in workflows

### Community Metrics
- [ ] Positive feedback from security researchers
- [ ] Adoption by security-conscious users
- [ ] Referenced in SLSA adoption examples
- [ ] Blog post or announcement published

---

## Definition of Done

Sprint 5 is complete when:

### Build Infrastructure
- [x] ADR-0006 accepted and merged
- [ ] Build workflow creates reproducible artifacts
- [ ] SLSA provenance generated for all releases
- [ ] Provenance signed by GitHub Actions
- [ ] Provenance verifiable with `slsa-verifier`

### Distribution
- [ ] Provenance uploaded to GitHub Releases
- [ ] Provenance uploaded to PyPI
- [ ] PyPI Trusted Publishing configured
- [ ] Release process automated (no manual steps)

### Documentation
- [ ] SLSA verification guide complete
- [ ] README includes SLSA badge
- [ ] Security documentation updated
- [ ] Release process documented
- [ ] ADR and Sprint docs complete

### Validation
- [ ] External party verifies package successfully
- [ ] Pre-release tested (v0.1.5-alpha1)
- [ ] Production release tested (v0.1.5)
- [ ] OpenSSF Scorecard improvement verified
- [ ] No critical issues found

### Quality Gates
- [ ] All tests pass (100%)
- [ ] Security review complete
- [ ] Code review complete
- [ ] No regressions introduced
- [ ] Backward compatibility maintained

---

## Post-Sprint Activities

### Monitoring
- Monitor GitHub Actions workflow success rate
- Monitor PyPI attestation availability
- Monitor consumer feedback on verification
- Monitor OpenSSF Scorecard trends

### Future Enhancements (Sprint 6+)
- **SLSA Build Level 3**: Hermetic builds, dependency provenance
- **Dependency Verification**: Verify all dependencies have SLSA provenance
- **Reproducible Builds**: Bit-for-bit reproducibility
- **Supply Chain Monitoring**: Continuous monitoring of dependency chain
- **Automated Verification**: CI/CD integration for consumers

### Documentation Improvements
- Video tutorial for verification
- Web-based verification tool
- Integration guides for popular CI/CD platforms
- Troubleshooting FAQ

---

## Related Documentation

- **ADR-0006**: Adopt SLSA Build Level 2 Compliance
- **ADR-0005**: Adopt Python Ecosystem Security Framework
- **ADR-0002**: Adopt Development Best Practices
- **Sprint 0**: Project Initialization (security framework)
- **Sprint 1**: Core Infrastructure (XMLDSig foundation)

---

## Notes

**Sprint Naming**: This is Sprint 5 because Sprint 4 was reserved for API integration (when Jux API Server becomes available). SLSA compliance is independent of API integration and can be implemented immediately.

**SLSA L3 Future**: This sprint achieves SLSA L2. SLSA L3 requires hermetic builds and is planned for a future sprint after L2 is stable.

**Consumer Impact**: SLSA L2 is backward compatible - consumers not verifying provenance will not be affected. Verification is opt-in.

**Maintenance Burden**: After initial setup, SLSA provenance is generated automatically. Maintenance is minimal (monitor SLSA generator updates).
