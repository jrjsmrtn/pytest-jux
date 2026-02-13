# SLSA Provenance Verification

pytest-jux releases include **SLSA Build Level 2** provenance attestations, providing cryptographic proof that packages were built from the public source repository on trusted infrastructure.

## What is SLSA?

Supply-chain Levels for Software Artifacts (SLSA, pronounced "salsa") is a security framework that prevents supply chain attacks. SLSA Level 2 provides:

- ✅ **Build Integrity**: Packages built on hosted infrastructure (GitHub Actions)
- ✅ **Source Traceability**: Cryptographic link to exact source code commit
- ✅ **Tamper Detection**: Any modification invalidates the signature
- ✅ **Independent Verification**: Anyone can verify package authenticity

## Quick Verification

### Prerequisites

Install the official SLSA verifier tool:

```bash
# Using Go (recommended)
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Or download binary from: https://github.com/slsa-framework/slsa-verifier/releases
```

### Verify a Release

```bash
# 1. Download package
pip download pytest-jux==0.1.5 --no-deps

# 2. Download provenance from GitHub Release
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.1.5/pytest-jux-0.1.5.intoto.jsonl

# 3. Verify provenance
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  pytest_jux-0.1.5-py3-none-any.whl
```

### Expected Output

```
Verified signature against tlog entry index 12345678 at URL: https://rekor.sigstore.dev/api/v1/log/entries/...
Verified build using builder "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v2.0.0" at commit sha256:abc123...
Verifying artifact pytest_jux-0.1.5-py3-none-any.whl: PASSED

PASSED: Verified SLSA provenance
```

## Detailed Verification

### Verify Specific Commit

Verify that a package was built from a specific source commit:

```bash
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  --source-tag v0.1.5 \
  pytest_jux-0.1.5-py3-none-any.whl
```

### Verify Source Branch

Verify the package was built from the main branch:

```bash
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  --source-branch main \
  pytest_jux-0.1.5-py3-none-any.whl
```

### Inspect Provenance Contents

View the provenance attestation contents:

```bash
cat pytest-jux-0.1.5.intoto.jsonl | jq .
```

Example provenance structure:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "pytest_jux-0.1.5-py3-none-any.whl",
      "digest": {
        "sha256": "abcdef1234567890..."
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
          "repository": "https://github.com/jux-tools/pytest-jux",
          "path": ".github/workflows/build-release.yml"
        }
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/jux-tools/pytest-jux@refs/tags/v0.1.5",
          "digest": {
            "gitCommit": "abc123def456..."
          }
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v2.0.0"
      },
      "metadata": {
        "invocationId": "https://github.com/jux-tools/pytest-jux/actions/runs/1234567890",
        "startedOn": "2025-10-26T12:00:00Z",
        "finishedOn": "2025-10-26T12:05:00Z"
      }
    }
  }
}
```

## PyPI Attestations

pytest-jux releases also include attestations on PyPI:

### View PyPI Attestations

1. Visit https://pypi.org/project/pytest-jux/
2. Click on the version (e.g., "0.1.5")
3. Scroll to "Attestations" section
4. Click "View attestations" to see provenance

### Download from PyPI

```bash
# PyPI attestations are automatically verified by pip (pip >= 24.2)
pip install pytest-jux==0.1.5 --require-hashes

# Or download attestations manually
pip download pytest-jux==0.1.5 --no-deps
```

## CI/CD Integration

### Verify in GitHub Actions

```yaml
# .github/workflows/verify-dependencies.yml
name: Verify Dependencies

on:
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install slsa-verifier
        run: |
          go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

      - name: Download and verify pytest-jux
        run: |
          VERSION="0.1.5"
          pip download pytest-jux==${VERSION} --no-deps
          curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl

          slsa-verifier verify-artifact \
            --provenance-path pytest-jux-${VERSION}.intoto.jsonl \
            --source-uri github.com/jux-tools/pytest-jux \
            pytest_jux-${VERSION}-py3-none-any.whl
