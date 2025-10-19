# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Security test suite for pytest-jux.

This module contains security-focused tests for signature verification,
XML attack protection, and cryptographic operations.

Test Categories:
- Signature attack tests (stripping, wrapping, bypass)
- XML attack tests (XXE, billion laughs, bombs)
- Cryptographic operation tests (constant-time, key validation)
- Fuzzing tests (malformed inputs)
"""

__all__ = []
