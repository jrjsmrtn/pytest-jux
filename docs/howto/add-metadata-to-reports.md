# How to Add Metadata to JUnit XML Reports

This guide shows how to add custom metadata to your JUnit XML test reports using pytest-metadata integration.

## Prerequisites

pytest-metadata is automatically installed as a required dependency of pytest-jux. No additional installation is needed.

## Quick Start

### Add Metadata via Command Line

Add metadata key-value pairs when running pytest:

```bash
pytest --junit-xml=report.xml --metadata ci_build_id 12345
```

This adds a property tag to the JUnit XML:

```xml
<testsuite>
  <properties>
    <property name="ci_build_id" value="12345"/>
  </properties>
  ...
</testsuite>
```

### Add Multiple Metadata Pairs

```bash
pytest --junit-xml=report.xml \
  --metadata ci_build_id 12345 \
  --metadata branch main \
  --metadata commit_sha abc123def
```

### Enable Metadata in Test Files

To include metadata in JUnit XML, mark your test module with the `include_metadata_in_junit_xml` fixture:

```python
# test_example.py
import pytest

# Enable metadata inclusion in JUnit XML
pytestmark = pytest.mark.usefixtures('include_metadata_in_junit_xml')

def test_something():
    assert True
```

## Common Use Cases

### CI/CD Pipeline Information

Capture build information in your CI/CD pipeline:

```bash
pytest --junit-xml=report.xml \
  --jux-sign --jux-publish \
  --metadata ci_provider "GitLab CI" \
  --metadata pipeline_id "$CI_PIPELINE_ID" \
  --metadata job_id "$CI_JOB_ID" \
  --metadata commit_sha "$CI_COMMIT_SHA" \
  --metadata branch "$CI_COMMIT_BRANCH"
```

### Environment Information

Add deployment or environment context:

```bash
pytest --junit-xml=report.xml \
  --metadata environment "staging" \
  --metadata region "us-west-2" \
  --metadata cluster "k8s-prod-01"
```

### JSON Metadata

For complex metadata structures, use JSON:

```bash
pytest --junit-xml=report.xml \
  --metadata-from-json '{"build": {"id": 123, "status": "success"}}'
```

Or load from a JSON file:

```bash
# metadata.json
{
  "ci": {
    "provider": "GitLab",
    "pipeline_id": 12345
  },
  "deployment": {
    "environment": "production",
    "region": "us-east-1"
  }
}
```

```bash
pytest --junit-xml=report.xml --metadata-from-json-file metadata.json
```

## Programmatic Metadata

### Using conftest.py

Add metadata programmatically using the `pytest_metadata` hook:

```python
# conftest.py
import platform
import pytest

@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata):
    """Add custom metadata to pytest session."""
    # Add system information
    metadata['os_type'] = platform.system()
    metadata['os_version'] = platform.release()

    # Add application version
    metadata['app_version'] = '1.2.3'

    # Remove sensitive data
    metadata.pop('Plugins', None)  # Don't include plugin list
```

### Access Metadata in Tests

Use the `metadata` fixture to access metadata in your tests:

```python
def test_with_metadata(metadata):
    """Test that can access metadata."""
    print(f"Running on: {metadata['Python']}")
    print(f"Platform: {metadata['Platform']}")
    assert True
```

## Integration with pytest-jux

### Automatic Environment Metadata

**New in v0.3.0**: pytest-jux automatically captures and adds environment metadata to every test report. This metadata is added via the `pytest_metadata` hook and includes:

#### Core Metadata (jux: prefix)
- `jux:hostname` - Machine hostname
- `jux:username` - User running tests
- `jux:platform` - OS and version
- `jux:python_version` - Python interpreter version
- `jux:pytest_version` - pytest version
- `jux:pytest_jux_version` - pytest-jux version
- `jux:timestamp` - ISO 8601 timestamp (UTC)

#### Project Name (no prefix)
- `project` - Project name (mandatory)
  - Extracted from git remote URL
  - Or read from `pyproject.toml` ([project] name)
  - Or from `JUX_PROJECT_NAME` environment variable
  - Or falls back to current directory name

#### Git Metadata (git: prefix) - Auto-detected
- `git:commit` - Git commit SHA
- `git:branch` - Git branch name
- `git:status` - Working tree status ("clean" or "dirty")
- `git:remote` - Git remote URL (credentials sanitized)

#### CI Metadata (ci: prefix) - Auto-detected
- `ci:provider` - CI provider ("github", "gitlab", "jenkins", "travis", "circleci")
- `ci:build_id` - CI build/pipeline ID
- `ci:build_url` - CI build URL

#### Environment Variables (env: prefix) - Auto-captured
- `env:GITHUB_SHA`, `env:GITHUB_REF`, etc. (GitHub Actions)
- `env:CI_COMMIT_SHA`, `env:CI_PIPELINE_ID`, etc. (GitLab CI)
- `env:GIT_COMMIT`, `env:BUILD_NUMBER`, etc. (Jenkins)
- And more for Travis CI, CircleCI

**Overriding automatic metadata**: You can override any automatic metadata by providing the same key via CLI:

```bash
# Override hostname (useful in containerized environments)
pytest --junit-xml=report.xml --metadata jux:hostname "custom-hostname"

# Override project name
pytest --junit-xml=report.xml --metadata project "my-custom-project-name"
```

### Signing Reports with Metadata

pytest-jux preserves all metadata when signing reports:

```bash
pytest --junit-xml=report.xml \
  --jux-sign \
  --jux-key .jux/signing_key.pem \
  --metadata build_id 12345 \
  --metadata environment production
```

