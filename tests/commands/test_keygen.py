# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for jux-keygen command."""

import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509 import load_pem_x509_certificate

from pytest_jux.commands.keygen import (
    generate_ecdsa_key,
    generate_rsa_key,
    generate_self_signed_cert,
    main,
    save_key,
)


class TestGenerateRsaKey:
    """Tests for RSA key generation."""

    def test_generates_2048_bit_rsa_key(self) -> None:
        """Test that RSA 2048-bit key is generated correctly."""
        key = generate_rsa_key(2048)
        assert isinstance(key, rsa.RSAPrivateKey)
        assert key.key_size == 2048

    def test_generates_3072_bit_rsa_key(self) -> None:
        """Test that RSA 3072-bit key is generated correctly."""
        key = generate_rsa_key(3072)
        assert isinstance(key, rsa.RSAPrivateKey)
        assert key.key_size == 3072

    def test_generates_4096_bit_rsa_key(self) -> None:
        """Test that RSA 4096-bit key is generated correctly."""
        key = generate_rsa_key(4096)
        assert isinstance(key, rsa.RSAPrivateKey)
        assert key.key_size == 4096

    def test_rsa_key_has_public_exponent_65537(self) -> None:
        """Test that RSA key uses public exponent 65537 (F4)."""
        key = generate_rsa_key(2048)
        public_key = key.public_key()
        assert public_key.public_numbers().e == 65537

    def test_rejects_invalid_key_size(self) -> None:
        """Test that invalid key sizes are rejected."""
        with pytest.raises(ValueError, match="Key size must be"):
            generate_rsa_key(1024)

    def test_generated_keys_are_unique(self) -> None:
        """Test that multiple generations produce different keys."""
        key1 = generate_rsa_key(2048)
        key2 = generate_rsa_key(2048)

        # Serialize both keys
        pem1 = key1.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pem2 = key2.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        assert pem1 != pem2


class TestGenerateEcdsaKey:
    """Tests for ECDSA key generation."""

    def test_generates_p256_ecdsa_key(self) -> None:
        """Test that ECDSA P-256 key is generated correctly."""
        key = generate_ecdsa_key("P-256")
        assert isinstance(key, ec.EllipticCurvePrivateKey)
        assert isinstance(key.curve, ec.SECP256R1)

    def test_generates_p384_ecdsa_key(self) -> None:
        """Test that ECDSA P-384 key is generated correctly."""
        key = generate_ecdsa_key("P-384")
        assert isinstance(key, ec.EllipticCurvePrivateKey)
        assert isinstance(key.curve, ec.SECP384R1)

    def test_generates_p521_ecdsa_key(self) -> None:
        """Test that ECDSA P-521 key is generated correctly."""
        key = generate_ecdsa_key("P-521")
        assert isinstance(key, ec.EllipticCurvePrivateKey)
        assert isinstance(key.curve, ec.SECP521R1)

    def test_rejects_invalid_curve(self) -> None:
        """Test that invalid curves are rejected."""
        with pytest.raises(ValueError, match="Unsupported curve"):
            generate_ecdsa_key("P-128")

    def test_generated_ecdsa_keys_are_unique(self) -> None:
        """Test that multiple generations produce different ECDSA keys."""
        key1 = generate_ecdsa_key("P-256")
        key2 = generate_ecdsa_key("P-256")

        # Serialize both keys
        pem1 = key1.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pem2 = key2.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        assert pem1 != pem2


class TestSaveKey:
    """Tests for key saving functionality."""

    def test_saves_rsa_key_to_file(self, tmp_path: Path) -> None:
        """Test that RSA key is saved correctly."""
        key = generate_rsa_key(2048)
        output_path = tmp_path / "test_key.pem"

        save_key(key, output_path)

        assert output_path.exists()
        assert output_path.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----")

    def test_saves_ecdsa_key_to_file(self, tmp_path: Path) -> None:
        """Test that ECDSA key is saved correctly."""
        key = generate_ecdsa_key("P-256")
        output_path = tmp_path / "test_key.pem"

        save_key(key, output_path)

        assert output_path.exists()
        assert output_path.read_bytes().startswith(b"-----BEGIN PRIVATE KEY-----")

    def test_sets_secure_file_permissions(self, tmp_path: Path) -> None:
        """Test that private key file has 0600 permissions."""
        key = generate_rsa_key(2048)
        output_path = tmp_path / "test_key.pem"

        save_key(key, output_path)

        # Check file permissions (owner read/write only)
        file_stat = output_path.stat()
        permissions = stat.filemode(file_stat.st_mode)
        assert permissions == "-rw-------"

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        """Test that existing key file is overwritten."""
        key1 = generate_rsa_key(2048)
        key2 = generate_rsa_key(2048)
        output_path = tmp_path / "test_key.pem"

        save_key(key1, output_path)
        original_content = output_path.read_bytes()

        save_key(key2, output_path)
        new_content = output_path.read_bytes()

        assert original_content != new_content

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that parent directories are created if they don't exist."""
        key = generate_rsa_key(2048)
        output_path = tmp_path / "subdir" / "test_key.pem"

        save_key(key, output_path)

        assert output_path.exists()


