# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Sphinx configuration for pytest-jux documentation."""

import sys
from pathlib import Path

# Add parent directory to path so we can import pytest_jux
sys.path.insert(0, str(Path(__file__).parent.parent))

# -- Project information -----------------------------------------------------

project = "pytest-jux"
copyright = "2025, Georges Martin"
author = "Georges Martin"

# The version info
# Read from pyproject.toml
import tomllib  # noqa: E402 - Required after Path import for Sphinx config

with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
    version = pyproject["project"]["version"]
    release = version

# -- General configuration ---------------------------------------------------

extensions = [
    # Sphinx core extensions
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx.ext.napoleon",  # Support for NumPy and Google style docstrings
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation
    "sphinx.ext.todo",  # Support for todo items
    # Third-party extensions
    "myst_parser",  # Markdown support
    "sphinx_argparse_cli",  # CLI documentation from argparse
    "sphinx_autodoc_typehints",  # Type hints in docs
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv",
    "sprints",  # Exclude sprint planning docs from built documentation
]

# -- MyST-Parser configuration -----------------------------------------------

# Enable MyST extensions
myst_enable_extensions = [
    "colon_fence",  # ::: fences
    "deflist",  # Definition lists
    "fieldlist",  # Field lists
    "html_admonition",  # HTML-style admonitions
    "html_image",  # HTML img tags
    "linkify",  # Auto-link URLs
    "replacements",  # Text replacements
    "smartquotes",  # Smart quotes
    "strikethrough",  # ~~strikethrough~~
    "substitution",  # Variable substitutions
    "tasklist",  # Task lists with checkboxes
]

# Heading anchors
myst_heading_anchors = 3

# -- Autodoc configuration ---------------------------------------------------

# Automatically extract typehints
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Include __init__ docstrings
autoclass_content = "both"

# Sort members by source order
autodoc_member_order = "bysource"

# Document __init__, __repr__, etc.
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "special-members": "__init__",
    "inherited-members": False,
    "show-inheritance": True,
}

# -- Autosummary configuration -----------------------------------------------

autosummary_generate = True  # Generate stub pages automatically

# -- Napoleon configuration --------------------------------------------------

# Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Include __init__ in class docs
napoleon_include_init_with_doc = True

# -- Intersphinx configuration -----------------------------------------------

# Link to external documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
    "lxml": ("https://lxml.de/apidoc", None),
    "cryptography": ("https://cryptography.io/en/latest", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages
html_theme = "furo"

# Theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#3f51b5",  # Indigo
        "color-brand-content": "#3f51b5",
    },
    "dark_css_variables": {
        "color-brand-primary": "#7986cb",  # Light indigo
        "color-brand-content": "#7986cb",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []  # No custom static files yet

# Custom sidebar templates
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon
# html_favicon = None

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = True

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output
todo_include_todos = False
