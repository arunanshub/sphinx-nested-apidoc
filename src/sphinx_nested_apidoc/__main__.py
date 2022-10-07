import argparse
import logging

from . import __version__, start_logging
from .nested import feed_sphinx_apidoc, rename_rsts

APP_NAME = "sphinx-nested-apidoc"

APP_DESC = """\
sphinx-nested-apidoc: When flattened is not enough.

sphinx-nested-apidoc is a command-line tool which generates nested directory
from sphinx-apidoc's flattened rst files. It is simply a wrapper over
sphinx-apidoc and you can pass additional arguments to it for extended
configuration.
"""

CLI_APP_EPILOG = """\
sphinx-nested-apidoc is licensed under MIT license.

Visit <https://github.com/arunanshub/sphinx-nested-apidoc> for more info.
"""


def main():
    logging_levels = {
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG,
    }

    ps = argparse.ArgumentParser(
        prog=APP_NAME,
        description=APP_DESC,
        epilog=CLI_APP_EPILOG,
    )
    group = ps.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=3,
        help="Increase application verbosity."
        " This option is repeatable and will increase verbosity each time "
        "it is repeated."
        " This option cannot be used when -q/--quiet is used.",
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
        version="%(prog)s " + __version__,
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
        "-o",
        "--output-dir",
        dest="destdir",
        required=True,
        type=str,
        help="directory to place all output",
    )
    ps.add_argument(
        "sphinx_commands",
        nargs=argparse.REMAINDER,
        help="Commands and flags to supply to sphinx-apidoc.",
    )

    args = ps.parse_args()

    if not args.quiet:
        if args.verbose > 5:
            verbose = 5
        else:
            verbose = args.verbose
        start_logging(logging_levels[verbose])

    sphinx_commands = args.sphinx_commands
    if args.force:
        sphinx_commands.append("-f")

    retcode = feed_sphinx_apidoc(
        "-o",
        args.destdir,
        args.module_path,
        *sphinx_commands,  # can filter sphinx commands
    )

    if (
        retcode
        or "-h" in args.sphinx_commands
        or "--help" in args.sphinx_commands
    ):
        ps.exit(retcode)
    rename_rsts(args.module_path, args.destdir, force=args.force)


if __name__ == "__main__":
    main()
