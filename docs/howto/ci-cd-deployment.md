# CI/CD Deployment Guide

_Integrate pytest-jux into your CI/CD pipeline_

**Audience:** System Administrators, DevOps Engineers
**Prerequisites:**
- Completed [Quick Start Guide](../tutorials/quick-start.md)
- Understanding of [Storage Modes](choosing-storage-modes.md)
- Production [Signing Keys](../tutorials/setting-up-signing-keys.md) ready

## Overview

This guide shows how to deploy pytest-jux across different CI/CD platforms:

- GitHub Actions
- GitLab CI/CD
- Jenkins
- Azure Pipelines
- CircleCI
- Generic Docker-based CI

## General Principles

Regardless of CI/CD platform, follow these principles:

### 1. Use Environment Variables for Secrets

```bash
# Good: Secrets in environment
export JUX_KEY_PATH=/tmp/signing_key.pem
export JUX_API_KEY=secret-value

# Bad: Secrets in configuration files
[jux]
api_key = hardcoded-secret  # ❌ Don't do this!
```

### 2. Use CACHE Storage Mode

```bash
# CI/CD should use CACHE mode for resilience
export JUX_STORAGE_MODE=cache
```

**Why CACHE?**
- Network failures won't break builds
- Reports published when API available
- Local storage for debugging

### 3. Clean Up Temporary Keys

```bash
# After test run
trap "rm -f /tmp/signing_key.pem" EXIT
```

### 4. Monitor Queue Size

```bash
# Alert if queue grows too large
jux-cache stats --json | jq '.queued_reports'
```

## GitHub Actions

### Basic Setup

`.github/workflows/test.yml`:

```yaml
name: Test with pytest-jux

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip uv
          uv pip install -e ".[dev]"
          uv pip install pytest-jux

      - name: Set up signing key
        env:
          JUX_SIGNING_KEY: ${{ secrets.JUX_SIGNING_KEY }}
        run: |
          mkdir -p ~/.jux
          echo "$JUX_SIGNING_KEY" > ~/.jux/signing_key.pem
          chmod 600 ~/.jux/signing_key.pem

      - name: Run tests with signing
        env:
          JUX_ENABLED: true
          JUX_SIGN: true
          JUX_KEY_PATH: ~/.jux/signing_key.pem
          JUX_STORAGE_MODE: cache
          JUX_API_URL: ${{ secrets.JUX_API_URL }}
          JUX_API_KEY: ${{ secrets.JUX_API_KEY }}
        run: |
          pytest --junit-xml=report.xml

      - name: Clean up
        if: always()
        run: |
          rm -f ~/.jux/signing_key.pem

      - name: Upload test report (if API publishing failed)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: report.xml
```

### Secrets Configuration

**Add secrets in GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `JUX_SIGNING_KEY` - Private key content (entire PEM file)
   - `JUX_API_URL` - API endpoint URL
   - `JUX_API_KEY` - API authentication key

### Multiple Environments

```yaml
name: Test Multiple Environments

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, production]

    environment: ${{ matrix.environment }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install pytest-jux
        run: |
          pip install pytest-jux

      - name: Set up signing key
        env:
          JUX_SIGNING_KEY: ${{ secrets.JUX_SIGNING_KEY }}
        run: |
          echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
          chmod 600 /tmp/signing_key.pem

      - name: Run tests
        env:
          JUX_ENABLED: true
          JUX_SIGN: true
          JUX_KEY_PATH: /tmp/signing_key.pem
          JUX_STORAGE_MODE: cache
          JUX_API_URL: ${{ vars.JUX_API_URL }}  # Environment variable
          JUX_API_KEY: ${{ secrets.JUX_API_KEY }}  # Environment secret
        run: |
          pytest --junit-xml=report.xml

      - name: Clean up
        if: always()
        run: rm -f /tmp/signing_key.pem
```

## GitLab CI/CD

### Basic Setup

`.gitlab-ci.yml`:

