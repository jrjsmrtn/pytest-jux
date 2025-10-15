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

import pytest


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
        "--jux-publish",
        action="store_true",
        default=False,
        help="Publish signed reports to Jux API",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure plugin based on command-line options.

    Args:
        config: pytest configuration object
    """
    # TODO: Implement plugin configuration
    pass
