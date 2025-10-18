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

"""Example tests demonstrating pytest-metadata integration with pytest-jux.

This example shows how to:
1. Enable metadata inclusion in JUnit XML reports
2. Access metadata in tests
3. Generate signed reports with custom metadata

Run this example with:

    pytest test_example.py \\
        --junit-xml=report.xml \\
        --jux-sign \\
        --jux-key ../../.jux-dogfood/signing_key.pem \\
        --metadata build_id 12345 \\
        --metadata environment staging \\
        --metadata commit_sha abc123def

The generated report.xml will include:
- Custom metadata as property tags
- XMLDSig signature
- Standard pytest information
"""

import pytest

# Enable metadata inclusion in JUnit XML
# This is required for pytest-metadata to add property tags to the XML
pytestmark = pytest.mark.usefixtures('include_metadata_in_junit_xml')


def test_basic_assertion():
    """A simple passing test."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    greeting = "Hello, pytest-jux!"
    assert "pytest-jux" in greeting
    assert greeting.startswith("Hello")


def test_with_metadata_access(metadata):
    """Test that can access session metadata.

    Args:
        metadata: pytest-metadata fixture providing access to session metadata
    """
    # You can access pytest metadata in tests
    print(f"\nPython version: {metadata.get('Python', 'unknown')}")
    print(f"Platform: {metadata.get('Platform', 'unknown')}")

    # Check for custom metadata added via command line
    if 'build_id' in metadata:
        print(f"Build ID: {metadata['build_id']}")

    if 'environment' in metadata:
        print(f"Environment: {metadata['environment']}")

    # The test always passes - this is just demonstrating metadata access
    assert True


@pytest.mark.parametrize("value,expected", [
    (0, False),
    (1, True),
    (42, True),
    (-1, True),
])
def test_parametrized(value, expected):
    """Parametrized test example.

    Args:
        value: Input value
        expected: Expected boolean result
    """
    assert bool(value) == expected


class TestCalculator:
    """Example test class demonstrating grouped tests."""

    def test_addition(self):
        """Test addition operation."""
        assert 2 + 2 == 4

    def test_subtraction(self):
        """Test subtraction operation."""
        assert 5 - 3 == 2

    def test_multiplication(self):
        """Test multiplication operation."""
        assert 3 * 4 == 12

    def test_division(self):
        """Test division operation."""
        assert 10 / 2 == 5


def test_list_operations():
    """Test list operations."""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert 3 in numbers
    assert numbers[0] == 1
    assert numbers[-1] == 5


@pytest.mark.slow
def test_marked_test():
    """Test with custom marker.

    This test is marked as 'slow' and can be selectively run or skipped
    using pytest markers.
    """
    # Simulate some work
    result = sum(range(1000))
    assert result == 499500


def test_exception_handling():
    """Test exception handling."""
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0


def test_approximate_comparison():
    """Test floating point comparison with pytest.approx."""
    assert 0.1 + 0.2 == pytest.approx(0.3)


@pytest.fixture
def sample_data():
    """Fixture providing sample test data."""
    return {"name": "pytest-jux", "version": "0.1.4", "type": "plugin"}


def test_with_fixture(sample_data):
    """Test using a custom fixture.

    Args:
        sample_data: Sample data from fixture
    """
    assert sample_data["name"] == "pytest-jux"
    assert "version" in sample_data
    assert sample_data["type"] == "plugin"