```yaml
stages:
  - test

test:
  image: python:3.11
  stage: test

  before_script:
    - pip install pytest-jux
    - echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
    - chmod 600 /tmp/signing_key.pem

  script:
    - pytest --junit-xml=report.xml

  after_script:
    - rm -f /tmp/signing_key.pem

  variables:
    JUX_ENABLED: "true"
    JUX_SIGN: "true"
    JUX_KEY_PATH: /tmp/signing_key.pem
    JUX_STORAGE_MODE: cache
    # JUX_API_URL and JUX_API_KEY set in CI/CD variables

  artifacts:
    when: always
    paths:
      - report.xml
    reports:
      junit: report.xml
```

### Secrets Configuration

**Add variables in GitLab:**
1. Go to Settings → CI/CD → Variables
2. Add variables:
   - `JUX_SIGNING_KEY` - Type: File, Protected, Masked
   - `JUX_API_URL` - Type: Variable
   - `JUX_API_KEY` - Type: Variable, Protected, Masked

### Multiple Environments

```yaml
.test_template:
  image: python:3.11
  before_script:
    - pip install pytest-jux
    - echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
    - chmod 600 /tmp/signing_key.pem
  script:
    - pytest --junit-xml=report.xml
  after_script:
    - rm -f /tmp/signing_key.pem
  variables:
    JUX_ENABLED: "true"
    JUX_SIGN: "true"
    JUX_KEY_PATH: /tmp/signing_key.pem
    JUX_STORAGE_MODE: cache

test:dev:
  extends: .test_template
  environment:
    name: development
  only:
    - develop

test:staging:
  extends: .test_template
  environment:
    name: staging
  only:
    - main

test:production:
  extends: .test_template
  environment:
    name: production
  only:
    - tags
  variables:
    JUX_STORAGE_MODE: api  # Production: require API
```

## Jenkins

### Declarative Pipeline

`Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        JUX_ENABLED = 'true'
        JUX_SIGN = 'true'
        JUX_STORAGE_MODE = 'cache'
        JUX_API_URL = credentials('jux-api-url')
        JUX_API_KEY = credentials('jux-api-key')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install pytest-jux'
            }
        }

        stage('Configure Signing') {
            steps {
                withCredentials([file(credentialsId: 'jux-signing-key', variable: 'KEY_FILE')]) {
                    sh '''
                        cp $KEY_FILE /tmp/signing_key.pem
                        chmod 600 /tmp/signing_key.pem
                    '''
                }
            }
        }

        stage('Test') {
            environment {
                JUX_KEY_PATH = '/tmp/signing_key.pem'
            }
            steps {
                sh 'pytest --junit-xml=report.xml'
            }
        }
    }

    post {
        always {
            junit 'report.xml'
            sh 'rm -f /tmp/signing_key.pem'
        }
    }
}
```

### Credentials Configuration

**Add credentials in Jenkins:**
1. Manage Jenkins → Credentials
2. Add credentials:
   - Type: Secret file → `jux-signing-key`
   - Type: Secret text → `jux-api-url`
   - Type: Secret text → `jux-api-key`

### Freestyle Job

For freestyle Jenkins jobs:

1. **Build Environment:**
   - ☑ Use secret text(s) or file(s)
     - Secret file: `jux-signing-key` → `KEY_FILE`
     - Secret text: `jux-api-url` → `JUX_API_URL`
     - Secret text: `jux-api-key` → `JUX_API_KEY`

2. **Build Steps (Execute shell):**
```bash
#!/bin/bash
set -e

# Install pytest-jux
pip install pytest-jux

# Set up signing key
cp $KEY_FILE /tmp/signing_key.pem
chmod 600 /tmp/signing_key.pem

# Run tests
export JUX_ENABLED=true
export JUX_SIGN=true
export JUX_KEY_PATH=/tmp/signing_key.pem
export JUX_STORAGE_MODE=cache
pytest --junit-xml=report.xml

# Clean up
rm -f /tmp/signing_key.pem
```

## Azure Pipelines

### Basic Setup

`azure-pipelines.yml`:

