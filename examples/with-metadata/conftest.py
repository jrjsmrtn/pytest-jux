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

"""pytest configuration for metadata example.

This conftest.py demonstrates how to programmatically add metadata to pytest
sessions using the pytest_metadata hook.
"""

import os
import platform

import pytest


@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata):
    """Add custom metadata to pytest session.

    This hook is called by pytest-metadata to allow plugins and conftest.py
    files to contribute metadata to the test session.

    Args:
        metadata: Dictionary of metadata that will be included in reports
    """
    # Add system information
    metadata['os_type'] = platform.system()
    metadata['os_release'] = platform.release()
    metadata['os_version'] = platform.version()
    metadata['machine'] = platform.machine()
    metadata['processor'] = platform.processor() or 'unknown'

    # Add Python implementation details
    metadata['python_implementation'] = platform.python_implementation()
    metadata['python_compiler'] = platform.python_compiler()

    # Add example application metadata
    metadata['app_name'] = 'pytest-jux-example'
    metadata['app_version'] = '0.1.4'
    metadata['test_suite'] = 'with-metadata-example'

    # Add environment variables if present (common in CI/CD)
    ci_vars = {
        'CI': os.getenv('CI'),
        'CI_COMMIT_SHA': os.getenv('CI_COMMIT_SHA'),
        'CI_COMMIT_BRANCH': os.getenv('CI_COMMIT_BRANCH'),
        'CI_JOB_ID': os.getenv('CI_JOB_ID'),
        'CI_PIPELINE_ID': os.getenv('CI_PIPELINE_ID'),
        'GITHUB_SHA': os.getenv('GITHUB_SHA'),
        'GITHUB_REF': os.getenv('GITHUB_REF'),
        'GITHUB_RUN_ID': os.getenv('GITHUB_RUN_ID'),
    }

    # Only add CI variables that are actually set
    for key, value in ci_vars.items():
        if value is not None:
            metadata[key] = value

    # Remove sensitive or overly verbose metadata
    # This is a best practice to avoid leaking secrets or cluttering reports
    metadata.pop('Plugins', None)  # Plugin list can be very long
    metadata.pop('JAVA_HOME', None)  # Remove if it exists (example of sensitive path)

    # You can also conditionally remove metadata based on environment
    if not os.getenv('CI'):
        # Remove some metadata when running locally
        metadata.pop('Packages', None)  # Local package versions may not be relevant


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest with custom markers.

    Args:
        config: pytest configuration object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items after collection.

    This hook demonstrates how to automatically add markers based on test names
    or other criteria.

    Args:
        config: pytest configuration object
        items: List of collected test items
    """
    # Example: automatically mark integration tests
    for item in items:
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
