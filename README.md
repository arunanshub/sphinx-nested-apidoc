# sphinx-nested-apidoc

[![CI](https://github.com/arunanshub/sphinx-nested-apidoc/actions/workflows/ci.yml/badge.svg)](https://github.com/arunanshub/sphinx-nested-apidoc/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Python Versions](https://img.shields.io/pypi/pyversions/sphinx-nested-apidoc)](https://pypi.org/project/sphinx-nested-apidoc)

When flattened is not enough.

## Installation

Use `pip` or `pip3` to install `sphinx-nested-apidoc`

```bash
pip install sphinx-nested-apidoc
```

or

```bash
pip3 install sphinx-nested-apidoc
```

## Introduction

`sphinx-apidoc` is a great tool for generating documentation, but it does not
replicate the directory structure of your package. `sphinx-nested-apidoc` aims
to solve that problem.

## Tutorial

Let's say we have the following directory structure of our package:

```
mymodule/
├── fruits/
│   ├── __init__.py
│   ├── mango.py
│   ├── pear.py
├── animals/
│   ├── special/
│   │   ├── __init__.py
│   │   ├── doggo.py
│   │   └── catto.py
│   ├── __init__.py
│   ├── monke.py
│   └── chimp.py
├── __init__.py
├── base.py
└── exceptions.py
```

And we want to generate documentation for this package in some directory `docs/`.

Let's see the difference.

### Using `sphinx-apidoc` we get

We use the following command:

```bash
sphinx-apidoc -o docs/ mymodule/ -e
```

It generates:

```
docs/
├── modules.rst
├── mymodule.animals.chimp.rst
├── mymodule.animals.monke.rst
├── mymodule.animals.rst
├── mymodule.animals.special.catto.rst
├── mymodule.animals.special.doggo.rst
├── mymodule.animals.special.rst
├── mymodule.base.rst
├── mymodule.exceptions.rst
├── mymodule.fruits.mango.rst
├── mymodule.fruits.pear.rst
├── mymodule.fruits.rst
└── mymodule.rst
```

This is not very clean, obviously.

### Using `sphinx-nested-apidoc` we get

We use the following command:

```bash
sphinx-nested-apidoc -o docs/ mymodule/
```

It generates:

```
docs/
├── modules.rst
└── mymodule/
    ├── animals/
    │   ├── chimp.rst
    │   ├── index.rst
    │   ├── monke.rst
    │   └── special/
    │       ├── catto.rst
    │       ├── doggo.rst
    │       └── index.rst
    ├── base.rst
    ├── exceptions.rst
    ├── fruits/
    │   ├── mango.rst
    │   ├── pear.rst
    │   └── index.rst
    └── index.rst
```

Looks clean!

### Want to name the package something else?

```bash
sphinx-nested-apidoc --package-name src -o docs/ mymodule/
```

It generates:

```
docs/
├── modules.rst
└── src/
    ├── animals/
    │   ├── chimp.rst
    │   ├── index.rst
    │   ├── monke.rst
    │   └── special/
    │       ├── catto.rst
    │       ├── doggo.rst
    │       └── index.rst
    ├── base.rst
    ├── exceptions.rst
    ├── fruits/
    │   ├── mango.rst
    │   ├── pear.rst
    │   └── index.rst
    └── index.rst
```

### As a Sphinx Extension

You can also use this as a sphinx extension.

Create a file called `docs/conf.py` and configure it like this:

```python
# ...
extensions = [
    "sphinx_nested_apidoc",
    # ...other extensions
]

# Name of the package directory.
sphinx_nested_apidoc_package_dir = "packagename"
# Name of the folder to put all the package documentation in. By default it is
# the name of the package itself.
sphinx_nested_apidoc_package_name = "src"
# ...
```

And then run:

```
sphinx-build docs docs/_build
```

## Usage Details

```text
usage: sphinx-nested-apidoc [-h] [-v | -q] [--version] [-f] [-n] -o DESTDIR
                            [--package-name PACKAGE_NAME] [-s SUFFIX]
                            [--implicit-namespaces]
                            module_path ...

Generates nested directory from sphinx-apidoc's flattened files. It is simply a
wrapper over sphinx-apidoc and you can pass additional arguments to it for
extended configuration.

positional arguments:
  module_path           Path to package to document.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase application verbosity. This option is
                        repeatable and will increase verbosity each time it is
                        repeated. This option cannot be used when -q/--quiet is
                        used. (default: 3)
  -q, --quiet           Disable logging. This option cannot be used when
                        -v/--verbose is used. (default: False)
  --version             show program's version number and exit
  -f, --force           Replace existing files. (default: False)
  -n, --dry-run         Run the script without creating files (default: False)
  -o DESTDIR, --output-dir DESTDIR
                        directory to place all output (default: None)
  --package-name PACKAGE_NAME
                        Name of the directory to put the package documentation
                        in. By default it is the name of the package itself.
                        (default: None)

sphinx-apidoc options:
  -s SUFFIX, --suffix SUFFIX
                        file suffix (default: rst)
  --implicit-namespaces
                        interpret module paths according to PEP-0420 implicit
                        namespaces specification (default: False)
  ...                   Commands and flags to supply to sphinx-apidoc. Note
                        that some arguments like `--dry-run` are ignored.

sphinx-nested-apidoc is licensed under MIT license. Visit
<https://github.com/arunanshub/sphinx-nested-apidoc> for more info.
```

## Sphinx Extension Configuration

The following configuration values are used:

| Option Name                                | Description                                                                                                     | Default            | Required? |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------|-----------|
| `sphinx_nested_apidoc_package_dir`         | This is where the package to document resides.                                                                  |                    | **YES**   |
| `sphinx_nested_apidoc_package_name`        | Name of the directory to put all the package documentation in. By default it is the name of the package itself. | `None`             |           |
| `sphinx_nested_apidoc_suffix`              | The suffix of the generated documentation files.                                                                | `rst`              |           |
| `sphinx_nested_apidoc_excluded_files`      | List of files (without extension) to exclude from modification/renaming.                                        | `index`, `modules` |           |
| `sphinx_nested_apidoc_module_first`        | put module documentation before submodule documentation.                                                        | `False`            |           |
| `sphinx_nested_apidoc_implicit_namespaces` | interpret module paths according to PEP-0420 implicit namespaces specification.                                 | `False`            |           |

## Some additional details

### What it does

- As you saw earlier, it generates a nested directory from a flattened one.
- Under the hood, it uses `sphinx-apidoc`. More on this below.

As stated above, `sphinx-nested-apidoc` uses `sphinx-apidoc` internally. This means,
you can configure `sphinx-apidoc` from `sphinx-nested-apidoc`. For example:

```bash
# You can pass arguments like this:
sphinx-nested-apidoc -o docs/ mymodule/ -- -M -F --ext-githubpages
# or you can simply omit the '--'.
```

Everything after the required positional argument of `sphinx-nested-apidoc` is
passed to `sphinx-apidoc`.

### What it does not do

- It does not modify the contents of the file. It just renames (or moves) them.
- It is not a standalone tool. It requires `sphinx-apidoc` for its work.

## License

[MIT](https://choosealicense.com/licenses/mit/)
