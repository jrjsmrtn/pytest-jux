# How to Backup and Restore Signing Keys

**Ensure business continuity with secure key backup and recovery procedures**

---

## Overview

Key backup and recovery are critical for:
- **Business Continuity**: Prevent loss of access to signed reports
- **Disaster Recovery**: Restore operations after system failure
- **Key Rotation**: Safely retire old keys while maintaining verification capability
- **Compliance**: Meet audit and regulatory requirements

This guide covers secure backup strategies and recovery procedures.

---

## Backup Strategy

### Backup Types

| Type | Frequency | Retention | Purpose |
|------|-----------|-----------|---------|
| **Full Backup** | After key generation | Permanent | Primary recovery |
| **Incremental Backup** | After each rotation | 2-3 years | Historical verification |
| **Emergency Backup** | Before changes | 90 days | Quick rollback |
| **Offsite Backup** | Weekly/Monthly | 1 year+ | Disaster recovery |

### What to Backup

**Essential Items**:
- ✅ Private keys (`.pem`, `.key`)
- ✅ Public certificates (`.crt`, `.pem`)
- ✅ Configuration files (`config.toml`)
- ✅ Key metadata (generation date, rotation history)

**Optional Items**:
- Signed test reports (if not in version control)
- Key generation scripts
- Documentation

**Never Backup**:
- ❌ Unencrypted keys in version control
- ❌ Keys in cloud storage without encryption
- ❌ Keys in email archives

---

## Local Backup

### Encrypted File Backup

**Method 1: GPG Encryption** (Recommended)

```bash
# 1. Create backup directory
mkdir -p ~/backups/pytest-jux/$(date +%Y%m%d)
cd ~/backups/pytest-jux/$(date +%Y%m%d)

# 2. Backup and encrypt private key
gpg --symmetric --cipher-algo AES256 \
  --output prod-key.pem.gpg \
  ~/.ssh/jux/production/prod-key.pem

# Enter passphrase (store in password manager)

# 3. Backup certificate (no encryption needed)
cp ~/.ssh/jux/production/prod-cert.pem prod-cert.pem

# 4. Verify backup
gpg --decrypt prod-key.pem.gpg > /tmp/test-key.pem
diff /tmp/test-key.pem ~/.ssh/jux/production/prod-key.pem
# Expected: No differences

# Clean up
shred -u /tmp/test-key.pem

# 5. Create backup manifest
cat > MANIFEST.txt << EOF
Backup Date: $(date)
Environment: production
Private Key: prod-key.pem.gpg (AES256 encrypted)
Certificate: prod-cert.pem
Checksum (key): $(sha256sum prod-key.pem.gpg | cut -d' ' -f1)
Checksum (cert): $(sha256sum prod-cert.pem | cut -d' ' -f1)
EOF

# 6. Set permissions
chmod 600 prod-key.pem.gpg
chmod 644 prod-cert.pem MANIFEST.txt
```

**Method 2: OpenSSL Encryption**

```bash
# Backup and encrypt with OpenSSL
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in ~/.ssh/jux/production/prod-key.pem \
  -out ~/backups/pytest-jux/$(date +%Y%m%d)/prod-key.pem.enc

# Enter encryption passphrase

# Verify
openssl enc -aes-256-cbc -d -pbkdf2 \
  -in ~/backups/pytest-jux/$(date +%Y%m%d)/prod-key.pem.enc \
  -out /tmp/test-key.pem

diff /tmp/test-key.pem ~/.ssh/jux/production/prod-key.pem
shred -u /tmp/test-key.pem
```

### Tarball Backup (All Keys)

```bash
# Create encrypted tarball of all keys
tar -czf - ~/.ssh/jux | \
  gpg --symmetric --cipher-algo AES256 \
  --output ~/backups/pytest-jux-full-$(date +%Y%m%d).tar.gz.gpg

# Verify backup
gpg --decrypt ~/backups/pytest-jux-full-$(date +%Y%m%d).tar.gz.gpg | \
  tar -tzf - | head

# Expected: List of files from ~/.ssh/jux/
```

---

## Offsite Backup

### Cloud Storage (Encrypted)

#### AWS S3

