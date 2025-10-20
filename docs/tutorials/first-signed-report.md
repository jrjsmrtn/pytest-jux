# Tutorial: Your First Signed Test Report

**Learn to sign and verify test reports in 15 minutes**

---

## What You'll Learn

By the end of this tutorial, you will:

✅ Install pytest-jux
✅ Generate cryptographic signing keys
✅ Run tests and automatically sign reports
✅ Verify report signatures
✅ Inspect signed report contents
✅ Understand the benefits of signed reports

**Time Required**: 15-20 minutes

**Difficulty**: Beginner

**Prerequisites**:
- Python 3.11+ installed
- Basic familiarity with pytest
- Command-line experience

---

## Why Sign Test Reports?

Test reports contain critical information about your software quality. Signing reports provides:

- **✅ Authenticity**: Prove reports come from your CI/CD pipeline
- **✅ Integrity**: Detect if reports were tampered with
- **✅ Non-repudiation**: Cryptographic proof of origin
- **✅ Trust**: Share test results with confidence

**Real-World Scenario**: Your team wants to publish test coverage reports to stakeholders. How do they know the reports weren't modified? Digital signatures solve this problem.

---

## Step 1: Installation

### Install pytest-jux

```bash
# Using pip
pip install pytest-jux

# Or using uv (recommended)
uv pip install pytest-jux
```

**Expected Output**:
```
Successfully installed pytest-jux-0.1.9 lxml-5.0.0 signxml-3.2.0 ...
```

### Verify Installation

```bash
# Check pytest-jux is installed
pytest --version

# Should show pytest-jux in the plugin list
```

**Expected Output**:
```
pytest 8.0.0
setuptools registered plugins:
  pytest-jux-0.1.9 at /path/to/pytest_jux/plugin.py
```

**✓ Checkpoint**: pytest-jux is installed and recognized by pytest

---

## Step 2: Create a Sample Test

Let's create a simple test to demonstrate signing.

### Create Test File

```bash
# Create test directory
mkdir -p my-first-signed-report
cd my-first-signed-report

# Create a simple test file
cat > test_example.py << 'EOF'
"""Simple test file for pytest-jux tutorial."""

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

def test_multiplication():
    """Test basic multiplication."""
    assert 2 * 3 == 6

def test_string_operations():
    """Test string operations."""
    assert "hello".upper() == "HELLO"
EOF
```

### Run Tests Without Signing (Baseline)

```bash
# Run tests and generate JUnit XML (unsigned)
pytest --junitxml=junit.xml
```

**Expected Output**:
```
======================== test session starts =========================
collected 3 items

test_example.py ...                                            [100%]

======================== 3 passed in 0.12s ==========================
```

**Result**: You now have an **unsigned** JUnit XML report at `junit.xml`.

**✓ Checkpoint**: Tests run successfully, JUnit XML report generated

---

## Step 3: Generate Signing Keys

Before we can sign reports, we need cryptographic keys.

### Generate RSA Key Pair

```bash
# Create directory for keys
mkdir -p ~/.ssh/jux

# Generate 4096-bit RSA key with certificate
jux-keygen \
  --type rsa \
  --bits 4096 \
  --output ~/.ssh/jux/tutorial-key.pem \
  --cert \
  --subject "CN=pytest-jux Tutorial" \
  --days-valid 365
```

**Expected Output**:
```
Generating RSA key...
  Key size: 4096 bits
  ✓ Private key saved: /Users/you/.ssh/jux/tutorial-key.pem
  ✓ Certificate saved: /Users/you/.ssh/jux/tutorial-key.crt
  ⚠ Self-signed certificate - NOT suitable for production use

Key generation complete!
```

### What Just Happened?

You generated two files:
1. **tutorial-key.pem**: Private key (keep this secret!)
2. **tutorial-key.crt**: Public certificate (share this freely)

**Security Note**: The private key should have permissions `600` (owner read/write only).

### Verify Key Permissions

```bash
# Check permissions
ls -la ~/.ssh/jux/

# Should show:
# -rw-------  1 you  staff  3.2K  tutorial-key.pem  (600 permissions)
# -rw-r--r--  1 you  staff  1.8K  tutorial-key.crt  (644 permissions)
```

**✓ Checkpoint**: Signing keys generated with correct permissions

---

