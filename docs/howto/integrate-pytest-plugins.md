# How to Integrate with Other pytest Plugins

**Use pytest-jux alongside popular pytest plugins**

---

## Overview

pytest-jux is designed to work seamlessly with other pytest plugins. This guide covers:
- Common plugin compatibility issues
- Configuration patterns for popular plugins
- Best practices for multi-plugin setups
- Troubleshooting plugin conflicts

---

## Compatible Plugins

pytest-jux has been tested with these popular pytest plugins:

| Plugin | Status | Notes |
|--------|--------|-------|
| **pytest-cov** | ✅ Fully compatible | Coverage reports work alongside signing |
| **pytest-xdist** | ✅ Compatible | Use `storage_mode=disabled` for parallel runs |
| **pytest-html** | ✅ Compatible | Separate HTML and XML outputs |
| **pytest-metadata** | ⚠️ Compatible | May duplicate metadata collection |
| **pytest-timeout** | ✅ Compatible | Timeout handling works correctly |
| **pytest-mock** | ✅ Compatible | No conflicts |
| **pytest-asyncio** | ✅ Compatible | Async tests sign normally |
| **pytest-django** | ✅ Compatible | Database fixtures work correctly |
| **pytest-flask** | ✅ Compatible | Flask fixtures work correctly |
| **pytest-bdd** | ✅ Compatible | BDD scenarios sign normally |

---

## pytest-cov (Coverage Reporting)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Run tests with coverage and signing
pytest \
  --cov=mypackage \
  --cov-report=html \
  --cov-report=term \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem \
  --jux-cert ~/.ssh/jux/dev-cert.pem

# Result:
# - Coverage report: htmlcov/index.html
# - Signed JUnit XML: ~/.local/share/pytest-jux/reports/<hash>.xml
```

### Configuration

**pytest.ini**:
```ini
[pytest]
addopts =
    --cov=mypackage
    --cov-report=html
    --cov-report=term-missing
    --junitxml=test-results/junit.xml
    --jux-key=~/.ssh/jux/dev-key.pem
    --jux-cert=~/.ssh/jux/dev-cert.pem
```

**pyproject.toml**:
```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=mypackage",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--junitxml=test-results/junit.xml",
    "--jux-key=~/.ssh/jux/dev-key.pem",
    "--jux-cert=~/.ssh/jux/dev-cert.pem",
]
```

### Coverage in Signed Reports

Coverage data is **not** included in JUnit XML by default. To include coverage in metadata:

```python
# conftest.py
import pytest

def pytest_configure(config):
    """Add coverage data to pytest-jux metadata."""
    config.pluginmanager.register(CoverageMetadataPlugin())

class CoverageMetadataPlugin:
    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session):
        """Capture coverage after tests complete."""
        if hasattr(session.config, '_cov'):
            cov = session.config._cov.cov
            # Coverage data available here
            # (Requires custom metadata collection - see advanced tutorial)
```

---

## pytest-xdist (Parallel Testing)

**Compatibility**: ✅ Compatible with configuration

### Issue: Storage Conflicts

pytest-xdist runs tests in parallel workers. Each worker tries to write to storage simultaneously, causing conflicts.

**Solution**: Disable storage during parallel runs

```bash
# Option 1: Disable storage with environment variable
export JUX_STORAGE_MODE=disabled
pytest -n auto --junitxml=junit.xml --jux-key key.pem

# Option 2: Disable storage with CLI flag
pytest -n auto --junitxml=junit.xml --jux-storage-mode disabled --jux-key key.pem
```

### Configuration

**pytest.ini**:
```ini
[pytest]
addopts =
    -n auto
    --junitxml=test-results/junit.xml
    --jux-storage-mode=disabled  ; Disable storage for xdist
    --jux-key=~/.ssh/jux/dev-key.pem
```

### Workaround: Per-Worker Storage

```python
# conftest.py
import pytest
import os

def pytest_configure(config):
    """Configure per-worker storage for xdist."""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')

    if worker_id != 'master':
        # Each worker uses separate storage directory
        storage_path = f"/tmp/pytest-jux-{worker_id}"
        os.environ['JUX_STORAGE_BASE_PATH'] = storage_path
        os.makedirs(storage_path, exist_ok=True)
