from __future__ import annotations

import os

from hypothesis import given
from hypothesis_fspaths import fspaths

from sphinx_nested_apidoc import core


@given(path=fspaths())
def test_file_path(path: str):
    sanitized_path = core.sanitize_path(os.fsdecode(path))
    assert not os.path.isabs(sanitized_path)