```bash
# 1. Encrypt and upload to S3
gpg --symmetric --cipher-algo AES256 \
  --output /tmp/prod-key.pem.gpg \
  ~/.ssh/jux/production/prod-key.pem

aws s3 cp /tmp/prod-key.pem.gpg \
  s3://my-backups/pytest-jux/production/prod-key-$(date +%Y%m%d).pem.gpg \
  --server-side-encryption AES256

# Clean up local temp file
shred -u /tmp/prod-key.pem.gpg

# 2. Verify upload
aws s3 ls s3://my-backups/pytest-jux/production/

# 3. Set lifecycle policy (optional - auto-delete old backups)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-backups \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json:
# {
#   "Rules": [{
#     "Id": "DeleteOldKeyBackups",
#     "Status": "Enabled",
#     "Prefix": "pytest-jux/",
#     "Expiration": { "Days": 365 }
#   }]
# }
```

#### Google Cloud Storage

```bash
# Upload encrypted backup to GCS
gpg --symmetric --cipher-algo AES256 \
  --output /tmp/prod-key.pem.gpg \
  ~/.ssh/jux/production/prod-key.pem

gsutil cp /tmp/prod-key.pem.gpg \
  gs://my-backups/pytest-jux/production/prod-key-$(date +%Y%m%d).pem.gpg

shred -u /tmp/prod-key.pem.gpg

# Verify
gsutil ls gs://my-backups/pytest-jux/production/
```

#### Azure Blob Storage

```bash
# Upload to Azure Blob Storage
gpg --symmetric --cipher-algo AES256 \
  --output /tmp/prod-key.pem.gpg \
  ~/.ssh/jux/production/prod-key.pem

az storage blob upload \
  --account-name mybackups \
  --container-name pytest-jux \
  --name production/prod-key-$(date +%Y%m%d).pem.gpg \
  --file /tmp/prod-key.pem.gpg

shred -u /tmp/prod-key.pem.gpg
```

### External Drive Backup

```bash
# 1. Mount encrypted external drive
# (Assuming LUKS-encrypted drive at /dev/sdb1)
sudo cryptsetup luksOpen /dev/sdb1 backup-drive
sudo mount /dev/mapper/backup-drive /mnt/backup

# 2. Create backup
tar -czf /mnt/backup/pytest-jux-$(date +%Y%m%d).tar.gz \
  ~/.ssh/jux/

# 3. Unmount and close
sudo umount /mnt/backup
sudo cryptsetup luksClose backup-drive

# 4. Store drive in secure location (fireproof safe, bank vault, etc.)
```

---

## Automated Backup Script

```bash
#!/bin/bash
# backup-keys.sh - Automated key backup script

set -euo pipefail

# Configuration
SOURCE_DIR="${HOME}/.ssh/jux"
BACKUP_BASE_DIR="${HOME}/backups/pytest-jux"
DATE=$(date +%Y%m%d)
BACKUP_DIR="${BACKUP_BASE_DIR}/${DATE}"
S3_BUCKET="s3://my-backups/pytest-jux"
RETENTION_DAYS=365

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup each environment
for env in production staging development; do
  if [ -d "${SOURCE_DIR}/${env}" ]; then
    echo "Backing up ${env} keys..."

    # Encrypt private key
    gpg --batch --yes --symmetric --cipher-algo AES256 \
      --passphrase-file "${HOME}/.backup-passphrase" \
      --output "${BACKUP_DIR}/${env}-key.pem.gpg" \
      "${SOURCE_DIR}/${env}/${env}-key.pem"

    # Copy certificate (no encryption)
    cp "${SOURCE_DIR}/${env}/${env}-cert.pem" \
       "${BACKUP_DIR}/${env}-cert.pem"

    # Compute checksums
    sha256sum "${BACKUP_DIR}/${env}-key.pem.gpg" >> "${BACKUP_DIR}/checksums.txt"
    sha256sum "${BACKUP_DIR}/${env}-cert.pem" >> "${BACKUP_DIR}/checksums.txt"
  fi
done

# Create manifest
cat > "${BACKUP_DIR}/MANIFEST.txt" << EOF
Backup Date: $(date)
Source: ${SOURCE_DIR}
Environments: production, staging, development
Encryption: GPG AES256
Retention: ${RETENTION_DAYS} days
EOF

# Upload to S3 (if configured)
if [ -n "${S3_BUCKET}" ]; then
  echo "Uploading to S3..."
  aws s3 sync "${BACKUP_DIR}" "${S3_BUCKET}/${DATE}/" \
    --server-side-encryption AES256
fi

# Clean up old backups
find "${BACKUP_BASE_DIR}" -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} +

echo "✓ Backup complete: ${BACKUP_DIR}"
```

