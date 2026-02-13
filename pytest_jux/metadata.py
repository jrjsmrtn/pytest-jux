# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Environment metadata capture for test reports.

This module re-exports metadata functionality from py-juxlib with
pytest-specific wrappers for backward compatibility.

Note:
    This module is a thin wrapper around juxlib.metadata for backward compatibility.
    New code should import directly from juxlib.metadata.

Usage:
    The metadata is automatically captured and added to test reports when
    pytest-jux is enabled. No manual intervention is required.

    For custom usage:
        from pytest_jux.metadata import capture_metadata

        metadata = capture_metadata()
        print(f"Running on: {metadata.hostname}")
"""

from __future__ import annotations

from typing import Any

# Re-export core functionality from juxlib
from juxlib.metadata import (
    CIInfo,
    GitInfo,
    capture_git_info,
    detect_ci_provider,
    detect_project_name,
    is_ci_environment,
    is_git_repository,
)
from juxlib.metadata import (
    EnvironmentMetadata as _JuxlibEnvironmentMetadata,
)
from juxlib.metadata import (
    capture_metadata as _juxlib_capture_metadata,
)


class EnvironmentMetadata(_JuxlibEnvironmentMetadata):
    """Environment metadata with pytest-specific backward compatibility.

    Extends juxlib's EnvironmentMetadata to provide backward-compatible
    pytest_version and pytest_jux_version attributes that map to tool_versions.
    """

    @property
    def pytest_version(self) -> str:
        """Get pytest version (backward compatibility).

        Returns:
            pytest version string, or "unknown" if not captured
        """
        return self.tool_versions.get("pytest", "unknown")

    @property
    def pytest_jux_version(self) -> str:
        """Get pytest-jux version (backward compatibility).

        Returns:
            pytest-jux version string, or "unknown" if not captured
        """
        return self.tool_versions.get("pytest_jux", "unknown")

    def __eq__(self, other: object) -> bool:
        """Check equality with another EnvironmentMetadata instance.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, (EnvironmentMetadata, _JuxlibEnvironmentMetadata)):
            return NotImplemented

        return (
            self.hostname == other.hostname
            and self.username == other.username
            and self.platform == other.platform
            and self.python_version == other.python_version
            and self.timestamp == other.timestamp
            and self.project_name == other.project_name
            and self.tool_versions == other.tool_versions
            and self.env == other.env
            and self.git_commit == other.git_commit
            and self.git_branch == other.git_branch
            and self.git_status == other.git_status
            and self.git_remote == other.git_remote
            and self.ci_provider == other.ci_provider
            and self.ci_build_id == other.ci_build_id
            and self.ci_build_url == other.ci_build_url
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        data = super().to_dict()
        # Add backward-compatible fields
        data["pytest_version"] = self.pytest_version
        data["pytest_jux_version"] = self.pytest_jux_version
        return data


def capture_metadata(
    include_env_vars: list[str] | None = None,
) -> EnvironmentMetadata:
    """Capture current environment metadata with pytest versions.

    This wrapper around juxlib's capture_metadata automatically captures
    pytest and pytest-jux versions for backward compatibility.

    Args:
        include_env_vars: List of environment variable names to capture.
                         If None, no additional env vars are captured.

    Returns:
        EnvironmentMetadata instance with current environment information
    """
    # Capture pytest version
    try:
        import pytest

        pytest_version = pytest.__version__
    except (ImportError, AttributeError):
        pytest_version = "unknown"

    # Capture pytest-jux version
    try:
        from pytest_jux import __version__

        pytest_jux_version = __version__
    except (ImportError, AttributeError):
        pytest_jux_version = "unknown"

    # Build tool versions dict
    tool_versions = {
        "pytest": pytest_version,
        "pytest_jux": pytest_jux_version,
    }

    # Use juxlib's capture_metadata
    juxlib_metadata = _juxlib_capture_metadata(
        include_env_vars=include_env_vars,
        tool_versions=tool_versions,
    )

    # Convert to our subclass for backward compatibility
    return EnvironmentMetadata(
        hostname=juxlib_metadata.hostname,
        username=juxlib_metadata.username,
        platform=juxlib_metadata.platform,
        python_version=juxlib_metadata.python_version,
        timestamp=juxlib_metadata.timestamp,
        project_name=juxlib_metadata.project_name,
        tool_versions=juxlib_metadata.tool_versions,
        env=juxlib_metadata.env,
        git_commit=juxlib_metadata.git_commit,
        git_branch=juxlib_metadata.git_branch,
        git_status=juxlib_metadata.git_status,
        git_remote=juxlib_metadata.git_remote,
        ci_provider=juxlib_metadata.ci_provider,
        ci_build_id=juxlib_metadata.ci_build_id,
        ci_build_url=juxlib_metadata.ci_build_url,
    )


__all__ = [
    # Main entry point
    "capture_metadata",
    # Data models (backward compatible subclass)
    "EnvironmentMetadata",
    # Re-exports from juxlib.metadata
    "GitInfo",
    "CIInfo",
    "detect_project_name",
    "capture_git_info",
    "is_git_repository",
    "detect_ci_provider",
    "is_ci_environment",
]
