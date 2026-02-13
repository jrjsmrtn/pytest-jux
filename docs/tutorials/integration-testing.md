# Tutorial: Integration Testing with Signed Reports

**Integrate pytest-jux into real projects and CI/CD pipelines**

---

## What You'll Learn

By the end of this tutorial, you will:

✅ Integrate pytest-jux into an existing Python project
✅ Configure multi-environment signing (dev, staging, production)
✅ Set up GitHub Actions CI/CD with automated signing
✅ Manage signing keys securely in CI/CD
✅ Implement report storage and caching strategies
✅ Debug signing issues in complex projects

**Time Required**: 30-45 minutes

**Difficulty**: Intermediate

**Prerequisites**:
- Completed [First Signed Report tutorial](first-signed-report.md)
- Familiarity with pytest test suites
- Basic CI/CD knowledge (GitHub Actions or GitLab CI)
- Understanding of environment variables

---

## Tutorial Overview

This tutorial simulates integrating pytest-jux into a real-world Python project with:
- Multiple test files and fixtures
- Development, staging, and production environments
- GitHub Actions CI/CD pipeline
- Secure key management
- Report storage and archival

**Scenario**: Your team maintains a Python library and wants to publish signed test reports to verify code quality for downstream users.

---

## Part 1: Project Setup

### Clone Sample Project

For this tutorial, we'll create a realistic project structure.

```bash
# Create project directory
mkdir -p pytest-jux-integration-demo
cd pytest-jux-integration-demo

# Initialize git repository
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Create Project Structure

```bash
# Create project structure
mkdir -p src/mylib tests/unit tests/integration .github/workflows

# Create package files
cat > src/mylib/__init__.py << 'EOF'
"""My Library - A sample Python library."""
__version__ = "1.0.0"

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
EOF

# Create unit tests
cat > tests/unit/test_math.py << 'EOF'
"""Unit tests for math operations."""
import pytest
from mylib import add, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(6, 2) == 3.0
    assert divide(1, 2) == 0.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)
EOF

# Create integration tests
cat > tests/integration/test_workflows.py << 'EOF'
"""Integration tests for common workflows."""
from mylib import add, multiply, divide

def test_complex_calculation():
    """Test a complex calculation workflow."""
    result = add(multiply(2, 3), divide(10, 2))
    assert result == 11.0

def test_chain_operations():
    """Test chaining multiple operations."""
    a = add(1, 2)
    b = multiply(a, 3)
    c = divide(b, 2)
    assert c == 4.5
EOF

# Create pytest configuration
cat > pytest.ini << 'EOF'
[pytest]
minversion = 7.4
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --junitxml=test-results/junit.xml

# pytest-jux configuration (will be environment-specific)
jux_environment = development
jux_storage_mode = auto
EOF
```

### Create pyproject.toml

```bash
cat > pyproject.toml << 'EOF'
[project]
name = "mylib"
version = "1.0.0"
description = "A sample Python library for pytest-jux integration tutorial"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-jux>=0.1.9",
    "pytest-cov>=4.1",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
EOF
```

### Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

**✓ Checkpoint**: Project structure created, dependencies installed

---

## Part 2: Multi-Environment Configuration

### Create Environment-Specific Configuration

```bash
# Create configuration directory
mkdir -p config

# Development configuration
cat > config/development.toml << 'EOF'
[jux]
environment = "development"
storage_mode = "disabled"  # Don't cache in dev

[jux.signing]
# Use ephemeral keys in development
private_key_path = "~/.ssh/jux/dev-key.pem"
certificate_path = "~/.ssh/jux/dev-cert.pem"
EOF

# Staging configuration
cat > config/staging.toml << 'EOF'
[jux]
environment = "staging"
storage_mode = "auto"

[jux.signing]
private_key_path = "~/.ssh/jux/staging-key.pem"
certificate_path = "~/.ssh/jux/staging-cert.pem"
EOF

# Production configuration
cat > config/production.toml << 'EOF'
[jux]
environment = "production"
storage_mode = "auto"

[jux.signing]
private_key_path = "~/.ssh/jux/prod-key.pem"
certificate_path = "~/.ssh/jux/prod-cert.pem"
EOF
```

### Generate Environment-Specific Keys

```bash
# Create keys directory
mkdir -p ~/.ssh/jux

# Generate development key
jux-keygen \
  --type rsa \
  --bits 2048 \
  --output ~/.ssh/jux/dev-key.pem \
  --cert \
  --subject "CN=MyLib Development" \
  --days-valid 90

# Generate staging key
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output ~/.ssh/jux/staging-key.pem \
  --cert \
  --subject "CN=MyLib Staging" \
  --days-valid 180

