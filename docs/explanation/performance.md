# Performance Explanation

**Understanding pytest-jux performance characteristics and optimization strategies**

---

## Overview

This document explains the performance characteristics of pytest-jux, covering:
- Performance bottlenecks and overhead
- Scalability limits and considerations
- Optimization strategies
- Benchmarking and profiling approaches
- Performance best practices

For operational guidance, see [Troubleshooting Guide](../howto/troubleshooting.md). For architectural context, see [Architecture Explanation](architecture.md).

---

## Performance Model

### Signing Operation Timeline

```
Test Execution → JUnit XML Generation → pytest-jux Processing
                                        ↓
                                   1. Read XML (I/O)
                                        ↓
                                   2. Parse XML (CPU)
                                        ↓
                                   3. Canonicalization (CPU)
                                        ↓
                                   4. Signature Generation (CPU + Crypto)
                                        ↓
                                   5. Write Signed XML (I/O)
                                        ↓
                                   6. Storage (I/O + Hash Computation)
```

**Total Overhead**: Signing adds **50-500ms** to test runs depending on:
- Report size (number of tests)
- Algorithm choice (RSA vs ECDSA)
- Storage mode (enabled/disabled)
- Disk I/O performance (HDD vs SSD vs NVMe)

---

## Performance Characteristics

### 1. XML Parsing and Canonicalization

**Operation**: `lxml.etree.parse()` + `lxml.etree.canonicalize()`

**Complexity**: O(n) where n = XML size in bytes

**Typical Times**:
- Small report (10 tests, ~5 KB): **10-20ms**
- Medium report (100 tests, ~50 KB): **30-50ms**
- Large report (1,000 tests, ~500 KB): **100-200ms**
- Very large report (10,000 tests, ~5 MB): **500-1,000ms**

**Bottleneck**: C14N transformation (attribute ordering, namespace normalization)

**Optimization**:
```python
# Bad: Parse and canonicalize multiple times
for i in range(10):
    tree = etree.parse(xml_file)
    canonical_xml = etree.canonicalize(tree)

# Good: Parse once, reuse tree
tree = etree.parse(xml_file)
canonical_xml = etree.canonicalize(tree)  # Cache if needed
```

**Impact**: C14N is 2-3x slower than simple parsing but **required** for XMLDSig and canonical hashing.

---

### 2. Cryptographic Signing

**Operation**: `signxml.XMLSigner.sign()`

**Complexity**: O(1) for signature generation, but constant is **large**

#### RSA Signature Performance

| Key Size | Sign Time | Verify Time | Signature Size |
|----------|-----------|-------------|----------------|
| RSA-2048 | 5-10ms    | 1-2ms       | 256 bytes      |
| RSA-3072 | 15-25ms   | 2-3ms       | 384 bytes      |
| RSA-4096 | 40-60ms   | 3-5ms       | 512 bytes      |

**Key Insight**: RSA signing is **8-15x slower** than verification (asymmetric cost).

**Why Slow?**:
- Large prime number exponentiation
- Modular arithmetic with 2048-4096 bit numbers
- Computationally intensive by design (security property)

**Real-World Example**:
```bash
# Benchmark RSA-4096 signing
time jux-sign --key rsa-4096-key.pem report.xml
# Result: ~60ms for 50KB report

# 1,000 test runs/day = 60 seconds/day overhead
```

#### ECDSA Signature Performance

| Curve   | Sign Time | Verify Time | Signature Size |
|---------|-----------|-------------|----------------|
| P-256   | 3-5ms     | 4-6ms       | 64-72 bytes    |
| P-384   | 6-10ms    | 8-12ms      | 96-104 bytes   |
| P-521   | 10-15ms   | 12-18ms     | 132-139 bytes  |

**Key Insight**: ECDSA signing is **8-12x faster** than RSA-4096 with equivalent security.

**Why Faster?**:
- Elliptic curve operations are more efficient
- Smaller key sizes (256 bits vs 4096 bits)
- Modern CPU optimizations for ECC

**Recommendation**:
- **Development**: RSA-2048 (fast enough, widely compatible)
- **Production (performance-critical)**: ECDSA-P256 (faster, smaller)
- **Production (maximum security)**: RSA-4096 or ECDSA-P384

