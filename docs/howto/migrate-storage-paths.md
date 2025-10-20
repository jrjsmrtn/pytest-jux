# How to Migrate Storage Paths

**Move pytest-jux storage to a new location**

---

## Overview

You may need to migrate pytest-jux storage locations for:
- **Disk Space**: Moving to larger partition
- **Performance**: Moving to faster storage (SSD, NVMe)
- **Organization**: Consolidating with other project data
- **Compliance**: Meeting data residency requirements
- **Cleanup**: Reorganizing directory structure

This guide covers safe migration procedures without losing data.

---

## Understanding Storage Structure

### Default Storage Locations (XDG-Compliant)

**Linux/macOS**:
```
~/.local/share/pytest-jux/        # Data directory (XDG_DATA_HOME)
├── reports/                       # Signed XML reports
│   └── <canonical-hash>.xml
├── metadata/                      # Report metadata
│   └── <canonical-hash>.json
└── storage.db                     # Storage index (future)

~/.config/pytest-jux/              # Configuration directory (XDG_CONFIG_HOME)
└── config.toml                    # Configuration file

~/.cache/pytest-jux/               # Cache directory (XDG_CACHE_HOME)
└── temp/                          # Temporary files
```

**Windows**:
```
%LOCALAPPDATA%\pytest-jux\         # Data directory
├── reports\
├── metadata\
└── storage.db

%APPDATA%\pytest-jux\              # Configuration
└── config.toml
```

### Custom Storage Paths

**Environment Variables**:
```bash
export JUX_STORAGE_BASE_PATH="/custom/storage/path"
export JUX_CONFIG_PATH="/custom/config/path"
```

**Configuration File** (`config.toml`):
```toml
[jux]
storage_base_path = "/custom/storage/path"
```

---

## Migration Scenarios

### Scenario 1: Migrate to Larger Disk

**Problem**: Running out of space on home partition

**Solution**: Move to `/mnt/data` partition

```bash
# 1. Check current storage usage
jux-cache stats

# Expected output:
# Storage path: /home/you/.local/share/pytest-jux
# Total reports: 1,234
# Total size: 456 MB
# Oldest: 2025-08-01
# Newest: 2025-10-20

# 2. Stop any running pytest processes
pkill -f pytest

# 3. Create new storage directory
sudo mkdir -p /mnt/data/pytest-jux/{reports,metadata}
sudo chown -R $USER:$USER /mnt/data/pytest-jux
chmod 755 /mnt/data/pytest-jux
chmod 755 /mnt/data/pytest-jux/{reports,metadata}

# 4. Copy data to new location (preserving timestamps)
rsync -av --progress \
  ~/.local/share/pytest-jux/ \
  /mnt/data/pytest-jux/

# 5. Verify copy completed successfully
diff -r ~/.local/share/pytest-jux/ /mnt/data/pytest-jux/

# Expected: No differences

# 6. Update configuration
cat >> ~/.config/pytest-jux/config.toml << EOF

# Storage migration: $(date)
[jux]
storage_base_path = "/mnt/data/pytest-jux"
EOF

# 7. Test new storage location
pytest --junitxml=migration-test.xml --jux-key ~/.ssh/jux/dev-key.pem

# 8. Verify storage path
jux-cache stats

# Expected: Storage path: /mnt/data/pytest-jux

# 9. Backup old storage (keep for 30 days)
mv ~/.local/share/pytest-jux ~/.local/share/pytest-jux.backup-$(date +%Y%m%d)

# 10. After 30 days, remove backup
# rm -rf ~/.local/share/pytest-jux.backup-YYYYMMDD
```

### Scenario 2: Migrate to Network Storage

**Problem**: Need centralized storage for team

**Solution**: Move to NFS/CIFS share

```bash
# 1. Mount network share
sudo mkdir -p /mnt/nfs/pytest-jux
sudo mount -t nfs nfs-server:/exports/pytest-jux /mnt/nfs/pytest-jux

# 2. Verify write permissions
touch /mnt/nfs/pytest-jux/test-write && rm /mnt/nfs/pytest-jux/test-write

# 3. Copy data
rsync -av --progress \
  ~/.local/share/pytest-jux/ \
  /mnt/nfs/pytest-jux/

# 4. Update configuration
cat >> ~/.config/pytest-jux/config.toml << EOF

[jux]
storage_base_path = "/mnt/nfs/pytest-jux"
EOF

# 5. Add to /etc/fstab for persistent mount
echo "nfs-server:/exports/pytest-jux /mnt/nfs/pytest-jux nfs defaults 0 0" | sudo tee -a /etc/fstab
```

