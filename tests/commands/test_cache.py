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

"""Tests for cache management command."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_jux.commands.cache import main
from pytest_jux.metadata import EnvironmentMetadata
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
                EnvironmentMetadata(
                    hostname="test",
                    username="test",
                    platform="test",
                    python_version="3.11",
                    pytest_version="8.0",
                    pytest_jux_version="0.1.4",
                    timestamp=f"2025-10-17T10:3{i}:00Z",
                ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
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

        storage.store_report(
            b"<testsuite name='test1'><testcase name='test_one'/></testsuite>",
            "sha256:test1",
            EnvironmentMetadata(
                hostname="test-host",
                username="test-user",
                platform="test-platform",
                python_version="3.11.0",
                pytest_version="8.0.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
        )

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

        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:test1",
            EnvironmentMetadata(
                hostname="test-host",
                username="test-user",
                platform="test-platform",
                python_version="3.11.0",
                pytest_version="8.0.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
        )

        with patch(
            "pytest_jux.commands.cache.get_default_storage_path", return_value=tmp_path
        ):
            result = main(["show", "sha256:test1", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert data["hash"] == "sha256:test1"
        assert data["metadata"]["hostname"] == "test-host"
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
                EnvironmentMetadata(
                    hostname="test",
                    username="test",
                    platform="test",
                    python_version="3.11",
                    pytest_version="8.0",
                    pytest_jux_version="0.1.4",
                    timestamp=f"2025-10-17T10:3{i}:00Z",
                ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-09-01T10:30:00Z",  # Old timestamp
            ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-09-01T10:30:00Z",
            ),
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
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:30:00Z",
            ),
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