```yaml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  python.version: '3.11'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '$(python.version)'
    displayName: 'Use Python $(python.version)'

  - script: |
      python -m pip install --upgrade pip
      pip install pytest-jux
    displayName: 'Install dependencies'

  - task: DownloadSecureFile@1
    name: juxSigningKey
    inputs:
      secureFile: 'jux-signing-key.pem'

  - script: |
      cp $(juxSigningKey.secureFilePath) /tmp/signing_key.pem
      chmod 600 /tmp/signing_key.pem
    displayName: 'Set up signing key'

  - script: |
      pytest --junit-xml=TEST-results.xml
    env:
      JUX_ENABLED: true
      JUX_SIGN: true
      JUX_KEY_PATH: /tmp/signing_key.pem
      JUX_STORAGE_MODE: cache
      JUX_API_URL: $(JUX_API_URL)
      JUX_API_KEY: $(JUX_API_KEY)
    displayName: 'Run tests'

  - script: |
      rm -f /tmp/signing_key.pem
    condition: always()
    displayName: 'Clean up'

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFiles: '**/TEST-*.xml'
      testRunTitle: 'Python $(python.version)'
```

### Variables Configuration

**Add variables in Azure DevOps:**
1. Pipelines → Library → Variable groups
2. Create variable group `jux-config`:
   - `JUX_API_URL` - Value: https://jux.example.com/api/v1/reports
   - `JUX_API_KEY` - Value: (secret) Lock icon

3. Secure files:
   - Pipelines → Library → Secure files
   - Upload `jux-signing-key.pem`

## CircleCI

### Basic Setup

`.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.11

    steps:
      - checkout

      - run:
          name: Install dependencies
          command: |
            pip install pytest-jux

      - run:
          name: Set up signing key
          command: |
            echo "$JUX_SIGNING_KEY" | base64 -d > /tmp/signing_key.pem
            chmod 600 /tmp/signing_key.pem

      - run:
          name: Run tests
          command: |
            pytest --junit-xml=test-results/junit.xml
          environment:
            JUX_ENABLED: true
            JUX_SIGN: true
            JUX_KEY_PATH: /tmp/signing_key.pem
            JUX_STORAGE_MODE: cache

      - run:
          name: Clean up
          when: always
          command: |
            rm -f /tmp/signing_key.pem

      - store_test_results:
          path: test-results

workflows:
  test:
    jobs:
      - test
```

### Environment Variables Configuration

**Add environment variables in CircleCI:**
1. Project Settings → Environment Variables
2. Add variables:
   - `JUX_SIGNING_KEY` - Base64-encoded private key
   - `JUX_API_URL` - API endpoint
   - `JUX_API_KEY` - API key

**Encode signing key:**
```bash
base64 < signing_key.pem | tr -d '\n'
# Copy output to JUX_SIGNING_KEY
```

## Generic Docker-Based CI

### Dockerfile

`Dockerfile.ci`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install pytest-jux

# Copy source code
COPY . .

# Entry point script
COPY ci-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### Entry Point Script

`ci-entrypoint.sh`:

```bash
#!/bin/bash
set -e

# Validate required environment variables
: ${JUX_SIGNING_KEY:?JUX_SIGNING_KEY environment variable is required}
: ${JUX_API_URL:?JUX_API_URL environment variable is required}

# Set up signing key
echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
chmod 600 /tmp/signing_key.pem

# Set pytest-jux configuration
export JUX_ENABLED=true
export JUX_SIGN=true
export JUX_KEY_PATH=/tmp/signing_key.pem
export JUX_STORAGE_MODE=cache

# Run tests
pytest --junit-xml=report.xml "$@"

# Clean up
rm -f /tmp/signing_key.pem
```

### Usage

```bash
# Build image
docker build -f Dockerfile.ci -t myproject-test:latest .

# Run tests
docker run --rm \
  -e JUX_SIGNING_KEY="$(cat ~/.jux/signing_key.pem)" \
  -e JUX_API_URL="https://jux.example.com/api/v1/reports" \
  -e JUX_API_KEY="$JUX_API_KEY" \
  myproject-test:latest
```

## Monitoring and Alerting

### Queue Size Monitoring