**Warning**: Network storage may have slower I/O. Consider using local cache with periodic sync.

### Scenario 3: Migrate to Cloud Storage

**Problem**: Need durable, scalable storage

**Solution**: Use S3-compatible storage with local cache

**Note**: pytest-jux currently requires local filesystem. Use tools like `s3fs` or `goofys` to mount S3 as filesystem.

```bash
# 1. Install s3fs
sudo apt-get install s3fs  # Debian/Ubuntu
# or
brew install s3fs  # macOS

# 2. Configure S3 credentials
echo "ACCESS_KEY:SECRET_KEY" > ~/.passwd-s3fs
chmod 600 ~/.passwd-s3fs

# 3. Mount S3 bucket
mkdir -p /mnt/s3/pytest-jux
s3fs pytest-jux-reports /mnt/s3/pytest-jux \
  -o passwd_file=~/.passwd-s3fs \
  -o use_cache=/tmp/s3fs-cache \
  -o allow_other

# 4. Migrate data
rsync -av --progress \
  ~/.local/share/pytest-jux/ \
  /mnt/s3/pytest-jux/

# 5. Update configuration
cat >> ~/.config/pytest-jux/config.toml << EOF

[jux]
storage_base_path = "/mnt/s3/pytest-jux"
EOF
```

**Performance Tip**: Use local cache with periodic S3 sync:
```bash
# Keep local storage, sync to S3 hourly
0 * * * * aws s3 sync ~/.local/share/pytest-jux/ s3://pytest-jux-reports/
```

---

## Migration Checklist

### Pre-Migration

- [ ] **Backup current data**: Create full backup before migration
- [ ] **Check disk space**: Ensure destination has sufficient space
- [ ] **Test destination**: Verify write permissions and I/O performance
- [ ] **Stop processes**: Stop all pytest processes using storage
- [ ] **Document**: Record current storage path and configuration

### During Migration

- [ ] **Copy data**: Use `rsync` or `cp -a` to preserve metadata
- [ ] **Verify integrity**: Compare checksums or use `diff -r`
- [ ] **Update configuration**: Set new storage path in config.toml
- [ ] **Test**: Run pytest and verify reports stored correctly
- [ ] **Check cache stats**: Verify storage path and report count

### Post-Migration

- [ ] **Keep backup**: Retain old storage for 30 days
- [ ] **Monitor**: Watch for issues in first 24-48 hours
- [ ] **Update documentation**: Document new storage location
- [ ] **Team notification**: Inform team of new storage path
- [ ] **Remove backup**: Delete old storage after grace period

---

## Environment-Specific Migration

### Development Environment

```bash
# Simple migration for development
export JUX_STORAGE_BASE_PATH="/new/storage/path"
mkdir -p /new/storage/path/{reports,metadata}
cp -r ~/.local/share/pytest-jux/* /new/storage/path/
```

### CI/CD Environment

**GitHub Actions**:
```yaml
# .github/workflows/test.yml
env:
  JUX_STORAGE_BASE_PATH: ${{ github.workspace }}/.pytest-jux-cache

jobs:
  test:
    steps:
      - name: Create storage directory
        run: mkdir -p .pytest-jux-cache/{reports,metadata}

      - name: Run tests
        run: pytest --junitxml=junit.xml

      - name: Archive reports
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: .pytest-jux-cache/reports/
```

**GitLab CI**:
```yaml
# .gitlab-ci.yml
variables:
  JUX_STORAGE_BASE_PATH: ${CI_PROJECT_DIR}/.pytest-jux-cache

test:
  script:
    - mkdir -p .pytest-jux-cache/{reports,metadata}
    - pytest --junitxml=junit.xml
  cache:
    paths:
      - .pytest-jux-cache/
```

### Production Environment

```bash
# Use dedicated partition
sudo mkdir -p /var/lib/pytest-jux/{reports,metadata}
sudo chown ci-user:ci-user /var/lib/pytest-jux
sudo chmod 755 /var/lib/pytest-jux

# Configuration
cat > /etc/pytest-jux/config.toml << EOF
[jux]
storage_base_path = "/var/lib/pytest-jux"
EOF

# Systemd service for automatic mount (if needed)
cat > /etc/systemd/system/pytest-jux-storage.mount << EOF
[Unit]
Description=pytest-jux Storage Mount
Before=jenkins.service

[Mount]
What=/dev/sdb1
Where=/var/lib/pytest-jux
Type=ext4
Options=defaults

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable pytest-jux-storage.mount
sudo systemctl start pytest-jux-storage.mount
```