```

### Verify in GitLab CI

```yaml
# .gitlab-ci.yml
verify-dependencies:
  stage: verify
  image: golang:1.21
  script:
    - go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest
    - export PATH="$PATH:$(go env GOPATH)/bin"

    - VERSION="0.1.5"
    - pip download pytest-jux==${VERSION} --no-deps
    - curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl

    - |
      slsa-verifier verify-artifact \
        --provenance-path pytest-jux-${VERSION}.intoto.jsonl \
        --source-uri github.com/jux-tools/pytest-jux \
        pytest_jux-${VERSION}-py3-none-any.whl
```

## What SLSA L2 Protects Against

SLSA Build Level 2 provides protection against:

| Threat | Protection | How |
|--------|-----------|-----|
| **Compromised Developer Workstation** | ✅ Yes | Builds run on GitHub Actions, not developer machines |
| **Malicious Build Script Injection** | ✅ Yes | Build process defined in version-controlled workflow |
| **Package Substitution** | ✅ Yes | Cryptographic link between source and artifact |
| **Man-in-the-Middle Attacks** | ✅ Yes | Signed provenance prevents tampering |
| **Supply Chain Backdoors** | ⚠️ Partial | Detects post-build tampering, not malicious source code |

### Limitations

SLSA L2 does **NOT** protect against:

- ❌ Malicious code in the source repository (requires code review)
- ❌ Compromised dependencies (requires dependency provenance verification)
- ❌ GitHub Actions platform compromise (SLSA L3+ required)

## Troubleshooting

### Verification Failed: Invalid Signature

**Error:**
```
FAILED: SLSA verification failed: invalid signature
```

**Solution:**
- Ensure provenance file matches the package version
- Download provenance from official GitHub Releases
- Check that package wasn't modified after download

### Verifier Not Found

**Error:**
```
slsa-verifier: command not found
```

**Solution:**
```bash
# Ensure Go is installed
go version

# Ensure GOPATH/bin is in PATH
export PATH="$PATH:$(go env GOPATH)/bin"

# Reinstall verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest
```

### Wrong Source URI

**Error:**
```
FAILED: expected source 'github.com/jux-tools/pytest-jux', got 'https://github.com/jux-tools/pytest-jux'
```

**Solution:**
Use the short form without `https://`:
```bash
--source-uri github.com/jux-tools/pytest-jux
```

### Provenance File Not Found

**Error:**
```
no such file or directory: pytest-jux-0.1.5.intoto.jsonl
```

**Solution:**
Download provenance from GitHub Release:
```bash
VERSION="0.1.5"
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl
```

## Security Best Practices

### For Consumers

1. **Always Verify**: Verify provenance before using in production
2. **Pin Versions**: Use exact versions, not version ranges
3. **Check Commit**: Verify the source commit hash matches expectations
4. **Automated Verification**: Add verification to CI/CD pipelines
5. **Monitor Releases**: Subscribe to GitHub release notifications

### For CI/CD Pipelines

1. **Fail on Verification Failure**: Don't continue if verification fails
2. **Cache Verifier**: Cache `slsa-verifier` binary to speed up builds
3. **Verify All Dependencies**: Check all security-critical dependencies
4. **Log Verification**: Keep audit logs of verification results
5. **Alert on Failures**: Send alerts when verification fails

## Alternative Verification Methods

### Using Python

```python
#!/usr/bin/env python3
"""Verify pytest-jux SLSA provenance using Python."""

import subprocess
import sys

def verify_package(version: str) -> bool:
    """Verify SLSA provenance for pytest-jux package."""
    package = f"pytest_jux-{version}-py3-none-any.whl"
    provenance = f"pytest-jux-{version}.intoto.jsonl"

    cmd = [
        "slsa-verifier",
        "verify-artifact",
        "--provenance-path", provenance,
        "--source-uri", "github.com/jux-tools/pytest-jux",
        "--source-tag", f"v{version}",
        package,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Verification PASSED for {package}")
        return True
    else:
        print(f"❌ Verification FAILED for {package}")
        print(result.stderr)
        return False

if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "0.1.5"
    success = verify_package(version)
    sys.exit(0 if success else 1)
```

