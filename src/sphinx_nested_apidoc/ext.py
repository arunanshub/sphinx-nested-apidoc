from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx

from . import __version__
from .core import feed_sphinx_apidoc, rename_files, sanitize_path


def _execute(
    package_dir: str,
    doc_dir: str,
    package_name: str | None,
    suffix: str,
    excluded_files: typing.Iterable[str],
    module_first: bool,
    implicit_namespaces: bool,
) -> None:
    extra_args = []
    if module_first:
        extra_args.append("--module-first")

    feed_sphinx_apidoc(
        doc_dir,
        package_dir,
        "--full",  # without `full` sphinx-build cannot find `index.rst`
        *extra_args,
        suffix=suffix,
        implicit_namespaces=implicit_namespaces,
    )

    rename_files(
        doc_dir,
        package_dir,
        (sanitize_path(package_name) if package_name is not None else None),
        suffix,
        implicit_namespaces=implicit_namespaces,
        excluded_files=excluded_files,
    )


def _builder_inited(app: Sphinx) -> None:
    config = app.config
    docdir = app.srcdir
    package_dir = config.sphinx_nested_apidoc_package_dir
    package_name = config.sphinx_nested_apidoc_package_name
    suffix = config.sphinx_nested_apidoc_suffix
    excluded_files = config.sphinx_nested_apidoc_excluded_files
    module_first = config.sphinx_nested_apidoc_module_first
    implicit_namespaces = config.sphinx_nested_apidoc_implicit_namespaces
    _execute(
        package_dir,
        docdir,
        package_name,
        suffix,
        excluded_files,
        module_first,
        implicit_namespaces,
    )


def setup(app: Sphinx) -> dict[str, str | bool]:
    rebuild_cond = "env"
    app.connect("builder-inited", _builder_inited)
    # package_dir is where our package to document resides.
    app.add_config_value(
        "sphinx_nested_apidoc_package_dir",
        None,
        rebuild_cond,
        [str],
    )
    # Name of the directory to put the package documentation in. By
    # default it is the name of the package itself.
    app.add_config_value(
        "sphinx_nested_apidoc_package_name",
        None,
        rebuild_cond,
        [str, None],
    )
    # The suffix of the generated documentation files.
    app.add_config_value(
        "sphinx_nested_apidoc_suffix",
        "rst",
        rebuild_cond,
        [str],
    )
    # List of files to exclude from modification/renaming.
    app.add_config_value(
        "sphinx_nested_apidoc_excluded_files",
        ("index", "modules"),
        rebuild_cond,
        [list],
    )
    # put module documentation before submodule documentation.
    app.add_config_value(
        "sphinx_nested_apidoc_module_first",
        False,
        rebuild_cond,
        [bool],
    )
    # interpret module paths according to PEP-0420 implicit namespaces
    # specification.
    app.add_config_value(
        "sphinx_nested_apidoc_implicit_namespaces",
        False,
        rebuild_cond,
        [bool],
    )

    return {"version": __version__, "parallel_read_safe": True}
