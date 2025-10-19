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
curl -L -O https://github.com/jrjsmrtn/pytest-jux/releases/download/v0.1.5/pytest-jux-0.1.5.intoto.jsonl

# 3. Verify provenance
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jrjsmrtn/pytest-jux \
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
  --source-uri github.com/jrjsmrtn/pytest-jux \
  --source-tag v0.1.5 \
  pytest_jux-0.1.5-py3-none-any.whl
```

### Verify Source Branch

Verify the package was built from the main branch:

```bash
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jrjsmrtn/pytest-jux \
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
          "repository": "https://github.com/jrjsmrtn/pytest-jux",
          "path": ".github/workflows/build-release.yml"
        }
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/jrjsmrtn/pytest-jux@refs/tags/v0.1.5",
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
        "invocationId": "https://github.com/jrjsmrtn/pytest-jux/actions/runs/1234567890",
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
          curl -L -O https://github.com/jrjsmrtn/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl

          slsa-verifier verify-artifact \
            --provenance-path pytest-jux-${VERSION}.intoto.jsonl \
            --source-uri github.com/jrjsmrtn/pytest-jux \
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
    - curl -L -O https://github.com/jrjsmrtn/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl

    - |
      slsa-verifier verify-artifact \
        --provenance-path pytest-jux-${VERSION}.intoto.jsonl \
        --source-uri github.com/jrjsmrtn/pytest-jux \
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
FAILED: expected source 'github.com/jrjsmrtn/pytest-jux', got 'https://github.com/jrjsmrtn/pytest-jux'
```

**Solution:**
Use the short form without `https://`:
```bash
--source-uri github.com/jrjsmrtn/pytest-jux
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
curl -L -O https://github.com/jrjsmrtn/pytest-jux/releases/download/v${VERSION}/pytest-jux-${VERSION}.intoto.jsonl
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
        "--source-uri", "github.com/jrjsmrtn/pytest-jux",
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

## Resources

### Official Documentation

- [SLSA Specification](https://slsa.dev/spec/v1.0/)
- [SLSA Verifier](https://github.com/slsa-framework/slsa-verifier)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)
- [PyPI Attestations](https://docs.pypi.org/attestations/)

### pytest-jux Security Documentation

- [ADR-0006: Adopt SLSA Build Level 2](../adr/0006-adopt-slsa-build-level-2-compliance.md)
- [Sprint 5: SLSA Compliance](../sprints/sprint-05-slsa-compliance.md)
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
3. Open an issue: https://github.com/jrjsmrtn/pytest-jux/issues
4. Security concerns: See [SECURITY.md](SECURITY.md) for responsible disclosure

---

**Last Updated**: 2025-10-19
**SLSA Level**: Build L2
**Generator Version**: slsa-github-generator v2.0.0