# Generate production key
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output ~/.ssh/jux/prod-key.pem \
  --cert \
  --subject "CN=MyLib Production" \
  --days-valid 365
```

**✓ Checkpoint**: Multi-environment configuration created

---

## Part 3: Local Testing with Different Environments

### Test Development Environment

```bash
# Run tests with development config
pytest \
  --jux-config config/development.toml \
  --jux-key ~/.ssh/jux/dev-key.pem \
  --jux-cert ~/.ssh/jux/dev-cert.pem
```

**Expected Output**:
```
======================== test session starts =========================
collected 6 items

tests/integration/test_workflows.py ..                          [ 33%]
tests/unit/test_math.py ....                                    [100%]

======================== 6 passed in 0.15s ==========================

pytest-jux: Report signed and stored
  Environment: development
  Storage mode: disabled (not cached)
  Signed report: test-results/junit.xml
```

### Test Staging Environment

```bash
# Run tests with staging config
pytest \
  --jux-config config/staging.toml \
  --jux-key ~/.ssh/jux/staging-key.pem \
  --jux-cert ~/.ssh/jux/staging-cert.pem
```

**Expected Output**:
```
======================== 6 passed in 0.15s ==========================

pytest-jux: Report signed and stored
  Environment: staging
  Hash: b2c3d4e5f6g7h8i9...
  Signed report: ~/.local/share/pytest-jux/reports/b2c3d4...xml
```

**Notice**: Staging reports are cached (`storage_mode = "auto"`), development reports are not.

**✓ Checkpoint**: Multi-environment testing works correctly

---

## Part 4: GitHub Actions CI/CD Integration

### Create GitHub Actions Workflow

```bash
# Create workflow file
cat > .github/workflows/test.yml << 'EOF'
name: Test with Signed Reports

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Generate ephemeral signing key
        run: |
          mkdir -p ~/.ssh/jux
          jux-keygen \
            --type rsa \
            --bits 4096 \
            --output ~/.ssh/jux/ci-key.pem \
            --cert \
            --subject "CN=GitHub Actions CI" \
            --days-valid 1

      - name: Run tests with signing
        env:
          JUX_ENVIRONMENT: ci
          JUX_KEY_PATH: ~/.ssh/jux/ci-key.pem
          JUX_CERT_PATH: ~/.ssh/jux/ci-key.crt
          JUX_STORAGE_MODE: disabled
        run: |
          pytest \
            --junitxml=test-results/junit.xml \
            --cov=src/mylib \
            --cov-report=xml \
            --cov-report=term

      - name: Verify signed report
        run: |
          jux-verify \
            -i test-results/junit.xml \
            --cert ~/.ssh/jux/ci-key.crt

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-py${{ matrix.python-version }}
          path: |
            test-results/
            coverage.xml

      - name: Upload signed reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: signed-reports-py${{ matrix.python-version }}
          path: test-results/junit.xml
EOF
```

### Commit and Push

```bash
# Add files to git
git add .
git commit -m "feat: Add pytest-jux integration with CI/CD"

# Create GitHub repository (if not exists)
# Then push:
# git remote add origin https://github.com/yourusername/pytest-jux-integration-demo.git
# git push -u origin main
```

**✓ Checkpoint**: GitHub Actions workflow configured

---

## Part 5: Secure Key Management in CI/CD

### Option 1: Ephemeral Keys (Recommended for Public Projects)

**Pros**: No secrets to manage, keys rotate automatically
**Cons**: Can't verify reports after CI run completes

```yaml
# Already implemented in workflow above
- name: Generate ephemeral signing key
  run: |
    jux-keygen \
      --type rsa \
      --bits 4096 \
      --output ~/.ssh/jux/ci-key.pem \
      --cert
```

### Option 2: GitHub Secrets (Recommended for Private Projects)

**Pros**: Persistent keys, reports verifiable long-term
**Cons**: Requires secret management

**Setup**:

1. Generate production key locally:
```bash
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output prod-ci-key.pem \
  --cert \
  --subject "CN=MyLib CI Production"
```

2. Add to GitHub Secrets:
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Add secrets:
     - `JUX_PRIVATE_KEY`: Content of `prod-ci-key.pem`
     - `JUX_CERTIFICATE`: Content of `prod-ci-key.crt`

3. Update workflow:
```yaml
- name: Configure signing keys from secrets
  run: |
    mkdir -p ~/.ssh/jux
    echo "${{ secrets.JUX_PRIVATE_KEY }}" > ~/.ssh/jux/ci-key.pem
    echo "${{ secrets.JUX_CERTIFICATE }}" > ~/.ssh/jux/ci-key.crt
    chmod 600 ~/.ssh/jux/ci-key.pem
    chmod 644 ~/.ssh/jux/ci-key.crt
