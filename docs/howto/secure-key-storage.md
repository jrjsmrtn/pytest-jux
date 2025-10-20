# How to Store Signing Keys Securely

**Best practices for protecting pytest-jux cryptographic keys**

---

## Overview

Secure key storage is critical for maintaining the integrity and trustworthiness of signed test reports. Compromised keys allow attackers to:
- ✗ Sign forged test reports
- ✗ Bypass CI/CD quality gates
- ✗ Hide test failures
- ✗ Inject malicious code

This guide covers secure storage practices for different environments.

---

## Key Storage Principles

### 1. **Confidentiality**: Private keys must never be exposed
- ✅ Never commit keys to version control
- ✅ Never log key contents
- ✅ Never share keys via unencrypted channels
- ✅ Never embed keys in source code

### 2. **Integrity**: Keys must not be tampered with
- ✅ Verify key checksums after transfer
- ✅ Use signed/encrypted storage
- ✅ Detect unauthorized modifications

### 3. **Availability**: Keys must be accessible when needed
- ✅ Maintain secure backups
- ✅ Document key locations
- ✅ Have recovery procedures

### 4. **Least Privilege**: Minimize key access
- ✅ Only authorized systems/users access keys
- ✅ Use separate keys per environment
- ✅ Rotate keys regularly

---

## File System Storage

### Recommended Permissions

**Private Keys** (highest security):
```bash
# Private key: Read/write by owner only
chmod 600 ~/.ssh/jux/prod-key.pem
ls -l ~/.ssh/jux/prod-key.pem
# Expected: -rw------- (600)
```

**Certificates** (can be shared):
```bash
# Certificate: Read by everyone, write by owner
chmod 644 ~/.ssh/jux/prod-cert.pem
ls -l ~/.ssh/jux/prod-cert.pem
# Expected: -rw-r--r-- (644)
```

**Key Directory**:
```bash
# Directory: Owner only
chmod 700 ~/.ssh/jux
ls -lad ~/.ssh/jux
# Expected: drwx------ (700)
```

### Secure Directory Structure

```
~/.ssh/jux/
├── production/           # Production keys (700)
│   ├── prod-key.pem      # Private key (600)
│   └── prod-cert.pem     # Certificate (644)
├── staging/              # Staging keys (700)
│   ├── staging-key.pem   # Private key (600)
│   └── staging-cert.pem  # Certificate (644)
├── development/          # Development keys (700)
│   ├── dev-key.pem       # Private key (600)
│   └── dev-cert.pem      # Certificate (644)
├── backups/              # Key backups (700)
│   └── *.backup          # Encrypted backups (600)
├── retired/              # Retired keys (700)
│   └── *.retired         # Old keys (400, read-only)
└── .gitignore            # Prevent accidental commits (644)
```

**Create secure structure**:
```bash
# Create directory structure
mkdir -p ~/.ssh/jux/{production,staging,development,backups,retired}

# Set permissions
chmod 700 ~/.ssh/jux ~/.ssh/jux/*

# Create .gitignore
cat > ~/.ssh/jux/.gitignore << 'EOF'
# Prevent accidental git commits
*.pem
*.key
*.crt
*.p12
*.pfx
!.gitignore
EOF
```

### Prevent Accidental Commits

**Global .gitignore**:
```bash
# Add to global .gitignore
cat >> ~/.gitignore_global << 'EOF'
# pytest-jux keys
*.pem
*.key
!requirements*.txt
!pytest*.txt
EOF

# Configure git to use global .gitignore
git config --global core.excludesfile ~/.gitignore_global
```

**Project .gitignore**:
```bash
# Add to project .gitignore
cat >> .gitignore << 'EOF'
# pytest-jux keys and certificates
*.pem
*.key
*.crt
*.p12
*.pfx
keys/
.ssh/
EOF
```

**Pre-commit Hook** (prevent commits):
```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -E '\.(pem|key|crt|p12|pfx)$'; then
  echo "ERROR: Attempting to commit private keys!"
  echo "Files:"
  git diff --cached --name-only | grep -E '\.(pem|key|crt|p12|pfx)$'
  exit 1
fi
```

---

## Environment Variables

### Local Development

**Secure environment variables**:
```bash
# In ~/.bashrc or ~/.zshrc (NOT in project files)
export JUX_KEY_PATH="${HOME}/.ssh/jux/development/dev-key.pem"
export JUX_CERT_PATH="${HOME}/.ssh/jux/development/dev-cert.pem"

# Restrict shell history from logging keys
export HISTCONTROL=ignorespace  # Ignore commands starting with space
```

