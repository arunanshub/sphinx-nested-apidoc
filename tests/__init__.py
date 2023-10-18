from __future__ import annotations

import os
from dataclasses import dataclass
import re

from hypothesis import strategies as st


@dataclass
class PathLike(os.PathLike):
    path: str

    def __fspath__(self):
        return self.path


@st.composite
def generate_path(draw: st.DrawFn, *, allow_pathlike=True) -> str | PathLike:
    windows_path_re = re.compile(r"^([A-z]:\\)?(\w+\\)*(\w+\.)+\w+$")
    unix_path_re = re.compile(r"^\/?(\w+\/)*(\w+\.)+\w+$")
    windows_path_strategy = st.from_regex(windows_path_re, fullmatch=True)
    unix_path_strategy = st.from_regex(unix_path_re, fullmatch=True)
    path = draw(st.one_of(windows_path_strategy, unix_path_strategy))

    if allow_pathlike:
        pathlike_strategy = st.sampled_from([str, PathLike])
        pathlike_fn = draw(pathlike_strategy)
        path = pathlike_fn(path)

    return path
