# How to Rotate Signing Keys

**Safely rotate pytest-jux signing keys without disrupting CI/CD pipelines**

---

## Overview

Key rotation is a critical security practice that involves replacing cryptographic keys periodically or when:
- Keys are compromised or suspected of being compromised
- Personnel with key access leave the organization
- Compliance requirements mandate periodic rotation
- Keys reach end-of-life (certificate expiration)
- Upgrading to stronger cryptographic algorithms

This guide provides step-by-step procedures for rotating signing keys safely.

---

## When to Rotate Keys

### Scheduled Rotation (Planned)

**Recommended Rotation Schedule**:
- **Production keys**: Every 90-180 days
- **Staging keys**: Every 180-365 days
- **Development keys**: Every 365 days or when needed

**Best Practice**: Rotate before certificate expiration:
```bash
# Check certificate expiration
openssl x509 -in ~/.ssh/jux/prod-key.crt -noout -enddate

# Expected output:
# notAfter=Dec 31 23:59:59 2025 GMT
```

### Emergency Rotation (Unplanned)

**Rotate immediately if**:
- ✗ Private key file was accidentally committed to version control
- ✗ Key file was accessed by unauthorized personnel
- ✗ Key file was exposed in logs or error messages
- ✗ System with key access was compromised
- ✗ Employee with key access left organization

---

## Rotation Strategy

### Strategy 1: Gradual Rotation (Recommended)

**Best for**: Production environments with continuous operations

**Process**:
1. Generate new key pair (while old key still valid)
2. Deploy new key to all systems (dual-key period)
3. Switch signing to use new key
4. Verify all systems use new key
5. Retire old key after grace period (7-30 days)

**Advantages**:
- ✅ Zero downtime
- ✅ Gradual rollout reduces risk
- ✅ Easy rollback if issues occur

**Disadvantages**:
- ⚠️ Requires managing two keys temporarily
- ⚠️ Longer rotation process

### Strategy 2: Immediate Rotation

**Best for**: Emergency rotations, development/staging environments

**Process**:
1. Generate new key pair
2. Deploy new key immediately
3. Invalidate old key
4. Re-sign any pending reports

**Advantages**:
- ✅ Fast rotation (minutes)
- ✅ Simpler process
- ✅ Immediate security improvement

**Disadvantages**:
- ⚠️ Potential downtime
- ⚠️ May break running CI/CD jobs
- ⚠️ Requires immediate deployment

---

## Step-by-Step: Gradual Rotation

### Phase 1: Generate New Key Pair

```bash
# 1. Create rotation directory
mkdir -p ~/.ssh/jux/rotation-$(date +%Y%m%d)
cd ~/.ssh/jux/rotation-$(date +%Y%m%d)

# 2. Generate new RSA key pair
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output prod-key-v2.pem \
  --cert \
  --subject "CN=pytest-jux Production v2, OU=CI/CD, O=YourOrg" \
  --days-valid 365

# Expected output:
# ✓ Private key saved: prod-key-v2.pem
# ✓ Certificate saved: prod-key-v2.crt
```

**Important**: Use descriptive subject names to track key versions.

### Phase 2: Backup Old Key

```bash
# 3. Backup current production key
cp ~/.ssh/jux/prod-key.pem ~/.ssh/jux/prod-key.pem.backup-$(date +%Y%m%d)
cp ~/.ssh/jux/prod-key.crt ~/.ssh/jux/prod-key.crt.backup-$(date +%Y%m%d)

# 4. Verify backup
diff ~/.ssh/jux/prod-key.pem ~/.ssh/jux/prod-key.pem.backup-$(date +%Y%m%d)
# Expected: No differences
```

### Phase 3: Test New Key

```bash
# 5. Test signing with new key
pytest --junitxml=test-rotation.xml \
  --jux-key rotation-$(date +%Y%m%d)/prod-key-v2.pem \
  --jux-cert rotation-$(date +%Y%m%d)/prod-key-v2.crt

# 6. Verify signature with new certificate
jux-verify \
  -i ~/.local/share/pytest-jux/reports/*.xml \
  --cert rotation-$(date +%Y%m%d)/prod-key-v2.crt

# Expected: ✓ Signature is valid
```