**Verify not exposed**:
```bash
# Check if accidentally exported in git
git grep JUX_KEY_PATH  # Should return nothing in committed files

# Check if in shell history
history | grep JUX_KEY_PATH  # Should be minimal
```

### CI/CD Secrets Management

#### GitHub Actions Secrets

**Store keys as secrets** (Web UI):
```
1. Go to: Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: JUX_KEY_PATH
4. Value: <paste private key contents>
5. Click "Add secret"
```

**Use in workflow** (never log):
```yaml
# .github/workflows/test.yml
env:
  JUX_KEY_PATH: ${{ secrets.JUX_KEY_PATH }}
  JUX_CERT_PATH: ${{ secrets.JUX_CERT_PATH }}

jobs:
  test:
    steps:
      - name: Write key to file (ephemeral)
        run: |
          mkdir -p ~/.ssh/jux
          echo "${{ secrets.JUX_KEY_PATH }}" > ~/.ssh/jux/ci-key.pem
          chmod 600 ~/.ssh/jux/ci-key.pem

      - name: Run tests
        run: pytest --junitxml=junit.xml --jux-key ~/.ssh/jux/ci-key.pem

      # Key automatically deleted when runner terminates
```

**NEVER log secrets**:
```yaml
# ❌ WRONG: This logs the secret
- run: echo "Key: ${{ secrets.JUX_KEY_PATH }}"

# ✅ CORRECT: Use without logging
- run: pytest --jux-key <(echo "${{ secrets.JUX_KEY_PATH }}")
```

#### GitLab CI/CD Variables

**Store as protected variable** (Web UI):
```
1. Go to: Settings → CI/CD → Variables
2. Click "Add variable"
3. Key: JUX_KEY_PATH
4. Value: <paste private key contents>
5. Type: File (GitLab writes to temp file)
6. ✅ Protect variable (only protected branches)
7. ✅ Mask variable (hide in logs)
8. Click "Add variable"
```

**Use in pipeline**:
```yaml
# .gitlab-ci.yml
test:
  variables:
    JUX_KEY_FILE: $JUX_KEY_PATH  # File path (GitLab creates temp file)
  script:
    - chmod 600 $JUX_KEY_FILE
    - pytest --junitxml=junit.xml --jux-key $JUX_KEY_FILE
```

#### Jenkins Credentials

**Store as secret file** (Web UI):
```
1. Go to: Manage Jenkins → Credentials → Add Credentials
2. Kind: Secret file
3. File: Upload prod-key.pem
4. ID: pytest-jux-prod-key
5. Description: "pytest-jux Production Signing Key"
6. Click "OK"
```

**Use in Jenkinsfile**:
```groovy
pipeline {
  agent any

  environment {
    JUX_KEY = credentials('pytest-jux-prod-key')  // Path to temp file
    JUX_CERT = credentials('pytest-jux-prod-cert')
  }

  stages {
    stage('Test') {
      steps {
        sh 'chmod 600 ${JUX_KEY}'
        sh 'pytest --junitxml=junit.xml --jux-key ${JUX_KEY}'
      }
    }
  }

  post {
    always {
      // Credentials automatically cleaned up
      cleanWs()
    }
  }
}
```

---

## Cloud Key Management Services (KMS)

### AWS Secrets Manager

**Store key in AWS Secrets Manager**:
```bash
# 1. Store private key
aws secretsmanager create-secret \
  --name pytest-jux/production/private-key \
  --secret-string file://~/.ssh/jux/prod-key.pem \
  --description "pytest-jux Production Private Key"

# 2. Store certificate
aws secretsmanager create-secret \
  --name pytest-jux/production/certificate \
  --secret-string file://~/.ssh/jux/prod-cert.pem \
  --description "pytest-jux Production Certificate"
```

**Retrieve key in CI/CD**:
```bash
# In CI/CD pipeline
aws secretsmanager get-secret-value \
  --secret-id pytest-jux/production/private-key \
  --query SecretString \
  --output text > /tmp/jux-key.pem

chmod 600 /tmp/jux-key.pem
pytest --junitxml=junit.xml --jux-key /tmp/jux-key.pem
rm -f /tmp/jux-key.pem  # Clean up
```