**Script: `monitor-jux-queue.sh`**
```bash
#!/bin/bash
# Monitor pytest-jux queue size

QUEUE_SIZE=$(jux-cache stats --json | jq '.queued_reports')
THRESHOLD=100

if [ "$QUEUE_SIZE" -gt "$THRESHOLD" ]; then
  echo "ALERT: pytest-jux queue size ($QUEUE_SIZE) exceeds threshold ($THRESHOLD)"
  # Send alert (e.g., PagerDuty, Slack, email)
  exit 1
fi

echo "Queue size OK: $QUEUE_SIZE reports"
exit 0
```

**Add to CI/CD:**
```yaml
# GitHub Actions
- name: Monitor queue
  run: ./scripts/monitor-jux-queue.sh
```

### API Health Check

```bash
#!/bin/bash
# Check if Jux API is reachable

curl -f -s -o /dev/null "$JUX_API_URL/health" || {
  echo "WARNING: Jux API is unreachable"
  echo "Reports will be queued locally"
}
```

## Best Practices

### 1. Always Use CACHE Mode in CI/CD

```yaml
# Good
environment:
  JUX_STORAGE_MODE: cache

# Avoid (network failures break builds)
environment:
  JUX_STORAGE_MODE: api
```

### 2. Clean Up Temporary Keys

```yaml
# Always clean up, even on failure
- name: Clean up
  if: always()
  run: rm -f /tmp/signing_key.pem
```

### 3. Use Separate Keys Per Environment

```
dev/    → dev-signing-key.pem
staging → staging-signing-key.pem
prod/   → prod-signing-key.pem
```

### 4. Store Keys as Files (Not Strings)

```yaml
# Good: Download as file
- task: DownloadSecureFile@1
  name: juxKey
  inputs:
    secureFile: 'signing-key.pem'

# Less secure: Echo string to file
- run: echo "$KEY" > /tmp/key.pem
```

### 5. Verify Permissions

```bash
# Set restrictive permissions
chmod 600 /tmp/signing_key.pem

# Verify
ls -la /tmp/signing_key.pem
# Should show: -rw------- (600)
```

### 6. Use Secret Rotation

```yaml
# Rotate secrets regularly
# Update CI/CD secrets every 6-12 months
```

## Troubleshooting

### "Key file not found"

**Problem:** CI job fails with key file not found.

**Diagnosis:**
```yaml
- name: Debug key setup
  run: |
    ls -la /tmp/
    echo "JUX_KEY_PATH=$JUX_KEY_PATH"
```

**Solution:** Ensure key is written before tests run.

### "Permission denied"

**Problem:** Cannot read signing key.

**Solution:**
```bash
chmod 600 /tmp/signing_key.pem
chown $(whoami) /tmp/signing_key.pem
```

### "API connection timeout"

**Problem:** Tests fail when API is unreachable.

**Solution:** Use CACHE mode:
```yaml
environment:
  JUX_STORAGE_MODE: cache  # Not 'api'
```

### Queue Growing Indefinitely

**Problem:** Reports accumulate in offline queue.

**Diagnosis:**
```bash
jux-cache stats
# Queued Reports: 5000  <-- Growing
```

**Solutions:**
1. Fix API connectivity
2. Increase queue processing frequency
3. Clean old queued reports:
   ```bash
   jux-cache clean --days 7
   ```

## Next Steps

Now that pytest-jux is deployed in CI/CD:

- **[Multi-Environment Configuration](multi-environment-config.md)** - Configure per-environment settings
- **[Managing Cached Reports](managing-cached-reports.md)** - Maintain local storage
- **[Troubleshooting Guide](troubleshooting.md)** - Fix common issues
- **[Monitoring Guide](monitoring.md)** - Set up alerts and dashboards

## Related Documentation

- **[Quick Start](../tutorials/quick-start.md)** - Basic setup
- **[Setting Up Signing Keys](../tutorials/setting-up-signing-keys.md)** - Production keys
- **[Choosing Storage Modes](choosing-storage-modes.md)** - Storage strategy
- **[Security Policy](../security/SECURITY.md)** - Security best practices