The signed XML will include both:
1. XMLDSig signature (added by pytest-jux)
2. Property tags with metadata (from pytest-metadata)

### Metadata in Stored Reports

**Important (v0.3.0+)**: All metadata is now embedded in JUnit XML `<properties>` elements and cryptographically signed with the report. There are no separate JSON sidecar files.

When storing reports locally, the XML file contains both user-provided metadata and environment metadata:

```
.jux/reports/
└── reports/
    └── sha256_abc123.xml          # Contains all metadata + signature
```

**XML file** (sha256_abc123.xml):
```xml
<testsuite>
  <properties>
    <!-- User-provided metadata (from CLI) -->
    <property name="build_id" value="12345"/>
    <property name="environment" value="production"/>

    <!-- Project name (mandatory, auto-detected) -->
    <property name="project" value="my-project"/>

    <!-- pytest-jux core metadata (automatic) -->
    <property name="jux:hostname" value="ci-runner-01"/>
    <property name="jux:username" value="gitlab-runner"/>
    <property name="jux:platform" value="Linux-5.15.0"/>
    <property name="jux:python_version" value="3.11.4"/>
    <property name="jux:pytest_version" value="8.4.2"/>
    <property name="jux:pytest_jux_version" value="0.3.0"/>
    <property name="jux:timestamp" value="2025-10-19T12:34:56+00:00"/>

    <!-- Git metadata (auto-detected) -->
    <property name="git:commit" value="abc123def456..."/>
    <property name="git:branch" value="main"/>
    <property name="git:status" value="clean"/>
    <property name="git:remote" value="https://gitlab.com/owner/my-project.git"/>

    <!-- CI metadata (auto-detected) -->
    <property name="ci:provider" value="gitlab"/>
    <property name="ci:build_id" value="789012"/>
    <property name="ci:build_url" value="https://gitlab.com/owner/my-project/-/pipelines/789012"/>

    <!-- Environment variables (auto-captured from CI) -->
    <property name="env:CI_COMMIT_SHA" value="abc123def456..."/>
    <property name="env:CI_PIPELINE_ID" value="789012"/>
    <property name="env:CI_JOB_ID" value="345678"/>
  </properties>
  <ds:Signature>...</ds:Signature>
  ...
</testsuite>
```

**Benefits of XML-embedded metadata:**
- ✅ All metadata cryptographically signed (tamper-proof)
- ✅ Single file for transport and storage
- ✅ Standard JUnit XML compliance
- ✅ No risk of files becoming separated

## Configuration File Integration

Add metadata configuration to `.jux.conf`:

```ini
[jux]
enabled = true
sign = true
key_path = .jux/signing_key.pem

# Metadata is added via command-line or conftest.py
# Example command:
# pytest --junit-xml=report.xml --metadata build_id $BUILD_ID
```

## Viewing Metadata

### In Terminal

Run pytest with `--verbose` to see metadata in the terminal header:

```bash
pytest --verbose --metadata build_id 12345
```

Output:
```
======================== test session starts =========================
platform linux -- Python 3.11.4, pytest-8.4.2, pluggy-1.6.0
metadata:
    Python: 3.11.4
    Platform: Linux-5.15.0
    build_id: 12345
...
```

### In JUnit XML

Inspect the generated XML file:

```bash
jux-inspect report.xml
```

Or view the raw XML:

```bash
grep -A5 "<properties>" report.xml
```

## Best Practices

1. **Consistent Keys**: Use snake_case for metadata keys (e.g., `build_id`, not `buildId`)
2. **Avoid Secrets**: Never include sensitive data (passwords, tokens) in metadata
3. **Structured Data**: Use JSON for complex hierarchical metadata
4. **CI Integration**: Capture CI/CD environment variables automatically
5. **Test Isolation**: Add metadata at module or session level, not per-test

## Troubleshooting

### Metadata Not Appearing in XML

Ensure you're using the `include_metadata_in_junit_xml` fixture:

```python
pytestmark = pytest.mark.usefixtures('include_metadata_in_junit_xml')
```

### Metadata Missing After Signing

pytest-jux preserves the entire XML structure including property tags. If metadata is missing:

1. Verify it exists in the unsigned XML first
2. Check that `jux-sign` is writing to the correct output file
3. Ensure XML structure is valid

### JSON Parsing Errors

When using `--metadata-from-json`, ensure JSON is valid:

```bash
# Test JSON validity
echo '{"key": "value"}' | python -m json.tool
```

## Related Documentation

- [pytest-metadata Documentation](https://github.com/pytest-dev/pytest-metadata)
- [JUnit XML Schema](https://github.com/windyroad/JUnit-Schema)
- [pytest-jux Storage Guide](../reference/storage.md)
- [Signing Reports Guide](signing-reports.md)

## Example Workflow

Complete CI/CD workflow with metadata:

```bash
#!/bin/bash
# ci-test.sh

# Run tests with metadata
pytest tests/ \
  --junit-xml=junit-report.xml \
  --jux-sign \
  --jux-key /secrets/signing_key.pem \
  --jux-publish \
  --metadata ci_provider "GitLab CI" \
  --metadata pipeline_id "$CI_PIPELINE_ID" \
  --metadata job_id "$CI_JOB_ID" \
  --metadata commit_sha "$CI_COMMIT_SHA" \
  --metadata branch "$CI_COMMIT_REF_NAME" \
  --metadata environment "$DEPLOY_ENV"

# Verify signature
jux-verify --input junit-report.xml --cert /certs/signing_key.crt

# Inspect report with metadata
jux-inspect junit-report.xml
```

This creates a signed, metadata-rich test report that can be traced back to the exact CI/CD build and deployment environment.
