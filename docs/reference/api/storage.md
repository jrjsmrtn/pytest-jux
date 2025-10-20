# storage API Reference

**Module**: `pytest_jux.storage`
**Purpose**: XDG-compliant local storage and caching for test reports
**Version**: 0.1.9+

---

## Overview

The `storage` module provides XDG-compliant local storage and caching for signed JUnit XML test reports. It implements duplicate detection, metadata persistence, and cache management.

### Purpose

- **Local Storage**: Store signed reports in XDG-compliant directories
- **Duplicate Detection**: Prevent storing duplicate reports (canonical hash)
- **Metadata Persistence**: Save and retrieve environment metadata
- **Cache Management**: Cleanup old reports, show statistics, purge cache

### When to Use This Module

- Storing signed test reports locally before publishing
- Caching reports for offline access
- Implementing duplicate detection in plugins
- Managing local report storage and cleanup

### Related Modules

- **`canonicalizer`**: Used for computing canonical hashes (duplicate detection)
- **`metadata`**: Captures metadata saved with reports
- **`plugin`**: Uses storage for caching (future)

---

## Module Documentation

```{eval-rst}
.. automodule:: pytest_jux.storage
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

---

## Classes

### `ReportStorage`

Main storage class for managing local test reports.

```{eval-rst}
.. autoclass:: pytest_jux.storage.ReportStorage
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

**Example**:
```python
from pathlib import Path
from pytest_jux.storage import ReportStorage
from pytest_jux.metadata import EnvironmentMetadata

# Initialize storage (default XDG location)
storage = ReportStorage()

# Store a signed report
report_xml = Path("test-results/junit-signed.xml").read_bytes()
metadata = EnvironmentMetadata.collect()

report_hash = storage.store_report(
    report_xml=report_xml,
    metadata=metadata
)
print(f"Stored report: {report_hash}")

# Retrieve report
retrieved_xml = storage.get_report(report_hash)
retrieved_metadata = storage.get_metadata(report_hash)
```

---

### `StorageError`

Exception raised for storage-related errors.

```{eval-rst}
.. autoclass:: pytest_jux.storage.StorageError
   :members:
   :show-inheritance:
```

---

## Functions

### `get_default_storage_path()`

Get default XDG-compliant storage path.

```{eval-rst}
.. autofunction:: pytest_jux.storage.get_default_storage_path
```

**Example**:
```python
from pytest_jux.storage import get_default_storage_path

# Get default storage path
storage_path = get_default_storage_path()
print(f"Storage: {storage_path}")
# Output: /Users/username/.local/share/pytest-jux
```

---

## XDG Directory Structure

The storage module follows XDG Base Directory Specification:

```
~/.local/share/pytest-jux/       # XDG_DATA_HOME/pytest-jux
├── reports/                      # Signed test reports
│   ├── <hash1>.xml              # Report file (canonical hash as filename)
│   ├── <hash2>.xml
│   └── ...
└── metadata/                     # Environment metadata
    ├── <hash1>.json             # Metadata for each report
    ├── <hash2>.json
    └── ...
```

### Storage Locations

- **Data Directory**: `$XDG_DATA_HOME/pytest-jux` (default: `~/.local/share/pytest-jux`)
- **Cache Directory**: `$XDG_CACHE_HOME/pytest-jux` (default: `~/.cache/pytest-jux`)
- **Config Directory**: `$XDG_CONFIG_HOME/pytest-jux` (default: `~/.config/pytest-jux`)

### Custom Storage Path

```python
from pathlib import Path
from pytest_jux.storage import ReportStorage

# Use custom storage path
custom_path = Path("/var/lib/jux-reports")
storage = ReportStorage(storage_path=custom_path)
```

---

## Usage Examples

### Storing Reports

```python
from pathlib import Path
from pytest_jux.storage import ReportStorage
from pytest_jux.metadata import EnvironmentMetadata

# Initialize storage
storage = ReportStorage()

# Read signed report
report_xml = Path("junit-signed.xml").read_bytes()

# Collect metadata
metadata = EnvironmentMetadata.collect()

# Store report
report_hash = storage.store_report(
    report_xml=report_xml,
    metadata=metadata
)

print(f"Stored: {report_hash}")
```

### Duplicate Detection

```python
from pytest_jux.storage import ReportStorage
from pytest_jux.metadata import EnvironmentMetadata

storage = ReportStorage()
report_xml = Path("junit-signed.xml").read_bytes()
metadata = EnvironmentMetadata.collect()

# First store - succeeds
hash1 = storage.store_report(report_xml, metadata)
print(f"First store: {hash1}")

# Second store - duplicate detected
hash2 = storage.store_report(report_xml, metadata)
print(f"Second store: {hash2}")
print(f"Same hash: {hash1 == hash2}")  # True - duplicate

# Storage only keeps one copy (deduplication)
```

### Retrieving Reports

```python
from pytest_jux.storage import ReportStorage, StorageError

storage = ReportStorage()

try:
    # Retrieve report by hash
    report_xml = storage.get_report("abc123...")
    metadata = storage.get_metadata("abc123...")

    print(f"Report size: {len(report_xml)} bytes")
    print(f"Hostname: {metadata.hostname}")
    print(f"Timestamp: {metadata.timestamp}")

except StorageError as e:
    print(f"Report not found: {e}")
```

