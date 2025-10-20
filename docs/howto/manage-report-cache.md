# How to Manage Report Cache

**Optimize storage usage and maintain report archives**

---

## Overview

pytest-jux stores signed test reports locally for:
- **Quick verification**: Access recent reports without re-running tests
- **Duplicate detection**: Prevent submitting duplicate reports to API
- **Historical analysis**: Compare test results over time
- **Offline access**: View reports when API is unavailable

This guide covers cache management strategies to balance storage usage with data retention needs.

---

## Understanding Report Cache

### Cache Structure

```
~/.local/share/pytest-jux/
├── reports/                           # Signed XML reports
│   ├── a1b2c3d4...e5f6.xml           # Report (canonical hash filename)
│   ├── f7e8d9c0...1a2b.xml
│   └── ...
├── metadata/                          # Report metadata
│   ├── a1b2c3d4...e5f6.json          # Metadata (matches report hash)
│   ├── f7e8d9c0...1a2b.json
│   └── ...
└── storage.db                         # Storage index (future feature)
```

### Metadata Contents

```json
{
  "canonical_hash": "a1b2c3d4e5f6789...",
  "signed": true,
  "timestamp": "2025-10-20T14:30:00Z",
  "environment": {
    "hostname": "dev-machine.local",
    "platform": "Darwin-23.5.0-arm64",
    "python_version": "3.11.14",
    "pytest_version": "8.0.0"
  },
  "test_results": {
    "total": 45,
    "passed": 43,
    "failed": 2,
    "errors": 0,
    "skipped": 0
  },
  "file_size": 12345,
  "storage_path": "/Users/you/.local/share/pytest-jux/reports/a1b2c3d4...xml"
}
```

---

## Cache Management Commands

### View Cache Statistics

```bash
# Show cache overview
jux-cache stats

# Expected output:
# Storage Path: /Users/you/.local/share/pytest-jux
# Total Reports: 1,234
# Total Size: 456.7 MB
# Oldest Report: 2025-08-01 10:30:00
# Newest Report: 2025-10-20 14:30:00
# Average Report Size: 370 KB
```

### List Cached Reports

```bash
# List all reports (most recent first)
jux-cache list

# List with details
jux-cache list --verbose

# Expected output:
# a1b2c3d4e5f6  2025-10-20 14:30:00  45 tests  43 passed  2 failed  signed
# f7e8d9c01a2b  2025-10-20 10:15:00  32 tests  32 passed  0 failed  signed
# ...

# List reports from specific date range
jux-cache list --since 2025-10-01 --until 2025-10-20

# List failed test reports
jux-cache list --failed-only
```

### Show Specific Report

```bash
# Show report details
jux-cache show a1b2c3d4e5f6

# Expected output:
# Canonical Hash: a1b2c3d4e5f6789abcdef...
# Timestamp: 2025-10-20 14:30:00
# Signed: Yes
# Tests: 45 total, 43 passed, 2 failed
# Environment: dev-machine.local (Darwin-23.5.0-arm64)
# Python: 3.11.14
# pytest: 8.0.0
# File: /Users/you/.local/share/pytest-jux/reports/a1b2c3d4...xml
# Size: 12.3 KB

# Show report XML content
jux-cache show a1b2c3d4e5f6 --xml
```

---

## Cache Cleanup Strategies

### Strategy 1: Age-Based Cleanup

**Remove reports older than N days**:

```bash
# Remove reports older than 30 days
jux-cache clean --days 30

# Expected output:
# Analyzing cache...
# Found 45 reports older than 30 days (12.5 MB)
# Remove these reports? [y/N]: y
# Removing reports...
# ✓ Removed 45 reports (12.5 MB freed)

# Dry run (show what would be removed)
jux-cache clean --days 30 --dry-run

# Expected: List of reports to be removed, but doesn't delete
```

**Automate with cron**:
```bash
# Daily cleanup (keep last 30 days)
0 2 * * * jux-cache clean --days 30 --yes >> /var/log/jux-cache-clean.log 2>&1
```

### Strategy 2: Size-Based Cleanup

**Keep cache under N MB**:

```bash
# Remove oldest reports until cache is under 100 MB
jux-cache clean --max-size 100MB

# Expected output:
# Current cache size: 456.7 MB
# Target size: 100 MB
# Will remove 235 oldest reports (356.7 MB)
# Proceed? [y/N]: y
# ✓ Removed 235 reports
# ✓ Cache size: 100.0 MB

# Keep cache under 1 GB
jux-cache clean --max-size 1GB
```

### Strategy 3: Count-Based Cleanup

**Keep only N most recent reports**:

```bash
# Keep only last 100 reports
jux-cache clean --keep-last 100

# Expected output:
# Total reports: 1,234
# Will remove 1,134 oldest reports
# Proceed? [y/N]: y
# ✓ Removed 1,134 reports
# ✓ Retained 100 most recent reports
```

### Strategy 4: Selective Cleanup

**Remove failed/passed reports selectively**:

```bash
# Remove all reports with no failures (keep only failed reports)
jux-cache clean --passed-only

# Remove all failed reports (keep only passing reports)
jux-cache clean --failed-only

# Remove reports from specific environment
jux-cache clean --environment development
```

### Strategy 5: Complete Purge

**Remove all cached reports**:

```bash
# DESTRUCTIVE: Remove all reports
jux-cache purge

# Expected output:
# WARNING: This will delete ALL cached reports!
# Total reports: 1,234 (456.7 MB)
# Type 'DELETE ALL' to confirm: DELETE ALL
# ✓ Purged all reports
# ✓ Cache is now empty

# Force purge (no confirmation)
jux-cache purge --yes --force
```

---

## Archive Strategies

### Archive to External Storage

**Before cleanup, archive old reports**:

```bash
#!/bin/bash
# archive-reports.sh - Archive old reports before cleanup

CACHE_DIR="${HOME}/.local/share/pytest-jux"
ARCHIVE_DIR="/mnt/backup/pytest-jux-archive"
ARCHIVE_DAYS=30

# Create archive directory
mkdir -p "${ARCHIVE_DIR}/reports" "${ARCHIVE_DIR}/metadata"

# Find reports older than 30 days
find "${CACHE_DIR}/reports" -name "*.xml" -mtime +${ARCHIVE_DAYS} | while read report; do
  hash=$(basename "$report" .xml)

  # Copy report and metadata to archive
  cp "$report" "${ARCHIVE_DIR}/reports/"
  cp "${CACHE_DIR}/metadata/${hash}.json" "${ARCHIVE_DIR}/metadata/"
done

# Create archive tarball
cd "${ARCHIVE_DIR}"
tar -czf "archive-$(date +%Y%m%d).tar.gz" reports/ metadata/

# Upload to cloud (optional)
aws s3 cp "archive-$(date +%Y%m%d).tar.gz" \
  s3://my-backups/pytest-jux-archives/

# Clean up archive files (keep tarball)
rm -rf reports/ metadata/

echo "✓ Archived reports older than ${ARCHIVE_DAYS} days"

# Now clean cache
jux-cache clean --days ${ARCHIVE_DAYS} --yes
```

**Schedule with cron**:
```bash
# Monthly archival (first day of month at 1 AM)
0 1 1 * * /path/to/archive-reports.sh >> /var/log/archive-reports.log 2>&1
```

### Compress Old Reports

**Compress reports to save space**:

```bash
#!/bin/bash
# compress-old-reports.sh - Compress old reports in-place

CACHE_DIR="${HOME}/.local/share/pytest-jux/reports"
COMPRESS_DAYS=7

# Find reports older than 7 days and compress
find "${CACHE_DIR}" -name "*.xml" -mtime +${COMPRESS_DAYS} ! -name "*.xml.gz" | while read report; do
  gzip "$report"
  echo "Compressed: $(basename $report)"
done

echo "✓ Compressed reports older than ${COMPRESS_DAYS} days"
```

**Note**: Compressed reports require decompression before use. Consider archiving to external storage instead.

---

## Backup Cached Reports

### Full Cache Backup

```bash
# Backup entire cache
tar -czf ~/backups/pytest-jux-cache-$(date +%Y%m%d).tar.gz \
  ~/.local/share/pytest-jux/

# Verify backup
tar -tzf ~/backups/pytest-jux-cache-$(date +%Y%m%d).tar.gz | head

# Restore from backup
tar -xzf ~/backups/pytest-jux-cache-20251020.tar.gz \
  -C ~/.local/share/
```

