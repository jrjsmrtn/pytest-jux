# Choosing Storage Modes

_Select the right storage mode for your needs_

**Audience:** Infrastructure Engineers, Integrators, Developers
**Type:** How-To Guide (problem-oriented)

## Overview

pytest-jux supports four storage modes:

| Mode | Local Storage | API Publishing | Offline Queue | Use Case |
|------|---------------|----------------|---------------|----------|
| **LOCAL** | ✅ | ❌ | ❌ | Development, no server |
| **API** | ❌ | ✅ | ❌ | Production, centralized |
| **BOTH** | ✅ | ✅ | ❌ | Hybrid, backup |
| **CACHE** | ✅ | ✅ (when available) | ✅ | Unreliable network |

This guide helps you choose the right mode for your situation.

## Decision Tree

```
Start
  │
  ├─ Do you have a Jux API Server?
  │   │
  │   NO ──> Use LOCAL mode
  │   │
  │   YES
  │     │
  │     ├─ Is your network reliable?
  │     │   │
  │     │   NO ──> Use CACHE mode
  │     │   │
  │     │   YES
  │     │     │
  │     │     ├─ Do you need local backup?
  │     │     │   │
  │     │     │   YES ──> Use BOTH mode
  │     │     │   │
  │     │     │   NO ──> Use API mode
```

## Mode 1: LOCAL (Development)

### When to Use

✅ **Best for:**
- Local development
- No Jux API Server available (yet)
- Offline testing
- Personal projects
- Learning pytest-jux

❌ **Not ideal for:**
- Team collaboration
- Centralized reporting
- Cross-environment analysis

### How It Works

```
┌──────────┐     ┌──────────────┐
│  pytest  │ --> │  pytest-jux  │
│          │     │  • Sign      │
└──────────┘     │  • Store     │
                 └──────┬───────┘
                        │
                        v
                 ~/.local/share/jux/reports/
                 ├── sha256:abc123.../
                 │   ├── report.xml
                 │   └── metadata.json
                 └── sha256:def456.../
                     ├── report.xml
                     └── metadata.json
```

**Reports stored:** Local filesystem only
**Network required:** No
**Offline capable:** Yes

### Configuration

```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = local
```

**Or via environment:**
```bash
export JUX_ENABLED=true
export JUX_SIGN=true
export JUX_KEY_PATH=~/.jux/signing_key.pem
export JUX_STORAGE_MODE=local
```

### Use Cases

**1. Local Development**
```bash
# Developer working on laptop
cd my-project
pytest --junit-xml=report.xml

# Report signed and stored locally
jux-cache list
```

**2. Offline Testing**
```bash
# No internet connection? No problem!
pytest --junit-xml=report.xml

# Reports stored locally, can inspect later
jux-inspect report.xml
```

**3. Learning and Experimentation**
```bash
# Try out pytest-jux without server setup
jux-config init
pytest --junit-xml=report.xml
jux-cache stats
```

### Managing Local Storage

**View cached reports:**
```bash
jux-cache list
jux-cache stats
```

**Clean old reports:**
```bash
# Remove reports older than 30 days
jux-cache clean --days 30

# Dry run first
jux-cache clean --days 30 --dry-run
```

**Custom storage location:**
```ini
[jux]
storage_mode = local
storage_path = /custom/path/jux-reports
```

## Mode 2: API (Production)

### When to Use

✅ **Best for:**
- Production CI/CD pipelines
- Centralized test reporting
- Team collaboration
- Cross-environment analysis
- No local storage needed

❌ **Not ideal for:**
- Unreliable networks
- Offline development
- No Jux API Server available

### How It Works

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  pytest  │ --> │  pytest-jux  │ --> │  Jux API     │
│          │     │  • Sign      │     │  Server      │
└──────────┘     │  • Publish   │     │  • Store     │
                 └──────────────┘     │  • Verify    │
                                      │  • Dedupe    │
                                      └──────────────┘
