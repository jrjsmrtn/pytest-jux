# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for jux-publish command."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from pytest_jux.api_client import PublishResponse
from pytest_jux.commands.publish import main
from pytest_jux.storage import ReportStorage


# Test fixtures
@pytest.fixture
def mock_publish_response() -> PublishResponse:
    """Create a mock successful publish response (jux-openapi SubmitResponse format)."""
    return PublishResponse(
        test_run_id="550e8400-e29b-41d4-a716-446655440000",
        message="Test report submitted successfully",
        test_count=10,
        failure_count=0,
        error_count=0,
        skipped_count=0,
        success_rate=100.0,
    )


@pytest.fixture
def sample_xml_content() -> str:
    """Sample JUnit XML content for testing."""
    return """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" errors="0" failures="0">
        <testcase classname="test" name="test_example" time="0.1"/>
    </testsuite>
</testsuites>
"""


@pytest.fixture
def sample_xml_file(tmp_path: Path, sample_xml_content: str) -> Path:
    """Create a sample XML file for testing."""
    xml_file = tmp_path / "report.xml"
    xml_file.write_text(sample_xml_content)
    return xml_file


class TestPublishSingleFile:
    """Tests for single file publishing."""

    def test_publish_single_file_success(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should successfully publish a single file."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
            ])

        assert result == 0
        mock_client.publish_report.assert_called_once()
        captured = capsys.readouterr()
        assert "published successfully" in captured.out.lower() or "✓" in captured.out

    def test_publish_single_file_not_found(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should fail when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.xml"

        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(nonexistent),
                "--api-url", "http://localhost:4000/api/v1",
            ])

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "failed" in captured.out.lower()

    def test_publish_single_file_api_error(
        self,
        sample_xml_file: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should handle API errors gracefully."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.side_effect = requests.exceptions.HTTPError(
                "401 Unauthorized"
            )
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
            ])

        assert result == 1
        captured = capsys.readouterr()
        assert "failed" in captured.out.lower() or "✗" in captured.out

    def test_publish_single_file_dry_run(
        self,
        sample_xml_file: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should not actually publish in dry-run mode."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--dry-run",
            ])

        assert result == 0
        mock_client.publish_report.assert_not_called()
        captured = capsys.readouterr()
        assert "dry run" in captured.out.lower() or "would publish" in captured.out.lower()

    def test_publish_single_file_json_output(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should output JSON when --json flag is used."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--json",
            ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["published"] == 1
        assert len(data["results"]) == 1

    def test_publish_single_file_verbose(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should show detailed output in verbose mode."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            result = main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--verbose",
            ])

        assert result == 0
        captured = capsys.readouterr()
        assert "Test run ID" in captured.out
        assert mock_publish_response.test_run_id in captured.out