### Incremental Backup

```bash
# Backup only new/modified reports (since last backup)
rsync -av --progress \
  --exclude='*.tmp' \
  ~/.local/share/pytest-jux/ \
  /mnt/backup/pytest-jux/

# Sync to cloud
aws s3 sync ~/.local/share/pytest-jux/ \
  s3://my-backups/pytest-jux/ \
  --storage-class STANDARD_IA
```

### Selective Backup

```bash
# Backup only failed test reports
jux-cache list --failed-only --format paths | while read report; do
  cp "$report" ~/backups/failed-reports/
done

# Backup reports from specific date range
jux-cache list --since 2025-10-01 --until 2025-10-20 --format paths | \
  xargs -I {} cp {} ~/backups/october-2025/
```

---

## Restore Cached Reports

### Restore from Full Backup

```bash
# 1. Stop pytest processes
pkill -f pytest

# 2. Backup current cache (just in case)
mv ~/.local/share/pytest-jux ~/.local/share/pytest-jux.old

# 3. Restore from backup
tar -xzf ~/backups/pytest-jux-cache-20251020.tar.gz -C ~/

# 4. Verify restored cache
jux-cache stats

# Expected: Report count matches backup

# 5. Test access
jux-cache list | head

# 6. Remove old backup after verification
rm -rf ~/.local/share/pytest-jux.old
```

### Restore from Cloud

```bash
# Restore from S3
aws s3 sync s3://my-backups/pytest-jux/ \
  ~/.local/share/pytest-jux/

# Verify
jux-cache stats
```

---

## Automated Cache Management

### Retention Policy Script

```bash
#!/bin/bash
# cache-retention-policy.sh - Automated cache management

set -euo pipefail

# Configuration
CACHE_DIR="${HOME}/.local/share/pytest-jux"
KEEP_DAYS_HOT=7        # Keep last 7 days locally
KEEP_DAYS_WARM=30      # Archive 7-30 days old
MAX_CACHE_SIZE="500MB" # Maximum cache size

# 1. Archive reports 7-30 days old
echo "Archiving warm reports..."
find "${CACHE_DIR}/reports" -name "*.xml" -mtime +${KEEP_DAYS_HOT} -mtime -${KEEP_DAYS_WARM} | \
  while read report; do
    hash=$(basename "$report" .xml)
    # Archive to cloud
    aws s3 cp "$report" "s3://my-backups/pytest-jux-warm/${hash}.xml"
    aws s3 cp "${CACHE_DIR}/metadata/${hash}.json" "s3://my-backups/pytest-jux-warm/${hash}.json"
  done

# 2. Remove reports older than 30 days
echo "Cleaning old reports..."
jux-cache clean --days ${KEEP_DAYS_WARM} --yes

# 3. Enforce maximum cache size
echo "Enforcing cache size limit..."
jux-cache clean --max-size ${MAX_CACHE_SIZE} --yes

# 4. Generate statistics
echo "Cache statistics:"
jux-cache stats

echo "✓ Cache management complete"
```

**Schedule daily**:
```bash
# Daily at 3 AM
0 3 * * * /path/to/cache-retention-policy.sh >> /var/log/cache-retention.log 2>&1
```

---

## Monitoring and Alerts

### Disk Usage Monitoring

```bash
#!/bin/bash
# monitor-cache-size.sh - Alert when cache exceeds threshold

CACHE_DIR="${HOME}/.local/share/pytest-jux"
THRESHOLD_MB=1000  # Alert if cache > 1 GB
ALERT_EMAIL="admin@example.com"

# Get cache size in MB
CACHE_SIZE_MB=$(du -sm "${CACHE_DIR}" | cut -f1)

if [ ${CACHE_SIZE_MB} -gt ${THRESHOLD_MB} ]; then
  echo "WARNING: pytest-jux cache is ${CACHE_SIZE_MB} MB (threshold: ${THRESHOLD_MB} MB)" | \
    mail -s "pytest-jux Cache Size Alert" ${ALERT_EMAIL}

  # Auto-cleanup (optional)
  # jux-cache clean --max-size ${THRESHOLD_MB}MB --yes
fi
```