```

**Reports stored:** Jux API Server only
**Network required:** Yes (fails if unavailable)
**Offline capable:** No

### Configuration

```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = api
api_url = https://jux.example.com/api/v1
api_key = your-api-key-here
```

**Or via environment (recommended for secrets):**
```bash
export JUX_ENABLED=true
export JUX_SIGN=true
export JUX_KEY_PATH=~/.jux/signing_key.pem
export JUX_STORAGE_MODE=api
export JUX_API_URL=https://jux.example.com/api/v1
export JUX_API_KEY=your-api-key-here  # Never commit this!
```

### Use Cases

**1. CI/CD Production Pipeline**
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest --junit-xml=report.xml
  env:
    JUX_STORAGE_MODE: api
    JUX_API_URL: ${{ secrets.JUX_API_URL }}
    JUX_API_KEY: ${{ secrets.JUX_API_KEY }}
```

**2. Centralized Team Reporting**
```bash
# All team members publish to same server
# No local storage cluttering developer machines

pytest --junit-xml=report.xml
# Report automatically published to team server
```

**3. Cross-Environment Analysis**
```bash
# Dev, staging, and prod all publish to same API
# Jux API Server provides unified view across environments
```

### Error Handling

**API unreachable:**
```
ERROR: Failed to publish report to API
  URL: https://jux.example.com/api/v1
  Error: Connection timeout
```

**Solution:** Use CACHE mode for unreliable networks (see below)

## Mode 3: BOTH (Hybrid)

### When to Use

✅ **Best for:**
- Paranoid deployments (belt and suspenders)
- Backup requirements
- Gradual migration (local → API)
- Local inspection + centralized storage
- Compliance with dual storage requirements

❌ **Not ideal for:**
- Space-constrained environments
- High-volume testing (duplicate storage)

### How It Works

```
                    ┌──────────────┐
              ┌────>│  Local       │
              │     │  Storage     │
┌──────────┐  │     └──────────────┘
│  pytest  │──┤
│          │  │
└──────────┘  │     ┌──────────────┐
              └────>│  Jux API     │
                    │  Server      │
                    └──────────────┘
```

**Reports stored:** Local filesystem AND API server
**Network required:** Yes (both operations must succeed)
**Offline capable:** No (API publish fails if offline)

### Configuration

```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = both
storage_path = ~/.local/share/jux/reports
api_url = https://jux.example.com/api/v1
api_key = your-api-key-here
```

### Use Cases

**1. Compliance Requirements**
```bash
# Auditor: "We need local and remote copies"
# BOTH mode satisfies dual-storage requirements

pytest --junit-xml=report.xml
# Stored locally AND published to API
```

**2. Local Inspection + Centralized Storage**
```bash
# Store on API for team visibility
# Keep local copy for quick inspection

pytest --junit-xml=report.xml
jux-cache show sha256:abc123...  # Local inspection
# Also available on team API server
```

**3. Migration Period**
```bash
# Migrating from local-only to API-based
# Keep local copies during transition

# Week 1-2: BOTH mode (validate API works)
# Week 3+: Switch to API mode once confident
```

### Trade-offs

**Pros:**
- ✅ Redundancy (backup if API fails later)
- ✅ Local inspection without API query
- ✅ Gradual migration path

**Cons:**
- ❌ Double storage space
- ❌ Slower (two write operations)
- ❌ Fails if either storage fails

## Mode 4: CACHE (Unreliable Networks)

### When to Use

✅ **Best for:**
- Unreliable network connections
- Intermittent connectivity
- Laptop development (coffee shop WiFi)
- Remote/traveling developers
- Network-resilient deployments

❌ **Not ideal for:**
- Reliable, high-bandwidth networks
- Real-time reporting requirements

### How It Works