### Phase 4: Deploy New Key (Gradual Rollout)

**For CI/CD environments**:

#### GitHub Actions (Secrets)

```bash
# 7. Update GitHub Secrets (via Web UI or CLI)

# Using GitHub CLI:
gh secret set JUX_KEY_PATH_V2 < rotation-$(date +%Y%m%d)/prod-key-v2.pem
gh secret set JUX_CERT_PATH_V2 < rotation-$(date +%Y%m%d)/prod-key-v2.crt

# Note: Keep old secrets (JUX_KEY_PATH, JUX_CERT_PATH) for rollback
```

**Update workflow** (dual-key period):
```yaml
# .github/workflows/test.yml
env:
  # Use new key for new runs
  JUX_KEY_PATH: ${{ secrets.JUX_KEY_PATH_V2 }}
  JUX_CERT_PATH: ${{ secrets.JUX_CERT_PATH_V2 }}

  # Keep old key for verification (if needed)
  JUX_KEY_PATH_V1: ${{ secrets.JUX_KEY_PATH }}
  JUX_CERT_PATH_V1: ${{ secrets.JUX_CERT_PATH }}
```

#### GitLab CI (Variables)

```bash
# 8. Update GitLab CI/CD Variables (via Web UI)

# Settings → CI/CD → Variables
# Add new variables:
# - JUX_KEY_PATH_V2: <paste prod-key-v2.pem contents>
# - JUX_CERT_PATH_V2: <paste prod-key-v2.crt contents>

# Keep existing JUX_KEY_PATH, JUX_CERT_PATH for rollback
```

**Update pipeline** (dual-key period):
```yaml
# .gitlab-ci.yml
test:
  variables:
    # Use new key
    JUX_KEY_PATH: ${JUX_KEY_PATH_V2}
    JUX_CERT_PATH: ${JUX_CERT_PATH_V2}
  script:
    - pytest --junitxml=junit.xml
```

#### Jenkins (Credentials)

```bash
# 9. Update Jenkins credentials

# Via Jenkins UI:
# Manage Jenkins → Credentials → Update Credentials
# Upload new prod-key-v2.pem and prod-key-v2.crt

# Update Jenkinsfile:
# Use new credential IDs, keep old for rollback
```

### Phase 5: Monitor and Verify

```bash
# 10. Monitor CI/CD runs for 24-48 hours
# Check all pipelines use new key successfully

# 11. Verify all new reports use new key
jux-cache list | tail -10  # Recent reports
jux-inspect -i <report-hash>.xml  # Check signature algorithm

# Expected: All new reports signed with prod-key-v2
```

### Phase 6: Retire Old Key

**After 7-30 day grace period**:

```bash
# 12. Revoke old key (mark as retired)
mv ~/.ssh/jux/prod-key.pem ~/.ssh/jux/retired/prod-key-v1.pem.retired-$(date +%Y%m%d)
mv ~/.ssh/jux/prod-key.crt ~/.ssh/jux/retired/prod-key-v1.crt.retired-$(date +%Y%m%d)

# 13. Install new key as current
cp rotation-$(date +%Y%m%d)/prod-key-v2.pem ~/.ssh/jux/prod-key.pem
cp rotation-$(date +%Y%m%d)/prod-key-v2.crt ~/.ssh/jux/prod-key.crt

# 14. Remove old CI/CD secrets (after verification)
# GitHub: gh secret delete JUX_KEY_PATH_V1 JUX_CERT_PATH_V1
# GitLab: Delete JUX_KEY_PATH_V1, JUX_CERT_PATH_V1 variables
# Jenkins: Delete old credentials
```

---

## Step-by-Step: Emergency Rotation

### Phase 1: Generate and Deploy Immediately

```bash
# 1. Generate new emergency key
mkdir -p ~/.ssh/jux/emergency-$(date +%Y%m%d-%H%M)
cd ~/.ssh/jux/emergency-$(date +%Y%m%d-%H%M)

jux-keygen \
  --type rsa \
  --bits 4096 \
  --output emergency-key.pem \
  --cert \
  --subject "CN=Emergency Rotation $(date +%Y-%m-%d)" \
  --days-valid 90

# 2. Immediately replace production key
cp ~/.ssh/jux/prod-key.pem ~/.ssh/jux/compromised/prod-key.pem.COMPROMISED-$(date +%Y%m%d-%H%M)
cp emergency-key.pem ~/.ssh/jux/prod-key.pem
cp emergency-key.crt ~/.ssh/jux/prod-key.crt

# 3. Update CI/CD secrets immediately
# (Same as gradual rotation Phase 4, but delete old secrets immediately)
```