```

**Consolidate after tests**:
```bash
# Merge worker storage into main storage
for worker_dir in /tmp/pytest-jux-*; do
  cp -r "${worker_dir}"/reports/* ~/.local/share/pytest-jux/reports/
  cp -r "${worker_dir}"/metadata/* ~/.local/share/pytest-jux/metadata/
done

# Clean up worker storage
rm -rf /tmp/pytest-jux-*
```

---

## pytest-html (HTML Reports)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Generate both HTML and signed XML reports
pytest \
  --html=report.html \
  --self-contained-html \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

### Configuration

**pytest.ini**:
```ini
[pytest]
addopts =
    --html=test-results/report.html
    --self-contained-html
    --junitxml=test-results/junit.xml
    --jux-key=~/.ssh/jux/dev-key.pem
```

**Note**: HTML reports and JUnit XML reports are independent. pytest-jux only signs JUnit XML.

---

## pytest-metadata (Metadata Collection)

**Compatibility**: ⚠️ Compatible (may duplicate metadata)

### Issue: Duplicate Metadata

Both pytest-metadata and pytest-jux collect environment metadata. This may result in:
- Duplicate metadata in JUnit XML
- Slightly different metadata formats

**Solution 1: Disable pytest-jux metadata**

```bash
# Use pytest-metadata only
pytest \
  --junitxml=junit.xml \
  --jux-metadata disabled \
  --jux-key ~/.ssh/jux/dev-key.pem
```

**Solution 2: Use pytest-metadata, extend with jux metadata**

```python
# conftest.py
import pytest
from pytest_jux.metadata import EnvironmentMetadata

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Add jux metadata to pytest-metadata."""
    if hasattr(config, '_metadata'):
        jux_metadata = EnvironmentMetadata.collect()
        config._metadata['jux'] = jux_metadata.to_dict()
```

### Best Practice

For most users: **Use pytest-jux metadata only** (simpler, no duplication)

---

## pytest-timeout (Timeout Handling)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Timeout + signing works correctly
pytest \
  --timeout=30 \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

**Configuration**:
```ini
[pytest]
timeout = 30
addopts = --junitxml=test-results/junit.xml --jux-key=~/.ssh/jux/dev-key.pem
```

**Note**: Timeout errors are correctly recorded in JUnit XML and signed.

---

## pytest-django (Django Testing)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Django tests with signing
pytest \
  --ds=myproject.settings \
  --reuse-db \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

### Configuration

**pytest.ini**:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = myproject.settings
addopts =
    --reuse-db
    --junitxml=test-results/junit.xml
    --jux-key=~/.ssh/jux/dev-key.pem
```

**Database Fixtures**:
```python
# conftest.py
import pytest

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up database for tests."""
    with django_db_blocker.unblock():
        # Database setup
        pass

# pytest-jux works correctly with Django database fixtures
```

---

## pytest-flask (Flask Testing)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Flask tests with signing
pytest \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

### Flask Client Fixture

```python
# conftest.py
import pytest
from myapp import create_app

@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app({'TESTING': True})
    yield app

@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()

# tests/test_app.py
def test_homepage(client):
    """Test homepage returns 200."""
    response = client.get('/')
    assert response.status_code == 200

# pytest-jux signs these test results correctly
```

---

## pytest-asyncio (Async Testing)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# Async tests with signing
pytest \
  --asyncio-mode=auto \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

### Async Test Example

```python
# tests/test_async.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    await asyncio.sleep(0.1)
    assert True

@pytest.mark.asyncio
async def test_async_http_client(httpx_client):
    """Test async HTTP client."""
    response = await httpx_client.get('https://example.com')
    assert response.status_code == 200

# pytest-jux signs async test results correctly
```

---

## pytest-bdd (Behavior-Driven Development)

**Compatibility**: ✅ Fully compatible

### Basic Usage

```bash
# BDD tests with signing
pytest \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/dev-key.pem
```

### BDD Scenario Example

```gherkin
# features/example.feature
Feature: User login
  Scenario: Successful login
    Given a user exists
    When the user logs in
    Then the user is authenticated
```

```python
# tests/test_login_steps.py
from pytest_bdd import scenarios, given, when, then

scenarios('../features/example.feature')

@given('a user exists')
def user_exists():
    return {'username': 'test', 'password': 'test123'}

@when('the user logs in')
def user_logs_in(user_exists):
    # Login logic
    return True

@then('the user is authenticated')
def user_authenticated(user_logs_in):
    assert user_logs_in is True

# pytest-jux signs BDD test results
```

---

## Multi-Plugin Configuration

### Example: Complete Testing Stack

**pytest.ini**:
```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage
addopts =
    --cov=mypackage
    --cov-report=html
    --cov-report=term-missing
    --cov-branch

    # Parallel execution
    -n auto
    --dist=loadscope

    # Timeout
    --timeout=30
    --timeout-method=thread

    # Output
    --junitxml=test-results/junit.xml
    --html=test-results/report.html
    --self-contained-html

    # pytest-jux (signing)
    --jux-storage-mode=disabled  ; Required for xdist
    --jux-key=~/.ssh/jux/dev-key.pem
    --jux-cert=~/.ssh/jux/dev-cert.pem

# Django (if applicable)
DJANGO_SETTINGS_MODULE = myproject.settings

# Asyncio (if applicable)
asyncio_mode = auto

[tool:pytest]
# Timeout
timeout = 30

# Coverage
[coverage:run]
source = mypackage
omit =
    */tests/*
    */migrations/*
```

### Example: Makefile Targets

```makefile
# Makefile

.PHONY: test test-cov test-parallel test-signed test-all

# Basic tests
test:
	pytest -v

# Tests with coverage
test-cov:
	pytest --cov=mypackage --cov-report=html --cov-report=term

# Parallel tests
test-parallel:
	pytest -n auto --dist=loadscope

# Signed tests (development)
test-signed:
	pytest --junitxml=junit.xml \
	  --jux-key ~/.ssh/jux/dev-key.pem \
	  --jux-cert ~/.ssh/jux/dev-cert.pem

# All: coverage + parallel + signed
test-all:
	pytest \
	  --cov=mypackage \
	  --cov-report=html \
	  --cov-report=term-missing \
	  -n auto \
	  --dist=loadscope \
	  --junitxml=junit.xml \
	  --jux-storage-mode=disabled \
	  --jux-key ~/.ssh/jux/dev-key.pem
```

---

## Troubleshooting Plugin Conflicts

### Issue: Plugins modify JUnit XML

**Problem**: Some plugins modify JUnit XML structure, breaking signatures

**Diagnosis**:
```bash
# Run without pytest-jux to see original XML
pytest --junitxml=baseline.xml

# Run with pytest-jux
pytest --junitxml=signed.xml --jux-key key.pem

# Compare structure (before signature)
diff <(xmllint --format baseline.xml) \
     <(xmllint --format signed.xml | sed '/<Signature/,/<\/Signature>/d')
```

**Solution**: Ensure pytest-jux runs **last** in hook order:

```python
# conftest.py
import pytest

def pytest_configure(config):
    """Ensure pytest-jux runs last."""
    config.pluginmanager.unregister(name='jux')
    from pytest_jux import plugin
    config.pluginmanager.register(plugin, name='jux')
```

### Issue: Metadata conflicts

**Problem**: Multiple plugins collect overlapping metadata

**Solution**: Disable duplicate metadata collection:

```bash
# Disable pytest-jux metadata if using pytest-metadata
pytest --junitxml=junit.xml --jux-metadata disabled --jux-key key.pem
```

### Issue: Storage conflicts with parallel execution

**Problem**: pytest-xdist workers conflict writing to storage

**Solution**: Disable storage for parallel runs:

```bash
pytest -n auto --junitxml=junit.xml --jux-storage-mode disabled --jux-key key.pem
```

---

## Best Practices

### Plugin Load Order

1. **✅ pytest-jux loads last**: Ensures XML is finalized before signing
2. **✅ Explicit plugin ordering**: Use `pytest_plugins` in conftest.py
3. **✅ Test compatibility**: Run tests with/without pytest-jux to verify

### Configuration Management

1. **✅ Centralize config**: Use pytest.ini or pyproject.toml
2. **✅ Environment-specific**: Different configs for dev/CI
3. **✅ Document plugin interactions**: Note in README or docs
4. **✅ Version pin plugins**: Prevent unexpected compatibility issues

### Testing

1. **✅ Test with plugins enabled**: Verify pytest-jux works in real setup
2. **✅ Monitor plugin updates**: Check compatibility after updates
3. **✅ CI/CD validation**: Run full plugin stack in CI

---

## See Also

- **[Troubleshooting Guide](troubleshooting.md)**: Plugin conflict debugging
- **[CI/CD Deployment](ci-cd-deployment.md)**: Plugin configuration in CI/CD
- **[Custom Signing Workflows](../tutorials/custom-signing-workflows.md)**: Advanced integration patterns
- **[Configuration Reference](../reference/configuration.md)**: Configuration options

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
