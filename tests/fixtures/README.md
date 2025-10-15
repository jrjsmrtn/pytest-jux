# Test Fixtures

This directory contains test fixtures for pytest-jux development and testing.

## JUnit XML Fixtures (`junit_xml/`)

Sample JUnit XML files for testing XML canonicalization and signing:

- **simple.xml**: Minimal JUnit XML with 1 passing test
- **passing.xml**: Multiple passing tests
- **failing.xml**: Test suite with 1 failure
- **namespaced.xml**: XML with namespaces (tests C14N)

### Usage

```python
import pytest
from pathlib import Path

@pytest.fixture
def junit_xml_simple():
    return Path(__file__).parent / "junit_xml" / "simple.xml"

def test_canonicalize(junit_xml_simple):
    xml_content = junit_xml_simple.read_text()
    # Test canonicalization...
```

## Cryptographic Keys (`keys/`)

**⚠️ SECURITY WARNING**: Keys in this directory are for **TESTING ONLY**. Never use these keys in production or commit real private keys to the repository!

Test keys will be generated programmatically during test runs or can be generated manually:

```bash
# Generate RSA test key
openssl genrsa -out tests/fixtures/keys/rsa_2048.pem 2048
openssl rsa -in tests/fixtures/keys/rsa_2048.pem -pubout -out tests/fixtures/keys/rsa_2048.pub

# Generate ECDSA test key
openssl ecparam -name prime256v1 -genkey -noout -out tests/fixtures/keys/ecdsa_p256.pem
openssl ec -in tests/fixtures/keys/ecdsa_p256.pem -pubout -out tests/fixtures/keys/ecdsa_p256.pub
```

### Key Types

- **RSA 2048-bit**: Standard RSA key for XMLDSig (RSA-SHA256)
- **ECDSA P-256**: Elliptic curve key for XMLDSig (ECDSA-SHA256)

## Adding New Fixtures

When adding new fixtures:

1. Place them in the appropriate subdirectory
2. Use descriptive filenames
3. Document them in this README
4. Ensure they don't contain sensitive data
5. Add corresponding test cases