```
                    ┌──────────────┐
              ┌────>│  Local       │
              │     │  Storage     │
┌──────────┐  │     └──────────────┘
│  pytest  │──┤
│          │  │     ┌──────────────┐
└──────────┘  └────>│  Offline     │───> (published when API available)
                    │  Queue       │
                    └──────────────┘
```

**Reports stored:** Local filesystem + offline queue
**Network required:** No (reports queued if API unavailable)
**Offline capable:** Yes (automatic retry when online)

### Configuration

```ini
[jux]
enabled = true
sign = true
key_path = ~/.jux/signing_key.pem
storage_mode = cache
storage_path = ~/.local/share/jux/reports
api_url = https://jux.example.com/api/v1
api_key = your-api-key-here
```

### How Offline Queue Works

**1. Network Available:**
```
pytest --> pytest-jux --> Local Storage (✓)
                      --> API Publish (✓)
```

**2. Network Unavailable:**
```
pytest --> pytest-jux --> Local Storage (✓)
                      --> Offline Queue (✓)
                      --> API Publish (✗ skipped)
```

**3. Network Restored:**
```
(background process)
Offline Queue --> API Publish (✓ retry)
              --> Remove from queue (✓)
```

### Use Cases

**1. Coffee Shop Development**
```bash
# Working on laptop at coffee shop
# Unreliable WiFi

pytest --junit-xml=report.xml
# Stored locally, queued for API publish

# Later, back at office with good WiFi
# Reports automatically published from queue
```

**2. Remote CI Runners**
```bash
# CI runner in remote location
# Network sometimes drops

# CACHE mode ensures no test results are lost
# Reports published when connectivity restored
```

**3. Traveling Developers**
```bash
# Developer on airplane
# No internet connection

pytest --junit-xml=report.xml
# Reports stored locally and queued

# On landing, reports auto-publish to API
```

### Managing the Queue

**View queued reports:**
```bash
jux-cache stats
# Shows:
#   Total Reports: 10
#   Queued Reports: 3  <-- Waiting for API
```

**Manual queue processing:**
```bash
# Force queue processing (when network restored)
jux-cache process-queue

# Or wait for automatic processing (next test run)
```

**Clear queue (if needed):**
```bash
# Remove queued reports without publishing
jux-cache clear-queue --confirm
```

## Comparison Matrix

| Feature | LOCAL | API | BOTH | CACHE |
|---------|-------|-----|------|-------|
| **Storage** |
| Local filesystem | ✅ | ❌ | ✅ | ✅ |
| API server | ❌ | ✅ | ✅ | ✅ (when available) |
| Offline queue | ❌ | ❌ | ❌ | ✅ |
| **Requirements** |
| Network required | ❌ | ✅ | ✅ | ❌ |
| API server required | ❌ | ✅ | ✅ | ⚠️ (optional) |
| Disk space | Low | None | High | Medium |
| **Behavior** |
| Offline capable | ✅ | ❌ | ❌ | ✅ |
| Real-time API | ❌ | ✅ | ✅ | ⚠️ (when online) |
| Automatic retry | ❌ | ❌ | ❌ | ✅ |
| **Best For** |
| Development | ✅ | ❌ | ❌ | ❌ |
| Production CI/CD | ❌ | ✅ | ⚠️ | ⚠️ |
| Unreliable network | ❌ | ❌ | ❌ | ✅ |
| Dual storage | ❌ | ❌ | ✅ | ❌ |

## Changing Storage Modes

You can switch storage modes at any time.

### From LOCAL to API

```bash
# 1. Set up API configuration
jux-config init --template full
# Edit config: storage_mode = api

# 2. Test API connectivity
curl -X POST https://jux.example.com/api/v1 \
  -H "Authorization: Bearer $JUX_API_KEY" \
  -H "Content-Type: application/xml" \
  -d @test-report.xml

# 3. Run tests with new mode
pytest --junit-xml=report.xml
```

**Note:** Existing local reports are NOT automatically published. Use manual publishing if needed.