### Cache Health Check

```bash
#!/bin/bash
# cache-health-check.sh - Verify cache integrity

CACHE_DIR="${HOME}/.local/share/pytest-jux"
ERRORS=0

# Check for orphaned metadata (metadata without corresponding report)
for metadata in "${CACHE_DIR}"/metadata/*.json; do
  hash=$(basename "$metadata" .json)
  report="${CACHE_DIR}/reports/${hash}.xml"

  if [ ! -f "$report" ]; then
    echo "ERROR: Orphaned metadata: $metadata"
    ((ERRORS++))
    # Fix: Remove orphaned metadata
    # rm "$metadata"
  fi
done

# Check for orphaned reports (reports without metadata)
for report in "${CACHE_DIR}"/reports/*.xml; do
  hash=$(basename "$report" .xml)
  metadata="${CACHE_DIR}/metadata/${hash}.json"

  if [ ! -f "$metadata" ]; then
    echo "ERROR: Missing metadata for: $report"
    ((ERRORS++))
    # Fix: Regenerate metadata
    # jux-inspect -i "$report" --json > "$metadata"
  fi
done

if [ ${ERRORS} -eq 0 ]; then
  echo "✓ Cache health check passed"
else
  echo "✗ Cache health check found ${ERRORS} errors"
  exit 1
fi
```

---

## Best Practices

### Cache Management

1. **✅ Regular cleanup**: Run automated cleanup weekly/monthly
2. **✅ Archive before delete**: Save old reports before removal
3. **✅ Monitor size**: Alert when cache exceeds threshold
4. **✅ Retention policy**: Define and enforce clear retention rules
5. **✅ Backup critical reports**: Archive failed tests and releases

### Storage Optimization

1. **✅ Hot/Warm/Cold tiers**: Local (7 days), Archive (30 days), Cloud (1 year+)
2. **✅ Compress archives**: Use gzip for long-term storage
3. **✅ Deduplicate**: Remove duplicate reports (same canonical hash)
4. **✅ Offload to cloud**: Use cloud storage for archives
5. **✅ Monitor growth**: Track cache growth rate

### Performance

1. **✅ Fast local storage**: Use SSD for cache
2. **✅ Limit cache size**: Prevent unbounded growth
3. **✅ Index reports**: Use storage.db for fast lookups (future)
4. **✅ Cleanup during off-hours**: Run cleanup at night
5. **✅ Incremental operations**: Avoid processing entire cache at once

---

## Troubleshooting

### Issue: Cache size growing too fast

**Solution**:
```bash
# 1. Check cache growth
jux-cache stats

# 2. Identify large reports
find ~/.local/share/pytest-jux/reports -type f -size +1M -exec ls -lh {} \;

# 3. Reduce report size (if possible)
# - Disable verbose output in tests
# - Limit captured stdout/stderr

# 4. Implement aggressive cleanup
jux-cache clean --days 7 --yes
```

### Issue: Orphaned files in cache

**Solution**:
```bash
# Run health check
./cache-health-check.sh

# Remove orphaned metadata
find ~/.local/share/pytest-jux/metadata -name "*.json" | while read meta; do
  hash=$(basename "$meta" .json)
  [ ! -f "~/.local/share/pytest-jux/reports/${hash}.xml" ] && rm "$meta"
done

# Regenerate missing metadata
find ~/.local/share/pytest-jux/reports -name "*.xml" | while read report; do
  hash=$(basename "$report" .xml)
  [ ! -f "~/.local/share/pytest-jux/metadata/${hash}.json" ] && \
    jux-inspect -i "$report" --json > "~/.local/share/pytest-jux/metadata/${hash}.json"
done
```

---

## See Also

- **[Migrate Storage Paths](migrate-storage-paths.md)**: Moving cache to new location
- **[Configuration Reference](../reference/configuration.md)**: Storage configuration options
- **[Troubleshooting Guide](troubleshooting.md)**: Storage-related issues
- **[CLI Reference: jux-cache](../reference/cli/index.md#jux-cache)**: Cache command reference

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
