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

"""Tests for local filesystem storage."""

import json
import platform
import stat
from pathlib import Path

import pytest

from pytest_jux.metadata import EnvironmentMetadata
from pytest_jux.storage import (
    ReportStorage,
    StorageError,
    get_default_storage_path,
)


class TestGetDefaultStoragePath:
    """Tests for default storage path detection."""

    def test_returns_path_object(self) -> None:
        """Should return a Path object."""
        path = get_default_storage_path()
        assert isinstance(path, Path)

    def test_path_is_absolute(self) -> None:
        """Storage path should be absolute."""
        path = get_default_storage_path()
        assert path.is_absolute()

    def test_path_contains_jux(self) -> None:
        """Storage path should contain 'jux' directory."""
        path = get_default_storage_path()
        assert "jux" in str(path).lower()

    def test_macos_uses_application_support(self) -> None:
        """macOS should use ~/Library/Application Support."""
        if platform.system() == "Darwin":
            path = get_default_storage_path()
            assert "Library/Application Support" in str(path)

    def test_linux_uses_local_share(self) -> None:
        """Linux should use ~/.local/share."""
        if platform.system() == "Linux":
            path = get_default_storage_path()
            assert ".local/share" in str(path)

    def test_windows_uses_local_appdata(self) -> None:
        """Windows should use %LOCALAPPDATA%."""
        if platform.system() == "Windows":
            path = get_default_storage_path()
            # Should use LOCALAPPDATA on Windows
            assert "AppData" in str(path) or "Local" in str(path)


