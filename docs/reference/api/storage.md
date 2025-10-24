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
- **Cache Management**: Cleanup old reports, show statistics, purge cache

**Note**: As of v0.3.0, environment metadata is embedded in JUnit XML `<properties>` elements and cryptographically signed with the report. There are no separate JSON sidecar files.

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

# Initialize storage (default XDG location)
storage = ReportStorage()

# Store a signed report (metadata embedded in XML)
report_xml = Path("test-results/junit-signed.xml").read_bytes()

report_hash = storage.store_report(
    xml_content=report_xml,
    canonical_hash="sha256:abc123..."
)
print(f"Stored report: {report_hash}")

# Retrieve report
retrieved_xml = storage.get_report(report_hash)

# Metadata is embedded in the XML <properties> elements
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
├── reports/                      # Signed test reports with embedded metadata
│   ├── <hash1>.xml              # Report file (canonical hash as filename)
│   ├── <hash2>.xml
│   └── ...
└── queue/                        # Queued reports (waiting for publish)
    ├── <hash1>.xml
    └── ...
```

**Note (v0.3.0+)**: The `metadata/` directory is no longer used. All metadata is embedded in XML `<properties>` elements and cryptographically signed.

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
from pytest_jux.canonicalizer import compute_canonical_hash, load_xml

# Initialize storage
storage = ReportStorage()

# Read signed report
report_xml = Path("junit-signed.xml").read_bytes()

# Compute canonical hash for duplicate detection
root = load_xml("junit-signed.xml")
canonical_hash = compute_canonical_hash(root)

# Store report (metadata embedded in XML)
storage.store_report(
    xml_content=report_xml,
    canonical_hash=canonical_hash
)

print(f"Stored: {canonical_hash}")
```

### Duplicate Detection

```python
from pathlib import Path
from pytest_jux.storage import ReportStorage
from pytest_jux.canonicalizer import compute_canonical_hash, load_xml

storage = ReportStorage()
report_xml = Path("junit-signed.xml").read_bytes()

# Compute canonical hash
root = load_xml("junit-signed.xml")
canonical_hash = compute_canonical_hash(root)

# First store - succeeds
storage.store_report(report_xml, canonical_hash)
print(f"First store: {canonical_hash}")

# Second store - duplicate detected (same hash)
if storage.report_exists(canonical_hash):
    print("Duplicate detected - report already stored")
else:
    storage.store_report(report_xml, canonical_hash)

# Storage only keeps one copy (deduplication)
```

### Retrieving Reports

```python
from pytest_jux.storage import ReportStorage, StorageError
from lxml import etree

storage = ReportStorage()

try:
    # Retrieve report by hash
    report_xml = storage.get_report("sha256:abc123...")

    print(f"Report size: {len(report_xml)} bytes")

    # Metadata is embedded in XML <properties>
    root = etree.fromstring(report_xml)
    properties = root.find(".//properties")

    for prop in properties.findall("property"):
        name = prop.get("name")
        value = prop.get("value")
        if name.startswith("jux:"):
            print(f"{name}: {value}")

except StorageError as e:
    print(f"Report not found: {e}")
```

### Listing Reports

```python
from pytest_jux.storage import ReportStorage
from lxml import etree

storage = ReportStorage()

# List all cached reports
reports = storage.list_reports()

print(f"Total reports: {len(reports)}")
for report_hash in reports:
    # Get report and extract timestamp from metadata
    report_xml = storage.get_report(report_hash)
    root = etree.fromstring(report_xml)
    timestamp_prop = root.find(".//property[@name='jux:timestamp']")
    timestamp = timestamp_prop.get("value") if timestamp_prop is not None else "N/A"
    print(f"  {report_hash[:16]}... - {timestamp}")
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
| Queued report not found | `StorageError` | `Queued report not found: <hash>` |
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

def store_report_thread_safe(report_xml, canonical_hash):
    with lock:
        return storage.store_report(report_xml, canonical_hash)
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
storage.store_report(report_xml, canonical_hash)
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