### Google Cloud Secret Manager

**Store key**:
```bash
# 1. Store private key
gcloud secrets create pytest-jux-prod-key \
  --data-file ~/.ssh/jux/prod-key.pem \
  --replication-policy automatic

# 2. Grant access to service account
gcloud secrets add-iam-policy-binding pytest-jux-prod-key \
  --member "serviceAccount:ci-cd@project.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

**Retrieve key**:
```bash
# In CI/CD pipeline
gcloud secrets versions access latest \
  --secret pytest-jux-prod-key > /tmp/jux-key.pem

chmod 600 /tmp/jux-key.pem
pytest --junitxml=junit.xml --jux-key /tmp/jux-key.pem
rm -f /tmp/jux-key.pem
```

### Azure Key Vault

**Store key**:
```bash
# 1. Store private key
az keyvault secret set \
  --vault-name pytest-jux-vault \
  --name prod-private-key \
  --file ~/.ssh/jux/prod-key.pem

# 2. Set access policy
az keyvault set-policy \
  --name pytest-jux-vault \
  --spn <service-principal-id> \
  --secret-permissions get
```

**Retrieve key**:
```bash
# In CI/CD pipeline
az keyvault secret download \
  --vault-name pytest-jux-vault \
  --name prod-private-key \
  --file /tmp/jux-key.pem

chmod 600 /tmp/jux-key.pem
pytest --junitxml=junit.xml --jux-key /tmp/jux-key.pem
rm -f /tmp/jux-key.pem
```

---

## Encrypted Storage

### GPG Encryption

**Encrypt private key for storage**:
```bash
# 1. Encrypt key with GPG
gpg --symmetric --cipher-algo AES256 \
  --output ~/.ssh/jux/prod-key.pem.gpg \
  ~/.ssh/jux/prod-key.pem

# Enter passphrase (store passphrase in password manager)

# 2. Verify encryption
file ~/.ssh/jux/prod-key.pem.gpg
# Expected: GPG symmetrically encrypted data (AES256 cipher)

# 3. Delete unencrypted key (after backup)
shred -u ~/.ssh/jux/prod-key.pem
```

**Decrypt for use**:
```bash
# Decrypt key (prompts for passphrase)
gpg --decrypt ~/.ssh/jux/prod-key.pem.gpg > /tmp/jux-key.pem
chmod 600 /tmp/jux-key.pem

# Use key
pytest --junitxml=junit.xml --jux-key /tmp/jux-key.pem

# Clean up
shred -u /tmp/jux-key.pem
```

### OpenSSL Encryption

**Encrypt key with AES-256**:
```bash
# Encrypt
openssl enc -aes-256-cbc -salt \
  -in ~/.ssh/jux/prod-key.pem \
  -out ~/.ssh/jux/prod-key.pem.enc

# Enter encryption passphrase

# Verify
file ~/.ssh/jux/prod-key.pem.enc
# Expected: openssl enc'd data with salted password
```

**Decrypt**:
```bash
# Decrypt
openssl enc -aes-256-cbc -d \
  -in ~/.ssh/jux/prod-key.pem.enc \
  -out /tmp/jux-key.pem

chmod 600 /tmp/jux-key.pem
pytest --junitxml=junit.xml --jux-key /tmp/jux-key.pem
shred -u /tmp/jux-key.pem
```

---

## Hardware Security Modules (HSM)

**Note**: pytest-jux does not currently support HSM integration (planned for future releases).

**Workaround** (export key from HSM for use):
```bash
# Export public certificate from HSM
# (Keep private key in HSM, use exported key for signing)

# Future: Direct HSM integration via PKCS#11
```

---

## Key Storage Security Checklist

### Development Environment

- [ ] **Private keys**: Stored in `~/.ssh/jux/` with 600 permissions
- [ ] **Certificates**: Stored with 644 permissions
- [ ] **Directory**: `~/.ssh/jux/` has 700 permissions
- [ ] **.gitignore**: Configured to prevent key commits
- [ ] **Environment variables**: Set in shell config (not committed)
- [ ] **Backups**: Encrypted backups stored securely

### Staging/Production Environment

- [ ] **CI/CD secrets**: Keys stored in secrets manager
- [ ] **Access control**: Only authorized pipelines access keys
- [ ] **Encryption**: Keys encrypted at rest
- [ ] **Ephemeral use**: Keys written to temp files (deleted after use)
- [ ] **Rotation schedule**: Keys rotated every 90-180 days
- [ ] **Monitoring**: Key access logged and monitored

### General

- [ ] **Separate keys**: Different keys for dev, staging, production
- [ ] **Documentation**: Key locations documented
- [ ] **Recovery**: Backup and recovery procedures tested
- [ ] **Audit**: Key access audited regularly

---

## Common Mistakes to Avoid

### ❌ **Mistake 1**: Committing keys to git

**Wrong**:
```bash
git add keys/prod-key.pem
git commit -m "Add production key"  # ❌ NEVER DO THIS
```

**If accidentally committed**:
```bash
# 1. Remove from history (use git-filter-repo or BFG)
git filter-repo --path keys/prod-key.pem --invert-paths

