# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests using local JUnit XML fixtures.

These tests verify that pytest-jux can handle JUnit XML files
from the local test fixtures.
"""

from pathlib import Path

import pytest
from conftest import (
    KEYS_DIR,
    get_local_junit_xml_files,
)

# Import has_signature from juxlib (not re-exported in pytest_jux)
from juxlib.signing import has_signature

from pytest_jux.canonicalizer import canonicalize_xml, compute_canonical_hash, load_xml
from pytest_jux.signer import load_private_key, sign_xml

# Get fixture file lists for parametrization
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
# Test Local Fixtures
# =============================================================================


class TestLocalFixtures:
    """Test with local JUnit XML fixtures."""

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
    def test_hash_is_deterministic(self, xml_file: Path) -> None:
        """Same file produces same hash on multiple loads."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree1 = load_xml(xml_file)
        tree2 = load_xml(xml_file)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

    @pytest.mark.parametrize(
        "xml_file",
        LOCAL_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_local_fixtures(self, xml_file: Path, rsa_key, rsa_cert_text) -> None:
        """All local fixtures can be signed."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)