Usage:
```bash
python verify_pytest_jux.py 0.1.5
```

## Software Bill of Materials (SBOM)

pytest-jux releases include a **CycloneDX SBOM** (Software Bill of Materials) that provides a complete inventory of all dependencies. This enables security auditing, vulnerability tracking, and compliance verification.

### What is an SBOM?

A Software Bill of Materials is a formal, machine-readable inventory of all components in a software package. The pytest-jux SBOM provides:

- ✅ **Dependency Inventory**: Complete list of all direct and transitive dependencies
- ✅ **Version Tracking**: Exact versions of all components
- ✅ **License Information**: License identifiers for each component
- ✅ **Vulnerability Scanning**: Enable automated security scanning
- ✅ **Compliance Auditing**: Support supply chain compliance requirements

### Quick SBOM Verification

#### Prerequisites

Install CycloneDX CLI tool:

```bash
# Using npm (recommended)
npm install -g @cyclonedx/cyclonedx-cli

# Using pip
pip install cyclonedx-bom

# Or download binary from: https://github.com/CycloneDX/cyclonedx-cli/releases
```

#### Download and Validate SBOM

```bash
# 1. Download SBOM from GitHub Release
VERSION="0.2.0"
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}-sbom.cdx.json

# 2. Validate SBOM format
cyclonedx-cli validate \
  --input-file pytest-jux-${VERSION}-sbom.cdx.json \
  --input-format json

# 3. View SBOM summary
cyclonedx-cli analyze \
  --input-file pytest-jux-${VERSION}-sbom.cdx.json
```

### Expected Output

```
Validating pytest-jux-0.2.0-sbom.cdx.json
✓ Valid CycloneDX BOM
  - Spec version: 1.6
  - Components: 42
  - Dependencies: 38
  - Format: JSON

Analysis:
  Total Components: 42
  Direct Dependencies: 8
  Transitive Dependencies: 34
  Licenses Found: 12
```

### Auditing Dependencies

#### Using pip-audit

Scan the SBOM for known vulnerabilities:

```bash
# Install pip-audit
pip install pip-audit

# Audit dependencies from SBOM
pip-audit --desc on -r <(cyclonedx-cli convert \
  --input-file pytest-jux-0.2.0-sbom.cdx.json \
  --output-format requirements.txt)
```

#### Using Grype

Alternative vulnerability scanning with Grype:

```bash
# Install Grype
brew install grype

# Scan SBOM
grype sbom:pytest-jux-0.2.0-sbom.cdx.json
```

#### Using OWASP Dependency-Check

Enterprise-grade vulnerability scanning:

```bash
# Install Dependency-Check
brew install dependency-check

# Scan SBOM
dependency-check \
  --scan pytest-jux-0.2.0-sbom.cdx.json \
  --format HTML \
  --out dependency-check-report.html
```

### Inspecting SBOM Contents

#### View Component List

```bash
# Pretty-print SBOM
cat pytest-jux-0.2.0-sbom.cdx.json | jq .

# List all components
cat pytest-jux-0.2.0-sbom.cdx.json | jq '.components[] | {name, version, licenses}'

# Count components
cat pytest-jux-0.2.0-sbom.cdx.json | jq '.components | length'
```

#### Extract License Information

```bash
# List all licenses
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | .licenses[]?.license.id' | sort -u

# Find components with specific license
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | select(.licenses[]?.license.id == "MIT")'
```

#### Find Specific Dependencies

```bash
# Search for a specific component
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | select(.name == "lxml")'

# List components from specific author/vendor
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | select(.author? == "Python Software Foundation")'
```

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/sbom-audit.yml
name: SBOM Audit

