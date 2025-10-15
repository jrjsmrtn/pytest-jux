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

"""Tests for pytest plugin hooks."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from lxml import etree

from pytest_jux.plugin import pytest_addoption, pytest_configure, pytest_sessionfinish


@pytest.fixture
def mock_parser() -> Mock:
    """Return a mock pytest parser."""
    parser = Mock()
    parser.getgroup = Mock(return_value=Mock())
    return parser


@pytest.fixture
def mock_config() -> Mock:
    """Return a mock pytest config."""
    config = Mock()
    config.getoption = Mock(return_value=None)
    config.pluginmanager = Mock()
    config.option = Mock()
    return config


@pytest.fixture
def mock_session() -> Mock:
    """Return a mock pytest session."""
    session = Mock()
    session.config = Mock()
    session.config.getoption = Mock(return_value=None)
    session.config.option = Mock()
    return session


@pytest.fixture
def test_key_path(tmp_path: Path) -> Path:
    """Create a test key file."""
    key_path = tmp_path / "test_key.pem"
    # Copy actual test key
    import shutil

    fixture_key = Path(__file__).parent / "fixtures" / "keys" / "rsa_2048.pem"
    shutil.copy(fixture_key, key_path)
    return key_path


@pytest.fixture
def test_cert_path(tmp_path: Path) -> Path:
    """Create a test certificate file."""
    cert_path = tmp_path / "test_cert.crt"
    # Copy actual test certificate
    import shutil

    fixture_cert = Path(__file__).parent / "fixtures" / "keys" / "rsa_2048.crt"
    shutil.copy(fixture_cert, cert_path)
    return cert_path


@pytest.fixture
def test_junit_xml(tmp_path: Path) -> Path:
    """Create a test JUnit XML file."""
    xml_path = tmp_path / "junit.xml"
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
    xml_path.write_text(xml_content)
    return xml_path


class TestPytestAddoption:
    """Tests for pytest_addoption hook."""

    def test_adds_jux_group(self, mock_parser: Mock) -> None:
        """Test that plugin adds Jux option group."""
        pytest_addoption(mock_parser)
        mock_parser.getgroup.assert_called_once_with(
            "jux", "Jux test report signing and publishing"
        )

    def test_adds_jux_sign_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-sign option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-sign option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-sign" in str(call) for call in calls)

    def test_adds_jux_key_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-key option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-key option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-key" in str(call) for call in calls)

    def test_adds_jux_cert_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-cert option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-cert option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-cert" in str(call) for call in calls)

    def test_adds_jux_publish_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-publish option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-publish option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-publish" in str(call) for call in calls)


class TestPytestConfigure:
    """Tests for pytest_configure hook."""

    def test_configure_without_signing(self, mock_config: Mock) -> None:
        """Test configuration when signing is disabled."""
        mock_config.getoption.return_value = False

        # Should not raise any errors
        pytest_configure(mock_config)

    def test_configure_with_signing_enabled(
        self, mock_config: Mock, test_key_path: Path
    ) -> None:
        """Test configuration when signing is enabled."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)

        # Should not raise any errors
        pytest_configure(mock_config)

    def test_configure_validates_key_path(self, mock_config: Mock) -> None:
        """Test that configure validates key path when signing enabled."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": None,
            "jux_cert": None,
        }.get(x)

        # Should raise error if signing enabled but no key provided
        with pytest.raises((ValueError, pytest.UsageError)):
            pytest_configure(mock_config)

    def test_configure_stores_settings_in_config(
        self, mock_config: Mock, test_key_path: Path
    ) -> None:
        """Test that configure stores settings in config object."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)

        pytest_configure(mock_config)

        # Verify settings were stored
        assert hasattr(mock_config, "_jux_sign")
        assert mock_config._jux_sign is True


