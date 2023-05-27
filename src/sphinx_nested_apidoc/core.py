from __future__ import annotations

import functools
import logging
import sys
from contextlib import redirect_stdout
from os import path
from pathlib import Path
from typing import Iterable, Iterator

from sphinx.ext import apidoc

logger = logging.getLogger(__name__)


@functools.lru_cache
def _safe_makedirs(name: Path, mode: int = 0o755) -> bool:
    """
    The same ``Path.mkdir``, except that it caches its arguments and returns
    boolean instead of raising an exception.

    Args:
        name: The name of the directory to create.
        mode: The creation mode.

    Returns:
        ``True`` if directory is created, ``False`` otherwise.
    """
    try:
        name.mkdir(mode, True, False)
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


def sanitize_path(path_: Path) -> Path:
    """
    Eliminates double slashes and relative path nastiness from the given path
    by treating them as relative to root path.

    Args:
        path_: A string representing the path to be sanitized.

    Returns:
        Sanitized path as string.

    Note:
        On Windows, if the path contains a different drive letter, it will
        return an empty string.
    """
    try:
        sanitized = (path.sep / path_).relative_to("/")
    except ValueError:
        # Windows issue: given path is a different drive. Since it is invalid
        # anyway, we return empty string.
        return Path()

    return Path() if sanitized == "." else sanitized


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
        output_dir:
            Directory where ``sphinx-apidoc`` should store its generated files.
        module_path:
            The path to the package that is being documented. Note that it is
            more appropriate to call it ``package_path`` but we are following
            ``sphinx-apidoc``'s conventions here.
        sphinx_arguments: The flags and command to pass to ``sphinx-apidoc``.

    Keyword arguments:
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
    source_dir: Path,
    extension: str = "rst",
) -> Iterator[Path]:
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
        msg = "extension must not start with '.'"
        raise ValueError(msg)

    yield from filter(
        Path.is_file, source_dir.glob(f"*{path.extsep}{extension}")
    )


def get_nested_dir_filename(sphinx_source_file: Path) -> Path:
    """
    Convert a ``sphinx-apidoc`` based source file name into a nested directory
    based path.

    Args:
        sphinx_source_file: A ``sphinx-apidoc`` generated file.

    Returns:
        A string representing the path of the file.

    Note:
        It does not handle the case where the source file is actually an index
        for a module, i.e. It does not rename "a.b.module.rst" to
        "some/path/a/b/module/index.rst". Use
        :py:func:`get_destination_filename` for that.
    """
    return Path(
        sphinx_source_file.stem.replace(".", path.sep)
        + sphinx_source_file.suffix
    )


@functools.lru_cache
def is_packagedir(directory: Path) -> bool:
    """Checks if given directory is a package.

    This function caches its input to improve performance.
    """
    return any(directory.glob("__init__*"))


def get_destination_filename(
    sphinx_source_file: Path,
    package_dir: Path,
    extension: str = "rst",
    implicit_namespaces: bool = False,
    package_name: Path | None = None,
) -> Path:
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
    if is_packagedir(package_dir) or implicit_namespaces:
        # /some/path/src => /some/path
        source_dir_component = package_dir.parent
    else:
        # /some/path/src/package remains same
        source_dir_component = package_dir

    # package.a.b.rst => package/a/b.rst
    dest_name = get_nested_dir_filename(sphinx_source_file)
    # package/a/b.rst => package/a/b
    package_dir_path = dest_name.with_suffix("")
    # does /some/path/src/package/a/b exist?
    if (source_dir_component / package_dir_path).exists():
        # package/a/b => package/a/b/index.rst
        dest_name = package_dir_path / f"index{path.extsep}{extension}"

    # package/a/b.rst => newname/a/b.rst
    if package_name is not None:
        dest_name = package_name / str(dest_name).split(path.sep, 1)[-1]
    return dest_name


def rename_files(
    sphinx_source_dir: Path,
    package_dir: Path,
    package_name: Path | None = None,
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
        # file_name: /a/b/c/docs/index.ext => index
        file_name = source_file.stem
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
        dest_path = sphinx_source_dir / nested_dir_path
        dest_dir = dest_path.parent

        if dry_run:
            logger.info("%s would be changed to %s", source_file, dest_path)
            continue

        # create the directories.
        # NOTE: We can create the directories beforehand by filtering out the
        # dirs from the destination filename.
        if not _safe_makedirs(dest_dir, mode=0o755):
            logger.debug("makedirs: %s already exists", dest_dir)

        if dest_path.exists() and not force:
            source_file.unlink()  # remove leftover source files.
            logger.warning("%s already exists. Skipping.", dest_path)
            continue

        source_file.rename(dest_path)
        logger.info("%s -> %s", source_file, dest_path)
