## v1.2.1 (2022-11-06)

### Refactor

- **ext**: make `ext` an internal module

## v1.2.0 (2022-10-28)

### Feat

- **ext**: add `rename_destdir_to` as extension argument
- **main**: add CLI flag to specify the name of directory in output dir
- **core**: allow renaming of generated package directory
- export `setup` function for `sphinx`
- **ext**: allow `sphinx-nested-apidoc` to be used as a sphinx extension
- **core**: allow caller to specify excluded files and check if given path is a file
- **core**: clean up leftover files if files are not renamed

### Fix

- **ext**: remove unused and redundant configuration values
- **core**: handle santization of names when name is like `.name`
- **main**: check if `rename_destdir_to` is None
- **main**: remove erroneous `--output-dir` flag

### Refactor

- **core**: log when creating directory
- **main**: rename cli argument to `--package-name`
- **core**: make `sanitize_path` a public function and remove unnecessary caching
- **main**: display complete Exception info on failure
- **core**: rename `args` to `sphinx_arguments`

### Perf

- **main**: sanitize argument beforehand to avoid unnecessary caching
- **core**: prevent repeated calls to `os.makedirs`
- **core**: cache the argument of `is_packagedir`

## v1.1.1 (2022-10-12)

### Fix

- **main**: remove unnecessary exception blocks; return `int` from main

## v1.1.0 (2022-10-12)

### Feat

- **main**: allow passing list of str to main; pass `force` flag for renaming
- **core**: use `apidoc.main` instead of `subprocess`; use `force` flag for renaming

## v1.0.0 (2022-10-12)

### BREAKING CHANGE

- Previously it ignored the topmost directory, ie. a file
of name `a.b.c.rst` would have the name `b/c.rst`. Now for `a.b.c.rst`,
`a/b/c.rst` is generated.

### Feat

- **core**: process additional arguments and raise error if command fails
- **__main__**: add additional flags to parser
- **core**: handle namespace and packages properly

### Refactor

- **init**: change the logger format to include `filename:lineno`
- **__init__**: use `%` formatting and add `__future__` import
- move codebase into `src` directory

## v0.3.2 (2021-08-22)

### Refactor

- **nested**: backport code to lower python version