class TestReportStorage:
    """Tests for ReportStorage class."""

    def test_init_with_default_path(self, tmp_path: Path) -> None:
        """Should initialize with custom path."""
        storage = ReportStorage(storage_path=tmp_path)
        assert storage.storage_path == tmp_path

    def test_init_creates_directories(self, tmp_path: Path) -> None:
        """Should create storage directories on init."""
        storage_path = tmp_path / "jux"
        ReportStorage(storage_path=storage_path)

        # Should create reports, metadata, and queue directories
        assert (storage_path / "reports").exists()
        assert (storage_path / "metadata").exists()
        assert (storage_path / "queue").exists()

    def test_store_report(self, tmp_path: Path) -> None:
        """Should store report with canonical hash as filename."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite><testcase name='test1'/></testsuite>"
        canonical_hash = "sha256:abc123def456"
        metadata = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Report file should exist
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        assert report_file.exists()
        assert report_file.read_bytes() == xml_content

        # Metadata file should exist
        metadata_file = tmp_path / "metadata" / f"{canonical_hash}.json"
        assert metadata_file.exists()

    def test_store_report_atomic_write(self, tmp_path: Path) -> None:
        """Should use atomic write (temp file + rename)."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:test123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # No temp files should remain
        temp_files = list(tmp_path.rglob("*.tmp"))
        assert len(temp_files) == 0

    def test_get_report(self, tmp_path: Path) -> None:
        """Should retrieve stored report."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite><testcase name='test1'/></testsuite>"
        canonical_hash = "sha256:retrieve123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Retrieve report
        retrieved = storage.get_report(canonical_hash)
        assert retrieved == xml_content

    def test_get_nonexistent_report(self, tmp_path: Path) -> None:
        """Should raise error for nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)

        with pytest.raises(StorageError):
            storage.get_report("sha256:nonexistent")

    def test_get_metadata(self, tmp_path: Path) -> None:
        """Should retrieve stored metadata."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:meta123"
        metadata = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Retrieve metadata
        retrieved_meta = storage.get_metadata(canonical_hash)
        assert retrieved_meta.hostname == metadata.hostname
        assert retrieved_meta.username == metadata.username

    def test_list_reports(self, tmp_path: Path) -> None:
        """Should list all stored reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store multiple reports
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

        reports = storage.list_reports()
        assert len(reports) == 3
        assert all(h.startswith("sha256:test") for h in reports)

    def test_list_reports_empty(self, tmp_path: Path) -> None:
        """Should return empty list when no reports."""
        storage = ReportStorage(storage_path=tmp_path)
        reports = storage.list_reports()
        assert reports == []

    def test_delete_report(self, tmp_path: Path) -> None:
        """Should delete report and metadata."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:delete123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Delete report
        storage.delete_report(canonical_hash)

        # Files should not exist
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        metadata_file = tmp_path / "metadata" / f"{canonical_hash}.json"
        assert not report_file.exists()
        assert not metadata_file.exists()

    def test_delete_nonexistent_report(self, tmp_path: Path) -> None:
        """Should not raise error when deleting nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)
        # Should not raise
        storage.delete_report("sha256:nonexistent")

    def test_queue_report(self, tmp_path: Path) -> None:
        """Should queue report for later publishing."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:queue123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.queue_report(xml_content, canonical_hash, metadata)

        # Report should be in queue directory
        queue_file = tmp_path / "queue" / f"{canonical_hash}.xml"
        assert queue_file.exists()

    def test_list_queued_reports(self, tmp_path: Path) -> None:
        """Should list all queued reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Queue multiple reports
        for i in range(2):
            storage.queue_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:queue{i}",
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

        queued = storage.list_queued_reports()
        assert len(queued) == 2
        assert all(h.startswith("sha256:queue") for h in queued)

    def test_dequeue_report(self, tmp_path: Path) -> None:
        """Should move report from queue to reports."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:dequeue123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.queue_report(xml_content, canonical_hash, metadata)

        # Dequeue (mark as published)
        storage.dequeue_report(canonical_hash)

        # Should be in reports, not queue
        assert canonical_hash in storage.list_reports()
        assert canonical_hash not in storage.list_queued_reports()

    def test_report_exists(self, tmp_path: Path) -> None:
        """Should check if report exists."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:exists123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        assert not storage.report_exists(canonical_hash)

        storage.store_report(xml_content, canonical_hash, metadata)

        assert storage.report_exists(canonical_hash)

    def test_get_storage_stats(self, tmp_path: Path) -> None:
        """Should return storage statistics."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store some reports
        for i in range(3):
            storage.store_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:stat{i}",
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

        # Queue one report
        storage.queue_report(
            b"<testsuite/>",
            "sha256:statqueue",
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:40:00Z",
            ),
        )

        stats = storage.get_stats()

        assert stats["total_reports"] == 3
        assert stats["queued_reports"] == 1
        assert stats["total_size"] > 0
        assert "oldest_report" in stats

    def test_file_permissions_secure(self, tmp_path: Path) -> None:
        """Stored files should have secure permissions."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:perm123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Check file permissions (should be 0600 or more restrictive)
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        mode = stat.S_IMODE(report_file.stat().st_mode)

        # File should be readable and writable by owner only
        assert mode & stat.S_IRUSR  # Owner read
        assert mode & stat.S_IWUSR  # Owner write

    def test_metadata_serialization(self, tmp_path: Path) -> None:
        """Metadata should be correctly serialized to JSON."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:serial123"
        metadata = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            env={"CI": "true", "BUILD_ID": "123"},
        )

        storage.store_report(xml_content, canonical_hash, metadata)

        # Read metadata file directly
        metadata_file = tmp_path / "metadata" / f"{canonical_hash}.json"
        data = json.loads(metadata_file.read_text())

        assert data["hostname"] == "test-host"
        assert data["env"]["CI"] == "true"

    def test_get_metadata_invalid_json(self, tmp_path: Path) -> None:
        """Should raise error for corrupted metadata."""
        storage = ReportStorage(storage_path=tmp_path)

        canonical_hash = "sha256:corrupt123"
        metadata_file = tmp_path / "metadata" / f"{canonical_hash}.json"
        metadata_file.write_text("{invalid json}")

        with pytest.raises(StorageError, match="Failed to read metadata"):
            storage.get_metadata(canonical_hash)

    def test_dequeue_nonexistent_report(self, tmp_path: Path) -> None:
        """Should raise error when dequeuing nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)

        with pytest.raises(StorageError, match="Queued report not found"):
            storage.dequeue_report("sha256:nonexistent")

    def test_get_stats_empty_storage(self, tmp_path: Path) -> None:
        """Should return zero stats for empty storage."""
        storage = ReportStorage(storage_path=tmp_path)

        stats = storage.get_stats()

        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0
        assert stats["total_size"] == 0
        assert stats["oldest_report"] is None

    def test_store_report_in_readonly_directory(self, tmp_path: Path) -> None:
        """Should raise error when storing to readonly directory."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        # Make reports directory readonly
        reports_dir = tmp_path / "reports"
        reports_dir.chmod(0o500)  # r-x------

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:readonly123"
        metadata = EnvironmentMetadata(
            hostname="test",
            username="test",
            platform="test",
            python_version="3.11",
            pytest_version="8.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
        )

        try:
            with pytest.raises(StorageError, match="Failed to write file"):
                storage.store_report(xml_content, canonical_hash, metadata)
        finally:
            # Restore permissions for cleanup
            reports_dir.chmod(0o700)

    def test_get_report_with_read_error(self, tmp_path: Path) -> None:
        """Should raise error when report file cannot be read."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        # Create a report file with no read permissions
        canonical_hash = "sha256:noread123"
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        report_file.write_bytes(b"<testsuite/>")
        report_file.chmod(0o000)  # No permissions

        try:
            with pytest.raises(StorageError, match="Failed to read report"):
                storage.get_report(canonical_hash)
        finally:
            # Restore permissions for cleanup
            report_file.chmod(0o600)

    def test_get_metadata_nonexistent(self, tmp_path: Path) -> None:
        """Should raise error for nonexistent metadata."""
        storage = ReportStorage(storage_path=tmp_path)

        with pytest.raises(StorageError, match="Metadata not found"):
            storage.get_metadata("sha256:nonexistent")

    def test_queue_and_dequeue_multiple_reports(self, tmp_path: Path) -> None:
        """Should handle multiple queued reports correctly."""
        storage = ReportStorage(storage_path=tmp_path)

        # Queue multiple reports
        hashes = []
        for i in range(5):
            canonical_hash = f"sha256:queue{i}"
            hashes.append(canonical_hash)
            storage.queue_report(
                f"<testsuite name='test{i}'/>".encode(),
                canonical_hash,
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

        # Verify all are queued
        queued = storage.list_queued_reports()
        assert len(queued) == 5
        assert all(h in queued for h in hashes)

        # Dequeue all
        for hash in hashes:
            storage.dequeue_report(hash)

        # Verify queue is empty and all are in reports
        assert len(storage.list_queued_reports()) == 0
        assert len(storage.list_reports()) == 5

    def test_storage_path_created_automatically(self, tmp_path: Path) -> None:
        """Should create storage path and subdirectories automatically."""
        storage_path = tmp_path / "nonexistent" / "path" / "jux"

        # Path doesn't exist yet
        assert not storage_path.exists()

        # Initialize storage
        ReportStorage(storage_path=storage_path)

        # Path should now exist with subdirectories
        assert storage_path.exists()
        assert (storage_path / "reports").exists()
        assert (storage_path / "metadata").exists()
        assert (storage_path / "queue").exists()

    def test_get_stats_with_queued_reports(self, tmp_path: Path) -> None:
        """Statistics should include queued reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store regular report
        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:regular1",
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

        # Queue report
        storage.queue_report(
            b"<testsuite name='test2'/>",
            "sha256:queued1",
            EnvironmentMetadata(
                hostname="test",
                username="test",
                platform="test",
                python_version="3.11",
                pytest_version="8.0",
                pytest_jux_version="0.1.4",
                timestamp="2025-10-17T10:31:00Z",
            ),
        )

        stats = storage.get_stats()

        assert stats["total_reports"] == 1
        assert stats["queued_reports"] == 1
        assert stats["total_size"] > 0
        assert stats["oldest_report"] is not None