**Setup**:
```bash
# 1. Store GPG passphrase securely
echo "your-secure-passphrase" > ~/.backup-passphrase
chmod 600 ~/.backup-passphrase

# 2. Make script executable
chmod +x backup-keys.sh

# 3. Schedule with cron (weekly backups)
crontab -e
# Add line:
# 0 2 * * 0 /path/to/backup-keys.sh >> /var/log/key-backup.log 2>&1
```

---

## Recovery Procedures

### Scenario 1: Restore from Local Backup

**Symptom**: Production key lost due to disk failure

**Recovery Steps**:
```bash
# 1. Find latest backup
ls -lt ~/backups/pytest-jux/ | head

# Example: 20251019/

# 2. Restore from backup
cd ~/backups/pytest-jux/20251019/

# 3. Decrypt private key
gpg --decrypt prod-key.pem.gpg > /tmp/prod-key.pem
# Enter passphrase

# 4. Verify integrity
diff MANIFEST.txt <(cat << EOF
Backup Date: 2025-10-19
Environment: production
Private Key: prod-key.pem.gpg (AES256 encrypted)
Certificate: prod-cert.pem
Checksum (key): $(sha256sum prod-key.pem.gpg | cut -d' ' -f1)
Checksum (cert): $(sha256sum prod-cert.pem | cut -d' ' -f1)
EOF
)

# 5. Restore to production location
mkdir -p ~/.ssh/jux/production
mv /tmp/prod-key.pem ~/.ssh/jux/production/prod-key.pem
cp prod-cert.pem ~/.ssh/jux/production/prod-cert.pem

# 6. Set permissions
chmod 600 ~/.ssh/jux/production/prod-key.pem
chmod 644 ~/.ssh/jux/production/prod-cert.pem

# 7. Test restored key
pytest --junitxml=recovery-test.xml \
  --jux-key ~/.ssh/jux/production/prod-key.pem \
  --jux-cert ~/.ssh/jux/production/prod-cert.pem

# Expected: ✓ Tests pass, report signed

# 8. Verify signature
jux-verify \
  -i ~/.local/share/pytest-jux/reports/*.xml \
  --cert ~/.ssh/jux/production/prod-cert.pem

# Expected: ✓ Signature is valid
```

### Scenario 2: Restore from Cloud Backup

**Symptom**: All local backups lost (disaster recovery)

**Recovery Steps**:
```bash
# 1. Download from S3
mkdir -p ~/recovery/pytest-jux
aws s3 sync s3://my-backups/pytest-jux/20251019/ \
  ~/recovery/pytest-jux/

# 2. Verify checksums
cd ~/recovery/pytest-jux/
sha256sum -c checksums.txt

# Expected: All OK

# 3. Decrypt and restore (same as Scenario 1, steps 3-8)
```

### Scenario 3: Restore from Encrypted Tarball

**Symptom**: Need to restore all keys at once

**Recovery Steps**:
```bash
# 1. Decrypt tarball
gpg --decrypt ~/backups/pytest-jux-full-20251019.tar.gz.gpg | \
  tar -xzf - -C /tmp/

# 2. Verify extracted keys
ls -la /tmp/.ssh/jux/

# 3. Restore to home directory
cp -r /tmp/.ssh/jux/* ~/.ssh/jux/

# 4. Set permissions
find ~/.ssh/jux -type f -name "*.pem" -exec chmod 600 {} \;
find ~/.ssh/jux -type f -name "*.crt" -exec chmod 644 {} \;

# 5. Clean up
shred -u /tmp/.ssh/jux/**/*.pem
rm -rf /tmp/.ssh/jux
```

---

## Recovery Testing

**Regularly test recovery procedures**:

```bash
#!/bin/bash
# test-recovery.sh - Test key recovery from backup

set -euo pipefail

# 1. Create test backup
BACKUP_DIR="/tmp/recovery-test-$(date +%s)"
mkdir -p "${BACKUP_DIR}"

# Encrypt production key
gpg --symmetric --cipher-algo AES256 \
  --output "${BACKUP_DIR}/prod-key.pem.gpg" \
  ~/.ssh/jux/production/prod-key.pem

# 2. Simulate recovery
RECOVERY_DIR="/tmp/recovery-$(date +%s)"
mkdir -p "${RECOVERY_DIR}"

# Decrypt
gpg --decrypt "${BACKUP_DIR}/prod-key.pem.gpg" > "${RECOVERY_DIR}/prod-key.pem"

# 3. Test recovered key
pytest --junitxml="${RECOVERY_DIR}/test.xml" \
  --jux-key "${RECOVERY_DIR}/prod-key.pem" \
  --jux-cert ~/.ssh/jux/production/prod-cert.pem

# 4. Verify signature
jux-verify -i "${RECOVERY_DIR}/test.xml" \
  --cert ~/.ssh/jux/production/prod-cert.pem

# 5. Clean up
shred -u "${RECOVERY_DIR}/prod-key.pem"
rm -rf "${BACKUP_DIR}" "${RECOVERY_DIR}"

echo "✓ Recovery test successful"
```

