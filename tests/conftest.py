# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Shared test fixtures and configuration.

This module provides fixtures for:
- pytest plugin testing (pytester)
- Integration testing with jux-mock-server
- Local test fixtures (keys, certificates, JUnit XML samples)
- Shared JUnit XML fixtures from junit-xml-test-fixtures repository
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

# Enable pytester plugin for testing pytest plugins
pytest_plugins = ["pytester"]

# =============================================================================
# Path Constants
# =============================================================================

# Local fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
KEYS_DIR = FIXTURES_DIR / "keys"
JUNIT_XML_DIR = FIXTURES_DIR / "junit_xml"

# Shared JUnit XML test fixtures repository
# Located at: ../junit-xml-test-fixtures/ relative to pytest-jux
SHARED_FIXTURES_DIR = Path(__file__).parent.parent.parent / "junit-xml-test-fixtures"

# Key subdirectories in shared fixtures
WINDYROAD_SCHEMA = SHARED_FIXTURES_DIR / "windyroad-junit-schema"

# =============================================================================
# Shared Fixture Availability
# =============================================================================

SHARED_FIXTURES_AVAILABLE = SHARED_FIXTURES_DIR.exists()


# Check if jux-mock-server is available for integration tests
# LiveMockServer (for external HTTP clients) requires jux-mock-server v0.5.0+
try:
    from jux_mock_server.testing import LiveMockServer

    LIVE_MOCK_SERVER_AVAILABLE = True
except ImportError:
    LIVE_MOCK_SERVER_AVAILABLE = False

if TYPE_CHECKING:
    from jux_mock_server.testing import LiveMockServer as LiveMockServerType


@pytest.fixture
def pytester_with_jux(pytester):
    """Pytester fixture with pytest-jux and pytest-metadata pre-installed.

    This ensures that integration tests have access to both plugins.
    """
    # Add the current source directory to the Python path
    pytester.syspathinsert()

    # Create a pytest.ini that loads both plugins
    pytester.makeini(
        """
        [pytest]
        """
    )

    return pytester


@pytest.fixture
def live_mock_server() -> Iterator[Any]:
    """Provide a live mock Jux server for external HTTP client tests.

    This fixture starts a real HTTP server on a random port, suitable
    for testing with external HTTP clients like JuxAPIClient.

    Requires jux-mock-server v0.5.0+ (LiveMockServer feature).

    Yields:
        LiveMockServer instance with url property and request recording.
    """
    if not LIVE_MOCK_SERVER_AVAILABLE:
        pytest.skip(
            "LiveMockServer not available. Requires jux-mock-server v0.5.0+ "
            "(install with: uv pip install -e ../jux-mock-server)"
        )
    with LiveMockServer() as server:  # type: ignore[name-defined]
        yield server


@pytest.fixture
def sample_junit_xml() -> str:
    """Sample JUnit XML for integration testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="pytest" tests="3" failures="1" errors="0" skipped="0" time="1.5">
    <properties>
      <property name="project" value="test-project"/>
      <property name="git:branch" value="main"/>
      <property name="git:commit" value="abc123def456"/>
    </properties>
    <testcase classname="tests.test_example" name="test_passing" time="0.5"/>
    <testcase classname="tests.test_example" name="test_another" time="0.5"/>
    <testcase classname="tests.test_example" name="test_failing" time="0.5">
      <failure message="AssertionError">assert False</failure>
    </testcase>
  </testsuite>
</testsuites>
"""


# =============================================================================
# Local Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to local test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def keys_dir() -> Path:
    """Path to test keys directory."""
    return KEYS_DIR


@pytest.fixture
def rsa_private_key_path() -> Path:
    """Path to RSA private key for testing."""
    return KEYS_DIR / "test-private.pem"


@pytest.fixture
def rsa_certificate_path() -> Path:
    """Path to RSA certificate for testing."""
    return KEYS_DIR / "test-cert.pem"


@pytest.fixture
def ec_private_key_path() -> Path:
    """Path to EC private key for testing."""
    return KEYS_DIR / "test-ec-private.pem"


@pytest.fixture
def ec_certificate_path() -> Path:
    """Path to EC certificate for testing."""
    return KEYS_DIR / "test-ec-cert.pem"


@pytest.fixture
def local_junit_xml_dir() -> Path:
    """Path to local JUnit XML fixtures directory."""
    return JUNIT_XML_DIR


# =============================================================================
# Shared JUnit XML Fixtures
# =============================================================================


@pytest.fixture
def shared_fixtures_available() -> bool:
    """Check if shared junit-xml-test-fixtures repository is available."""
    return SHARED_FIXTURES_AVAILABLE


@pytest.fixture
def shared_fixtures_dir() -> Path:
    """Path to shared junit-xml-test-fixtures repository.

    Raises:
        pytest.skip: If shared fixtures are not available
    """
    if not SHARED_FIXTURES_AVAILABLE:
        pytest.skip("Shared junit-xml-test-fixtures not available")
    return SHARED_FIXTURES_DIR


# =============================================================================
# Parametrized Fixture Helpers
# =============================================================================




def get_local_junit_xml_files() -> list[Path]:
    """Get all local JUnit XML fixture files."""
    if not JUNIT_XML_DIR.exists():
        return []
    return sorted(JUNIT_XML_DIR.glob("*.xml"))




# =============================================================================
# Pytest Configuration
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "shared_fixtures: tests that require shared junit-xml-test-fixtures",
    )


@pytest.fixture(autouse=True)
def skip_shared_fixture_tests(request: pytest.FixtureRequest) -> Iterator[None]:
    """Skip tests marked with shared_fixtures if fixtures unavailable."""
    marker = request.node.get_closest_marker("shared_fixtures")
    if marker is not None and not SHARED_FIXTURES_AVAILABLE:
        pytest.skip("Shared junit-xml-test-fixtures not available")
    yield
