# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for pytest-jux.

These tests use jux-mock-server's LiveMockServer to test the full
HTTP client flow against a real server.

Requirements:
- jux-mock-server v0.5.0+ (for LiveMockServer)
- Install with: uv pip install -e ../jux-mock-server
"""