**Schedule quarterly**:
```bash
# Add to cron (quarterly on Jan 1, Apr 1, Jul 1, Oct 1)
0 3 1 1,4,7,10 * /path/to/test-recovery.sh >> /var/log/recovery-test.log 2>&1
```

---

## Backup Rotation and Retention

### Retention Policy

**Recommended Retention**:
- **Last 7 days**: Daily backups (for quick recovery)
- **Last 4 weeks**: Weekly backups (for recent history)
- **Last 12 months**: Monthly backups (for audit compliance)
- **Retired keys**: Permanent backups (for signature verification)

### Automated Rotation

```bash
#!/bin/bash
# rotate-backups.sh - Backup rotation script

BACKUP_DIR="${HOME}/backups/pytest-jux"

# Keep daily backups for 7 days
find "${BACKUP_DIR}" -name "daily-*" -mtime +7 -exec rm -rf {} +

# Keep weekly backups for 28 days (4 weeks)
find "${BACKUP_DIR}" -name "weekly-*" -mtime +28 -exec rm -rf {} +

# Keep monthly backups for 365 days (1 year)
find "${BACKUP_DIR}" -name "monthly-*" -mtime +365 -exec rm -rf {} +

echo "✓ Backup rotation complete"
```

---

## Multi-Site Backup Strategy

**3-2-1 Backup Rule**:
- **3 copies** of data (1 primary + 2 backups)
- **2 different storage types** (local + cloud)
- **1 offsite backup** (geographically separate)

**Example Setup**:
```
Primary: ~/.ssh/jux/ (local filesystem)
Backup 1: ~/backups/pytest-jux/ (local encrypted backups)
Backup 2: s3://my-backups/pytest-jux/ (AWS S3 - offsite)
Backup 3: External drive (secure physical location)
```

---

## Emergency Recovery Plan

### Preparation

**Create recovery documentation**:
```markdown
# Emergency Recovery Plan

## Contact Information
- Security Team: security@example.com
- On-Call Engineer: +1-555-0123

## Backup Locations
1. Local: ~/backups/pytest-jux/
2. Cloud: s3://my-backups/pytest-jux/
3. External Drive: Stored in safe (location: office safe)

## Recovery Steps
1. Identify latest backup
2. Decrypt backup
3. Restore keys
4. Test keys
5. Update CI/CD secrets
6. Verify all systems

## Passphrase Storage
- GPG Passphrase: 1Password vault "Emergency Recovery"
- Cloud Access: AWS IAM role "BackupRecovery"

## Recovery Time Objective (RTO)
- Local recovery: < 30 minutes
- Cloud recovery: < 2 hours
- Full disaster recovery: < 4 hours
```

### Recovery Drill

**Quarterly drill procedure**:
1. Simulate key loss (rename production key)
2. Restore from backup following documented procedure
3. Verify restored key works
4. Document any issues or improvements
5. Update recovery plan if needed
6. Restore original key

---

## Backup Checklist

### Daily/Weekly Backup

- [ ] **Automated backup** runs successfully
- [ ] **Backup logs** reviewed for errors
- [ ] **Checksums** computed and verified
- [ ] **Cloud upload** completed (if configured)
- [ ] **Local backup** retained per policy

### Monthly Review

- [ ] **Test recovery** from latest backup
- [ ] **Verify checksums** of stored backups
- [ ] **Check expiration** of certificates
- [ ] **Review retention** policy compliance
- [ ] **Update documentation** if procedures changed

### Quarterly Tasks

- [ ] **Full recovery drill** completed successfully
- [ ] **Offsite backup** verified accessible
- [ ] **Passphrase rotation** (if using static passphrases)
- [ ] **Backup location** security audit
- [ ] **Recovery documentation** updated

---

## See Also

- **[Rotate Signing Keys](rotate-signing-keys.md)**: Key rotation procedures
- **[Secure Key Storage](secure-key-storage.md)**: Secure storage best practices
- **[Troubleshooting Guide](troubleshooting.md)**: Recovery from key issues
- **[CI/CD Deployment Guide](ci-cd-deployment.md)**: CI/CD integration

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