on:
  pull_request:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Download SBOM
        run: |
          VERSION="0.2.0"
          curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}-sbom.cdx.json

      - name: Install tools
        run: |
          npm install -g @cyclonedx/cyclonedx-cli
          pip install pip-audit

      - name: Validate SBOM
        run: |
          cyclonedx-cli validate \
            --input-file pytest-jux-${VERSION}-sbom.cdx.json \
            --fail-on-errors

      - name: Audit vulnerabilities
        run: |
          cyclonedx-cli convert \
            --input-file pytest-jux-${VERSION}-sbom.cdx.json \
            --output-format requirements.txt \
            --output-file requirements.txt
          pip-audit -r requirements.txt --desc
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
sbom-audit:
  stage: security
  image: python:3.11
  script:
    - VERSION="0.2.0"
    - curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}-sbom.cdx.json

    - npm install -g @cyclonedx/cyclonedx-cli
    - pip install pip-audit

    - cyclonedx-cli validate --input-file pytest-jux-${VERSION}-sbom.cdx.json
    - cyclonedx-cli convert --input-file pytest-jux-${VERSION}-sbom.cdx.json --output-format requirements.txt --output-file requirements.txt
    - pip-audit -r requirements.txt --desc
  only:
    - schedules
    - merge_requests
```

### SBOM Generation (For Developers)

If you're building from source and want to generate your own SBOM:

```bash
# Install cyclonedx-bom
pip install cyclonedx-bom

# Generate SBOM from pyproject.toml
cyclonedx-py requirements \
  --pyproject pyproject.toml \
  --format json \
  --output-file pytest-jux-custom-sbom.cdx.json

# Validate generated SBOM
cyclonedx-cli validate --input-file pytest-jux-custom-sbom.cdx.json
```

### Comparing SBOMs

Compare SBOMs between versions to track dependency changes:

```bash
# Download two versions
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.1.8/pytest-jux-0.1.8-sbom.cdx.json
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.2.0/pytest-jux-0.2.0-sbom.cdx.json

# Extract component names and versions
jq '.components[] | "\(.name)@\(.version)"' pytest-jux-0.1.8-sbom.cdx.json | sort > v0.1.8-deps.txt
jq '.components[] | "\(.name)@\(.version)"' pytest-jux-0.2.0-sbom.cdx.json | sort > v0.2.0-deps.txt

# Show differences
diff v0.1.8-deps.txt v0.2.0-deps.txt
```

### SBOM Use Cases

#### Security Auditing

```bash
# Find all components with CVEs
grype sbom:pytest-jux-0.2.0-sbom.cdx.json --only-fixed

# Generate security report
dependency-check --scan pytest-jux-0.2.0-sbom.cdx.json --format ALL
```

#### License Compliance

```bash
# Extract all licenses for review
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | {name, version, license: .licenses[]?.license.id}' | \
  jq -s 'group_by(.license) | map({license: .[0].license, count: length, components: map(.name)})'

# Find GPL-licensed components (example)
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | select(.licenses[]?.license.id | contains("GPL"))'
```

#### Supply Chain Verification

```bash
# Verify all components are from trusted sources
cat pytest-jux-0.2.0-sbom.cdx.json | \
  jq '.components[] | {name, version, purl: .purl}' | \
  grep "pkg:pypi/"
```

### Troubleshooting

#### SBOM Validation Failed

**Error:**
```
ERROR: Invalid BOM: Missing required field 'version'
```

**Solution:**
- Ensure you downloaded the complete SBOM file
- Re-download from GitHub Releases
- Check file integrity (not corrupted)

#### CycloneDX CLI Not Found

**Error:**
```
cyclonedx-cli: command not found
```

**Solution:**
```bash
# Install via npm
npm install -g @cyclonedx/cyclonedx-cli

