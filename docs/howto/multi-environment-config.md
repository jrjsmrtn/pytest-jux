# Multi-Environment Configuration

_Configure pytest-jux for development, staging, and production environments_

**Audience:** System Administrators, DevOps Engineers
**Prerequisites:**
- Understanding of [Configuration Management](../tutorials/quick-start.md#step-3-configure-pytest-jux)
- Familiarity with [Storage Modes](choosing-storage-modes.md)

## Overview

Different environments have different requirements. This guide shows how to configure pytest-jux appropriately for each environment in your deployment pipeline.

## Configuration Hierarchy

pytest-jux loads configuration from multiple sources with the following precedence:

```
1. Command-line arguments      (highest priority)
2. Environment variables
3. Configuration files:
   a. Project: .jux.conf
   b. User: ~/.config/jux/config
   c. System: /etc/jux/config
4. Defaults                    (lowest priority)
```

Higher priority sources override lower priority sources.

## Environment Profiles

### Development Environment

**Characteristics:**
- Developer laptops/workstations
- Offline capable
- Fast iteration
- Local storage only
- Self-signed certificates OK

**Configuration:**

`~/.config/jux/config` (developer machine):
```ini
[jux]
# Enable plugin
enabled = true

# Signing (optional for dev)
sign = false

# Storage: local only
storage_mode = local
storage_path = ~/.local/share/jux/reports

# Keys (if signing enabled)
# key_path = ~/.jux/dev/signing_key.pem
```

**Rationale:**
- `sign = false`: Faster test runs, signing not critical in dev
- `storage_mode = local`: No API server needed
- Minimal configuration for easy setup

**Alternative (signing enabled):**
```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/dev/signing_key.pem
storage_mode = local
```

### Staging Environment

**Characteristics:**
- Pre-production testing
- API server available
- Network may be unreliable
- Closer to production config
- Real certificates preferred

**Configuration:**

`/etc/jux/config` (staging servers):
```ini
[jux]
# Enable plugin
enabled = true

# Signing required
sign = true
key_path = /etc/jux/staging/signing_key.pem
cert_path = /etc/jux/staging/signing_key.crt

# Storage: cache mode (resilient)
storage_mode = cache
storage_path = /var/lib/jux/reports

# API configuration
api_url = https://jux-staging.example.com/api/v1
# api_key set via environment variable
```

**Environment variables (CI/CD):**
```bash
export JUX_API_KEY="staging-api-key-secret"
```

**Rationale:**
- `sign = true`: Validate signing in staging
- `storage_mode = cache`: Resilient to network issues
- `api_key` in env var: Don't commit secrets to git
- Real certificates: Test prod-like setup

### Production Environment

**Characteristics:**
- Production CI/CD pipelines
- API server highly available
- Network reliable
- Strict security requirements
- CA-signed certificates required

**Configuration:**

`/etc/jux/config` (production servers):
```ini
[jux]
# Enable plugin
enabled = true

# Signing required
sign = true
key_path = /etc/jux/production/signing_key.pem
cert_path = /etc/jux/production/signing_key.crt

# Storage: cache mode (belt and suspenders)
storage_mode = cache
storage_path = /var/lib/jux/reports

# API configuration
api_url = https://jux.example.com/api/v1
# api_key set via environment variable
```

**Environment variables (CI/CD):**
```bash
export JUX_API_KEY="$PRODUCTION_API_KEY_SECRET"
```

**Rationale:**
- `sign = true`: All production reports must be signed
- `storage_mode = cache`: Even reliable networks can fail
- Strict permissions: 0400 for keys (read-only)
- CA-signed certificates: Trust chain verification

## Configuration Management Strategies

### Strategy 1: Configuration Files Per Environment

**Structure:**
```
project/
├── .jux.dev.conf       # Development config
├── .jux.staging.conf   # Staging config
├── .jux.prod.conf      # Production config
└── .gitignore          # Exclude *.conf with secrets
```

**Usage:**
```bash
# Development
cp .jux.dev.conf .jux.conf

# Staging
cp .jux.staging.conf .jux.conf

# Production
cp .jux.prod.conf .jux.conf
```

**Or via symlinks:**
```bash
# Development
ln -sf .jux.dev.conf .jux.conf

# CI/CD determines which config to use
ln -sf .jux.${ENVIRONMENT}.conf .jux.conf
```

### Strategy 2: Environment Variables Override

**Base configuration (committed to git):**

`.jux.conf`:
```ini
[jux]
# Common settings
enabled = true
sign = true

# Environment-specific (overridden by env vars)
storage_mode = local
```

**Environment-specific variables:**

**Development:**
```bash
# No overrides needed
```

**Staging:**
```bash
export JUX_STORAGE_MODE=cache
export JUX_KEY_PATH=/etc/jux/staging/signing_key.pem
export JUX_API_URL=https://jux-staging.example.com/api/v1
export JUX_API_KEY=$STAGING_API_KEY
```

**Production:**
```bash
export JUX_STORAGE_MODE=cache
export JUX_KEY_PATH=/etc/jux/production/signing_key.pem
export JUX_API_URL=https://jux.example.com/api/v1
export JUX_API_KEY=$PRODUCTION_API_KEY
```

### Strategy 3: Hierarchical Configuration

**System-level** (`/etc/jux/config`):
```ini
[jux]
# Defaults for all users on this system
enabled = true
sign = true
storage_mode = cache
```

**User-level** (`~/.config/jux/config`):
```ini
[jux]
# Developer overrides
sign = false
storage_mode = local
```

**Project-level** (`.jux.conf`):
```ini
[jux]
# Project-specific overrides
# (empty - use system/user defaults)
```

## Platform-Specific Examples

### GitHub Actions

Use GitHub Environments for configuration:

**Development** (branch: `develop`):
```yaml
name: Test Development

on:
  push:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    environment: development

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: pytest --junit-xml=report.xml
        env:
          JUX_ENABLED: true
          JUX_SIGN: false
          JUX_STORAGE_MODE: local
```

**Staging** (branch: `main`):
```yaml
name: Test Staging

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Set up signing key
        env:
          JUX_SIGNING_KEY: ${{ secrets.JUX_SIGNING_KEY }}
        run: |
          echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
          chmod 600 /tmp/signing_key.pem

      - name: Run tests
        run: pytest --junit-xml=report.xml
        env:
          JUX_ENABLED: true
          JUX_SIGN: true
          JUX_KEY_PATH: /tmp/signing_key.pem
          JUX_STORAGE_MODE: cache
          JUX_API_URL: ${{ vars.JUX_API_URL }}
          JUX_API_KEY: ${{ secrets.JUX_API_KEY }}
```

**Production** (tags: `v*`):
```yaml
name: Test Production

on:
  push:
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Set up signing key
        env:
          JUX_SIGNING_KEY: ${{ secrets.JUX_SIGNING_KEY }}
        run: |
          echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
          chmod 400 /tmp/signing_key.pem  # Read-only in prod

      - name: Run tests
        run: pytest --junit-xml=report.xml
        env:
          JUX_ENABLED: true
          JUX_SIGN: true
          JUX_KEY_PATH: /tmp/signing_key.pem
          JUX_STORAGE_MODE: cache
          JUX_API_URL: ${{ vars.JUX_API_URL }}
          JUX_API_KEY: ${{ secrets.JUX_API_KEY }}
```

### GitLab CI/CD

Use GitLab Environments:

`.gitlab-ci.yml`:
```yaml
.test_template:
  image: python:3.11
  before_script:
    - pip install pytest-jux
    - |
      if [ -n "$JUX_SIGNING_KEY" ]; then
        echo "$JUX_SIGNING_KEY" > /tmp/signing_key.pem
        chmod 600 /tmp/signing_key.pem
        export JUX_KEY_PATH=/tmp/signing_key.pem
      fi
  script:
    - pytest --junit-xml=report.xml
  after_script:
    - rm -f /tmp/signing_key.pem

test:dev:
  extends: .test_template
  environment:
    name: development
  variables:
    JUX_ENABLED: "true"
    JUX_SIGN: "false"
    JUX_STORAGE_MODE: local
  only:
    - develop

test:staging:
  extends: .test_template
  environment:
    name: staging
  variables:
    JUX_ENABLED: "true"
    JUX_SIGN: "true"
    JUX_STORAGE_MODE: cache
    # JUX_API_URL and JUX_API_KEY from CI/CD variables
  only:
    - main

test:production:
  extends: .test_template
  environment:
    name: production
  variables:
    JUX_ENABLED: "true"
    JUX_SIGN: "true"
    JUX_STORAGE_MODE: cache
    # JUX_API_URL and JUX_API_KEY from CI/CD variables
  only:
    - tags
```

### Jenkins

Use Jenkins environments plugin:

```groovy
pipeline {
    agent any

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'])
    }

    environment {
        JUX_ENABLED = 'true'
        JUX_STORAGE_MODE = getStorageMode(params.ENVIRONMENT)
        JUX_SIGN = getSigningEnabled(params.ENVIRONMENT)
    }

    stages {
        stage('Configure') {
            steps {
                script {
                    if (params.ENVIRONMENT != 'dev') {
                        withCredentials([
                            file(credentialsId: "jux-${params.ENVIRONMENT}-key", variable: 'KEY_FILE')
                        ]) {
                            sh 'cp $KEY_FILE /tmp/signing_key.pem'
                            sh 'chmod 600 /tmp/signing_key.pem'
                            env.JUX_KEY_PATH = '/tmp/signing_key.pem'
                        }
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh 'pytest --junit-xml=report.xml'
            }
        }
    }

    post {
        always {
            sh 'rm -f /tmp/signing_key.pem'
        }
    }
}

def getStorageMode(env) {
    return env == 'dev' ? 'local' : 'cache'
}

def getSigningEnabled(env) {
    return env == 'dev' ? 'false' : 'true'
}
```

## Key Management Per Environment

### Separate Keys Per Environment

**Directory structure:**
```
/etc/jux/
├── development/
│   ├── signing_key.pem
│   └── signing_key.crt
├── staging/
│   ├── signing_key.pem
│   └── signing_key.crt
└── production/
    ├── signing_key.pem
    └── signing_key.crt
```

**Deployment with Ansible:**

```yaml
# deploy-jux-keys.yml
---
- name: Deploy pytest-jux keys per environment
  hosts: "{{ target_env }}_servers"
  vars:
    key_source: "{{ lookup('env', 'KEY_VAULT_PATH') }}/{{ target_env }}"
    key_dest: "/etc/jux/{{ target_env }}"

  tasks:
    - name: Create key directory
      file:
        path: "{{ key_dest }}"
        state: directory
        mode: '0700'
        owner: jenkins
        group: jenkins

    - name: Copy signing key
      copy:
        src: "{{ key_source }}/signing_key.pem"
        dest: "{{ key_dest }}/signing_key.pem"
        mode: "{{ '0400' if target_env == 'production' else '0600' }}"
        owner: jenkins
        group: jenkins

    - name: Copy certificate
      copy:
        src: "{{ key_source }}/signing_key.crt"
        dest: "{{ key_dest }}/signing_key.crt"
        mode: '0644'
        owner: jenkins
        group: jenkins
```

**Usage:**
```bash
# Deploy to staging
ansible-playbook deploy-jux-keys.yml -e target_env=staging

# Deploy to production
ansible-playbook deploy-jux-keys.yml -e target_env=production
```

## Configuration Validation

### Verify Current Configuration

```bash
# Check effective configuration
jux-config dump

# Output shows sources:
#   jux_enabled = true
#     Source: env:JUX_ENABLED
#   jux_sign = true
#     Source: /etc/jux/config
#   jux_key_path = /etc/jux/production/signing_key.pem
#     Source: /etc/jux/config
```

### Validate Configuration

```bash
# Basic validation
jux-config validate

# Strict validation (check dependencies)
jux-config validate --strict

# Example output:
#   ⚠ jux_sign is enabled but jux_key_path is not set
#   ⚠ jux_publish is enabled but jux_api_url is not set
```

### Test Configuration

**Staging:**
```bash
# Set environment
export ENVIRONMENT=staging
export JUX_KEY_PATH=/etc/jux/staging/signing_key.pem
export JUX_API_URL=https://jux-staging.example.com/api/v1

# Validate
jux-config validate --strict

# Test signing
pytest --junit-xml=/tmp/test-report.xml tests/test_smoke.py
jux-verify /tmp/test-report.xml --cert /etc/jux/staging/signing_key.crt
```

**Production:**
```bash
# Set environment
export ENVIRONMENT=production
export JUX_KEY_PATH=/etc/jux/production/signing_key.pem
export JUX_API_URL=https://jux.example.com/api/v1

# Validate
jux-config validate --strict

# Test signing
pytest --junit-xml=/tmp/test-report.xml tests/test_smoke.py
jux-verify /tmp/test-report.xml --cert /etc/jux/production/signing_key.crt
```

## Troubleshooting

### Wrong Configuration Being Used

**Problem:** Configuration from wrong environment being applied.

**Diagnosis:**
```bash
# Check what's being loaded
jux-config dump --json | jq '
  to_entries[] |
  select(.value.source != "default") |
  {key: .key, value: .value.value, source: .value.source}
'
```

**Solution:** Verify configuration file precedence:
```bash
# List config files in precedence order
jux-config view --all
```

### Environment Variables Not Overriding

**Problem:** Environment variables not taking effect.

**Check:**
```bash
# Verify environment variables are set
env | grep ^JUX_

# Check if config file is overriding (it shouldn't)
# Environment variables have higher precedence
```

**Solution:** Ensure variable names are correct:
```bash
# Correct format
export JUX_ENABLED=true

# Wrong format
export jux_enabled=true  # ❌ Must be uppercase
```

### API Key in Wrong Environment

**Problem:** Accidentally using production API key in staging.

**Prevention:**
```bash
# Use environment-specific secret names
# Staging
export JUX_API_KEY=$STAGING_API_KEY

# Production
export JUX_API_KEY=$PRODUCTION_API_KEY

# Never use generic names like $API_KEY
```

## Best Practices

### 1. Minimize Configuration in Git

```ini
# Good: .jux.conf (committed)
[jux]
enabled = true
sign = true
storage_mode = local  # Default, overridden by env vars

# Bad: Don't commit secrets
[jux]
api_key = secret-123  # ❌ Never commit!
```

### 2. Use Environment Variables for Secrets

```bash
# Good
export JUX_API_KEY=$SECRET_FROM_VAULT

# Bad
[jux]
api_key = hardcoded-secret  # ❌
```

### 3. Separate Keys Per Environment

```
✅ /etc/jux/dev/signing_key.pem
✅ /etc/jux/staging/signing_key.pem
✅ /etc/jux/prod/signing_key.pem

❌ /etc/jux/signing_key.pem  # Don't share keys!
```

### 4. Document Environment Differences

Create a `ENVIRONMENTS.md` file:

```markdown
# Environment Configuration

| Setting | Dev | Staging | Production |
|---------|-----|---------|------------|
| Signing | Optional | Required | Required |
| Storage | LOCAL | CACHE | CACHE |
| API | None | staging API | prod API |
| Key Type | RSA 2048 | RSA 4096 | RSA 4096 |
| Certificate | Self-signed | CA-signed | CA-signed |
```

### 5. Use Configuration as Code

```yaml
# terraform/jux-config.tf
resource "aws_ssm_parameter" "jux_staging_api_key" {
  name  = "/jux/staging/api_key"
  type  = "SecureString"
  value = var.staging_api_key
}

resource "aws_ssm_parameter" "jux_production_api_key" {
  name  = "/jux/production/api_key"
  type  = "SecureString"
  value = var.production_api_key
}
```

### 6. Test Environment Promotion

```bash
# Test in dev → staging → production
make test-dev
make test-staging
make test-production

# Each target uses appropriate environment config
```

## Environment Comparison Matrix

| Feature | Development | Staging | Production |
|---------|-------------|---------|------------|
| **Signing** | Optional | Required | Required |
| **Storage Mode** | LOCAL | CACHE | CACHE |
| **API Server** | None | staging-jux | prod-jux |
| **Key Algorithm** | RSA 2048 | RSA 4096 | RSA 4096 |
| **Certificate** | Self-signed | CA-signed | CA-signed |
| **Key Permissions** | 0600 | 0600 | 0400 (read-only) |
| **Queue Monitoring** | No | Optional | Required |
| **Backup** | No | Yes | Yes (encrypted) |
| **Rotation** | Annual | Every 2 years | Every 2-3 years |
| **Access Control** | Developer | CI/CD only | CI/CD only |

## Next Steps

Now that you understand multi-environment configuration:

- **[Managing Cached Reports](managing-cached-reports.md)** - Maintain local storage
- **[CI/CD Deployment](ci-cd-deployment.md)** - Deploy to CI/CD pipelines
- **[Troubleshooting Guide](troubleshooting.md)** - Fix configuration issues

## Related Documentation

- **[Quick Start](../tutorials/quick-start.md)** - Basic configuration
- **[Choosing Storage Modes](choosing-storage-modes.md)** - Storage strategy
- **[Setting Up Signing Keys](../tutorials/setting-up-signing-keys.md)** - Key management
- **[Configuration Reference](../reference/configuration.md)** - All options
