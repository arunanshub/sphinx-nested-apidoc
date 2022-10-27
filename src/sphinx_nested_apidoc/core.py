from __future__ import annotations

import functools
import glob
import logging
import os
import sys
from contextlib import redirect_stdout
from os import path
from typing import Iterable, Iterator

from sphinx.ext import apidoc

logger = logging.getLogger(__name__)


@functools.lru_cache
def _safe_makedirs(name: str, mode: int = 0o755) -> bool:
    """
    The same ``os.makedirs``, except that it caches its arguments and returns
    boolean instead of raising an exception.

    Args:
        name: The name of the directory to create.
        mode: The creation mode.

    Returns:
        ``True`` if directory is created, ``False`` otherwise.
    """
    try:
        os.makedirs(name, mode, exist_ok=False)
    except FileExistsError:
        return False

    logger.debug("Create directory %s", name)
    return True


def _add_flag_if_not_present(
    arg: list[str],
    cond: bool,
    short_flag: str | None,
    flag: str,
) -> None:
    if cond and (flag not in arg or short_flag not in arg):
        arg.append(flag)


def sanitize_path(p: str) -> str:
    """
    Eliminates double slashes and relative path nastiness from the given path
    by treating them as relative to root path.

    Args:
        p: A string representing the path to be sanitized.

    Returns:
        Sanitized path as string.

    Note:
        On Windows, if the path contains a different drive letter, it will
        return an empty string.
    """
    try:
        sanitized = path.relpath(path.join(path.sep, p), path.sep)
    except ValueError:
        # Windows issue: given path is a different drive. Since it is invalid
        # anyway, we return empty string.
        return ""

    return "" if sanitized == "." else sanitized


def feed_sphinx_apidoc(
    output_dir: str,
    module_path: str,
    *sphinx_arguments: str,
    implicit_namespaces: bool = False,
    force: bool = False,
    suffix: str = "rst",
) -> bool:
    """Pass commands and flags to ``sphinx-apidoc``.

    Arguments:
        args: The flags and command to pass to ``sphinx-apidoc``.
        implicit_namespaces:
            Interpret module paths according to PEP-0420 implicit namespaces
            specification.
        force: Replace existing files.
        suffix: File suffix of the generated files.

    Returns:
        True if help flag is passed, otherwise False.

    Caution:
        ``sphinx-apidoc`` cannot handle situations where the supposed file in
        the ``output_dir`` is actually a directory.
    """
    # `--separate` puts documentation for each module on its own page.
    arguments = [
        "--output-dir",
        output_dir,
        module_path,
        "--separate",
        "--suffix",
        suffix,
        *sphinx_arguments,
    ]

    # show help info if user passes help flag.
    # NOTE: sphinx-apidoc's cmdline parser allows long options to be
    # abbreviated to a prefix. We can prevent it by using itertools.accumulate,
    # but choose to trust the user.
    help_flags = ("-h", "--help")
    if any(flag in sphinx_arguments for flag in help_flags):
        stdout = sys.stdout
        is_help = True
    else:
        is_help = False
        stdout = None
        _add_flag_if_not_present(
            arguments,
            implicit_namespaces,
            None,
            "--implicit-namespaces",
        )
        _add_flag_if_not_present(arguments, force, "-f", "--force")

        # if sphinx-apidoc is dry running, we cannot locate the generated
        # files.
        if "-n" in arguments:
            arguments.remove("-n")
        if "--dry-run" in arguments:
            arguments.remove("--dry-run")

    logger.debug("arguments: %s", arguments)
    logger.debug("stdout: %s", stdout)
    with redirect_stdout(stdout):
        apidoc.main(arguments)

    return is_help


def yield_source_files(
    source_dir: str,
    extension: str = "rst",
) -> Iterator[str]:
    """Yields files from source directory that end with the given extension.

    Args:
        source_dir: The directory where the files are located.
        extension: The extension of the file, without the "." prefix.

    Yields:
        Path to file that end with ``extension``.

    Raises:
        ValueError: If extension starts with a ".".
    """
    if extension.startswith("."):
        raise ValueError("extension must not start with '.'")

    pattern = path.join(
        path.normpath(source_dir),
        f"*{path.extsep}{extension}",
    )
    yield from filter(path.isfile, glob.iglob(pattern))


def get_nested_dir_filename(sphinx_source_file: str) -> str:
    """
    Convert a ``sphinx-apidoc`` based source file name into a nested directory
    based path.

    Args:
        sphinx_source_file: A ``sphinx-apidoc`` generated file.
        dest_dir: The destination directory where the new fill will be stored.

    Returns:
        A string representing the path of the file.

    Note:
        It does not handle the case where the source file is actually an index
        for a module, ie. It does not rename "a.b.module.rst" to
        "some/path/a/b/module/index.rst". Use
        :py:func:`get_destination_filename` for that.
    """
    src_filename = path.basename(sphinx_source_file)
    src_filename, ext = path.splitext(src_filename)
    return src_filename.replace(".", path.sep) + ext


