# Copyright 2025 Georges Martin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for jux-verify command."""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from pytest_jux.canonicalizer import load_xml
from pytest_jux.commands.keygen import (
    generate_ecdsa_key,
    generate_rsa_key,
    generate_self_signed_cert,
    save_key,
)
from pytest_jux.commands.verify import main
from pytest_jux.signer import sign_xml


@pytest.fixture
def signed_xml(tmp_path: Path) -> tuple[Path, Path]:
    """Create a signed XML file with certificate."""
    # Create test XML
    xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
    xml_path = tmp_path / "test.xml"
    xml_path.write_text(xml_content)

    # Generate key and certificate
    key = generate_rsa_key(2048)
    key_path = tmp_path / "key.pem"
    save_key(key, key_path)

    cert_path = tmp_path / "cert.crt"
    generate_self_signed_cert(key, cert_path)
    cert = cert_path.read_bytes()

    # Sign XML
    tree = load_xml(xml_path)
    signed_tree = sign_xml(tree, key, cert)

    # Save signed XML
    signed_path = tmp_path / "signed.xml"
    signed_path.write_bytes(
        etree.tostring(signed_tree, xml_declaration=True, encoding="utf-8")
    )

    return signed_path, cert_path


class TestVerifyCommand:
    """Tests for jux-verify CLI command."""

    def test_verifies_valid_signature(self, signed_xml: tuple[Path, Path]) -> None:
        """Test verification of valid signature."""
        signed_path, cert_path = signed_xml

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path)],
        ):
            exit_code = main()

        assert exit_code == 0

    def test_verifies_from_stdin(self, signed_xml: tuple[Path, Path]) -> None:
        """Test verification from stdin."""
        signed_path, cert_path = signed_xml
        signed_content = signed_path.read_text()

        mock_stdin = StringIO(signed_content)

        with (
            patch.object(sys, "argv", ["jux-verify", "--cert", str(cert_path)]),
            patch("sys.stdin", mock_stdin),
        ):
            exit_code = main()

        assert exit_code == 0

    def test_fails_for_tampered_xml(
        self, signed_xml: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Test verification fails for tampered XML."""
        signed_path, cert_path = signed_xml

        # Tamper with the signed XML
        tree = load_xml(signed_path)
        testcase = tree.find(".//testcase")
        assert testcase is not None
        testcase.set("name", "tampered_test")

        tampered_path = tmp_path / "tampered.xml"
        tampered_path.write_bytes(
            etree.tostring(tree, xml_declaration=True, encoding="utf-8")
        )

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", str(tampered_path), "--cert", str(cert_path)],
        ):
            exit_code = main()

        assert exit_code == 1

    def test_fails_for_unsigned_xml(self, tmp_path: Path) -> None:
        """Test verification fails for unsigned XML."""
        # Create unsigned XML
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "unsigned.xml"
        xml_path.write_text(xml_content)

        # Generate certificate
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key, cert_path)

        with patch.object(
            sys, "argv", ["jux-verify", "-i", str(xml_path), "--cert", str(cert_path)]
        ):
            exit_code = main()

        assert exit_code == 1

    def test_fails_for_missing_input_file(self, signed_xml: tuple[Path, Path]) -> None:
        """Test error handling for missing input file."""
        _, cert_path = signed_xml

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", "/nonexistent.xml", "--cert", str(cert_path)],
        ):
            exit_code = main()

        assert exit_code == 1

    def test_fails_for_missing_certificate_file(
        self, signed_xml: tuple[Path, Path]
    ) -> None:
        """Test error handling for missing certificate file."""
        signed_path, _ = signed_xml

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", str(signed_path), "--cert", "/nonexistent.crt"],
        ):
            exit_code = main()

        assert exit_code == 1

    def test_quiet_mode_with_stdout(self, signed_xml: tuple[Path, Path]) -> None:
        """Test quiet mode when outputting to stdout."""
        signed_path, cert_path = signed_xml

        # Capture stdout and stderr
        captured_stdout = StringIO()
        captured_stderr = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path), "-q"],
            ),
            patch("sys.stdout", captured_stdout),
            patch("sys.stderr", captured_stderr),
        ):
            exit_code = main()

        assert exit_code == 0
        # Quiet mode should produce no output
        assert captured_stdout.getvalue() == ""
        assert captured_stderr.getvalue() == ""

    def test_uses_certificate_from_env_var(
        self, signed_xml: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading certificate from environment variable."""
        signed_path, cert_path = signed_xml
        monkeypatch.setenv("JUX_CERT_PATH", str(cert_path))

        with patch.object(sys, "argv", ["jux-verify", "-i", str(signed_path)]):
            exit_code = main()

        assert exit_code == 0

    def test_verifies_ecdsa_signature(self, tmp_path: Path) -> None:
        """Test verification of ECDSA signature."""
        # Create test XML
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "test.xml"
        xml_path.write_text(xml_content)

        # Generate ECDSA key and certificate
        key = generate_ecdsa_key("P-256")
        key_path = tmp_path / "key.pem"
        save_key(key, key_path)

        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key, cert_path)
        cert = cert_path.read_bytes()

        # Sign XML
        tree = load_xml(xml_path)
        signed_tree = sign_xml(tree, key, cert)

        # Save signed XML
        signed_path = tmp_path / "signed.xml"
        signed_path.write_bytes(
            etree.tostring(signed_tree, xml_declaration=True, encoding="utf-8")
        )

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path)],
        ):
            exit_code = main()

        assert exit_code == 0

    def test_json_output(self, signed_xml: tuple[Path, Path]) -> None:
        """Test JSON output format."""
        signed_path, cert_path = signed_xml

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                [
                    "jux-verify",
                    "-i",
                    str(signed_path),
                    "--cert",
                    str(cert_path),
                    "--json",
                ],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = captured_stdout.getvalue()
        assert '"valid": true' in output or '"valid":true' in output

    def test_json_output_for_invalid_signature(
        self, signed_xml: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Test JSON output format for invalid signature."""
        signed_path, cert_path = signed_xml

        # Tamper with the signed XML
        tree = load_xml(signed_path)
        testcase = tree.find(".//testcase")
        assert testcase is not None
        testcase.set("name", "tampered_test")

        tampered_path = tmp_path / "tampered.xml"
        tampered_path.write_bytes(
            etree.tostring(tree, xml_declaration=True, encoding="utf-8")
        )

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                [
                    "jux-verify",
                    "-i",
                    str(tampered_path),
                    "--cert",
                    str(cert_path),
                    "--json",
                ],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 1
        output = captured_stdout.getvalue()
        assert '"valid": false' in output or '"valid":false' in output

    def test_missing_input_file_with_json(self, signed_xml: tuple[Path, Path]) -> None:
        """Test missing input file with JSON output."""
        _, cert_path = signed_xml

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", "/nonexistent.xml", "--cert", str(cert_path), "--json"],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 1

    def test_missing_cert_with_json(self, signed_xml: tuple[Path, Path]) -> None:
        """Test missing certificate with JSON output."""
        signed_path, _ = signed_xml

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", "/nonexistent.crt", "--json"],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 1

    def test_verification_value_error_with_json(self, tmp_path: Path) -> None:
        """Test ValueError from verification with JSON output."""
        # Create unsigned XML (will raise ValueError: No signature found)
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "unsigned.xml"
        xml_path.write_text(xml_content)

        # Generate certificate
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key, cert_path)

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(xml_path), "--cert", str(cert_path), "--json"],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 1
        output = captured_stdout.getvalue()
        assert "error" in output.lower()

    def test_verification_value_error_quiet_mode(self, tmp_path: Path) -> None:
        """Test ValueError from verification with quiet mode."""
        # Create unsigned XML (will raise ValueError: No signature found)
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "unsigned.xml"
        xml_path.write_text(xml_content)

        # Generate certificate
        key = generate_rsa_key(2048)
        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key, cert_path)

        with patch.object(
            sys,
            "argv",
            ["jux-verify", "-i", str(xml_path), "--cert", str(cert_path), "-q"],
        ):
            exit_code = main()

        assert exit_code == 1

    def test_success_with_quiet_and_json(self, signed_xml: tuple[Path, Path]) -> None:
        """Test successful verification with both quiet and JSON flags."""
        signed_path, cert_path = signed_xml

        captured_stdout = StringIO()

        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path), "-q", "--json"],
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        # Even with quiet, JSON output should be produced
        output = captured_stdout.getvalue()
        assert '"valid": true' in output or '"valid":true' in output

    def test_generic_exception_with_json(self, signed_xml: tuple[Path, Path]) -> None:
        """Test generic exception handling with JSON output."""
        signed_path, cert_path = signed_xml

        captured_stdout = StringIO()

        # Mock load_xml to raise generic exception
        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path), "--json"],
            ),
            patch("sys.stdout", captured_stdout),
            patch("pytest_jux.commands.verify.load_xml", side_effect=RuntimeError("Unexpected error")),
        ):
            exit_code = main()

        assert exit_code == 1
        output = captured_stdout.getvalue()
        assert "error" in output.lower()
        assert "unexpected error" in output.lower()

    def test_generic_exception_with_quiet(self, signed_xml: tuple[Path, Path]) -> None:
        """Test generic exception handling with quiet mode."""
        signed_path, cert_path = signed_xml

        captured_stderr = StringIO()

        # Mock load_xml to raise generic exception
        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path), "-q"],
            ),
            patch("sys.stderr", captured_stderr),
            patch("pytest_jux.commands.verify.load_xml", side_effect=RuntimeError("Unexpected error")),
        ):
            exit_code = main()

        assert exit_code == 1
        # Quiet mode suppresses error output
        output = captured_stderr.getvalue()
        assert output == ""

    def test_generic_exception_normal_output(self, signed_xml: tuple[Path, Path]) -> None:
        """Test generic exception handling with normal output."""
        signed_path, cert_path = signed_xml

        captured_stderr = StringIO()

        # Mock load_xml to raise generic exception
        with (
            patch.object(
                sys,
                "argv",
                ["jux-verify", "-i", str(signed_path), "--cert", str(cert_path)],
            ),
            patch("sys.stderr", captured_stderr),
            patch("pytest_jux.commands.verify.load_xml", side_effect=RuntimeError("Unexpected error")),
        ):
            exit_code = main()

        assert exit_code == 1
        output = captured_stderr.getvalue()
        assert "Error:" in output
        assert "Unexpected error" in output