```

**✓ Checkpoint**: Secure key management configured

---

## Part 6: Report Storage and Archival

### Configure Local Storage

```bash
# View cache statistics
jux-cache stats
```

**Expected Output**:
```
Cache Statistics:
  Total reports:      3
  Total size:         42.5 KB
  Oldest report:      2025-10-20T10:00:00Z
  Newest report:      2025-10-20T14:30:00Z
  Storage location:   ~/.local/share/pytest-jux/
```

### List Cached Reports

```bash
# List all cached reports
jux-cache list
```

**Expected Output**:
```
Cached Reports (3 total):

  b2c3d4e5f6g7h8i9...
    Timestamp: 2025-10-20T14:30:00Z
    Hostname:  your-machine.local
    Username:  you

  c3d4e5f6g7h8i9j0...
    Timestamp: 2025-10-20T12:15:00Z
    Hostname:  your-machine.local
    Username:  you
```

### Clean Up Old Reports

```bash
# Remove reports older than 30 days
jux-cache clean --days 30
```

**Expected Output**:
```
Cleaned up 0 reports older than 30 days
```

### Archive Reports (CI/CD)

In GitHub Actions, reports are automatically archived as artifacts. Download them:

1. Go to: Actions → Your workflow run
2. Scroll to "Artifacts" section
3. Download "signed-reports-py3.11"

**✓ Checkpoint**: Report storage and archival configured

---

## Part 7: Debugging Integration Issues

### Common Issue 1: "Private key not found" in CI

**Symptom**:
```
Error: Private key not found: ~/.ssh/jux/ci-key.pem
```

**Cause**: Tilde expansion doesn't work in environment variables

**Solution**: Use absolute path or `$HOME`:
```yaml
env:
  JUX_KEY_PATH: $HOME/.ssh/jux/ci-key.pem
```

### Common Issue 2: Test reports not signed

**Symptom**: Tests pass but no signing message appears

**Cause**: Missing `--junitxml` option

**Solution**: Ensure pytest.ini has:
```ini
[pytest]
addopts = --junitxml=test-results/junit.xml
```

### Common Issue 3: Signature verification fails

**Symptom**:
```
Error: Signature verification failed
```

**Debug Steps**:

1. **Check certificate matches key**:
```bash
# Extract public key from private key
openssl rsa -in key.pem -pubout -out key-pub.pem

# Extract public key from certificate
openssl x509 -in cert.pem -pubkey -noout -out cert-pub.pem

# Compare (should be identical)
diff key-pub.pem cert-pub.pem
```

2. **Verify XML wasn't modified**:
```bash
# Inspect canonical hash
jux-inspect -i junit.xml

# Sign again and compare hashes
jux-sign -i original.xml -o signed2.xml --key key.pem
jux-inspect -i signed2.xml
```

3. **Check file permissions**:
```bash
ls -la ~/.ssh/jux/
# Private key should be 600, certificate should be 644
```

**✓ Checkpoint**: Debugging strategies understood

---

## Part 8: Advanced Configuration

### Create Makefile for Common Tasks

```bash
cat > Makefile << 'EOF'
.PHONY: test test-dev test-staging test-prod verify-staging verify-prod clean

# Development testing (no caching)
test-dev:
	pytest \
		--jux-config config/development.toml \
		--jux-key ~/.ssh/jux/dev-key.pem \
		--jux-cert ~/.ssh/jux/dev-cert.pem

# Staging testing (with caching)
test-staging:
	pytest \
		--jux-config config/staging.toml \
		--jux-key ~/.ssh/jux/staging-key.pem \
		--jux-cert ~/.ssh/jux/staging-cert.pem

# Production testing (with caching)
test-prod:
	pytest \
		--jux-config config/production.toml \
		--jux-key ~/.ssh/jux/prod-key.pem \
		--jux-cert ~/.ssh/jux/prod-cert.pem

# Verify staging report
verify-staging:
	jux-verify \
		-i test-results/junit.xml \
		--cert ~/.ssh/jux/staging-cert.pem

# Verify production report
verify-prod:
	jux-verify \
		-i test-results/junit.xml \
		--cert ~/.ssh/jux/prod-cert.pem

# Clean up
clean:
	rm -rf test-results/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	jux-cache purge
EOF
```

**Usage**:
```bash
# Run staging tests
make test-staging

# Verify staging report
make verify-staging

# Clean up
make clean
```

### Create Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'

# pytest-jux aliases
alias pytest-dev='pytest --jux-config config/development.toml'
alias pytest-staging='pytest --jux-config config/staging.toml'
alias pytest-prod='pytest --jux-config config/production.toml'
alias jux-verify-staging='jux-verify --cert ~/.ssh/jux/staging-cert.pem'
alias jux-verify-prod='jux-verify --cert ~/.ssh/jux/prod-cert.pem'
EOF

# Reload shell
source ~/.bashrc
```