### Listing Reports

```python
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# List all cached reports
reports = storage.list_reports()

print(f"Total reports: {len(reports)}")
for report_hash in reports:
    metadata = storage.get_metadata(report_hash)
    print(f"  {report_hash[:16]}... - {metadata.timestamp}")
```

### Cache Statistics

```python
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# Get cache statistics
stats = storage.get_stats()

print(f"Total reports: {stats['total_reports']}")
print(f"Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
print(f"Oldest report: {stats['oldest_timestamp']}")
print(f"Newest report: {stats['newest_timestamp']}")
```

### Cache Cleanup

```python
from datetime import timedelta
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# Clean up reports older than 30 days
days_old = 30
removed_count = storage.cleanup_old_reports(days=days_old)

print(f"Removed {removed_count} reports older than {days_old} days")
```

### Purging Cache

```python
from pytest_jux.storage import ReportStorage

storage = ReportStorage()

# Purge all cached reports
purged_count = storage.purge()

print(f"Purged {purged_count} reports from cache")
```

---

## Duplicate Detection

The storage module uses **canonical hashing** for duplicate detection:

1. **Canonicalize XML**: Apply C14N to normalize XML
2. **Compute SHA-256**: Hash the canonical form
3. **Use as Key**: Hash becomes filename (`<hash>.xml`)

This ensures:
- ✅ Semantically identical reports produce same hash
- ✅ Only one copy stored (deduplication)
- ✅ Fast duplicate lookup (O(1) by hash)

**Example**:
```python
from pytest_jux.canonicalizer import load_xml, compute_canonical_hash
from pytest_jux.storage import ReportStorage

# Two reports with same content, different formatting
report1 = load_xml("report1.xml")
report2 = load_xml("report2.xml")

# Compute canonical hashes
hash1 = compute_canonical_hash(report1)
hash2 = compute_canonical_hash(report2)

if hash1 == hash2:
    print("Reports are duplicates")
    # Storage will only keep one copy
```

---

## Error Handling

### StorageError

Raised for storage-related errors:

| Error Scenario | Exception | Message |
|----------------|-----------|---------|
| Report not found | `StorageError` | `Report not found: <hash>` |
| Metadata not found | `StorageError` | `Metadata not found: <hash>` |
| Permission denied | `PermissionError` | `Permission denied: <path>` |
| Disk full | `OSError` | `No space left on device` |

**Example**:
```python
from pytest_jux.storage import ReportStorage, StorageError

storage = ReportStorage()

try:
    report = storage.get_report("nonexistent-hash")
except StorageError as e:
    print(f"Error: {e}")
    # Output: Error: Report not found: nonexistent-hash
```

---

## Thread Safety

The `ReportStorage` class is **thread-safe** for read operations:
- ✅ Safe to call `get_report()` concurrently
- ✅ Safe to call `list_reports()` concurrently
- ⚠️ Write operations (`store_report()`) should be synchronized

For concurrent writes, use external locking:
```python
import threading
from pytest_jux.storage import ReportStorage

storage = ReportStorage()
lock = threading.Lock()

def store_report_thread_safe(report_xml, metadata):
    with lock:
        return storage.store_report(report_xml, metadata)
```

---

## Performance

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `store_report()` | O(n) | 10-50ms |
| `get_report()` | O(1) | <1ms |
| `list_reports()` | O(m) | <10ms |
| `cleanup_old_reports()` | O(m) | 10-100ms |

Where:
- n = Report XML size
- m = Number of cached reports

---

## Storage Modes

The storage module supports different modes (configured via `storage_mode` in config):

### 1. Auto Mode (Default)
```python
storage = ReportStorage()  # Automatic deduplication
storage.store_report(report_xml, metadata)
```

### 2. Disabled Mode
```python
# Storage disabled (no caching)
# Use this for CI/CD where reports are published immediately
storage = None  # Don't use storage at all
```

### 3. Custom Path Mode
```python
from pathlib import Path

# Use custom directory
custom_storage = ReportStorage(storage_path=Path("/opt/jux/reports"))
```

---

## CLI Integration

The storage module is used by the `jux-cache` CLI command:

```bash
# Show cache statistics
jux-cache stats

# List all cached reports
jux-cache list

# Show specific report
jux-cache show <hash>

# Cleanup old reports
jux-cache clean --days 30

# Purge all reports
jux-cache purge
```

See [jux-cache CLI reference](../cli/index.md#jux-cache) for details.

---

## See Also

- **[canonicalizer API](canonicalizer.md)**: Canonical hashing (used for duplicate detection)
- **[metadata API](metadata.md)**: Environment metadata (stored with reports)
- **[jux-cache CLI](../cli/index.md#jux-cache)**: Cache management command
- **[XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)**: XDG standard

---

**Module Path**: `pytest_jux.storage`
**Source Code**: `pytest_jux/storage.py`
**Tests**: `tests/test_storage.py`
**Last Updated**: 2025-10-20
