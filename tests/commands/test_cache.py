# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for cache management command."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_jux.canonicalizer import compute_canonical_hash, load_xml
from pytest_jux.commands.cache import main
from pytest_jux.storage import ReportStorage


class TestCacheList:
    """Tests for jux-cache list command."""

    def test_list_empty_cache(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should show message when cache is empty."""
        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "No cached reports found" in captured.out or "0 reports" in captured.out

    def test_list_cached_reports(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should list all cached reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store some reports
        for i in range(3):
            storage.store_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:test{i}",
            )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "sha256:test0" in captured.out
        assert "sha256:test1" in captured.out
        assert "sha256:test2" in captured.out

    def test_list_json_output(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should output JSON format when --json flag is used."""
        storage = ReportStorage(storage_path=tmp_path)

        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:test1",
        )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["list", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert "reports" in data
        assert len(data["reports"]) == 1
        assert data["reports"][0]["hash"] == "sha256:test1"

    def test_list_with_custom_storage_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should use custom storage path when --storage-path is provided."""
        custom_path = tmp_path / "custom"
        storage = ReportStorage(storage_path=custom_path)

        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:test1",
        )

        # --storage-path must come before subcommand
        result = main(["--storage-path", str(custom_path), "list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "sha256:test1" in captured.out


class TestCacheShow:
    """Tests for jux-cache show command."""

    def test_show_report(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Should display report details."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store report with metadata in properties
        report_xml = b"""<testsuite name='test1'>
            <properties>
                <property name="jux:hostname" value="test-host"/>
                <property name="jux:username" value="test-user"/>
            </properties>
            <testcase name='test_one'/>
        </testsuite>"""
        storage.store_report(report_xml, "sha256:test1")

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", "sha256:test1"])

        captured = capsys.readouterr()
        assert result == 0
        assert "sha256:test1" in captured.out
        assert "test-host" in captured.out
        assert "test-user" in captured.out

    def test_show_nonexistent_report(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should show error for nonexistent report."""
        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", "sha256:nonexistent"])

        captured = capsys.readouterr()
        assert result == 1
        assert "not found" in captured.err.lower() or "error" in captured.err.lower()

    def test_show_json_output(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should output JSON format when --json flag is used."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store report with metadata in properties
        report_xml = b"""<testsuite name='test1'>
            <properties>
                <property name="jux:hostname" value="test-host"/>
            </properties>
        </testsuite>"""
        storage.store_report(report_xml, "sha256:test1")

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", "sha256:test1", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert data["hash"] == "sha256:test1"
        assert data["metadata"]["jux:hostname"] == "test-host"  # Updated key format
        assert "report" in data


class TestCacheStats:
    """Tests for jux-cache stats command."""

    def test_stats_empty_cache(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should show zero stats for empty cache."""
        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["stats"])

        captured = capsys.readouterr()
        assert result == 0
        assert "0" in captured.out or "empty" in captured.out.lower()

    def test_stats_with_reports(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should show statistics for cached reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store multiple reports
        for i in range(5):
            storage.store_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:test{i}",
            )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["stats"])

        captured = capsys.readouterr()
        assert result == 0
        assert "5" in captured.out
        assert "reports" in captured.out.lower()

    def test_stats_json_output(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should output JSON format when --json flag is used."""
        storage = ReportStorage(storage_path=tmp_path)

        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:test1",
        )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["stats", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert "total_reports" in data
        assert data["total_reports"] == 1
        assert "total_size" in data


class TestCacheClean:
    """Tests for jux-cache clean command."""

    def test_clean_old_reports(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should remove reports older than specified days."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store old report
        old_hash = "sha256:old"
        storage.store_report(
            b"<testsuite name='old'/>",
            old_hash,
        )

        # Manually set old mtime
        old_file = tmp_path / "reports" / f"{old_hash}.xml"
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        old_file.touch()
        import os

        os.utime(old_file, (old_time, old_time))

        # Store recent report
        recent_hash = "sha256:recent"
        storage.store_report(
            b"<testsuite name='recent'/>",
            recent_hash,
        )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["clean", "--days", "30"])

        assert result == 0

        # Old report should be deleted
        assert not (tmp_path / "reports" / f"{old_hash}.xml").exists()

        # Recent report should remain
        assert (tmp_path / "reports" / f"{recent_hash}.xml").exists()

    def test_clean_dry_run(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Should not delete reports in dry-run mode."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store old report
        old_hash = "sha256:old"
        storage.store_report(
            b"<testsuite name='old'/>",
            old_hash,
        )

        # Manually set old mtime
        old_file = tmp_path / "reports" / f"{old_hash}.xml"
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        old_file.touch()
        import os

        os.utime(old_file, (old_time, old_time))

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["clean", "--days", "30", "--dry-run"])

        captured = capsys.readouterr()
        assert result == 0
        assert (
            "dry run" in captured.out.lower() or "would remove" in captured.out.lower()
        )

        # Report should still exist
        assert old_file.exists()

    def test_clean_no_reports_to_delete(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle case when no reports need deletion."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store recent report only
        storage.store_report(
            b"<testsuite name='recent'/>",
            "sha256:recent",
        )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["clean", "--days", "30"])

        captured = capsys.readouterr()
        assert result == 0
        assert "0" in captured.out or "no reports" in captured.out.lower()


class TestCacheCommand:
    """Tests for general cache command behavior."""

    def test_no_subcommand(self, capsys: pytest.CaptureFixture) -> None:
        """Should show help when no subcommand provided."""
        result = main([])

        captured = capsys.readouterr()
        assert result == 2  # argparse default for missing subcommand
        assert "usage" in captured.out.lower()

    def test_invalid_subcommand(self, capsys: pytest.CaptureFixture) -> None:
        """Should show error for invalid subcommand."""
        # Invalid subcommands cause argparse to call sys.exit(2)
        with pytest.raises(SystemExit) as excinfo:
            main(["invalid"])

        assert excinfo.value.code == 2
        captured = capsys.readouterr()
        assert "invalid" in captured.err.lower()

    def test_help_option(self, capsys: pytest.CaptureFixture) -> None:
        """Should show help with --help option."""
        with pytest.raises(SystemExit) as excinfo:
            main(["--help"])

        assert excinfo.value.code == 0
        captured = capsys.readouterr()
        assert "usage" in captured.out.lower()
        assert "list" in captured.out
        assert "show" in captured.out
        assert "stats" in captured.out
        assert "clean" in captured.out

    def test_list_with_storage_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle case when report exists but is corrupted."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store a valid report
        report_hash = "sha256:test1"
        storage.store_report(
            b"<testsuite name='test1'/>",
            report_hash
        )

        # Corrupt the XML file to cause read errors
        report_file = tmp_path / "reports" / f"{report_hash}.xml"
        report_file.write_bytes(b"\x00\x00\x00")  # Invalid XML

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["list"])

        # Should succeed and show report hash even with corrupted content
        assert result == 0
        captured = capsys.readouterr()
        assert "1 total" in captured.out

    def test_show_with_env_vars(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should display environment variables from XML properties in show command."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store a report with environment metadata in XML properties
        report_hash = "sha256:test1"
        report_xml = b"""<testsuite name='test1'>
            <properties>
                <property name="jux:env:CI" value="true"/>
                <property name="jux:env:BUILD_ID" value="12345"/>
            </properties>
        </testsuite>"""
        storage.store_report(report_xml, report_hash)

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", report_hash])

        assert result == 0
        captured = capsys.readouterr()
        # Should display the report hash
        assert report_hash in captured.out

    def test_show_with_storage_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle corrupted XML gracefully in show command."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store a valid report
        report_hash = "sha256:test1"
        storage.store_report(b"<testsuite name='test1'/>", report_hash)

        # Corrupt the XML file
        report_file = tmp_path / "reports" / f"{report_hash}.xml"
        report_file.write_bytes(b"\x00\x00\x00")  # Invalid XML

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", report_hash])

        # Should succeed but show N/A for metadata (graceful degradation)
        assert result == 0
        captured = capsys.readouterr()
        # Metadata extraction fails gracefully, showing N/A values
        assert "N/A" in captured.out
        assert report_hash in captured.out

    def test_list_json_with_storage_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should list reports in JSON format with N/A metadata for corrupted XML."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store a valid report
        report_hash = "sha256:test1"
        storage.store_report(b"<testsuite name='test1'/>", report_hash)

        # Corrupt the XML file
        report_file = tmp_path / "reports" / f"{report_hash}.xml"
        report_file.write_bytes(b"\x00\x00\x00")  # Invalid XML

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["list", "--json"])

        # Should succeed and include report with N/A metadata (graceful degradation)
        assert result == 0
        captured = capsys.readouterr()
        # JSON should include the report with N/A metadata
        assert report_hash in captured.out
        assert '"timestamp": "N/A"' in captured.out

    def test_list_generic_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle generic errors in list command."""
        from unittest.mock import patch

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            with patch(
                "pytest_jux.commands.cache.ReportStorage",
                side_effect=Exception("Unexpected error"),
            ):
                result = main(["list"])

        # Should fail with error code 1
        assert result == 1
        captured = capsys.readouterr()
        assert "Error listing reports" in captured.err

    def test_show_generic_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle generic errors in show command."""
        from unittest.mock import patch

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            with patch(
                "pytest_jux.commands.cache.ReportStorage",
                side_effect=Exception("Unexpected error"),
            ):
                result = main(["show", "sha256:test"])

        # Should fail with error code 1
        assert result == 1
        captured = capsys.readouterr()
        assert "Error showing report" in captured.err

    def test_stats_generic_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle generic errors in stats command."""
        from unittest.mock import patch

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            with patch(
                "pytest_jux.commands.cache.ReportStorage",
                side_effect=Exception("Unexpected error"),
            ):
                result = main(["stats"])

        # Should fail with error code 1
        assert result == 1
        captured = capsys.readouterr()
        assert "Error getting statistics" in captured.err

    def test_clean_generic_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should handle generic errors in clean command."""
        from unittest.mock import patch

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            with patch(
                "pytest_jux.commands.cache.ReportStorage",
                side_effect=Exception("Unexpected error"),
            ):
                result = main(["clean", "--days", "30"])

        # Should fail with error code 1
        assert result == 1
        captured = capsys.readouterr()
        assert "Error cleaning cache" in captured.err

    def test_format_size_pb(self) -> None:
        """Should format very large sizes in petabytes."""
        from pytest_jux.commands.cache import _format_size

        # Test PB range (> 1024 TB)
        size_pb = 1024 * 1024 * 1024 * 1024 * 1024 * 2  # 2 PB
        result = _format_size(size_pb)
        assert "PB" in result
