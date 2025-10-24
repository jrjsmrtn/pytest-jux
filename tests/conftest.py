# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Shared test fixtures and configuration."""

import pytest

# Enable pytester plugin for testing pytest plugins
pytest_plugins = ["pytester"]


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
