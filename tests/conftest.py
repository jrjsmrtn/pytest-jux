# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Shared test fixtures and configuration."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pytest

# Enable pytester plugin for testing pytest plugins
pytest_plugins = ["pytester"]


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
