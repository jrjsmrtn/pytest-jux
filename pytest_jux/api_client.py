# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Jux API client for publishing signed JUnit XML reports.

This module re-exports the Jux API client from py-juxlib for backward compatibility.
All functionality is provided by juxlib.api.

API Specification: Jux API v1.0.0 (released 2025-01-24)
Endpoint: POST /api/v1/junit/submit
Content-Type: application/xml
Authentication: Bearer token (remote) or localhost bypass

Example:
    >>> from pytest_jux.api_client import JuxAPIClient, PublishResponse
    >>> client = JuxAPIClient(
    ...     api_url="https://jux.example.com/api/v1",
    ...     bearer_token="your-api-token"
    ... )
    >>> response = client.publish_report(signed_xml)
    >>> print(response.test_run.id)

Note:
    This module is a thin wrapper around juxlib.api for backward compatibility.
    New code should import directly from juxlib.api.
"""

# Re-export from juxlib.api for backward compatibility
from juxlib.api import JuxAPIClient, PublishResponse, TestRun

__all__ = ["JuxAPIClient", "PublishResponse", "TestRun"]