class TestPytestSessionfinish:
    """Tests for pytest_sessionfinish hook."""

    def test_does_nothing_when_signing_disabled(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test that hook does nothing when signing is disabled."""
        mock_session.config._jux_sign = False
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should not raise any errors
        pytest_sessionfinish(mock_session, 0)

        # XML should be unchanged
        original_content = test_junit_xml.read_text()
        assert "<Signature" not in original_content

    def test_does_nothing_without_junit_xml(self, mock_session: Mock) -> None:
        """Test that hook does nothing when no JUnit XML is configured."""
        mock_session.config._jux_sign = True
        mock_session.config.option.xmlpath = None

        # Should not raise any errors
        pytest_sessionfinish(mock_session, 0)

    def test_signs_junit_xml_when_enabled(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        test_cert_path: Path,
    ) -> None:
        """Test that hook signs JUnit XML when signing is enabled."""
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = str(test_cert_path)
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify XML was signed
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_signs_junit_xml_without_certificate(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that hook can sign JUnit XML without certificate."""
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify XML was signed
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_preserves_original_junit_xml_content(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that signing preserves original JUnit XML content."""
        # Read original content
        original_tree = etree.parse(str(test_junit_xml))
        original_testcase = original_tree.find(".//testcase")
        assert original_testcase is not None
        original_name = original_testcase.get("name")

        # Configure and sign
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        pytest_sessionfinish(mock_session, 0)

        # Verify original content is preserved
        signed_tree = etree.parse(str(test_junit_xml))
        signed_testcase = signed_tree.find(".//testcase")
        assert signed_testcase is not None
        assert signed_testcase.get("name") == original_name

    def test_handles_invalid_key_path(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test that hook handles invalid key path gracefully."""
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = "/nonexistent/key.pem"
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should issue a warning but not fail the test run
        with pytest.warns(UserWarning, match="Failed to sign JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)

    def test_handles_invalid_xml(
        self, mock_session: Mock, test_key_path: Path, tmp_path: Path
    ) -> None:
        """Test that hook handles invalid XML gracefully."""
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("not valid xml")

        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(invalid_xml)

        # Should issue a warning but not fail the test run
        with pytest.warns(UserWarning, match="Failed to sign JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)


class TestPluginIntegration:
    """Integration tests for the full plugin workflow."""

    def test_full_workflow_with_signing(
        self, mock_parser: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test complete workflow: configure → sign → verify."""
        # Step 1: Add options
        pytest_addoption(mock_parser)
        assert mock_parser.getgroup.called

        # Step 2: Configure
        mock_config = Mock()
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)
        pytest_configure(mock_config)

        # Step 3: Run sessionfinish
        mock_session = Mock()
        mock_session.config = mock_config
        mock_session.config.option.xmlpath = str(test_junit_xml)
        pytest_sessionfinish(mock_session, 0)

        # Verify result
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_workflow_without_signing(
        self, mock_parser: Mock, test_junit_xml: Path
    ) -> None:
        """Test workflow when signing is disabled."""
        original_content = test_junit_xml.read_text()

        # Configure without signing
        mock_config = Mock()
        mock_config.getoption.return_value = False
        pytest_configure(mock_config)

        # Run sessionfinish
        mock_session = Mock()
        mock_session.config = mock_config
        mock_session.config._jux_sign = False
        mock_session.config.option.xmlpath = str(test_junit_xml)
        pytest_sessionfinish(mock_session, 0)

        # Verify XML is unchanged
        assert test_junit_xml.read_text() == original_content
        assert "<Signature" not in original_content


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_configure_with_cert_but_no_key(self, mock_config: Mock) -> None:
        """Test configuration with certificate but no key."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": None,
            "jux_cert": "/path/to/cert.crt",
        }.get(x)

        # Should raise error - can't have cert without key
        with pytest.raises((ValueError, pytest.UsageError)):
            pytest_configure(mock_config)

    def test_sessionfinish_with_missing_config_attributes(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test sessionfinish when config attributes are missing."""
        # Config without _jux_sign attribute
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should handle gracefully (treat as signing disabled)
        pytest_sessionfinish(mock_session, 0)

    def test_sessionfinish_preserves_xml_on_error(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that sessionfinish doesn't corrupt XML on signing error."""
        original_content = test_junit_xml.read_text()

        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = "/nonexistent/key.pem"
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Attempt to sign (will fail)
        try:
            pytest_sessionfinish(mock_session, 0)
        except Exception:
            pass

        # Original XML should be preserved
        assert test_junit_xml.read_text() == original_content
