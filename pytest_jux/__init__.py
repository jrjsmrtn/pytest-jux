# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
pytest-jux: A pytest plugin for signing and publishing JUnit XML test reports.

This plugin integrates with pytest to automatically:
1. Sign JUnit XML test reports using XML digital signatures (XMLDSig)
2. Calculate canonical hashes for duplicate detection
3. Publish signed reports to a Jux REST API backend
"""

from importlib.metadata import metadata as _metadata

_meta = _metadata("pytest-jux")
__version__ = _meta["Version"]
__author__ = _meta["Author-email"].split("<")[0].strip()
__email__ = _meta["Author-email"].split("<")[1].rstrip(">")

# Import plugin hooks when plugin module is available
try:  # pragma: no cover
    from pytest_jux.plugin import pytest_addoption, pytest_configure

    __all__ = ["pytest_addoption", "pytest_configure", "__version__"]
except ImportError:  # pragma: no cover
    # Plugin module not yet implemented
    __all__ = ["__version__"]
