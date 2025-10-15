# Test Cryptographic Keys

**⚠️ SECURITY WARNING**: These keys are for **TESTING PURPOSES ONLY**.

**NEVER** use these keys in production or for signing real data!

## Note on X.509 Certificates

Self-signed certificates (*.crt files) are included for testing certificate-based
signing. However, XMLDSig verification with self-signed certificates may fail
validation due to missing trust chains. This is expected behavior and does not
indicate a problem with the signing implementation.

For production use, proper X.509 certificates from a trusted Certificate Authority
should be used.

## Keys in this directory

### RSA Keys
- **rsa_2048.pem**: RSA 2048-bit private key (PKCS#1 format)
- **rsa_2048.pub**: Corresponding RSA public key

### ECDSA Keys
- **ecdsa_p256.pem**: ECDSA P-256 (secp256r1) private key
- **ecdsa_p256.pub**: Corresponding ECDSA public key

## Usage in Tests

These keys are used for testing XML digital signature generation and verification:

```python
from pathlib import Path

key_dir = Path(__file__).parent / "fixtures" / "keys"
rsa_key_path = key_dir / "rsa_2048.pem"
ecdsa_key_path = key_dir / "ecdsa_p256.pem"
```

## Regenerating Keys

If you need to regenerate these test keys:

```bash
# RSA 2048-bit
openssl genrsa -out tests/fixtures/keys/rsa_2048.pem 2048
openssl rsa -in tests/fixtures/keys/rsa_2048.pem -pubout -out tests/fixtures/keys/rsa_2048.pub

# ECDSA P-256
openssl ecparam -name prime256v1 -genkey -noout -out tests/fixtures/keys/ecdsa_p256.pem
openssl ec -in tests/fixtures/keys/ecdsa_p256.pem -pubout -out tests/fixtures/keys/ecdsa_p256.pub
```

## Security Note

These keys are committed to the repository for testing purposes. They should NEVER be used for:
- Production signing
- Real data signing
- Any security-sensitive operations

Always generate and securely store real keys outside of version control.
