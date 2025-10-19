# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for configuration management command."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_jux.commands.config_cmd import main


class TestConfigList:
    """Tests for jux-config list command."""

    def test_list_all_options(self, capsys: pytest.CaptureFixture) -> None:
        """Should list all configuration options."""
        result = main(["list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "jux_enabled" in captured.out
        assert "jux_sign" in captured.out
        assert "jux_publish" in captured.out
        assert "jux_storage_mode" in captured.out
        assert "jux_api_url" in captured.out

    def test_list_shows_types(self, capsys: pytest.CaptureFixture) -> None:
        """Should show type information for each option."""
        result = main(["list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "bool" in captured.out  # jux_enabled type
        assert "enum" in captured.out  # jux_storage_mode type
        assert "path" in captured.out  # jux_key_path type

    def test_list_shows_defaults(self, capsys: pytest.CaptureFixture) -> None:
        """Should show default values."""
        result = main(["list"])

        captured = capsys.readouterr()
        assert result == 0
        assert "false" in captured.out.lower()  # Default for jux_enabled
        assert "local" in captured.out.lower()  # Default for jux_storage_mode

    def test_list_json_output(self, capsys: pytest.CaptureFixture) -> None:
        """Should output JSON format when --json flag is used."""
        result = main(["list", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert "options" in data
        assert "jux_enabled" in data["options"]
        assert data["options"]["jux_enabled"]["type"] == "bool"
        assert data["options"]["jux_enabled"]["default"] is False


class TestConfigDump:
    """Tests for jux-config dump command."""

    def test_dump_default_config(self, capsys: pytest.CaptureFixture) -> None:
        """Should dump default configuration."""
        result = main(["dump"])

        captured = capsys.readouterr()
        assert result == 0
        assert "jux_enabled" in captured.out
        assert "false" in captured.out.lower()

    def test_dump_shows_sources(self, capsys: pytest.CaptureFixture) -> None:
        """Should show configuration sources."""
        result = main(["dump"])

        captured = capsys.readouterr()
        assert result == 0
        assert "default" in captured.out.lower()

    def test_dump_json_output(self, capsys: pytest.CaptureFixture) -> None:
        """Should output JSON format when --json flag is used."""
        result = main(["dump", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output - returns config dict directly
        data = json.loads(captured.out)
        assert "jux_enabled" in data
        assert isinstance(data["jux_enabled"], bool)

    def test_dump_with_env_vars(
        self, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should show environment variable overrides."""
        monkeypatch.setenv("JUX_ENABLED", "true")

        # Mock to prevent .jux.conf from being loaded
        with patch(
            "pytest_jux.commands.config_cmd._find_config_files",
            return_value=[],
        ):
            result = main(["dump"])

        captured = capsys.readouterr()
        assert result == 0
        assert "true" in captured.out.lower()
        assert "env" in captured.out.lower() or "environment" in captured.out.lower()

    def test_dump_with_config_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should show configuration from file."""
        config_file = tmp_path / "test.conf"
        config_file.write_text("[jux]\nenabled = true\n")

        with patch(
            "pytest_jux.commands.config_cmd._find_config_files",
            return_value=[config_file],
        ):
            result = main(["dump"])

        captured = capsys.readouterr()
        assert result == 0
        assert "true" in captured.out.lower()


class TestConfigView:
    """Tests for jux-config view command."""

    def test_view_specific_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should view specific configuration file."""
        config_file = tmp_path / "test.conf"
        config_file.write_text("[jux]\nenabled = true\nsign = true\n")

        result = main(["view", str(config_file)])

        captured = capsys.readouterr()
        assert result == 0
        assert "[jux]" in captured.out
        assert "enabled = true" in captured.out
        assert "sign = true" in captured.out

    def test_view_nonexistent_file(self, capsys: pytest.CaptureFixture) -> None:
        """Should show error for nonexistent file."""
        result = main(["view", "/nonexistent/path/config.conf"])

        captured = capsys.readouterr()
        assert result == 1
        assert "not found" in captured.err.lower() or "error" in captured.err.lower()

    def test_view_all_files(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should view all configuration files with --all flag."""
        config_file1 = tmp_path / "config1.conf"
        config_file1.write_text("[jux]\nenabled = true\n")

        config_file2 = tmp_path / "config2.conf"
        config_file2.write_text("[jux]\nsign = true\n")

        with patch(
            "pytest_jux.commands.config_cmd._find_config_files",
            return_value=[config_file1, config_file2],
        ):
            result = main(["view", "--all"])

        captured = capsys.readouterr()
        assert result == 0
        assert str(config_file1) in captured.out
        assert str(config_file2) in captured.out


class TestConfigInit:
    """Tests for jux-config init command."""

    def test_init_default_path(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should create config file at default path."""
        # Mock home directory
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = main(["init"])

        captured = capsys.readouterr()
        assert result == 0
        assert (
            "created" in captured.out.lower() or "initialized" in captured.out.lower()
        )

    def test_init_custom_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should create config file at custom path."""
        config_file = tmp_path / "custom.conf"

        result = main(["init", "--path", str(config_file)])

        assert result == 0
        assert config_file.exists()

        # Verify file content
        content = config_file.read_text()
        assert "[jux]" in content

    def test_init_existing_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should not overwrite existing file without --force."""
        config_file = tmp_path / "existing.conf"
        config_file.write_text("existing content")

        result = main(["init", "--path", str(config_file)])

        captured = capsys.readouterr()
        assert result == 1
        assert "exists" in captured.err.lower()
        assert config_file.read_text() == "existing content"

    def test_init_with_force(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should overwrite existing file with --force."""
        config_file = tmp_path / "existing.conf"
        config_file.write_text("existing content")

        result = main(["init", "--path", str(config_file), "--force"])

        assert result == 0
        assert config_file.read_text() != "existing content"
        assert "[jux]" in config_file.read_text()

    def test_init_with_template(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should use full template when --template=full."""
        config_file = tmp_path / "full.conf"

        result = main(["init", "--path", str(config_file), "--template", "full"])

        assert result == 0
        assert config_file.exists()

        content = config_file.read_text()
        # Full template should have commented examples
        assert "#" in content
        assert "enabled" in content.lower()


class TestConfigValidate:
    """Tests for jux-config validate command."""

    def test_validate_default_config(self, capsys: pytest.CaptureFixture) -> None:
        """Should validate default configuration successfully."""
        result = main(["validate"])

        captured = capsys.readouterr()
        assert result == 0
        assert "valid" in captured.out.lower()

    def test_validate_with_warnings(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should show warnings for incomplete configuration."""
        # Enable signing without key path
        monkeypatch.setenv("JUX_SIGN", "true")

        # Mock to prevent .jux.conf from being loaded
        with patch(
            "pytest_jux.commands.config_cmd._find_config_files",
            return_value=[],
        ):
            result = main(["validate", "--strict"])

        captured = capsys.readouterr()
        assert result == 0  # Still valid, just warnings
        assert "warning" in captured.out.lower()
        assert "jux_key_path" in captured.out

    def test_validate_with_config_file(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Should validate configuration from file."""
        config_file = tmp_path / "valid.conf"
        config_file.write_text("[jux]\nenabled = true\n")

        with patch(
            "pytest_jux.commands.config_cmd._find_config_files",
            return_value=[config_file],
        ):
            result = main(["validate"])

        captured = capsys.readouterr()
        assert result == 0
        assert "valid" in captured.out.lower()

    def test_validate_invalid_config(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should handle invalid configuration values gracefully."""
        # Set invalid storage mode
        monkeypatch.setenv("JUX_STORAGE_MODE", "invalid_mode")

        result = main(["validate"])

        captured = capsys.readouterr()
        # Invalid env vars are silently skipped by load_from_env(),
        # so validation passes
        assert result == 0
        assert "valid" in captured.out.lower()

    def test_validate_json_output(self, capsys: pytest.CaptureFixture) -> None:
        """Should output JSON format when --json flag is used."""
        result = main(["validate", "--json"])

        captured = capsys.readouterr()
        assert result == 0

        # Parse JSON output
        data = json.loads(captured.out)
        assert "valid" in data
        assert data["valid"] is True


class TestConfigCommand:
    """Tests for general config command behavior."""

    def test_no_subcommand(self, capsys: pytest.CaptureFixture) -> None:
        """Should show help when no subcommand provided."""
        result = main([])

        captured = capsys.readouterr()
        assert result == 2
        assert "usage" in captured.out.lower()

    def test_invalid_subcommand(self, capsys: pytest.CaptureFixture) -> None:
        """Should show error for invalid subcommand."""
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
        assert "dump" in captured.out
        assert "view" in captured.out
        assert "init" in captured.out
        assert "validate" in captured.out
