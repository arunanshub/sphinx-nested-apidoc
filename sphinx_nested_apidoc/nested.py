import glob
import logging
import os
import subprocess
from os import path

logger = logging.getLogger(__name__)


def feed_sphinx_apidoc(*args):
    if ("-h" in args) or ("--help" in args):
        stdout = None
    else:
        stdout = subprocess.PIPE

    with subprocess.Popen(
        ["sphinx-apidoc", "-e", *args],
        stdout=stdout,
    ) as proc:
        stdout, stderr = proc.communicate()

        if stdout:
            logger.debug("Not showing sphinx-apidoc output to reduce clutter.")
        elif stderr:
            return 1

        return proc.returncode


def get_modname(module):
    return path.normpath(module).rsplit(path.sep, 1)[-1]


def get_package_structure(
    srcdir,
    modname=None,
    exclude=("__pycache__",),
):
    srcdir = path.normpath(srcdir)
    module_name = modname or get_modname(srcdir)
    for src, _, _ in os.walk(srcdir):
        if path.basename(src) in exclude:
            continue
        yield path.normpath(
            path.join(
                module_name,
                src.rsplit(module_name, 1)[-1].strip(path.sep),
            )
        )


def make_package_stucture(
    srcdir,
    destdir,
    modname=None,
    exclude=("__pycache__",),
):
    modname = modname or get_modname(srcdir)
    destdir = path.normpath(destdir)
    for package in get_package_structure(srcdir, modname, exclude):
        dest = path.join(destdir, package.split(modname)[-1].strip(path.sep))

        # yields a tuple with 2 elements:
        # pacakage is the original structure of the module
        # dest is the directory that will be created.
        yield package, dest.strip(path.sep)
        try:
            os.mkdir(dest)
        except FileExistsError:
            logger.warning(f"{dest} exists. Skipping.")
            pass


def rename_rsts(moddir, srcdir, destdir=None, force=False):
    # moddir will be used to compare the directory structure.
    # srcdir should have the .rst files already present.
    # destdir is where the nested structure will be kept.
    destdir = destdir or srcdir
    moddir, srcdir, destdir = [
        path.normpath(i) for i in (moddir, srcdir, destdir)
    ]

    if not path.exists(destdir):
        os.mkdir(destdir)

    dirs = list(make_package_stucture(moddir, destdir))
    modname = get_modname(moddir)
    files = glob.glob(path.join(srcdir, f"{modname}*.rst"))

    for src, dest in dirs:
        for file in files:
            as_dot = src.replace(path.sep, ".")
            basefile = path.basename(file)

            if basefile == as_dot + ".rst":
                if basefile == modname + ".rst":
                    continue
                new = path.join(dest, "index.rst")
                _try_rename(file, new, force)
                continue

            last_two_parts = ".".join(basefile.rsplit(".", 2)[-2:])
            if basefile == ".".join((as_dot, last_two_parts)):
                new = path.join(dest, last_two_parts)
                part = path.splitext(new)[0]
                if path.isdir(part):
                    logger.debug(
                        f"Assumption failed: {new} is a dir {part}. Skipping."
                    )
                    continue
                _try_rename(file, new, force)


def _try_rename(file, new, force):
    if os.path.exists(new):
        if not force:
            logger.info(f"Skipping generation of {new}. Only removing {file}")
            os.remove(file)
            return

    try:
        os.rename(file, new)
        logger.info(f"{file} -> {new}")
    except FileExistsError:
        logger.info(f"Forced: {new} exists. Removing.")
        os.remove(new)
        os.rename(file, new)
        logger.info(f"Forced: {file} -> {new}")