# Verify installation
cyclonedx-cli --version
```

#### pip-audit Incompatible SBOM Format

**Error:**
```
ERROR: Cannot read CycloneDX JSON format
```

**Solution:**
```bash
# Convert SBOM to requirements.txt first
cyclonedx-cli convert \
  --input-file pytest-jux-0.2.0-sbom.cdx.json \
  --output-format requirements.txt \
  --output-file requirements.txt

# Then run pip-audit
pip-audit -r requirements.txt
```

#### Grype Fails to Parse SBOM

**Error:**
```
ERROR: failed to parse SBOM
```

**Solution:**
```bash
# Ensure SBOM is valid JSON
cat pytest-jux-0.2.0-sbom.cdx.json | jq . > /dev/null

# Validate with CycloneDX CLI
cyclonedx-cli validate --input-file pytest-jux-0.2.0-sbom.cdx.json

# Use correct Grype syntax
grype sbom:pytest-jux-0.2.0-sbom.cdx.json
```

### SBOM Best Practices

#### For Consumers

1. **Verify SBOM Integrity**: Always validate SBOM format before using
2. **Automate Scanning**: Set up automated vulnerability scanning in CI/CD
3. **Track Changes**: Compare SBOMs between versions to identify new dependencies
4. **License Review**: Audit licenses for compliance with your organization's policies
5. **Archive SBOMs**: Keep historical SBOMs for audit trail

#### For Security Teams

1. **Continuous Monitoring**: Scan SBOMs regularly for new vulnerabilities
2. **Blocklist Components**: Identify and block problematic dependencies
3. **Compliance Checks**: Automate license compliance verification
4. **Incident Response**: Use SBOMs for rapid vulnerability impact assessment
5. **Supply Chain Mapping**: Build dependency graphs from SBOM data

## Resources

### Official Documentation

- [SLSA Specification](https://slsa.dev/spec/v1.0/)
- [SLSA Verifier](https://github.com/slsa-framework/slsa-verifier)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)
- [PyPI Attestations](https://docs.pypi.org/attestations/)
- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [CycloneDX CLI](https://github.com/CycloneDX/cyclonedx-cli)
- [NTIA SBOM Minimum Elements](https://www.ntia.gov/files/ntia/publications/sbom_minimum_elements_report.pdf)

### Security Tools

- [pip-audit](https://github.com/pypa/pip-audit) - PyPA vulnerability scanner
- [Grype](https://github.com/anchore/grype) - Vulnerability scanner for containers and SBOMs
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) - Dependency vulnerability scanner
- [Trivy](https://github.com/aquasecurity/trivy) - Comprehensive security scanner

### pytest-jux Security Documentation

- [ADR-0006: Adopt SLSA Build Level 2](../adr/0006-adopt-slsa-build-level-2-compliance.md)
- [Sprint 5: SLSA Compliance](../sprints/sprint-05-slsa-compliance.md)
- [Sprint 6: OpenSSF Best Practices](../sprints/sprint-06-openssf-badge.md)
- [Security Policy](SECURITY.md)
- [Threat Model](THREAT_MODEL.md)

### Community Resources

- [OpenSSF SLSA Guide](https://openssf.org/blog/2023/12/14/slsa-build-level-1-requirements/)
- [SLSA Tooling](https://slsa.dev/spec/v1.0/tooling)
- [Sigstore Transparency Log](https://docs.sigstore.dev/logging/overview/)

## Support

If you encounter issues with SLSA verification:

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Review the [SLSA Verifier Issues](https://github.com/slsa-framework/slsa-verifier/issues)
3. Open an issue: https://github.com/jux-tools/pytest-jux/issues
4. Security concerns: See [SECURITY.md](SECURITY.md) for responsible disclosure

---

**Last Updated**: 2025-10-20
**SLSA Level**: Build L2
**Generator Version**: slsa-github-generator v2.0.0
**SBOM Format**: CycloneDX 1.6 (JSON)
