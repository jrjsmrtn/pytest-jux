# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Local filesystem storage for signed test reports.

This module re-exports storage functionality from py-juxlib for
backward compatibility. All functionality is provided by juxlib.storage.

Note:
    This module is a thin wrapper around juxlib.storage for backward compatibility.
    New code should import directly from juxlib.storage.
"""

# Re-export from juxlib.storage
from juxlib.storage import ReportStorage, get_default_storage_path

# Import specific error types from juxlib.errors for re-export
from juxlib.errors import (
    QueuedReportNotFoundError,
    ReportNotFoundError,
    StorageNotFoundError,
    StorageWriteError,
)


class StorageError(Exception):
    """Raised when storage operations fail.

    This is a backward-compatible exception class. New code should use
    the more specific exception types from juxlib.errors:
    - ReportNotFoundError
    - QueuedReportNotFoundError
    - StorageWriteError
    - StorageNotFoundError
    """

    pass


__all__ = [
    # Main classes
    "ReportStorage",
    # Utility functions
    "get_default_storage_path",
    # Backward-compatible exception
    "StorageError",
    # Specific exceptions from juxlib
    "ReportNotFoundError",
    "QueuedReportNotFoundError",
    "StorageNotFoundError",
    "StorageWriteError",
]
