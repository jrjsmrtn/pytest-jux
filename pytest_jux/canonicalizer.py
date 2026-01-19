# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""XML canonicalization and hashing for JUnit XML reports.

This module re-exports XML canonicalization functionality from py-juxlib for
backward compatibility. All functionality is provided by juxlib.signing.

Note:
    This module is a thin wrapper around juxlib.signing for backward compatibility.
    New code should import directly from juxlib.signing.
"""

# Re-export from juxlib.signing
from juxlib.signing import (
    canonicalize_xml,
    compute_canonical_hash,
    load_xml,
)

# Backward compatibility imports
from pathlib import Path
from typing import cast
from lxml import etree
import hashlib

__all__ = [
    "canonicalize_xml",
    "compute_canonical_hash",
    "load_xml",
    # Backward compatibility exports
    "Path",
    "cast",
    "etree",
    "hashlib",
]
