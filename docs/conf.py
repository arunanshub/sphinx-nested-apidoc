# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

from datetime import date

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sphinx-nested-apidoc"
author = "Arunanshu Biswas"
copyright = f"2021-{date.today().year}, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

sphinx_nested_apidoc_package_dir = "src"
sphinx_nested_apidoc_package_name = "src"

language = "en"

# Order by source
autodoc_member_order = "bysource"

# Show typehints in documentation only.
autodoc_typehints = "signature"

# Do not show the fully qualified name for a type.
autodoc_typehints_format = "short"

# map to python builtins
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
