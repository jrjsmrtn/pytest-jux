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

"""pytest plugin hooks for Jux test report signing and publishing.

This module implements the pytest plugin hooks for capturing JUnit XML
reports, signing them with XMLDSig, and publishing them to the Jux API.
"""

from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add plugin command-line options.

    Args:
        parser: pytest command-line parser
    """
    group = parser.getgroup("jux", "Jux test report signing and publishing")
    group.addoption(
        "--jux-sign",
        action="store_true",
        default=False,
        help="Enable signing of JUnit XML reports",
    )
    group.addoption(
        "--jux-key",
        action="store",
        default=None,
        help="Path to private key for signing (PEM format)",
    )
    group.addoption(
        "--jux-cert",
        action="store",
        default=None,
        help="Path to X.509 certificate for signing (PEM format, optional)",
    )
    group.addoption(
        "--jux-publish",
        action="store_true",
        default=False,
        help="Publish signed reports to Jux API",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure plugin based on command-line options.

    Args:
        config: pytest configuration object

    Raises:
        pytest.UsageError: If configuration is invalid
    """
    jux_sign = config.getoption("jux_sign")
    jux_key = config.getoption("jux_key")
    jux_cert = config.getoption("jux_cert")

    # Store configuration in config object for later use
    config._jux_sign = jux_sign  # type: ignore[attr-defined]
    config._jux_key_path = jux_key  # type: ignore[attr-defined]
    config._jux_cert_path = jux_cert  # type: ignore[attr-defined]

    # Validate configuration
    if jux_sign:
        if not jux_key:
            raise pytest.UsageError(
                "Error: --jux-sign requires --jux-key to specify the private key path"
            )

        # Verify key file exists
        key_path = Path(jux_key)
        if not key_path.exists():
            raise pytest.UsageError(f"Error: Key file not found: {jux_key}")

        # If certificate provided, verify it exists
        if jux_cert:
            cert_path = Path(jux_cert)
            if not cert_path.exists():
                raise pytest.UsageError(
                    f"Error: Certificate file not found: {jux_cert}"
                )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Sign JUnit XML report after test session completes.

    This hook is called after the test session finishes. If signing is enabled
    and a JUnit XML report was generated, it signs the report with the
    configured private key.

    Args:
        session: pytest session object
        exitstatus: pytest exit status code
    """
    # Check if signing is enabled
    if not getattr(session.config, "_jux_sign", False):
        return

    # Check if JUnit XML report was configured
    xmlpath = getattr(session.config.option, "xmlpath", None)
    if not xmlpath:
        return

    # Get configuration
    key_path_str = getattr(session.config, "_jux_key_path", None)
    cert_path_str = getattr(session.config, "_jux_cert_path", None)

    if not key_path_str:
        return

    try:
        # Load the generated JUnit XML
        xml_path = Path(xmlpath)
        if not xml_path.exists():
            # XML file wasn't generated (no tests ran, etc.)
            return

        tree = load_xml(xml_path)

        # Load private key
        key = load_private_key(Path(key_path_str))

        # Load certificate if provided
        cert: str | bytes | None = None
        if cert_path_str:
            cert = Path(cert_path_str).read_bytes()

        # Sign the XML
        signed_tree = sign_xml(tree, key, cert)

        # Write signed XML back to file
        with open(xml_path, "wb") as f:
            f.write(
                etree.tostring(
                    signed_tree,
                    xml_declaration=True,
                    encoding="utf-8",
                    pretty_print=True,
                )
            )

    except Exception as e:
        # Report error but don't fail the test run
        import warnings

        warnings.warn(f"Failed to sign JUnit XML report: {e}", stacklevel=2)