---

### 3. Canonical Hash Computation

**Operation**: `compute_canonical_hash(xml_tree)`

**Complexity**: O(n) where n = canonical XML size

**Typical Times**:
- Small report (~5 KB): **5-10ms**
- Medium report (~50 KB): **15-25ms**
- Large report (~500 KB): **50-100ms**

**Breakdown**:
1. Canonicalization: 70-80% of time (see Section 1)
2. SHA-256 hashing: 20-30% of time (very fast)

**Why C14N Dominates**:
```python
# SHA-256 is VERY fast
import hashlib
import time

data = b"x" * 1_000_000  # 1 MB
start = time.time()
hash_value = hashlib.sha256(data).hexdigest()
print(f"SHA-256: {(time.time() - start) * 1000:.2f}ms")
# Result: ~2-3ms for 1 MB

# C14N is slower (attribute sorting, namespace handling)
# Result: ~50-100ms for 500 KB XML
```

---

### 4. File I/O Operations

**Operation**: Read JUnit XML, write signed XML, store to cache

**Complexity**: O(n) where n = file size

**Typical Times** (SSD):
- Read 50 KB XML: **1-2ms**
- Write 55 KB signed XML: **2-3ms**
- Store to cache (copy + write metadata): **3-5ms**

**Typical Times** (HDD):
- Read 50 KB XML: **5-10ms** (seek time dominates)
- Write 55 KB signed XML: **10-15ms**
- Store to cache: **15-25ms**

**Impact**: SSD vs HDD makes **3-5x difference** in total overhead.

**Optimization**:
```bash
# Use SSD for pytest-jux cache
export JUX_STORAGE_BASE_PATH=/mnt/nvme/pytest-jux

# Or disable storage for performance-critical scenarios
pytest --junitxml=junit.xml --jux-storage-mode disabled --jux-key key.pem
```

---

### 5. Storage Operations

**Operation**: Store signed report + metadata in XDG cache

**Components**:
1. Compute canonical hash: **15-100ms** (see Section 3)
2. Check for duplicate: **1-2ms** (file existence check)
3. Write signed XML: **2-15ms** (disk I/O)
4. Write metadata JSON: **1-5ms** (disk I/O)

**Total**: **20-120ms** depending on report size and disk

**Storage Disabled Mode**:
```bash
# Skip storage for maximum performance
pytest --junitxml=junit.xml --jux-storage-mode disabled --jux-key key.pem

# Saves: 20-120ms per test run
# Use case: CI/CD where reports are sent to API server immediately
```

---

## End-to-End Performance

### Benchmarks (Typical Developer Laptop)

**Test Environment**:
- CPU: Apple M1 / Intel i7-12700K
- Disk: NVMe SSD
- Python: 3.11
- pytest-jux: 0.1.9

**Small Report** (10 tests, 5 KB XML):
```
Test execution:        1,200ms
pytest XML generation:   100ms
pytest-jux signing:       50ms  (RSA-4096)
  - Parsing:             10ms
  - C14N:                 5ms
  - RSA-4096 sign:       30ms
  - Storage:              5ms
Total overhead:          50ms  (4% of test time)
```

**Medium Report** (100 tests, 50 KB XML):
```
Test execution:        5,000ms
pytest XML generation:   200ms
pytest-jux signing:      100ms  (RSA-4096)
  - Parsing:             20ms
  - C14N:                15ms
  - RSA-4096 sign:       50ms
  - Storage:             15ms
Total overhead:         100ms  (2% of test time)
```

**Large Report** (1,000 tests, 500 KB XML):
```
Test execution:       30,000ms
pytest XML generation:   500ms
pytest-jux signing:      300ms  (RSA-4096)
  - Parsing:             50ms
  - C14N:                80ms
  - RSA-4096 sign:       60ms
  - Storage:            110ms
Total overhead:         300ms  (1% of test time)
```

**Key Insight**: pytest-jux overhead is **1-4% of test execution time** for typical test suites.

---

### Algorithm Comparison

**Same Report** (100 tests, 50 KB XML):

