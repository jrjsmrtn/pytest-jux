# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""XML digital signature generation for JUnit XML reports.

This module re-exports XML signing functionality from py-juxlib for backward
compatibility. All functionality is provided by juxlib.signing.

Note:
    This module is a thin wrapper around juxlib.signing for backward compatibility.
    New code should import directly from juxlib.signing.
"""

# Re-export types and functions from juxlib.signing
from juxlib.signing import (
    PrivateKey,
    load_private_key,
    sign_xml,
    verify_signature,
)

# Re-export for backward compatibility with code using these names
from lxml import etree
from signxml import XMLSigner, XMLVerifier
import signxml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

__all__ = [
    "PrivateKey",
    "load_private_key",
    "sign_xml",
    "verify_signature",
    # Backward compatibility exports
    "XMLSigner",
    "XMLVerifier",
    "signxml",
    "etree",
    "ec",
    "rsa",
    "serialization",
]
