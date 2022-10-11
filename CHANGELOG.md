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