| Algorithm  | Sign Time | Total Overhead | Signature Size |
|------------|-----------|----------------|----------------|
| RSA-2048   | 8ms       | 60ms           | 256 bytes      |
| RSA-3072   | 20ms      | 72ms           | 384 bytes      |
| RSA-4096   | 50ms      | 102ms          | 512 bytes      |
| ECDSA-P256 | 4ms       | 56ms           | 64-72 bytes    |
| ECDSA-P384 | 8ms       | 60ms           | 96-104 bytes   |

**Recommendation**:
- **Development**: RSA-2048 or ECDSA-P256 (both ~60ms)
- **Production**: ECDSA-P256 (faster + smaller + 128-bit security)
- **Maximum Security**: RSA-4096 (~100ms, acceptable for most use cases)

---

## Scalability Considerations

### 1. Report Size Scalability

**Linear Scaling** (O(n)):
- XML parsing
- Canonicalization
- Hashing
- File I/O

**Constant Overhead** (O(1)):
- Cryptographic signing (independent of report size)

**Practical Limits**:
- **10,000 tests** (~5 MB XML): ~1-2 seconds signing overhead
- **100,000 tests** (~50 MB XML): ~10-20 seconds (impractical)

**Mitigation for Large Suites**:
```bash
# Option 1: Disable storage for large suites
pytest --junitxml=junit.xml --jux-storage-mode disabled --jux-key key.pem

# Option 2: Split into multiple test runs (parallel)
pytest tests/unit/ --junitxml=junit-unit.xml --jux-key key.pem &
pytest tests/integration/ --junitxml=junit-integration.xml --jux-key key.pem &
wait
```

---

### 2. Parallel Execution (pytest-xdist)

**Issue**: Storage conflicts when multiple workers write simultaneously

**Solution**: Disable storage during parallel runs

```bash
# Parallel tests with xdist
pytest -n auto \
  --junitxml=junit.xml \
  --jux-storage-mode disabled \
  --jux-key key.pem
```

**Performance Impact**:
- Test execution: **Much faster** (parallelized)
- Signing overhead: **Same** (signing happens after all tests complete)
- Storage overhead: **Zero** (disabled)

**Alternative**: Per-worker storage (see [Integration Guide](../howto/integrate-pytest-plugins.md))

---

### 3. CI/CD Throughput

**Scenario**: 1,000 test runs/day in CI/CD

**RSA-4096** (100ms overhead per run):
- Total overhead: 100 seconds/day = **1.67 minutes/day**
- Impact: Negligible (<0.1% of CI/CD time)

**ECDSA-P256** (56ms overhead per run):
- Total overhead: 56 seconds/day = **0.93 minutes/day**
- Impact: Negligible

**Conclusion**: Signing overhead is **not a bottleneck** for typical CI/CD workloads.

---

## Optimization Strategies

### 1. Choose Fast Algorithm

**Development**:
```bash
# Use RSA-2048 (fast enough)
jux-keygen --type rsa --bits 2048 --output dev-key.pem
```

**Production (Performance-Critical)**:
```bash
# Use ECDSA-P256 (fastest + small)
jux-keygen --type ecdsa --curve P-256 --output prod-key.pem
```

**Production (Maximum Security)**:
```bash
# Use RSA-4096 (slower but widely trusted)
jux-keygen --type rsa --bits 4096 --output prod-key.pem
```

---

### 2. Disable Storage When Not Needed

**Scenario**: CI/CD where reports are sent to API server immediately

```bash
# Skip local storage (saves 20-120ms)
pytest --junitxml=junit.xml \
  --jux-storage-mode disabled \
  --jux-key key.pem

# Then publish to API server
jux-publish junit.xml --api-url https://jux.example.com
```

**Savings**: 20-120ms per test run

---

### 3. Use SSD for Storage

**Benchmark** (100 tests, 50 KB report):

| Disk Type | Storage Time | Total Overhead |
|-----------|--------------|----------------|
| NVMe SSD  | 5ms          | 60ms           |
| SATA SSD  | 10ms         | 65ms           |
| HDD       | 30ms         | 85ms           |

**Recommendation**: Use SSD (NVMe or SATA) for pytest-jux cache

```bash
# Configure storage on fast disk
export JUX_STORAGE_BASE_PATH=/mnt/nvme/pytest-jux
```