# 2. Force push (coordinate with team)
git push --force

# 3. ROTATE KEY IMMEDIATELY (consider it compromised)
jux-keygen --output new-key.pem --cert
```

### ❌ **Mistake 2**: Logging key contents

**Wrong**:
```bash
echo "Key path: $JUX_KEY_PATH"
cat $JUX_KEY_PATH  # ❌ Logs key contents
```

**Correct**:
```bash
echo "Key path: [REDACTED]"
# Use key without logging:
pytest --jux-key "$JUX_KEY_PATH"
```

### ❌ **Mistake 3**: Insecure file permissions

**Wrong**:
```bash
chmod 644 ~/.ssh/jux/prod-key.pem  # ❌ World-readable
```

**Correct**:
```bash
chmod 600 ~/.ssh/jux/prod-key.pem  # ✅ Owner only
```

### ❌ **Mistake 4**: Sharing keys via email/chat

**Wrong**:
```
Hey team, here's the prod key:
-----BEGIN RSA PRIVATE KEY-----  # ❌ NEVER SHARE THIS WAY
...
```

**Correct**:
```bash
# Use secure sharing:
# 1. Encrypt with recipient's GPG key
gpg --encrypt --recipient team@example.com prod-key.pem

# 2. Or use password manager (1Password, LastPass, etc.)

# 3. Or use secrets manager (AWS Secrets Manager, etc.)
```

---

## Monitoring and Auditing

### Key Access Logging

**Monitor key file access** (Linux):
```bash
# Install auditd
sudo apt-get install auditd

# Monitor key directory
sudo auditctl -w ~/.ssh/jux -p war -k pytest-jux-keys

# View audit logs
sudo ausearch -k pytest-jux-keys
```

### CI/CD Secrets Audit

**GitHub Actions**:
```yaml
# Audit secret usage
# Settings → Actions → General → "Workflow permissions"
# Enable "Read repository contents permission"

# Review secret usage in workflows:
# Settings → Secrets and variables → Actions → "Actions secrets"
# Click secret → "Used in" shows which workflows use it
```

**AWS Secrets Manager Audit**:
```bash
# CloudTrail logs secret access
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=pytest-jux/production/private-key \
  --max-results 50
```

---

## Best Practices Summary

### Storage

1. **✅ Use proper permissions**: 600 for private keys, 644 for certificates
2. **✅ Separate by environment**: Different keys for dev/staging/prod
3. **✅ Encrypt at rest**: Use GPG/OpenSSL or cloud KMS
4. **✅ Prevent commits**: .gitignore and pre-commit hooks
5. **✅ Use secrets managers**: For CI/CD and production

### Access Control

1. **✅ Least privilege**: Only authorized users/systems access keys
2. **✅ Ephemeral access**: Delete keys after use in CI/CD
3. **✅ Audit access**: Log and monitor key usage
4. **✅ Rotate regularly**: 90-180 days for production keys
5. **✅ Revoke when needed**: Immediate rotation if compromised

### Documentation

1. **✅ Document locations**: Where keys are stored
2. **✅ Document procedures**: How to access/use keys
3. **✅ Document rotation**: When keys were last rotated
4. **✅ Document recovery**: Backup and restore procedures
5. **✅ Document incidents**: Key compromises and responses

---

## See Also

- **[Rotate Signing Keys](rotate-signing-keys.md)**: Key rotation procedures
- **[Backup and Restore Keys](backup-restore-keys.md)**: Backup strategies
- **[CI/CD Deployment Guide](ci-cd-deployment.md)**: CI/CD integration
- **[Multi-Environment Configuration](multi-environment-config.md)**: Environment setup

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
