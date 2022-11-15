from __future__ import annotations

import os

from hypothesis import given
from hypothesis_fspaths import fspaths

from sphinx_nested_apidoc import core

from . import dotted_filenames


@given(path=fspaths())
def test_sanitize_path(path: str):
    sanitized_path = core.sanitize_path(os.fsdecode(path))
    assert not os.path.isabs(sanitized_path)


@given(dotted_filenames())
def test_get_nested_dir_filename(filename: str):
    nested = core.get_nested_dir_filename(filename)
    path, ext = os.path.splitext(nested)
    # the only `.` in nested path is the extension separator.
    assert not path.count(".")
    # the extensions of filename and nested path should match.
    assert os.path.splitext(filename)[-1] == ext
