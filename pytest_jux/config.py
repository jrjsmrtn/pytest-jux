# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Configuration management for pytest-jux.

This module re-exports configuration functionality from py-juxlib for
backward compatibility. All functionality is provided by juxlib.config.

Note:
    This module is a thin wrapper around juxlib.config for backward compatibility.
    New code should import directly from juxlib.config.
"""

# Re-export all configuration classes and functions from juxlib
from juxlib.config import (
    ConfigSchema,
    ConfigurationManager,
    ConfigValidationError,
    StorageMode,
    get_default_config_path,
    get_xdg_config_home,
    get_xdg_data_home,
)

__all__ = [
    # Main classes
    "ConfigurationManager",
    "ConfigSchema",
    "StorageMode",
    # Exceptions
    "ConfigValidationError",
    # Utility functions
    "get_default_config_path",
    "get_xdg_config_home",
    "get_xdg_data_home",
]
