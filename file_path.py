from __future__ import annotations

import os

from hypothesis import strategies as st


@st.composite
def file_path(
    draw: st.DrawFn,
    maxdepth: int | None = 15,
    extension: str | None = None,
    absolute: bool = True,
    pathsep: str = os.path.sep,
) -> str:
    # generate valid names for both filename and directories. The name can be
    # empty: this checks whether our function can tolerate non-normalized
    # filenames.
    # TODO: Allow filenames to be UTF-8 encoded. For that we need to ensure
    # that the filenames do not contain punctuation characters.
    char_gen = st.characters(blacklist_characters=[".", "/", "\\"])
    validname_st = st.text(char_gen, min_size=0)

    extension = (
        draw(st.text(char_gen, min_size=1)) if extension is None else extension
    )
    file = draw(validname_st)
    path = f"{pathsep}{file}.{extension}"

    loop_range = draw(st.integers(min_value=0, max_value=maxdepth))
    for _ in range(loop_range):
        path = f"{pathsep}{draw(validname_st)}{path}"
    return path if absolute else path[len(pathsep) :]
