from __future__ import annotations

import glob
import logging
import os
import subprocess
from os import path
from typing import Iterator

logger = logging.getLogger(__name__)


def _add_flag_if_not_present(arg: list[str], flag: bool, name: str) -> None:
    if flag and name not in arg:
        arg.append("--implicit-namespaces")


def feed_sphinx_apidoc(
    *args: str,
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

    Raises:
        ValueError: If ``sphinx-apidoc`` exited with non-zero exit code.
    """
    arguments = ["sphinx-apidoc", "--separate", "--suffix", suffix, *args]

    # show help info if user passes help flag.
    help_flags = ("--help", "-h")
    if any(flag in args for flag in help_flags):
        stdout = None
        is_help = True
    else:
        is_help = False
        stdout = subprocess.PIPE
        # `--separate` puts documentation for each module on its own page.
        _add_flag_if_not_present(
            arguments,
            implicit_namespaces,
            "--implicit-namespaces",
        )
        _add_flag_if_not_present(arguments, force, "--force")

    with subprocess.Popen(arguments, stdout=stdout) as proc:
        if proc.wait():
            raise ValueError("sphinx-apidoc exited with non-zero exit code")

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
    """
    if extension.startswith("."):
        raise ValueError("extension must not start with '.'")

    pattern = path.join(
        path.normpath(source_dir),
        f"*{path.extsep}{extension}",
    )
    yield from glob.iglob(pattern)


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


def is_packagedir(directory: str) -> bool:
    """Checks if given directory is a package."""
    return any("__init__" in name for name in os.listdir(directory))


def get_destination_filename(
    sphinx_source_file: str,
    package_dir: str,
    extension: str = "rst",
    implicit_namespaces: bool = False,
) -> str:
    """
    Convert a ``sphinx-apidoc`` generated source file name into a nested
    directory based path, and insert "index" files where necessary.

    Args:
        sphinx_source_file: Path to the ``sphinx-apidoc`` generated file.
        package_dir:
            The directory to compare ``sphinx-apidoc`` generated file against.
        extension: The extension of the ``sphinx-apidoc`` generated file.
        implicit_namespaces:
            Whether to treat ``package_dir`` as a package. If ``False``, any
            directory that does not contain ``__init__`` file will be ignored.

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
    return dest_name


def rename_files(
    sphinx_source_dir: str,
    package_dir: str,
    extension: str = "rst",
    implicit_namespaces: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Renames the ``sphinx-apidoc`` generated files located in the source
    directory.

    Args:
        sphinx_source_dir:
            Path where the ``sphinx-apidoc`` generated files are located.
        package_dir:
            The directory to compare ``sphinx-apidoc`` generated file against.
        extension: The extension of the ``sphinx-apidoc`` generated file.
        implicit_namespaces:
            Whether to treat ``package_dir`` as a package. If ``False``, any
            directory that does not contain ``__init__`` file will be ignored.
        dry_run: Runs but does not actually rename the files.
    """
    for source_file in yield_source_files(sphinx_source_dir, extension):
        nested_dir_path = get_destination_filename(
            source_file,
            package_dir,
            extension,
            implicit_namespaces,
        )
        dest_path = path.join(sphinx_source_dir, nested_dir_path)
        dest_dir = path.split(dest_path)[0]

        if dry_run:
            logger.info("%s would be changed to %s", source_file, dest_path)
            continue

        # create the directories.
        # NOTE: We can create the directories beforehand by filtering out the
        # dirs from the destination filename.
        try:
            os.makedirs(dest_dir, exist_ok=False, mode=0o755)
        except FileExistsError:
            logger.debug("makedirs: %s already exists", dest_dir)

        # replace the sphinx file with the new file.
        try:
            os.replace(source_file, dest_path)
        except OSError:
            logger.warning("replace: %s already exists", dest_path)

        logger.info("%s -> %s", source_file, dest_path)