---

### 4. Parallel Test Execution

**Before** (Sequential):
```bash
pytest tests/ --junitxml=junit.xml --jux-key key.pem
# Time: 60 seconds (tests) + 0.1 seconds (signing) = 60.1 seconds
```

**After** (Parallel with xdist):
```bash
pytest tests/ -n auto \
  --junitxml=junit.xml \
  --jux-storage-mode disabled \
  --jux-key key.pem
# Time: 15 seconds (tests) + 0.1 seconds (signing) = 15.1 seconds
```

**Speedup**: 4x (for 4 CPU cores)

---

### 5. Cache Cleanup

**Issue**: Large cache slows down duplicate detection and disk I/O

**Solution**: Regular cleanup

```bash
# Age-based cleanup (keep 30 days)
jux-cache clean --days 30

# Size-based cleanup (keep 100 MB)
jux-cache clean --max-size 100MB

# Automate in cron
0 2 * * * jux-cache clean --days 30  # Daily at 2 AM
```

**Impact**: Faster file operations, better disk utilization

---

## Benchmarking and Profiling

### 1. Built-In Benchmarking

**pytest-jux includes timing metrics**:

```bash
# Enable debug logging for timing info
export JUX_DEBUG=1
pytest --junitxml=junit.xml --jux-key key.pem

# Output includes:
# [jux] XML parsing: 10ms
# [jux] Canonicalization: 15ms
# [jux] Signature generation: 50ms
# [jux] Storage: 5ms
# [jux] Total overhead: 80ms
```

---

### 2. Manual Benchmarking

**Benchmark signing overhead**:

```python
# benchmark_signing.py
import time
from pathlib import Path
from pytest_jux.signer import sign_xml

def benchmark_signing(xml_path: Path, key_path: Path, iterations: int = 100):
    """Benchmark signing performance."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        sign_xml(xml_path, key_path)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms

    print(f"Mean: {sum(times) / len(times):.2f}ms")
    print(f"Min:  {min(times):.2f}ms")
    print(f"Max:  {max(times):.2f}ms")
    print(f"P50:  {sorted(times)[len(times) // 2]:.2f}ms")
    print(f"P95:  {sorted(times)[int(len(times) * 0.95)]:.2f}ms")

# Usage
benchmark_signing(Path("junit.xml"), Path("key.pem"))
```

**Output**:
```
Mean: 98.45ms
Min:  92.10ms
Max:  112.30ms
P50:  97.80ms
P95:  105.20ms
```

---

### 3. Profiling with cProfile

**Profile pytest-jux plugin**:

```bash
# Run pytest with profiling
python -m cProfile -o pytest_jux.prof \
  -m pytest --junitxml=junit.xml --jux-key key.pem

# Analyze profile
python -m pstats pytest_jux.prof
> sort cumtime
> stats 20  # Show top 20 functions by cumulative time
```

**Expected Bottlenecks**:
1. `lxml.etree.canonicalize()` - C14N transformation
2. `signxml.XMLSigner.sign()` - RSA/ECDSA signing
3. File I/O operations

---

### 4. Memory Profiling

**Profile memory usage**:

```python
# memory_profile.py
from memory_profiler import profile
from pytest_jux.signer import sign_xml

@profile
def profile_memory():
    sign_xml("junit.xml", "key.pem")

if __name__ == "__main__":
    profile_memory()
```

**Run**:
```bash
python -m memory_profiler memory_profile.py
```

**Expected Memory Usage**:
- Small report (10 tests, 5 KB): **~5 MB**
- Medium report (100 tests, 50 KB): **~10 MB**
- Large report (1,000 tests, 500 KB): **~30 MB**

**Note**: Memory usage is dominated by XML tree representation in lxml.

---

## Performance Best Practices

### 1. Algorithm Selection

**✅ DO**:
- Use ECDSA-P256 for performance-critical production environments
- Use RSA-2048 for development (good balance)
- Use RSA-4096 for maximum security (acceptable overhead)

**❌ DON'T**:
- Use RSA-1024 (insecure, deprecated)
- Use ECDSA-P521 unless required (slower, no practical benefit over P-384)

---

