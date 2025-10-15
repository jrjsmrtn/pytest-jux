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