---

## Rollback Procedure

If migration causes issues:

```bash
# 1. Stop pytest processes
pkill -f pytest

# 2. Revert configuration
# Remove or comment out storage_base_path in config.toml
sed -i.bak '/storage_base_path/d' ~/.config/pytest-jux/config.toml

# 3. Restore from backup (if needed)
rm -rf ~/.local/share/pytest-jux
mv ~/.local/share/pytest-jux.backup-YYYYMMDD ~/.local/share/pytest-jux

# 4. Verify original location works
pytest --junitxml=rollback-test.xml --jux-key ~/.ssh/jux/dev-key.pem

# 5. Check storage path
jux-cache stats

# Expected: Storage path: /home/you/.local/share/pytest-jux
```

---

## Troubleshooting

### Issue: "Permission denied" after migration

**Cause**: Incorrect file/directory permissions

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:$USER /new/storage/path
chmod 755 /new/storage/path
chmod 755 /new/storage/path/{reports,metadata}
find /new/storage/path -type f -exec chmod 644 {} \;
```

### Issue: Reports not found after migration

**Cause**: Configuration not updated or data not copied

**Solution**:
```bash
# 1. Verify configuration
jux-config show | grep storage_base_path

# 2. Check data copied
ls -la /new/storage/path/reports/ | wc -l

# 3. Compare with original
ls -la ~/.local/share/pytest-jux/reports/ | wc -l

# 4. Re-copy if needed
rsync -av ~/.local/share/pytest-jux/ /new/storage/path/
```

### Issue: Slow performance after migration

**Cause**: Network storage latency or slow disk

**Solution**:
```bash
# Test I/O performance
dd if=/dev/zero of=/new/storage/path/test-io bs=1M count=100
# Compare with original location

# If network storage:
# - Use local cache with periodic sync
# - Consider local storage for active reports, archive to network
```

---

## Advanced: Multi-Tier Storage

**Strategy**: Hot storage (local SSD) + Cold storage (network/cloud)

```bash
# Hot storage (last 7 days)
[jux]
storage_base_path = "/mnt/ssd/pytest-jux"

# Archive old reports to cold storage
#!/bin/bash
# archive-old-reports.sh

HOT_STORAGE="/mnt/ssd/pytest-jux"
COLD_STORAGE="/mnt/nfs/pytest-jux-archive"
ARCHIVE_DAYS=7

# Move reports older than 7 days to cold storage
find "${HOT_STORAGE}/reports" -name "*.xml" -mtime +${ARCHIVE_DAYS} \
  -exec mv {} "${COLD_STORAGE}/reports/" \;

find "${HOT_STORAGE}/metadata" -name "*.json" -mtime +${ARCHIVE_DAYS} \
  -exec mv {} "${COLD_STORAGE}/metadata/" \;

echo "✓ Archived reports older than ${ARCHIVE_DAYS} days"
```

**Schedule with cron**:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/archive-old-reports.sh >> /var/log/archive-reports.log 2>&1
```

---

## Best Practices

### Storage Selection

1. **✅ Local SSD/NVMe**: Best performance for active storage
2. **✅ Network storage**: Good for centralized team access
3. **✅ Cloud storage**: Best for durability and scalability
4. **⚠️ Network mounted**: May have latency issues
5. **❌ Removable media**: Not recommended (unreliable)

### Migration Timing

1. **✅ Off-hours**: Migrate during low-usage periods
2. **✅ Gradual**: Test with subset before full migration
3. **✅ Reversible**: Keep backup for rollback
4. **✅ Documented**: Record migration steps and date
5. **✅ Monitored**: Watch for issues post-migration

### Performance

1. **✅ Benchmark**: Test I/O before and after
2. **✅ Cache**: Use local cache for network storage
3. **✅ Tier**: Hot (local) + Cold (network/cloud)
4. **✅ Cleanup**: Archive or delete old reports
5. **✅ Monitor**: Track storage usage and performance

---

## See Also

- **[Manage Report Cache](manage-report-cache.md)**: Cache management and cleanup
- **[Troubleshooting Guide](troubleshooting.md)**: Storage-related issues
- **[Multi-Environment Configuration](multi-environment-config.md)**: Environment-specific storage
- **[Configuration Reference](../reference/configuration.md)**: Storage configuration options

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