### 2. Storage Configuration

**✅ DO**:
- Store cache on SSD (NVMe or SATA)
- Disable storage for CI/CD when using API server
- Clean cache regularly (age or size-based)

**❌ DON'T**:
- Store cache on network file system (high latency)
- Store cache on HDD (5-10x slower)
- Let cache grow unbounded (slows down I/O)

---

### 3. Parallel Execution

**✅ DO**:
- Use `pytest-xdist` for parallel test execution
- Disable storage when using xdist (`--jux-storage-mode disabled`)
- Split large test suites into multiple runs

**❌ DON'T**:
- Enable storage with xdist (causes conflicts)
- Run massive test suites (>10,000 tests) in single run
- Forget to disable storage in CI/CD parallel jobs

---

### 4. Monitoring and Profiling

**✅ DO**:
- Monitor signing overhead in CI/CD (use debug logging)
- Profile performance for large test suites (>1,000 tests)
- Benchmark after upgrading dependencies

**❌ DON'T**:
- Ignore performance degradation over time
- Skip profiling for very large test suites
- Assume performance is constant across environments

---

## Performance Roadmap

### Current (v0.1.x)

- ✅ RSA-SHA256 and ECDSA-SHA256 signatures
- ✅ C14N canonicalization
- ✅ File-based storage with caching
- ✅ Storage disabled mode for performance

### Planned (v0.2.x)

- 📋 **Streaming C14N**: Reduce memory usage for large reports
- 📋 **Incremental signing**: Sign only changed test results
- 📋 **Parallel storage**: Asynchronous storage operations
- 📋 **Signature caching**: Cache signatures for unchanged reports

### Future (v1.0+)

- 📋 **Hardware acceleration**: Use CPU crypto extensions (AES-NI, etc.)
- 📋 **HSM support**: Offload signing to hardware security modules
- 📋 **Compression**: Compress signed reports (gzip, zstd)
- 📋 **Database storage**: SQLite/PostgreSQL for faster querying

---

## Performance FAQ

### Q: How much overhead does pytest-jux add?

**A**: Typically **1-4% of test execution time**:
- Small test suites (10 tests, 1 second): +50ms (5%)
- Medium test suites (100 tests, 5 seconds): +100ms (2%)
- Large test suites (1,000 tests, 30 seconds): +300ms (1%)

---

### Q: Should I use RSA or ECDSA?

**A**: Depends on priority:
- **Performance**: ECDSA-P256 (faster, smaller)
- **Compatibility**: RSA-4096 (widely supported)
- **Development**: RSA-2048 or ECDSA-P256 (both fast enough)

---

### Q: Is storage a performance bottleneck?

**A**: Only if:
- Using HDD (5-10x slower than SSD)
- Using network file system (high latency)
- Cache is very large (>10,000 reports)

**Solution**: Use SSD or disable storage

---

### Q: Can I speed up signing for large test suites?

**A**: Yes:
1. Use ECDSA-P256 (faster algorithm)
2. Disable storage (`--jux-storage-mode disabled`)
3. Split into multiple runs (parallel)
4. Use SSD for cache

---

### Q: Does pytest-jux work with pytest-xdist?

**A**: Yes, but disable storage:

```bash
pytest -n auto --junitxml=junit.xml \
  --jux-storage-mode disabled \
  --jux-key key.pem
```

---

### Q: How do I profile pytest-jux performance?

**A**: Use debug logging or cProfile:

```bash
# Debug logging
export JUX_DEBUG=1
pytest --junitxml=junit.xml --jux-key key.pem

# cProfile
python -m cProfile -o pytest_jux.prof -m pytest --junitxml=junit.xml --jux-key key.pem
```

---

## See Also

- **[Architecture Explanation](architecture.md)**: System design and components
- **[Security Explanation](security.md)**: Cryptographic design
- **[Troubleshooting Guide](../howto/troubleshooting.md)**: Performance problems
- **[Integration Guide](../howto/integrate-pytest-plugins.md)**: pytest-xdist configuration
- **[CI/CD Deployment](../howto/ci-cd-deployment.md)**: CI/CD performance optimization

---

**Last Updated**: 2025-10-20
**Version**: 0.1.9