class TestGenerateSelfSignedCert:
    """Tests for self-signed certificate generation."""

    def test_generates_cert_for_rsa_key(self, tmp_path: Path) -> None:
        """Test that self-signed certificate is generated for RSA key."""
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "test_cert.crt"

        generate_self_signed_cert(key, cert_path, "Test Subject")

        assert cert_path.exists()
        cert_data = cert_path.read_bytes()
        assert cert_data.startswith(b"-----BEGIN CERTIFICATE-----")

    def test_generates_cert_for_ecdsa_key(self, tmp_path: Path) -> None:
        """Test that self-signed certificate is generated for ECDSA key."""
        key = generate_ecdsa_key("P-256")
        cert_path = tmp_path / "test_cert.crt"

        generate_self_signed_cert(key, cert_path, "Test Subject")

        assert cert_path.exists()
        cert_data = cert_path.read_bytes()
        assert cert_data.startswith(b"-----BEGIN CERTIFICATE-----")

    def test_cert_has_correct_subject(self, tmp_path: Path) -> None:
        """Test that certificate has the specified subject."""
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "test_cert.crt"
        subject_name = "CN=test.example.com"

        generate_self_signed_cert(key, cert_path, subject_name)

        cert = load_pem_x509_certificate(cert_path.read_bytes())
        # The subject should contain the CN
        subject_str = cert.subject.rfc4514_string()
        assert "test.example.com" in subject_str

    def test_cert_validity_period(self, tmp_path: Path) -> None:
        """Test that certificate has appropriate validity period."""
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "test_cert.crt"

        generate_self_signed_cert(key, cert_path, "Test Subject", days_valid=365)

        cert = load_pem_x509_certificate(cert_path.read_bytes())
        validity_seconds = (
            cert.not_valid_after_utc - cert.not_valid_before_utc
        ).total_seconds()

        # Should be approximately 365 days (within 1 hour tolerance)
        expected_seconds = 365 * 24 * 60 * 60
        assert abs(validity_seconds - expected_seconds) < 3600


class TestMainCommand:
    """Tests for main command-line interface."""

    def test_generates_rsa_key_via_cli(self, tmp_path: Path) -> None:
        """Test generating RSA key via CLI."""
        output_path = tmp_path / "key.pem"

        with patch(
            "sys.argv",
            [
                "jux-keygen",
                "--type",
                "rsa",
                "--bits",
                "2048",
                "--output",
                str(output_path),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_generates_ecdsa_key_via_cli(self, tmp_path: Path) -> None:
        """Test generating ECDSA key via CLI."""
        output_path = tmp_path / "key.pem"

        with patch(
            "sys.argv",
            [
                "jux-keygen",
                "--type",
                "ecdsa",
                "--curve",
                "P-256",
                "--output",
                str(output_path),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_generates_key_with_certificate(self, tmp_path: Path) -> None:
        """Test generating key with self-signed certificate."""
        key_path = tmp_path / "key.pem"
        cert_path = tmp_path / "key.crt"

        with patch(
            "sys.argv",
            [
                "jux-keygen",
                "--type",
                "rsa",
                "--bits",
                "2048",
                "--output",
                str(key_path),
                "--cert",
                "--subject",
                "CN=test.example.com",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert key_path.exists()
        assert cert_path.exists()

    def test_requires_output_path(self) -> None:
        """Test that output path is required."""
        with patch("sys.argv", ["jux-keygen", "--type", "rsa"]):
            with pytest.raises(SystemExit):
                main()

    def test_validates_key_type(self, tmp_path: Path) -> None:
        """Test that invalid key type is rejected."""
        output_path = tmp_path / "key.pem"

        with patch(
            "sys.argv",
            ["jux-keygen", "--type", "invalid", "--output", str(output_path)],
        ):
            with pytest.raises((ValueError, SystemExit)):
                main()

    def test_default_rsa_key_size_is_2048(self, tmp_path: Path) -> None:
        """Test that default RSA key size is 2048 bits."""
        output_path = tmp_path / "key.pem"

        with patch(
            "sys.argv", ["jux-keygen", "--type", "rsa", "--output", str(output_path)]
        ):
            exit_code = main()

        assert exit_code == 0
        # Load the key and check size
        from pytest_jux.signer import load_private_key

        key = load_private_key(output_path)
        assert isinstance(key, rsa.RSAPrivateKey)
        assert key.key_size == 2048

    def test_default_ecdsa_curve_is_p256(self, tmp_path: Path) -> None:
        """Test that default ECDSA curve is P-256."""
        output_path = tmp_path / "key.pem"

        with patch(
            "sys.argv", ["jux-keygen", "--type", "ecdsa", "--output", str(output_path)]
        ):
            exit_code = main()

        assert exit_code == 0
        # Load the key and check curve
        from pytest_jux.signer import load_private_key

        key = load_private_key(output_path)
        assert isinstance(key, ec.EllipticCurvePrivateKey)
        assert isinstance(key.curve, ec.SECP256R1)

    def test_displays_help_text(self) -> None:
        """Test that help text is displayed."""
        with patch("sys.argv", ["jux-keygen", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Help should exit with code 0
            assert exc_info.value.code == 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handles_permission_error_gracefully(self, tmp_path: Path) -> None:
        """Test that permission errors are handled gracefully."""
        key = generate_rsa_key(2048)
        # Try to save to a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        output_path = readonly_dir / "key.pem"

        with pytest.raises(PermissionError):
            save_key(key, output_path)

    def test_handles_invalid_output_path(self) -> None:
        """Test that invalid output paths are rejected."""
        key = generate_rsa_key(2048)

        with pytest.raises((OSError, ValueError)):
            save_key(key, Path("/invalid/path/key.pem"))

    def test_cert_generation_without_subject(self, tmp_path: Path) -> None:
        """Test that certificate generation requires a subject."""
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "cert.crt"

        # Should use a default subject if none provided
        generate_self_signed_cert(key, cert_path)

        assert cert_path.exists()