### Phase 2: Revoke Compromised Key

```bash
# 4. Mark old key as compromised (DO NOT USE)
chmod 000 ~/.ssh/jux/compromised/prod-key.pem.COMPROMISED-*

# 5. Document compromise
cat > ~/.ssh/jux/compromised/INCIDENT-$(date +%Y%m%d-%H%M).txt << EOF
Date: $(date)
Reason: <describe reason for emergency rotation>
Action: Key rotated immediately
New Key: emergency-$(date +%Y%m%d-%H%M)/emergency-key.pem
Old Key: COMPROMISED - DO NOT USE
EOF

# 6. Notify team
echo "ALERT: Signing key rotated due to compromise. All systems updated."
```

### Phase 3: Post-Incident Review

```bash
# 7. Verify all systems use new key
# (Monitor CI/CD pipelines, check recent reports)

# 8. Plan permanent rotation (after emergency)
# Schedule formal key rotation within 30-90 days
```

---

## Multi-Environment Rotation

### Rotating Keys Across Environments

```bash
# Production rotation
jux-keygen --output ~/.ssh/jux/prod-key-v2.pem --cert --subject "CN=Prod v2" --days-valid 365

# Staging rotation (simultaneous or separate)
jux-keygen --output ~/.ssh/jux/staging-key-v2.pem --cert --subject "CN=Staging v2" --days-valid 365

# Development rotation
jux-keygen --output ~/.ssh/jux/dev-key-v2.pem --cert --subject "CN=Dev v2" --days-valid 365
```

**Update configuration**:
```toml
# ~/.config/pytest-jux/config.toml
[jux]
environment = "production"

[jux.environments.production]
private_key_path = "~/.ssh/jux/prod-key-v2.pem"
certificate_path = "~/.ssh/jux/prod-key-v2.crt"

[jux.environments.staging]
private_key_path = "~/.ssh/jux/staging-key-v2.pem"
certificate_path = "~/.ssh/jux/staging-key-v2.crt"

[jux.environments.development]
private_key_path = "~/.ssh/jux/dev-key-v2.pem"
certificate_path = "~/.ssh/jux/dev-key-v2.crt"
```

---

## Rotation Checklist

Use this checklist for each rotation:

### Pre-Rotation

- [ ] **Schedule**: Rotation date/time planned and communicated
- [ ] **Backup**: Current keys backed up securely
- [ ] **Access**: Verify access to all systems requiring update
- [ ] **Testing**: Test environment ready for verification
- [ ] **Rollback Plan**: Documented rollback procedure

### During Rotation

- [ ] **Generate**: New key pair generated successfully
- [ ] **Verify**: New key tested and verified
- [ ] **Deploy**: New key deployed to all required systems
- [ ] **Monitor**: Systems monitored for issues
- [ ] **Document**: Rotation documented in change log

### Post-Rotation

- [ ] **Verify**: All systems using new key
- [ ] **Grace Period**: Old key kept for rollback (7-30 days)
- [ ] **Retire**: Old key retired after grace period
- [ ] **Review**: Rotation process reviewed and improved
- [ ] **Schedule Next**: Next rotation scheduled

---

## Rollback Procedure

If rotation causes issues:

```bash
# 1. Restore old key immediately
cp ~/.ssh/jux/prod-key.pem.backup-$(date +%Y%m%d) ~/.ssh/jux/prod-key.pem
cp ~/.ssh/jux/prod-key.crt.backup-$(date +%Y%m%d) ~/.ssh/jux/prod-key.crt

# 2. Revert CI/CD secrets to old version
# GitHub: Restore JUX_KEY_PATH to old value
# GitLab: Restore JUX_KEY_PATH to old value
# Jenkins: Restore old credential

# 3. Verify rollback
pytest --junitxml=rollback-test.xml --jux-key ~/.ssh/jux/prod-key.pem --jux-cert ~/.ssh/jux/prod-key.crt
jux-verify -i rollback-test.xml --cert ~/.ssh/jux/prod-key.crt

# Expected: ✓ Signature is valid

# 4. Document rollback reason
cat > ~/.ssh/jux/ROLLBACK-$(date +%Y%m%d-%H%M).txt << EOF
Date: $(date)
Reason: <describe reason for rollback>
Action: Reverted to previous key
Next Steps: <plan for re-attempting rotation>
EOF
```