## Step 4: Sign Your First Test Report

Now let's sign a test report using pytest integration.

### Run Tests with Automatic Signing

```bash
# Run tests with signing enabled
pytest \
  --junitxml=junit.xml \
  --jux-key ~/.ssh/jux/tutorial-key.pem \
  --jux-cert ~/.ssh/jux/tutorial-key.crt
```

**Expected Output**:
```
======================== test session starts =========================
collected 3 items

test_example.py ...                                            [100%]

======================== 3 passed in 0.12s ==========================

pytest-jux: Report signed and stored
  Hash: a1b2c3d4e5f6789...
  Signed report: /Users/you/.local/share/pytest-jux/reports/a1b2c3d4...xml
```

### What Just Happened?

pytest-jux automatically:
1. ✅ Generated JUnit XML report (`junit.xml`)
2. ✅ Signed the report with your private key
3. ✅ Added XMLDSig signature to the XML
4. ✅ Stored the signed report locally
5. ✅ Computed a canonical hash for duplicate detection

**✓ Checkpoint**: Test report signed successfully

---

## Step 5: Inspect the Signed Report

Let's examine what a signed report looks like.

### View Signed Report Structure

```bash
# Inspect the signed report
jux-inspect -i ~/.local/share/pytest-jux/reports/a1b2c3d4*.xml
```

**Expected Output**:
```
Report Statistics:
  Tests:     3
  Passed:    3
  Failed:    0
  Errors:    0
  Skipped:   0

Report Details:
  Canonical Hash: a1b2c3d4e5f6789...
  Signed:         Yes

Signature Information:
  Algorithm:      RSA-SHA256
  Key Size:       4096 bits
```

### View Signature in XML

```bash
# View last 30 lines of signed report (shows signature)
tail -30 ~/.local/share/pytest-jux/reports/a1b2c3d4*.xml
```

**Expected Output** (excerpt):
```xml
  </testsuite>

  <!-- Digital Signature -->
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="">
        <DigestValue>abc123...</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>xyz789...</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>MIIEpDCCA...</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
</testsuites>
```

**Key Elements**:
- `<CanonicalizationMethod>`: XML normalization algorithm (C14N)
- `<SignatureMethod>`: Signature algorithm (RSA-SHA256)
- `<DigestValue>`: Hash of canonical XML
- `<SignatureValue>`: Encrypted hash (digital signature)
- `<X509Certificate>`: Public certificate embedded in report

**✓ Checkpoint**: Understood signed report structure

---

## Step 6: Verify the Signature

Now let's verify the signature to prove the report is authentic and unmodified.

### Verify Signed Report

```bash
# Verify the signature
jux-verify \
  -i ~/.local/share/pytest-jux/reports/a1b2c3d4*.xml \
  --cert ~/.ssh/jux/tutorial-key.crt
```

**Expected Output**:
```
✓ Signature is valid

Signature Details:
  Algorithm:      RSA-SHA256
  Key Size:       4096 bits
  Signed At:      2025-10-20T14:30:00Z
  Verified At:    2025-10-20T14:35:00Z
  Status:         VALID
```

**✓ Checkpoint**: Signature verification successful

---

## Step 7: Test Tamper Detection

Let's prove that signatures detect tampering.

### Modify the Signed Report

```bash
# Copy the signed report
cp ~/.local/share/pytest-jux/reports/a1b2c3d4*.xml tampered-report.xml

# Modify the report (change test count)
sed -i.bak 's/tests="3"/tests="999"/' tampered-report.xml
```

### Attempt to Verify Tampered Report

```bash
# Try to verify tampered report
jux-verify -i tampered-report.xml --cert ~/.ssh/jux/tutorial-key.crt
```

**Expected Output**:
```
✗ Signature verification failed

Error: Signature verification failed - XML has been modified

The report has been tampered with or corrupted.
```

**What Happened?**
Even a tiny change (changing `tests="3"` to `tests="999"`) invalidates the signature. This proves the report was modified after signing.

**✓ Checkpoint**: Tamper detection works correctly

---

## Step 8: Inspect Report Metadata

Signed reports include environment metadata for reproducibility.

### View Report Metadata

```bash
# Show full report details with metadata
jux-inspect \
  -i ~/.local/share/pytest-jux/reports/a1b2c3d4*.xml \
  --json | python3 -m json.tool
```

