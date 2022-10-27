from __future__ import annotations

import argparse
import logging

from . import __version__, start_logging
from .core import feed_sphinx_apidoc, rename_files, sanitize_path

logger = logging.getLogger(__name__)

APP_NAME = "sphinx-nested-apidoc"

APP_DESC = """\
Generates nested directory from sphinx-apidoc's flattened files. It is
simply a wrapper over sphinx-apidoc and you can pass additional arguments to it
for extended configuration.
"""

CLI_APP_EPILOG = f"""\
{APP_NAME} is licensed under MIT license.

Visit <https://github.com/arunanshub/sphinx-nested-apidoc> for more info.
"""


def main(argv: list[str] | None = None) -> int:
    logging_levels = {
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG,
    }

    ps = argparse.ArgumentParser(
        description=APP_DESC,
        epilog=CLI_APP_EPILOG,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = ps.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=3,
        help="Increase application verbosity."
        " This option is repeatable and will increase verbosity each time it"
        " is repeated. This option cannot be used when -q/--quiet is used.",
    )
    group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Disable logging."
        " This option cannot be used when -v/--verbose is used.",
    )
    ps.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    ps.add_argument(
        "module_path",
        type=str,
        help="Path to package to document.",
    )
    ps.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Replace existing files.",
    )
    ps.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Run the script without creating files",
    )
    ps.add_argument(
        "-o",
        "--output-dir",
        dest="destdir",
        required=True,
        type=str,
        help="directory to place all output",
    )
    ps.add_argument(
        "--package-name",
        type=str,
        help="Name of the directory to put the package documentation in."
        " By default it is the name of the package itself.",
    )

    # sphinx-apidoc specific options
    sphinx_group = ps.add_argument_group("sphinx-apidoc options")
    sphinx_group.add_argument(
        "-s",
        "--suffix",
        default="rst",
        help="file suffix",
    )
    sphinx_group.add_argument(
        "--implicit-namespaces",
        action="store_true",
        help="interpret module paths according to PEP-0420 implicit namespaces"
        " specification",
    )
    sphinx_group.add_argument(
        "sphinx_commands",
        nargs=argparse.REMAINDER,
        help="Commands and flags to supply to sphinx-apidoc. Note that some"
        " arguments like `--dry-run` are ignored.",
        metavar="...",
    )

    args = ps.parse_args(argv)
    if not args.quiet:
        verbose = args.verbose
        if args.verbose > 5:
            verbose = 5
        start_logging(logging_levels[verbose])

    is_help = feed_sphinx_apidoc(
        args.destdir,
        args.module_path,
        *args.sphinx_commands,
        implicit_namespaces=args.implicit_namespaces,
        force=args.force,
        suffix=args.suffix,
    )

    if is_help:
        ps.exit(0)

    try:
        rename_files(
            args.destdir,
            args.module_path,
            package_name=(
                sanitize_path(args.package_name)
                if args.package_name is not None
                else None
            ),
            extension=args.suffix,
            implicit_namespaces=args.implicit_namespaces,
            dry_run=args.dry_run,
            force=args.force,
        )
    except ValueError as e:
        logger.error("%s", e, exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    main()