**✓ Checkpoint**: Advanced configuration completed

---

## Part 9: Integration Testing Best Practices

### 1. Environment Isolation

**Best Practice**: Use different keys for each environment

```bash
# Development: Short-lived, low security
jux-keygen --type rsa --bits 2048 --days-valid 90

# Staging: Medium security
jux-keygen --type rsa --bits 4096 --days-valid 180

# Production: High security
jux-keygen --type rsa --bits 4096 --days-valid 365
```

### 2. Storage Strategy

| Environment | Storage Mode | Rationale |
|-------------|--------------|-----------|
| Development | `disabled` | Frequent test runs, reports ephemeral |
| Staging | `auto` | Cache for debugging, test report consistency |
| Production | `auto` | Archive for compliance, auditing |
| CI/CD | `disabled` | Reports uploaded as artifacts |

### 3. Key Rotation

```bash
# Rotate keys quarterly
# 1. Generate new keys
jux-keygen --output new-prod-key.pem --cert

# 2. Update configuration
# Edit config/production.toml with new key paths

# 3. Update CI/CD secrets
# Update GitHub Secrets with new key

# 4. Archive old key (for verifying historical reports)
mv ~/.ssh/jux/prod-key.pem ~/.ssh/jux/prod-key-2025Q3.pem.archived
```

### 4. Report Verification Pipeline

```yaml
# Add verification step to CI/CD
- name: Verify all signed reports
  run: |
    for report in test-results/*.xml; do
      echo "Verifying $report"
      jux-verify -i "$report" --cert ~/.ssh/jux/ci-key.crt
    done
```

**✓ Checkpoint**: Best practices understood

---

## Summary: What You Accomplished

**✅ Completed**:
1. Integrated pytest-jux into a realistic Python project
2. Configured multi-environment signing (dev, staging, production)
3. Set up GitHub Actions CI/CD with automated signing
4. Implemented secure key management strategies
5. Configured report storage and archival
6. Learned debugging techniques for integration issues
7. Created advanced configuration with Makefile and aliases
8. Applied integration testing best practices

**🎓 Skills Learned**:
- Multi-environment configuration
- CI/CD integration (GitHub Actions)
- Secure key management (ephemeral vs persistent)
- Report storage strategies
- Debugging integration issues
- Advanced pytest-jux configuration

---

## Next Steps

### Intermediate → Advanced

Now that you've mastered integration, try:

1. **[Custom Signing Workflows](custom-signing-workflows.md)**: Implement custom signing logic
2. **[Multi-Environment Configuration Guide](../howto/multi-environment-config.md)**: Deep dive into configuration
3. **[CI/CD Deployment Guide](../howto/ci-cd-deployment.md)**: More CI/CD examples (GitLab CI, Jenkins)

### Production Deployment

- **[Security Best Practices](../explanation/security.md)**: Production security guidelines
- **[Key Management Guide](../howto/key-management.md)**: Enterprise key management
- **[Monitoring Guide](../howto/monitoring.md)**: Monitor signing operations

---

## Troubleshooting

### GitHub Actions: "jux-keygen: command not found"

**Problem**: pytest-jux not installed in CI

**Solution**: Ensure installation step:
```yaml
- name: Install dependencies
  run: pip install -e ".[dev]"
```

### GitHub Actions: Key file permissions error

**Problem**: Private key has wrong permissions (too open)

**Solution**: Fix permissions after creating key:
```yaml
- name: Generate ephemeral signing key
  run: |
    jux-keygen --output ~/.ssh/jux/ci-key.pem --cert
    chmod 600 ~/.ssh/jux/ci-key.pem
```

### Local: Configuration file not found

**Problem**: Config file path incorrect

**Solution**: Use absolute path or check working directory:
```bash
# Absolute path
pytest --jux-config "$(pwd)/config/development.toml"

# Or set environment variable
export JUX_CONFIG_FILE="$(pwd)/config/development.toml"
pytest
```

---

## Clean Up (Optional)

```bash
# Remove project directory
cd ..
rm -rf pytest-jux-integration-demo

# Remove ephemeral keys (keep prod keys if needed)
rm ~/.ssh/jux/dev-key.pem ~/.ssh/jux/dev-cert.pem

# Clear cache
jux-cache purge
```

---

## Feedback

Was this tutorial helpful? Have suggestions?

- **Report Issues**: https://github.com/jux-tools/pytest-jux/issues
- **Contribute**: PRs welcome!

---

**Tutorial Version**: 1.0
**pytest-jux Version**: 0.1.9
**Last Updated**: 2025-10-20