@functools.lru_cache
def is_packagedir(directory: str) -> bool:
    """Checks if given directory is a package.

    This function caches its input to improve performance.
    """
    return any("__init__" in name for name in os.listdir(directory))


def get_destination_filename(
    sphinx_source_file: str,
    package_dir: str,
    extension: str = "rst",
    implicit_namespaces: bool = False,
    package_name: str | None = None,
) -> str:
    """
    Convert a ``sphinx-apidoc`` generated source file name into a nested
    directory based path, and rename to "index" files where necessary.

    Args:
        sphinx_source_file: Path to the ``sphinx-apidoc`` generated file.
        package_dir:
            The directory to compare ``sphinx-apidoc`` generated file against.
        extension: The extension of the ``sphinx-apidoc`` generated file.
        implicit_namespaces:
            Whether to treat ``package_dir`` as a package. If ``False``, any
            directory that does not contain ``__init__`` file will be ignored.
        package_name:
            Name of the directory to put all the package documentation in. This
            resides in the documentation directory. For example, it renames
            ``docs/myproj/a/b/c.rst`` to ``docs/newname/a/b/c.rst``, where
            ``newname`` is the new name of the directory. If ``None``, the name
            is derived from ``package_dir`` and sphinx source file.

    Returns:
        A string representing the path of the file.
    """
    package_dir = path.normpath(package_dir)

    # determine the source dir component that will be used to derive the
    # package directory from the sphinx-apidoc generated files.
    if is_packagedir(package_dir) or implicit_namespaces:
        root_module_name = path.basename(package_dir)
        source_dir_component = package_dir.rsplit(root_module_name, 1)[0]
    else:
        source_dir_component = package_dir

    nested_dir_path = dest_name = get_nested_dir_filename(sphinx_source_file)
    # determine the original directory path
    package_dir_path = path.splitext(nested_dir_path)[0]
    # check whether the package directory exists
    if path.exists(path.join(source_dir_component, package_dir_path)):
        dest_name = path.join(
            package_dir_path,
            f"index{path.extsep}{extension}",
        )

    # "docs/package/b/c/d.rst" => "docs/renamed/b/c/d.rst"
    if package_name is not None:
        dest_name = path.join(package_name, dest_name.split(path.sep, 1)[-1])
    return dest_name


def rename_files(
    sphinx_source_dir: str,
    package_dir: str,
    package_name: str | None = None,
    extension: str = "rst",
    implicit_namespaces: bool = False,
    dry_run: bool = False,
    force: bool = False,
    excluded_files: Iterable[str] = ("index", "modules"),
) -> None:
    """
    Renames the ``sphinx-apidoc`` generated files located in the source
    directory.

    Args:
        sphinx_source_dir:
            Path where the ``sphinx-apidoc`` generated files are located.
        package_dir:
            The directory to compare ``sphinx-apidoc`` generated file against.
        package_name:
            Name of the directory to put all the package documentation in. This
            resides in the documentation directory. For example, it renames
            ``docs/myproj/a/b/c.rst`` to ``docs/newname/a/b/c.rst``, where
            ``newname`` is the new name of the directory. If ``None``, the name
            is derived from ``package_dir`` and sphinx source file.
        extension: The extension of the ``sphinx-apidoc`` generated file.
        implicit_namespaces:
            Whether to treat ``package_dir`` as a package. If ``False``, any
            directory that does not contain ``__init__`` file will be ignored.
        dry_run: Runs but does not actually rename the files.
        force: Whether to replace files if they already exist.
        excluded_files:
            Name of files (**without extension**) that should not be
            renamed/modified. By default, it excludes ``index`` and
            ``modules``.
    """
    for source_file in yield_source_files(sphinx_source_dir, extension):
        # ignore `index` and `modules` files by default. `modules` is generated
        # when `sphinx-apidoc --full` is not used.
        # file_name: /a/b/c/docs/index.ext => index.ext => index
        file_name = path.splitext(path.basename(source_file))[0]
        if file_name in excluded_files:
            logger.debug("Skipping excluded file: %s", source_file)
            continue

        nested_dir_path = get_destination_filename(
            source_file,
            package_dir,
            extension,
            implicit_namespaces,
            package_name,
        )
        dest_path = path.join(sphinx_source_dir, nested_dir_path)
        dest_dir = path.split(dest_path)[0]

        if dry_run:
            logger.info("%s would be changed to %s", source_file, dest_path)
            continue

        # create the directories.
        # NOTE: We can create the directories beforehand by filtering out the
        # dirs from the destination filename.
        if not _safe_makedirs(dest_dir, mode=0o755):
            logger.debug("makedirs: %s already exists", dest_dir)

        if path.exists(dest_path) and not force:
            os.remove(source_file)  # remove leftover source files.
            logger.warning("%s already exists. Skipping.", dest_path)
            continue

        os.replace(source_file, dest_path)
        logger.info("%s -> %s", source_file, dest_path)