class TestPublishQueue:
    """Tests for queue publishing."""

    def test_publish_empty_queue(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should handle empty queue gracefully."""
        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                ])

        assert result == 0
        captured = capsys.readouterr()
        assert "no reports" in captured.out.lower()

    def test_publish_queue_success(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should successfully publish all queued reports."""
        # Create storage and queue some reports
        storage = ReportStorage(storage_path=tmp_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")
        storage.queue_report(sample_xml_content.encode(), "sha256:test2")

        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.publish_report.return_value = mock_publish_response
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                ])

        assert result == 0
        assert mock_client.publish_report.call_count == 2
        captured = capsys.readouterr()
        assert "2" in captured.out  # Should mention 2 reports

        # Verify reports were dequeued
        assert len(storage.list_queued_reports()) == 0
        assert len(storage.list_reports()) == 2

    def test_publish_queue_partial_failure(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should return exit code 2 on partial failure."""
        # Create storage and queue some reports
        storage = ReportStorage(storage_path=tmp_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")
        storage.queue_report(sample_xml_content.encode(), "sha256:test2")

        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                # First call succeeds, second fails
                mock_client.publish_report.side_effect = [
                    mock_publish_response,
                    requests.exceptions.HTTPError("500 Server Error"),
                ]
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                ])

        assert result == 2  # Partial success
        captured = capsys.readouterr()
        assert "1" in captured.out  # Some reference to counts

    def test_publish_queue_all_fail(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should return exit code 1 when all reports fail."""
        # Create storage and queue some reports
        storage = ReportStorage(storage_path=tmp_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")
        storage.queue_report(sample_xml_content.encode(), "sha256:test2")

        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.publish_report.side_effect = requests.exceptions.HTTPError(
                    "500 Server Error"
                )
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                ])

        assert result == 1  # All failed
        captured = capsys.readouterr()
        assert "failed" in captured.out.lower()

    def test_publish_queue_dry_run(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should not actually publish in dry-run mode."""
        # Create storage and queue some reports
        storage = ReportStorage(storage_path=tmp_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")
        storage.queue_report(sample_xml_content.encode(), "sha256:test2")

        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                    "--dry-run",
                ])

        assert result == 0
        mock_client.publish_report.assert_not_called()
        # Reports should still be in queue
        assert len(storage.list_queued_reports()) == 2

    def test_publish_queue_json_output(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should output JSON when --json flag is used."""
        # Create storage and queue a report
        storage = ReportStorage(storage_path=tmp_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")

        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.publish_report.return_value = mock_publish_response
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                    "--json",
                ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert data["published"] == 1
        assert data["failed"] == 0
        assert len(data["results"]) == 1

    def test_publish_queue_with_custom_storage_path(
        self,
        tmp_path: Path,
        sample_xml_content: str,
        mock_publish_response: PublishResponse,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should use custom storage path when provided."""
        custom_path = tmp_path / "custom"
        storage = ReportStorage(storage_path=custom_path)
        storage.queue_report(sample_xml_content.encode(), "sha256:test1")

        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            result = main([
                "--queue",
                "--api-url", "http://localhost:4000/api/v1",
                "--storage-path", str(custom_path),
            ])

        assert result == 0
        mock_client.publish_report.assert_called_once()


class TestPublishConfiguration:
    """Tests for configuration options."""

    def test_bearer_token_passed_to_client(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
    ) -> None:
        """Should pass bearer token to API client."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--bearer-token", "test-token",  # noqa: S106 - Test token
            ])

        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["bearer_token"] == "test-token"  # noqa: S105 - Test token

    def test_timeout_passed_to_client(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
    ) -> None:
        """Should pass timeout to API client."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--timeout", "60",
            ])

        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["timeout"] == 60

    def test_max_retries_passed_to_client(
        self,
        sample_xml_file: Path,
        mock_publish_response: PublishResponse,
    ) -> None:
        """Should pass max_retries to API client."""
        with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.publish_report.return_value = mock_publish_response
            mock_client_class.return_value = mock_client

            main([
                "--file", str(sample_xml_file),
                "--api-url", "http://localhost:4000/api/v1",
                "--max-retries", "5",
            ])

        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["max_retries"] == 5


class TestPublishArgParsing:
    """Tests for argument parsing."""

    def test_requires_file_or_queue(self, capsys: pytest.CaptureFixture) -> None:
        """Should require either --file or --queue."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--api-url", "http://localhost:4000/api/v1"])

        assert exc_info.value.code != 0

    def test_file_and_queue_mutually_exclusive(
        self,
        sample_xml_file: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should not allow both --file and --queue."""
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--file", str(sample_xml_file),
                "--queue",
                "--api-url", "http://localhost:4000/api/v1",
            ])

        assert exc_info.value.code != 0

    def test_requires_api_url(
        self,
        sample_xml_file: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should require --api-url."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--file", str(sample_xml_file)])

        assert exc_info.value.code != 0


class TestPublishEmptyQueueJson:
    """Tests for JSON output with empty queue."""

    def test_empty_queue_json_output(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Should return proper JSON for empty queue."""
        with patch(
            "pytest_jux.commands.publish.get_default_storage_path",
            return_value=tmp_path,
        ):
            with patch("pytest_jux.commands.publish.JuxAPIClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client_class.return_value = mock_client

                result = main([
                    "--queue",
                    "--api-url", "http://localhost:4000/api/v1",
                    "--json",
                ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert "No reports in queue" in data.get("message", "")