**Expected Output** (excerpt):
```json
{
  "tests": 3,
  "passed": 3,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "canonical_hash": "a1b2c3d4e5f6789...",
  "signed": true,
  "metadata": {
    "hostname": "your-machine.local",
    "platform": "Darwin-23.5.0-arm64",
    "python_version": "3.11.14",
    "pytest_version": "8.0.0",
    "timestamp": "2025-10-20T14:30:00Z",
    "git_commit": "abc123...",
    "git_branch": "main"
  }
}
```

**Why Metadata Matters**:
- **Reproducibility**: Know exact environment that produced results
- **Debugging**: Identify environmental differences causing failures
- **Auditing**: Track when/where/how tests were run

**✓ Checkpoint**: Understood metadata capture

---

## Step 9: Understanding the Workflow

Let's review what we've accomplished:

```
┌─────────────────────┐
│  1. Generate Keys   │
│  (jux-keygen)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Run Tests       │
│  (pytest)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Sign Report     │
│  (automatic)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. Store Locally   │
│  (XDG cache)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. Verify          │
│  (jux-verify)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  6. Inspect         │
│  (jux-inspect)      │
└─────────────────────┘
```

---

## Summary: What You Accomplished

**✅ Completed**:
1. Installed pytest-jux
2. Created a sample test suite
3. Generated cryptographic signing keys (RSA 4096-bit)
4. Signed test reports automatically with pytest
5. Verified report signatures
6. Detected tampering attempts
7. Inspected report metadata

**🎓 Skills Learned**:
- Key generation with `jux-keygen`
- Automatic signing with pytest integration
- Signature verification with `jux-verify`
- Report inspection with `jux-inspect`
- Understanding XMLDSig signatures
- Tamper detection

---

## Next Steps

### Beginner → Intermediate

Now that you've mastered the basics, try:

1. **[CI/CD Integration](../howto/ci-cd-deployment.md)**: Integrate pytest-jux into GitHub Actions or GitLab CI
2. **[Multi-Environment Setup](../howto/multi-environment-config.md)**: Configure production, staging, and development environments
3. **[Advanced Tutorial](integration-testing.md)**: Learn to sign reports in complex projects

### Explore More

- **[Configuration Reference](../reference/configuration.md)**: Complete configuration options
- **[API Reference](../reference/api/index.md)**: Programmatic usage
- **[Security Best Practices](../explanation/security.md)**: Production deployment guidelines

---

## Troubleshooting

### "Private key not found"

**Problem**: pytest can't find your private key.

**Solution**: Use absolute path:
```bash
pytest \
  --junitxml=junit.xml \
  --jux-key /Users/you/.ssh/jux/tutorial-key.pem \
  --jux-cert /Users/you/.ssh/jux/tutorial-key.crt
```

---

### "Permission denied"

**Problem**: Key file has wrong permissions.

**Solution**: Fix permissions:
```bash
chmod 600 ~/.ssh/jux/tutorial-key.pem
chmod 644 ~/.ssh/jux/tutorial-key.crt
```

---

### "Signature verification failed" (unexpected)

**Problem**: Verification fails but report wasn't modified.

**Possible Causes**:
1. Using wrong certificate
2. Report was modified (even whitespace changes break signature)
3. XML encoding issues

**Solution**: Re-sign the report:
```bash
jux-sign \
  -i junit.xml \
  -o junit-signed.xml \
  --key ~/.ssh/jux/tutorial-key.pem \
  --cert ~/.ssh/jux/tutorial-key.crt
```

---

## Clean Up (Optional)

If you want to remove tutorial files:

```bash
# Remove test directory
cd ..
rm -rf my-first-signed-report

# Remove signing keys (CAUTION: Only if you don't need them)
rm ~/.ssh/jux/tutorial-key.pem
rm ~/.ssh/jux/tutorial-key.crt

# Clear cached reports
jux-cache purge
```

---

## Feedback

Was this tutorial helpful? Have suggestions for improvement?

- **Report Issues**: https://github.com/jrjsmrtn/pytest-jux/issues
- **Contribute**: PRs welcome for documentation improvements

---

**Tutorial Version**: 1.0
**pytest-jux Version**: 0.1.9
**Last Updated**: 2025-10-20