### From API to CACHE

```bash
# 1. Update configuration
jux-config dump > ~/.config/jux/config.backup
jux-config init --force
# Edit: storage_mode = cache

# 2. Verify configuration
jux-config validate --strict

# 3. Test with network disabled
# Disable WiFi, run tests
pytest --junit-xml=report.xml

# 4. Re-enable network and verify queue processing
```

## Environment-Specific Modes

Different environments may need different modes:

**Development:**
```ini
# ~/.config/jux/config (developer laptop)
[jux]
storage_mode = local
```

**Staging:**
```ini
# /etc/jux/config (staging servers)
[jux]
storage_mode = cache
api_url = https://jux-staging.example.com/api/v1
```

**Production:**
```bash
# Environment variables (CI/CD)
export JUX_STORAGE_MODE=api
export JUX_API_URL=https://jux.example.com/api/v1
export JUX_API_KEY=$PRODUCTION_API_KEY
```

## Troubleshooting

### "Storage mode 'api' requires api_url"

**Problem:** API mode configured but no API URL provided.

**Solution:**
```ini
[jux]
storage_mode = api
api_url = https://jux.example.com/api/v1  # Add this
api_key = your-api-key-here
```

### Reports Not Publishing

**Problem:** CACHE mode reports stuck in queue.

**Diagnosis:**
```bash
jux-cache stats
# Queued Reports: 50  <-- Growing number
```

**Solutions:**

1. **Check API connectivity:**
```bash
curl -I https://jux.example.com/api/v1
```

2. **Check API credentials:**
```bash
jux-config dump | grep api_key
# Verify key is correct
```

3. **Manually process queue:**
```bash
jux-cache process-queue --verbose
```

### Disk Space Issues

**Problem:** LOCAL or BOTH mode filling disk.

**Solution:**
```bash
# Check current usage
jux-cache stats

# Clean old reports
jux-cache clean --days 7

# Or switch to API mode
jux-config dump > ~/.config/jux/config.backup
# Edit: storage_mode = api
```

## Best Practices

### 1. Start with LOCAL, Graduate to API

```
Development --> LOCAL mode (learn the tool)
       ↓
Staging    --> CACHE mode (validate API integration)
       ↓
Production --> API mode (centralized reporting)
```

### 2. Use CACHE for CI/CD

Even with reliable networks, use CACHE mode in CI/CD for resilience:

```yaml
env:
  JUX_STORAGE_MODE: cache  # Not 'api'
  JUX_API_URL: ${{ secrets.JUX_API_URL }}
```

**Why:** Network hiccups won't fail your builds.

### 3. Keep API Keys in Environment Variables

```ini
# Good: .jux.conf (committed to git)
[jux]
storage_mode = api
api_url = https://jux.example.com/api/v1
# api_key not in file - use JUX_API_KEY env var

# Bad: api_key in file (security risk)
[jux]
api_key = secret-key-123  # ❌ Don't commit secrets!
```

### 4. Monitor Queue Size

For CACHE mode, monitor queue growth:

```bash
# Add to monitoring
jux-cache stats --json | jq '.queued_reports'
```

Alert if queue exceeds threshold (e.g., >100 reports).

## Next Steps

Now that you understand storage modes:

- **[Multi-Environment Configuration](multi-environment-config.md)** - Configure different modes per environment
- **[CI/CD Deployment](ci-cd-deployment.md)** - Integrate with your pipeline
- **[Managing Cached Reports](managing-cached-reports.md)** - Maintain local storage
- **[Troubleshooting Guide](troubleshooting.md)** - Fix common issues

## Related Documentation

- **[Quick Start](../tutorials/quick-start.md)** - Get started with LOCAL mode
- **[Understanding pytest-jux](../explanation/understanding-pytest-jux.md)** - Learn the concepts
- **[Configuration Reference](../reference/configuration.md)** - All configuration options
