# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for API publishing functionality.

These tests verify the publishing flow using jux-mock-server's LiveMockServer.
Tests are skipped if jux-mock-server is not installed.

DEPENDENCY: jux-mock-server v0.5.0+ (LiveMockServer feature)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from pytest_jux.api_client import JuxAPIClient, PublishResponse

if TYPE_CHECKING:
    pass

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestJuxAPIClientIntegration:
    """Integration tests for JuxAPIClient against live mock server."""

    def test_publish_report_success(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
    ) -> None:
        """Test successful report publishing to live mock server."""
        client = JuxAPIClient(
            api_url=f"{live_mock_server.url}/api/v1",
            timeout=10,
        )

        response = client.publish_report(sample_junit_xml)

        # Verify response
        assert isinstance(response, PublishResponse)
        assert response.test_run_id is not None
        assert response.message is not None

        # Verify request was received
        assert live_mock_server.request_count("/api/v1/junit/submit") == 1

        # Verify request content
        request = live_mock_server.last_request("/api/v1/junit/submit")
        assert request is not None
        assert b"test-project" in request.body

    def test_publish_report_with_bearer_token(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
    ) -> None:
        """Test that bearer token is included in request headers."""
        client = JuxAPIClient(
            api_url=f"{live_mock_server.url}/api/v1",
            bearer_token="test-token-12345",  # noqa: S106
            timeout=10,
        )

        client.publish_report(sample_junit_xml)

        # Verify request was received with auth header
        request = live_mock_server.last_request("/api/v1/junit/submit")
        assert request is not None
        # Starlette stores headers with lowercase keys
        auth_header = request.headers.get("authorization", "")
        assert auth_header == "Bearer test-token-12345"

    def test_publish_report_server_error(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
    ) -> None:
        """Test handling of server errors."""
        # Configure mock server to return error
        live_mock_server.configure_error(
            "/api/v1/junit/submit",
            status=503,
            detail="Service unavailable",
        )

        client = JuxAPIClient(
            api_url=f"{live_mock_server.url}/api/v1",
            timeout=10,
            max_retries=1,  # Reduce retries for faster test
        )

        with pytest.raises(Exception):  # HTTPError or similar
            client.publish_report(sample_junit_xml)

    def test_publish_report_captures_xml_content(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
    ) -> None:
        """Test that the full XML content is sent to the server."""
        client = JuxAPIClient(
            api_url=f"{live_mock_server.url}/api/v1",
            timeout=10,
        )

        client.publish_report(sample_junit_xml)

        # Verify the XML was sent correctly
        request = live_mock_server.last_request("/api/v1/junit/submit")
        assert request is not None
        body = request.body.decode("utf-8")
        assert "testsuites" in body
        assert "testsuite" in body
        assert 'name="pytest"' in body
        assert "git:branch" in body
        assert "git:commit" in body


class TestPublishCommandIntegration:
    """Integration tests for jux-publish command against live mock server."""

    def test_publish_single_file_success(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test jux-publish command with single file."""
        from pytest_jux.commands.publish import main

        # Create test XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        result = main([
            "--file", str(xml_file),
            "--api-url", f"{live_mock_server.url}/api/v1",
        ])

        assert result == 0

        # Verify request was made
        assert live_mock_server.request_count("/api/v1/junit/submit") == 1

    def test_publish_with_bearer_token(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
    ) -> None:
        """Test jux-publish command with bearer token."""
        from pytest_jux.commands.publish import main

        # Create test XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        main([
            "--file", str(xml_file),
            "--api-url", f"{live_mock_server.url}/api/v1",
            "--bearer-token", "my-secret-token",  # noqa: S106
        ])

        # Verify bearer token was sent
        request = live_mock_server.last_request("/api/v1/junit/submit")
        assert request is not None
        auth_header = request.headers.get("authorization", "")
        assert auth_header == "Bearer my-secret-token"

    def test_publish_server_error_returns_nonzero(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
    ) -> None:
        """Test jux-publish returns non-zero on server error."""
        from pytest_jux.commands.publish import main

        # Configure mock server to return error
        live_mock_server.configure_error(
            "/api/v1/junit/submit",
            status=500,
            detail="Internal server error",
        )

        # Create test XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        result = main([
            "--file", str(xml_file),
            "--api-url", f"{live_mock_server.url}/api/v1",
        ])

        assert result != 0

    def test_publish_json_output(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test jux-publish with JSON output format."""
        import json

        from pytest_jux.commands.publish import main

        # Create test XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        result = main([
            "--file", str(xml_file),
            "--api-url", f"{live_mock_server.url}/api/v1",
            "--json",
        ])

        assert result == 0

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["published"] == 1


class TestPluginIntegration:
    """Integration tests for pytest plugin publishing functionality."""

    def test_plugin_publishes_on_session_finish(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
    ) -> None:
        """Test that plugin publishes report at session end."""
        from unittest.mock import MagicMock

        from pytest_jux.config import StorageMode
        from pytest_jux.plugin import pytest_sessionfinish

        # Create XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        # Create mock session
        mock_session = MagicMock()
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = True
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = f"{live_mock_server.url}/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(xml_file)

        # Run sessionfinish - should publish to API
        with pytest.warns(UserWarning, match="Report published to Jux API"):
            pytest_sessionfinish(mock_session, 0)

        # Verify request was made
        assert live_mock_server.request_count("/api/v1/junit/submit") == 1

    def test_plugin_publishes_with_api_storage_mode(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
    ) -> None:
        """Test plugin publishes in API storage mode."""
        from unittest.mock import MagicMock

        from pytest_jux.config import StorageMode
        from pytest_jux.plugin import pytest_sessionfinish

        # Create XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        # Create mock session with API storage mode
        mock_session = MagicMock()
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = False
        mock_session.config._jux_storage_mode = StorageMode.API
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = f"{live_mock_server.url}/api/v1"
        mock_session.config._jux_bearer_token = "test-token"  # noqa: S105
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(xml_file)

        # Run sessionfinish - should publish to API
        with pytest.warns(UserWarning, match="Report published to Jux API"):
            pytest_sessionfinish(mock_session, 0)

        # Verify request was made with bearer token
        request = live_mock_server.last_request("/api/v1/junit/submit")
        assert request is not None
        auth_header = request.headers.get("authorization", "")
        assert auth_header == "Bearer test-token"

    def test_plugin_handles_server_error_gracefully(
        self,
        live_mock_server: Any,
        sample_junit_xml: str,
        tmp_path: Path,
    ) -> None:
        """Test plugin handles server errors without crashing."""
        from unittest.mock import MagicMock

        from pytest_jux.config import StorageMode
        from pytest_jux.plugin import pytest_sessionfinish

        # Configure mock server to return error
        live_mock_server.configure_error(
            "/api/v1/junit/submit",
            status=503,
            detail="Service unavailable",
        )

        # Create XML file
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(sample_junit_xml, encoding="utf-8")

        # Create mock session
        mock_session = MagicMock()
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = True
        mock_session.config._jux_storage_mode = StorageMode.BOTH
        mock_session.config._jux_storage_path = str(tmp_path)
        mock_session.config._jux_api_url = f"{live_mock_server.url}/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 10
        mock_session.config._jux_api_max_retries = 1
        mock_session.config.option.xmlpath = str(xml_file)

        # Run sessionfinish - should fail gracefully
        with pytest.warns(UserWarning, match="Failed to publish"):
            pytest_sessionfinish(mock_session, 0)

        # Session should complete without crashing