---

## Automation

### Automated Rotation Script

```bash
#!/bin/bash
# rotate-keys.sh - Automated key rotation

set -euo pipefail

# Configuration
KEY_DIR="${HOME}/.ssh/jux"
ROTATION_DIR="${KEY_DIR}/rotation-$(date +%Y%m%d)"
BACKUP_DIR="${KEY_DIR}/backups"
KEY_TYPE="rsa"
KEY_BITS=4096
KEY_VALIDITY_DAYS=365
SUBJECT_PREFIX="CN=pytest-jux Production"

# Create directories
mkdir -p "${ROTATION_DIR}" "${BACKUP_DIR}"

# 1. Generate new key pair
echo "Generating new key pair..."
jux-keygen \
  --type "${KEY_TYPE}" \
  --bits "${KEY_BITS}" \
  --output "${ROTATION_DIR}/new-key.pem" \
  --cert \
  --subject "${SUBJECT_PREFIX} $(date +%Y-%m-%d)" \
  --days-valid "${KEY_VALIDITY_DAYS}"

# 2. Backup current key
echo "Backing up current key..."
cp "${KEY_DIR}/prod-key.pem" "${BACKUP_DIR}/prod-key-$(date +%Y%m%d).pem.backup"
cp "${KEY_DIR}/prod-key.crt" "${BACKUP_DIR}/prod-key-$(date +%Y%m%d).crt.backup"

# 3. Test new key
echo "Testing new key..."
pytest --junitxml=/tmp/rotation-test.xml \
  --jux-key "${ROTATION_DIR}/new-key.pem" \
  --jux-cert "${ROTATION_DIR}/new-key.crt"

# 4. Verify signature
jux-verify \
  -i ~/.local/share/pytest-jux/reports/*.xml \
  --cert "${ROTATION_DIR}/new-key.crt"

echo "✓ New key generated and tested successfully"
echo "Next steps:"
echo "1. Deploy new key to CI/CD: ${ROTATION_DIR}/new-key.pem"
echo "2. Monitor systems for 24-48 hours"
echo "3. Retire old key: mv ${KEY_DIR}/prod-key.pem ${KEY_DIR}/retired/"
```

**Usage**:
```bash
chmod +x rotate-keys.sh
./rotate-keys.sh
```

---

## Best Practices

### Key Rotation

1. **✅ Rotate regularly**: Don't wait for certificate expiration
2. **✅ Test first**: Always test new key before deployment
3. **✅ Gradual rollout**: Use dual-key period for production
4. **✅ Monitor closely**: Watch for issues during grace period
5. **✅ Document everything**: Keep rotation logs for audit

### Emergency Rotation

1. **✅ Act quickly**: Generate and deploy new key immediately
2. **✅ Revoke compromised key**: Mark as compromised, don't delete
3. **✅ Investigate root cause**: Understand how compromise occurred
4. **✅ Notify team**: Communicate emergency rotation to all stakeholders
5. **✅ Plan permanent rotation**: Schedule formal rotation after emergency

### Automation

1. **✅ Automate where possible**: Use scripts for repetitive steps
2. **✅ Validate automation**: Test rotation scripts in staging first
3. **✅ Keep manual override**: Allow manual intervention if needed
4. **✅ Alert on failures**: Monitor rotation scripts and alert on errors

---

## See Also

- **[Secure Key Storage](secure-key-storage.md)**: Best practices for storing keys
- **[Backup and Restore Keys](backup-restore-keys.md)**: Key backup procedures
- **[Multi-Environment Configuration](multi-environment-config.md)**: Environment-specific configuration
- **[CI/CD Deployment Guide](ci-cd-deployment.md)**: CI/CD integration patterns

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
