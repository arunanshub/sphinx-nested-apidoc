# sphinx-nested-apidoc

<p align="center">
  <a href="https://pypi.org/project/sphinx-nested-apidoc/" alt="Upload Python Package">
    <img src="https://github.com/arunanshub/sphinx-nested-apidoc/workflows/Upload%20Python%20Package/badge.svg" />
  </a>
</p>

When flattened is not enough.

# Installation

Use `pip` or `pip3` to install `sphinx-nested-apidoc`

```bash
pip install sphinx-nested-apidoc
```

or

```bash
pip3 install sphinx-nested-apidoc
```

# Introduction

`sphinx-apidoc` is a great tool for generating documentation, but it does not
replicate the directory structure of your package. `sphinx-nested-apidoc` aims
to solve that problem.

# Usage Overview

Let's say we have the following directory structure of our package:

```
mymodule/
├── fruits/
│   ├── __init__.py
│   ├── apple.py
│   ├── pear.py
│   ├── guava.py
│   └── mango.py
├── animals/
│   ├── special/
│   │   ├── __init__.py
│   │   ├── doggo.py
│   │   └── catto.py
│   ├── __init__.py
│   ├── bear.py
│   ├── giraffe.py
│   ├── monke.py
│   └── chimp.py
├── __init__.py
├── base.py
├── exceptions.py
└── secret.py
```

And we want to generate documentation for this package in some directory `docs/`.

## A short comparison

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
├── mymodule.animals.bear.rst
├── mymodule.animals.chimp.rst
├── mymodule.animals.giraffe.rst
├── mymodule.animals.monke.rst
├── mymodule.animals.rst
├── mymodule.animals.special.catto.rst
├── mymodule.animals.special.doggo.rst
├── mymodule.animals.special.rst
├── mymodule.base.rst
├── mymodule.exceptions.rst
├── mymodule.fruits.apple.rst
├── mymodule.fruits.guava.rst
├── mymodule.fruits.mango.rst
├── mymodule.fruits.pear.rst
├── mymodule.fruits.rst
├── mymodule.rst
└── mymodule.secret.rst
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
├── animals/
│   ├── bear.rst
│   ├── chimp.rst
│   ├── giraffe.rst
│   ├── index.rst
│   ├── monke.rst
│   └── special
│       ├── catto.rst
│       ├── doggo.rst
│       └── index.rst
├── fruits/
│   ├── apple.rst
│   ├── guava.rst
│   ├── index.rst
│   ├── mango.rst
│   └── pear.rst
├── index.rst
├── base.rst
├── exceptions.rst
├── modules.rst
├── mymodule.rst
└── secret.rst
```

Looks clean!

# Usage Details

```
usage: sphinx-nested-apidoc [-h] [-v | -q] [--version] [-f] -o DESTDIR
                            module_path ...

sphinx-nested-apidoc: When flattened is not enough. sphinx-nested-apidoc is a
command-line tool which generates nested directory from sphinx-apidoc's
flattened rst files. It is simply a wrapper over sphinx-apidoc and you can
pass additional arguments to it for extended configuration.

positional arguments:
  module_path           Path to package to document.
  sphinx_commands       Commands and flags to supply to sphinx-apidoc.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase application verbosity. This option is
                        repeatable and will increase verbosity each time it is
                        repeated. This option cannot be used when -q/--quiet
                        is used.
  -q, --quiet           Disable logging. This option cannot be used when
                        -v/--verbose is used.
  --version             show program's version number and exit
  -f, --force           Replace existing files.
  -o DESTDIR, --output-dir DESTDIR
                        directory to place all output

sphinx-nested-apidoc is licensed under MIT license. Visit
<https://github.com/arunanshub/sphinx-nested-apidoc> for more info.
```

# Some additional details

## What it does

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

## What it does not do

- It does not modify the contents of the file. It just renames (or moves) them.
- It is not a standalone tool. It requires `sphinx-apidoc` for its work.

# License

[MIT](https://choosealicense.com/licenses/mit/)
