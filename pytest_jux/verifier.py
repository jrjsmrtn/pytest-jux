# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""XML signature verification using XMLDSig.

This module re-exports XML verification functionality from py-juxlib for
backward compatibility. All functionality is provided by juxlib.signing.

Note:
    This module is a thin wrapper around juxlib.signing for backward compatibility.
    New code should import directly from juxlib.signing.
"""

from cryptography.hazmat.primitives.asymmetric import ec, rsa
from juxlib.signing import (
    verify_with_certificate,
    verify_with_public_key,
)
from lxml import etree

# Type aliases (backward compatibility)
PublicKeyTypes = rsa.RSAPublicKey | ec.EllipticCurvePublicKey
CertOrKeyType = PublicKeyTypes | bytes | str


def verify_signature(tree: etree._Element, cert_or_key: CertOrKeyType) -> bool:
    """Verify XML digital signature.

    Args:
        tree: XML element tree with signature
        cert_or_key: Certificate (bytes/string) or public key object

    Returns:
        True if signature is valid, False otherwise

    Raises:
        ValueError: If no signature is found or certificate is invalid
    """
    # Find signature element
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature is None:
        raise ValueError("No signature found in XML")

    # Dispatch based on type
    if isinstance(cert_or_key, bytes | str):
        # Certificate provided
        cert = cert_or_key if isinstance(cert_or_key, str) else cert_or_key.decode()
        return verify_with_certificate(tree, cert)
    else:
        # Public key object
        return verify_with_public_key(tree, cert_or_key)


__all__ = [
    "verify_signature",
    "verify_with_certificate",
    "verify_with_public_key",
    # Backward compatibility type aliases
    "PublicKeyTypes",
    "CertOrKeyType",
]
