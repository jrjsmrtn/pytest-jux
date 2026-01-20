# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests using shared JUnit XML fixtures.

These tests verify that pytest-jux can handle real-world JUnit XML
files from the shared junit-xml-test-fixtures repository.
"""

from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.canonicalizer import canonicalize_xml, compute_canonical_hash, load_xml
from pytest_jux.signer import load_private_key, sign_xml
from pytest_jux.verifier import verify_signature

# Import has_signature from juxlib (not re-exported in pytest_jux)
from juxlib.signing import has_signature

from conftest import (
    KEYS_DIR,
    get_local_junit_xml_files,
    get_testmoapp_xml_files,
)

# Get fixture file lists for parametrization
TESTMOAPP_FILES = get_testmoapp_xml_files()
LOCAL_FILES = get_local_junit_xml_files()

# Test key paths
RSA_KEY_PATH = KEYS_DIR / "rsa_2048.pem"
RSA_CERT_PATH = KEYS_DIR / "rsa_2048.crt"


@pytest.fixture
def rsa_key():
    """Load RSA private key for signing tests."""
    if not RSA_KEY_PATH.exists():
        pytest.skip("Test RSA key not available")
    return load_private_key(RSA_KEY_PATH)


@pytest.fixture
def rsa_cert_text():
    """Load RSA certificate as text for signing tests."""
    if not RSA_CERT_PATH.exists():
        pytest.skip("Test RSA certificate not available")
    return RSA_CERT_PATH.read_text()


# =============================================================================
# Test Loading XML Files
# =============================================================================


@pytest.mark.shared_fixtures
class TestLoadXMLWithSharedFixtures:
    """Test XML loading with shared JUnit XML fixtures."""

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_load_testmoapp_examples(self, xml_file: Path) -> None:
        """Verify we can load all testmoapp example files."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        # All testmoapp examples have testsuites or testsuite as root
        assert tree.tag in ("testsuites", "testsuite")

    @pytest.mark.parametrize(
        "xml_file",
        LOCAL_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_load_local_fixtures(self, xml_file: Path) -> None:
        """Verify we can load local JUnit XML fixtures."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        # Local fixtures have testsuites or testsuite as root
        # Handle namespaced tags by extracting local name
        local_tag = tree.tag.split("}")[-1] if "}" in tree.tag else tree.tag
        assert local_tag in ("testsuites", "testsuite")


# =============================================================================
# Test Canonicalization
# =============================================================================


@pytest.mark.shared_fixtures
class TestCanonicalizeWithSharedFixtures:
    """Test XML canonicalization with shared fixtures."""

    def test_canonicalize_junit_complete(self, junit_complete_xml: str) -> None:
        """Canonicalize complete JUnit XML produces consistent output."""
        tree = load_xml(junit_complete_xml)

        c14n_bytes = canonicalize_xml(tree)

        # C14N output should be bytes
        assert isinstance(c14n_bytes, bytes)
        # Should contain the XML content
        assert b"<testsuites" in c14n_bytes
        assert b"Tests.Registration" in c14n_bytes

    def test_canonicalize_produces_consistent_hash(
        self, junit_complete_xml: str
    ) -> None:
        """Same XML content produces same canonical hash."""
        tree1 = load_xml(junit_complete_xml)
        tree2 = load_xml(junit_complete_xml)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_canonicalize_all_testmoapp_files(self, xml_file: Path) -> None:
        """All testmoapp files can be canonicalized."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)
        c14n_bytes = canonicalize_xml(tree)

        assert isinstance(c14n_bytes, bytes)
        assert len(c14n_bytes) > 0


# =============================================================================
# Test Signing
# =============================================================================


@pytest.mark.shared_fixtures
class TestSigningWithSharedFixtures:
    """Test XML signing with shared JUnit XML fixtures."""

    def test_sign_junit_complete(
        self, junit_complete_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign complete JUnit XML file."""
        tree = load_xml(junit_complete_xml)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    def test_sign_and_verify_junit_complete(
        self, junit_complete_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign and verify complete JUnit XML file."""
        tree = load_xml(junit_complete_xml)
        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        # Verification should succeed (requires certificate for self-signed)
        is_valid = verify_signature(signed_tree, rsa_cert_text)
        assert is_valid is True

    def test_sign_junit_basic(
        self, junit_basic_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign basic JUnit XML file."""
        tree = load_xml(junit_basic_xml)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_all_testmoapp_files(
        self, xml_file: Path, rsa_key, rsa_cert_text
    ) -> None:
        """All testmoapp files can be signed."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_and_verify_all_testmoapp_files(
        self, xml_file: Path, rsa_key, rsa_cert_text
    ) -> None:
        """All testmoapp files can be signed and verified."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)
        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        # Verification requires certificate for self-signed certs
        is_valid = verify_signature(signed_tree, rsa_cert_text)

        assert is_valid is True


# =============================================================================
# Test Hash Consistency
# =============================================================================


@pytest.mark.shared_fixtures
class TestHashConsistencyWithSharedFixtures:
    """Test hash computation consistency with shared fixtures."""

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_hash_is_deterministic(self, xml_file: Path) -> None:
        """Same file produces same hash on multiple loads."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree1 = load_xml(xml_file)
        tree2 = load_xml(xml_file)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

    def test_different_files_produce_different_hashes(
        self,
        junit_basic_xml: str,
        junit_complete_xml: str,
    ) -> None:
        """Different XML files produce different hashes."""
        tree1 = load_xml(junit_basic_xml)
        tree2 = load_xml(junit_complete_xml)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 != hash2


# =============================================================================
# Test XML Structure Parsing
# =============================================================================


@pytest.mark.shared_fixtures
class TestXMLStructureWithSharedFixtures:
    """Test XML structure parsing with shared fixtures."""

    def test_junit_complete_has_properties(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has properties element."""
        tree = load_xml(junit_complete_xml)

        properties = tree.find(".//properties")

        assert properties is not None
        # Should have multiple property elements
        property_elements = properties.findall("property")
        assert len(property_elements) > 0

    def test_junit_complete_has_testcases(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has testcase elements."""
        tree = load_xml(junit_complete_xml)

        testcases = tree.findall(".//testcase")

        assert len(testcases) > 0
        # Each testcase should have name attribute
        for tc in testcases:
            assert tc.get("name") is not None

    def test_junit_complete_has_results(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has failure/error/skipped elements."""
        tree = load_xml(junit_complete_xml)

        failures = tree.findall(".//failure")
        errors = tree.findall(".//error")
        skipped = tree.findall(".//skipped")

        # junit-complete.xml should have at least one of each
        assert len(failures) >= 1
        assert len(errors) >= 1
        assert len(skipped) >= 1

    def test_extract_testsuite_attributes(self, junit_complete_xml: str) -> None:
        """Can extract testsuite attributes from complete JUnit XML."""
        tree = load_xml(junit_complete_xml)

        testsuite = tree.find(".//testsuite")

        assert testsuite is not None
        assert testsuite.get("name") == "Tests.Registration"
        assert testsuite.get("tests") == "8"
        assert testsuite.get("failures") == "1"
        assert testsuite.get("errors") == "1"


# =============================================================================
# Test Local Fixtures
# =============================================================================


class TestLocalFixtures:
    """Test with local JUnit XML fixtures."""

    @pytest.mark.parametrize(
        "xml_file",
        LOCAL_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_canonicalize_local_fixtures(self, xml_file: Path) -> None:
        """All local fixtures can be canonicalized."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)
        c14n_bytes = canonicalize_xml(tree)

        assert isinstance(c14n_bytes, bytes)
        assert len(c14n_bytes) > 0

    @pytest.mark.parametrize(
        "xml_file",
        LOCAL_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_local_fixtures(
        self, xml_file: Path, rsa_key, rsa_cert_text
    ) -> None:
        """All local fixtures can be signed."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)
